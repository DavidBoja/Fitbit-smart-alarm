
import pandas as pd
import sys
import requests
import json
from datetime import datetime, timedelta
import time
import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import matplotlib
matplotlib.use('Agg')
import matplotlib.dates as mdates

import matplotlib.pyplot as plt


UTC_OFFSET = '+01:00'

plt.rc('axes', titlesize=50)
plt.rc('xtick', labelsize=30)
plt.rc('ytick', labelsize=30)

def auth_google_drive():
    '''
    Authorize script to use your google drive.
    Return:
    gauth - GoogleDrive object with your authorized g. drive
    '''

    from pydrive.auth import GoogleAuth
    from pydrive.drive import GoogleDrive

    gauth = GoogleAuth()
    gauth.DEFAULT_SETTINGS['client_config_file'] = "client_secret.json"
    gauth.LoadCredentialsFile("mycreds.txt")

    if gauth.credentials is None:
        # Authenticate if they're not there
        gauth.LocalWebserverAuth()
    elif gauth.access_token_expired:
    # Refresh them if expired
        gauth.Refresh()
    else:
        # Initialize the saved creds
        gauth.Authorize()
    # Save the current credentials to a file
    gauth.SaveCredentialsFile("mycreds.txt")

    drive = GoogleDrive(gauth)

    return drive


def save_heart_plot(my_heart, heart_threshold):
    '''
    Create a plot with time on x axis and heart rate on y axis.
    Save the plot to your google drive.
    '''

    # Create plot
    fig, ax = plt.subplots(1, figsize=(50,20))
    fig.autofmt_xdate()
    plt.plot(my_heart.time, my_heart.value, linewidth=5)

    # try:
    #     plt.gcf().subplots_adjust(bottom=0.2)
    # except Exception as e:
    #     print('COULD NOT do plt.gcf().subplots_adjust(bottom=0.2)')
    #     print(e)


    # Format time on x axis
    xfmt = mdates.DateFormatter('%H:%M:%S')
    ax.xaxis.set_major_formatter(xfmt)
    ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=30))

    # Plot heart threshold horizontal line
    plt.plot(my_heart.time, [heart_threshold]*len(my_heart), color='red', linewidth=4)

    # More formatting
    date_now = datetime.now().strftime('%d_%m_%y')
    plt.title('Sleeping heart rates {}'.format(date_now))
    plt.tight_layout()

    # Save plot to disk
    image_name = 'Sleeping_heart_rates_{}'.format(date_now)
    plt.savefig(image_name)
    #plt.show()

    if image_name in os.listdir():
        print('Saved image name is: {}'.format(image_name))
    else:
        print('I did not save an image. What a great program I am!')
        return


    # Upload image to google drive
    try:
        drive = auth_google_drive()

        file = drive.CreateFile({'title':image_name})
        file.SetContentFile(image_name)
        file.Upload()
    except Exception as e:
        print('COULD NOT SAVE IMAGE TO GOOGLE DRIVE -.- !')
        print(e)


def set_alarm(alarm_time, profile, tracker_id, ACCESS_TOKEN):
    '''
    Create alarm on fitbit api at alarm_time time.
    Return:
    True --> that indicates the alarm is set
    False --> the alarm was not set
    '''

    weekdays = ['SUNDAY', 'MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY']
    today = weekdays[datetime.today().weekday()]

    alarm_time = alarm_time.strftime("%H:%M") + UTC_OFFSET

    r = requests.post('https://api.fitbit.com/1/user/{}/devices/tracker/{}/alarms.json'
                      .format(profile['encodedId'],tracker_id),
                      data = {'time':alarm_time,
                              'enabled':True,
                              'recurring':False,
                              'weekDays':today},
                      headers={'Authorization': 'Bearer {}'.format(ACCESS_TOKEN)})

    if (r.status_code == requests.codes.ok):
        return True
    else:
        return False


