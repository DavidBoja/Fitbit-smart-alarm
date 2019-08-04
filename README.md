# Fitbit-smart-alarm

This is a "hacky" implementation of a smart alarm for older Fitbit devices which do not come with one.
A smart alarm is an alarm that tries to wake you up in between time t1 and t2, when it deems you are the most awake. 

The overall implementation looks like:
![Implementation](https://github.com/DavidBoja/Fitbit-smart-alarm/blob/master/images/Fitbit%20drawing.jpg)
The smart alarm is implemented on Heroku; a server which, among many other things, let's you run a scheduled python script for free.
The app continuously asks the Fitbit api for your current heart rate (HR). If the HR is above a certain threshold, it send a request to set an alarm. 
When the alarm is set, an HR graph is created and saved to your Google Drive. 
On the mobile side, the Automate app continuously synchronizes your watch with the phone, so the latest data would be available on the Fitbit api.

### 1) Fitbit api
To obtain Fitbit credentials you need to create a Fitbit app following [this link](https://dev.fitbit.com/apps/new) with the following information:
![Create an app for Fitbit](https://github.com/DavidBoja/Fitbit-smart-alarm/blob/master/images/fitbit_api_register_app.png)
Once you have created the app, you'll obtain the Client ID and Client Secret, which will be used to make api requests.

Go to the "Manage my apps" tab and click on your app. Click on the "OAuth 2.0 tutorial page" and follow the instructions till the 1A) step. The output of step 1A) gives you a couple of lines of a curl request. The line we're interested in is
```
-H 'Authorization: Basic whatever_your_code_is'
```
We will remember the "whatever_your_code_is" variable as FITBIT_AUTHORIZATION in step 2) of this tutorial.

![Fitbit authorization](https://github.com/DavidBoja/Fitbit-smart-alarm/blob/master/images/fitbit_authorization_hidden.png)

### 2) Heroku
The python script "smart_alarm.py" does all the work on a Heroku server.

To setup your Heroku app, you firstly need to create a [Heroku](https://heroku.com) account. 
Use the Heroku CLI to create your app by following [these steps](https://devcenter.heroku.com/articles/heroku-cli).

Next, download this repository locally by following [this link](https://help.github.com/en/articles/cloning-a-repository). Instead of cloning it from the terminal, it may be easier to download it as a ZIP and extract it to the Heroku app folder.

Next, we need to setup environment variables and the Heroku scheduler. <br>
Login with your account to [Heroku.com](https://dashboard.heroku.com/apps) and find the Settings tab in your app just created.
There, you need to add the following variables (listed as key:value):
1. CHROMEDRIVER_PATH: /app/.chromedriver/bin/chromedriver
2. CLIENT_ID: the Fitbit Client ID obtained from step 1)
3. CLIENT_SECRET: the Fitbit Client Secret obtained from step 1)
4. EMAIL: your Fitbit login email
5. FITBIT_AUTHORIZATION: variable from step 1)
6. GOOGLE_CHROME_BIN: /app/.apt/usr/bin/google-chrome
7. PASSW_FIT: your Fitbit account password
8. TZ: your timezone (you can find the complete list [here](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones))

![config variables](https://github.com/DavidBoja/Fitbit-smart-alarm/blob/master/images/config_vars_hidden.png)

Scrolling down, you need to add 2 buildpacks in the Buildpacks section by pressing "Add buildpack" and pasting the following two repos one at a time:
1. https://github.com/heroku/heroku-buildpack-chromedriver.git
2. https://github.com/heroku/heroku-buildpack-google-chrome.git

The next step is to set the Heroku scheduler.
Go to the Resources tab of your app on the Heroku page. In the text box "Quickly add add-ons from Elements" type in "Heroku Scheduler" and install it. Now, on the overveiw page, there's an installed app Heroku scheduler; click on it and add a new job "every day at.." whatever time you want. Be careful of the timezones. In the "Run Command" you'll put the smart alarm script:
```
python smart_alarm.py t1 t2 heart_threshold second_threshold
```
where the parameters are the following:
1. t1 (7) --> integer signaling the hour from which the smart alarm tries to wake you up.
              the parameter is NOT USED because time t1 is set with the Heroku Scheduler rather than the script
2. t2 (8) --> integer signaling the hour untill the smart alarm tries to wake you up
3. heart_threshold (75) --> integer signaling the HR above which you deem yourself to be awake (or awakeining)
4. second_threshold (1) --> integer signaling how many seconds does your heart rate need to be above the heart_threshold to
                            create the alarm


![heroku_scheduler](https://github.com/DavidBoja/Fitbit-smart-alarm/blob/master/images/heroku_scheduler.png)
My smart alarm tries to wake me up from 7am and 8am. It sets an alarm if my HR is above 75 for 1 second. The Heroku Scheduler recurrence is set to 5am since my timezone is UTC+02:00.

NOTE: the parameter t2 needs to be "bigger" than the time of recurrence set on the Heroku Scheduler since the app continues to make api requests until the alarm is not set or the time has not reached t2.

### 3) Google Drive (OPTIONAL)
After the alarm has been set, an HR graph is created and saved to your Google Drive.
To enable the Google Drive API follow [this page](https://developers.google.com/drive/api/v2/enable-drive-api). This should provide you with a credentials.json file which will allow you authentification. 

By having the credentials.json run the following python code locally to obtain the "mycreds.txt" file. This will run a window in your internet browser. Follow the instructions and authorize.
```
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

gauth = GoogleAuth()
gauth.DEFAULT_SETTINGS['client_config_file'] = "client_secret.json"

gauth.LocalWebserverAuth()

gauth.SaveCredentialsFile("mycreds.txt")
```
The "credentials.json" and "mycreds.txt" should be in the project folder before you push your app to the Heroku servers (if you want the Google Drive functionality).

### 4) Automate app
The automate app is downloadable from the Google Play store [here](https://play.google.com/store/apps/details?id=com.llamalab.automate&referrer=utm_source%3Dhomepage). Install it. 
Depending on the version of Android, you may need to install the "Automate connectivity permissions" and "Automate superuser permissions" apps for allowing Android to compute Automate Flows without rooting your phone.
On the community pages, there is an FlowChart by the name "Fitbit smart alarm" by user "DavidBoja". Download it. This FlowChart synchronizes the watch with the Fitbit app on a tighter interval than Fitbit.

### 5) Fitbit app
In the account settings for the Fitbit app, select your device. Set the "All-Day Sync", "Always Connected" and "Keep-Alive Widget" to ON status, as this improves watch-phone communications.

### 6) Usage
Before going to bed, turn on the Automate app and lock the phone. The app will sync the Fitbit watch and phone the whole night. At the time you wanted your alarm to wake you up (the time you set on Heroku) the watch will continue synching while the Heroku app tries to find an appropriate time to wake you up. If your HR doesen't cross the heart_threshold, the app sets an alarm for time t2 + 5 minutes. After an alarm has been set, a message is displayed on your phone from the Automate app with the appropriate battery consumption during the syching time.