def set_smart_alarm(t1,t2,heart_threshold,second_threshold):
    '''
    Set a smart alarm from t1 hours till t2 hours.
    The alarm checks if heart rate crosses heart_threshold for a 
    duration of second_threshold seconds.
    If the threshold is crossed, the alarm is set.
    If the threshold is not crossed, and the clock reaches t2 hours,
    the alarm is set at t2 hours.
    DISCLAIMER : t1 is not actually used. It is set on heroku as 
    a daily scheduled task.
    '''
    ##############################################################
    #                   PERSONAL DATA
    ##############################################################

    CLIENT_ID = os.environ['CLIENT_ID']
    CLIENT_SECRET = os.environ['CLIENT_SECRET']

    alarm_set = False

    ##############################################################
    #                FITBIT AUTHORIZATION
    ##############################################################


    # create instance of google chrome browser to control with selenium
    chrome_exec_shim = os.environ.get("GOOGLE_CHROME_BIN", "chromedriver")
    CHROMEDRIVER_PATH = os.environ.get('CHROMEDRIVER_PATH')
    opts = webdriver.ChromeOptions()
    opts.binary_location = chrome_exec_shim
    opts.add_argument('--headless')
    opts.add_argument('--no-sandbox')
    opts.add_argument('--disable-dev-shm-usage')
    opts.add_argument('--disable-gpu')
    browser = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, chrome_options=opts)

    # The url to authorize script to use everything the fitbit api offers
    # (activity, heart_rate, sleep, weight,..)
    url = 'https://www.fitbit.com/oauth2/authorize?response_type=code&client_id={}&redirect_uri=http%3A%2F%2F127.0.0.1%3A8080%2F&scope=activity%20heartrate%20location%20nutrition%20profile%20settings%20sleep%20social%20weight&expires_in=604800'.format(CLIENT_ID)
    browser.get(url)

    time.sleep(5)


    # Login to your fitbit account
    EMAIL = os.environ.get('EMAIL')
    PASSW_FIT = os.environ.get('PASSW_FIT')

    email = browser.find_element_by_xpath('//input[@placeholder="Your email address"]')
    email.send_keys(EMAIL)
    passw = browser.find_element_by_xpath('//input[@placeholder="Enter your password"]')
    passw.send_keys(PASSW_FIT)

    passw.send_keys(Keys.ENTER)

    time.sleep(10)

    print('selenium done')

    # Get a code from the url with which you can get the ACCESS_TOKEN
    # and REFRESH_TOKEN
    try:
        code = browser.current_url.split('?code=')[1].split('#_=_')[0]
    except Exception as e:
        print('Could not get code from browser url. The link is:')
        print(browser.current_url)
        print(e)
        sys.exit()

    FITBIT_AUTHORIZATION = os.environ.get('FITBIT_AUTHORIZATION')

    r = requests.post('https://api.fitbit.com/oauth2/token',
                      data = {'clientId':CLIENT_ID,
                              'grant_type':'authorization_code',
                              'redirect_uri':'http://127.0.0.1:8080/',
                              'code':code},
                      headers={'Authorization': 'Basic {}'.format(FITBIT_AUTHORIZATION),
                                'Content-Type': 'application/x-www-form-urlencoded'})


    content = json.loads(r.content)

    ACCESS_TOKEN = content['access_token']
    REFRESH_TOKEN = content['refresh_token']

    print('#####################################################################')
    print('ACCESS TOKEN {}....'.format(ACCESS_TOKEN[:5]))
    print('REFRESH_TOKEN {}....'.format(REFRESH_TOKEN[:5]))
    print('####################################################################')

    browser.close()

    ##############################################################
    #                   GET YOUR PROFILE ID
    ##############################################################
    r = requests.get('https://api.fitbit.com/1/user/-/profile.json',
                     headers={'Authorization': 'Bearer {}'.format(ACCESS_TOKEN)})

    profile = (json.loads(r.content))['user']
    if profile:
        print('Got my profile')
    else:
        print('Error while getting profile, check again')


    ##############################################################
    #             GET TRACKER ID FOR MANAGING ALARMS
    ##############################################################
    r = requests.get('https://api.fitbit.com/1/user/-/devices.json'
                 .format(profile['encodedId']),
            headers={'Authorization': 'Bearer {}'.format(ACCESS_TOKEN)})

    tracker_id = json.loads(r.content)[0]['id']
    print('Tracker id: {}'.format(tracker_id))

    ##############################################################
    #                DELETE PREVIOUS ALARMS
    ##############################################################
    r = requests.get('https://api.fitbit.com/1/user/{}/devices/tracker/{}/alarms.json'
                 .format(profile['encodedId'],tracker_id),
            headers={'Authorization': 'Bearer {}'.format(ACCESS_TOKEN)})

    alarms = json.loads(r.content)['trackerAlarms']

    for alarm in alarms:
        r = requests.delete('https://api.fitbit.com/1/user/{}/devices/tracker/{}/alarms/{}.json'
                            .format(profile['encodedId'], tracker_id, alarm['alarmId']),
                            headers={'Authorization': 'Bearer {}'.format(ACCESS_TOKEN)})

    print('Deleted all previous alarms. The tracker needs to sync for the effects to take change')

    ##############################################################
    #           FIRST API REQUEST TO GET CHECK IF
    #               FITBIT IS SYNCING AT ALL
    ##############################################################
    print('Making first api request for heart rates')
    r = requests.get('https://api.fitbit.com/1/user/{}/activities/heart/date/today/1d/1sec.json'
                     .format(profile['encodedId']),
                headers={'Authorization': 'Bearer {}'.format(ACCESS_TOKEN)})

    my_heart = json.loads(r.content)['activities-heart-intraday']['dataset']
    my_heart = pd.DataFrame(my_heart)

    # If there aren't 10 seconds of data available, fitbit is not syncing,
    # meaning I probably did not want an alarm to wake me up
    # aborting execution
    try:
        last_ten_heart_rates = my_heart.loc[(my_heart.shape[0]-10):,:]
    except:
        print('FITBIT IS NOT SYNCING DUDE')
        return

    try:
        auth_google_drive()
    except Exception as e:
        print('COULD NOT AUTHORIZE GOOGLE DRIVE.')
        print('THE ERROR IS: ')
        print(e)

    print('Last ten heart rates:')
    print(last_ten_heart_rates)

    # if my heart rate went above the heart_threshold in the last 10 sec,
    # and was above that level for at least second_threshold,
    # sound the alarm because i seem to be waking up

    if (sum(last_ten_heart_rates.value > heart_threshold) > second_threshold):
        # set alarm
        last_ten_heart_rates['time'] = pd.to_datetime(last_ten_heart_rates['time'])
        alarm_time = last_ten_heart_rates.time[last_ten_heart_rates.index[-1]] + timedelta(minutes=5)
        alarm_set = set_alarm(alarm_time, profile, tracker_id, ACCESS_TOKEN)

        # Save sleep graph
        save_heart_plot(my_heart, heart_threshold)

        print('Alarm set for {}:{}. Wake up you lazy ass mofo'.format(alarm_time.hour,alarm_time.minute))

    if not alarm_set:
        # mark the last checked time we checked if you were sleeping
        # last_checked_index is the index of that time in the dataframe
        print('Seems you haven\'t been trying to wake up!')
        last_checked_index = my_heart.shape[0]


    ##############################################################
    #       MAKE API REQUESTS FOR YOUR HEART RATE WHILE THE
    #           ALARM IS NOT SET AND THE TIME IS BELOW t2
    ##############################################################
    print('Entering while statement')
    while((not alarm_set) and (datetime.now().hour < t2)):
        r = requests.get('https://api.fitbit.com/1/user/{}/activities/heart/date/today/1d/1sec.json'
                         .format(profile['encodedId']),
                    headers={'Authorization': 'Bearer {}'.format(ACCESS_TOKEN)})

        my_heart = json.loads(r.content)['activities-heart-intraday']['dataset']
        my_heart = pd.DataFrame(my_heart)
        my_heart['time'] = pd.to_datetime(my_heart['time'])

        # Check only from the last time we made a check
        my_heart2 = my_heart.loc[last_checked_index:,:].copy()
        print('my_heart2:')
        print(my_heart2)

        # if my heart rate went above the heart_threshold in the last number of sec,
        # (from the last time we made a check if I was waking up)
        # and was above that level for at least second_threshold,
        # sound the alarm because i seem to be waking up

        if sum(my_heart2.value > heart_threshold) > second_threshold:
            # set alarm
            alarm_time = my_heart2.loc[my_heart2[my_heart2.value > heart_threshold].index[-1],:].time + timedelta(minutes=5)
            alarm_set = set_alarm(alarm_time, profile, tracker_id, ACCESS_TOKEN)

            # Save sleep graph
            save_heart_plot(my_heart, heart_threshold)

            print('Alarm set for {}:{}'.format(alarm_time.hour,alarm_time.minute))

        else:
            print('Seems you havent been trying to wake up you lazy bastard')
            last_checked_index = my_heart.shape[0]
            time.sleep(120)


    # If I wasn't trying to wake up before t2 hours, set alarm for t2 hours + 5 min
    if not alarm_set:
        alarm_time = datetime.now() + timedelta(minutes=5)
        set_alarm(alarm_time, profile, tracker_id, ACCESS_TOKEN)

        # Save sleep graph
        save_heart_plot(my_heart, heart_threshold)

        print('Supriiiiiiiiiiiise!! STOP SLEEPING')

if __name__ == "__main__":
    import argparse

    parser_of_args = argparse.ArgumentParser(description='Set smartly choosen alarm')
    parser_of_args.add_argument('t1', type=int,
                                help='You dont want to be waken before this time. \n' +
                                'NOTE: argument t1 is not used here, but rather set on the'+
                                'server that runse the script every day at t1 hours')
    parser_of_args.add_argument('t2',type=int,
                                help='You want to be waken up before this time')
    parser_of_args.add_argument('heart_threshold',type=int,
                                help='Heart rate above which you deem to be awake')
    parser_of_args.add_argument('second_threshold',type=int,
                                help='How long does your heart rate need to be above heart_threshold for you to deem you are awake')
    args = parser_of_args.parse_args()



    set_smart_alarm(args.t1,args.t2, args.heart_threshold, args.second_threshold)
