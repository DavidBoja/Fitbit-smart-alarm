# Fitbit-smart-alarm

This is a "hacky" implementation of a Fitbit smart alarm for older Fitbit devices which do not come with one.
A smart alarm is an alarm that tries to wake you up in between time t1 and t2, when it deems you are the most awake.

The overall implementation looks like:
![Implementation](https://github.com/DavidBoja/Fitbit-smart-alarm/blob/master/images/Fitbit%20drawing.jpg)
The smart alarm is implemented on Heroku; a server which, among many other things, let's you run a scheduled python script for free.
The app continuously asks the Fitbit api for your current heart rate (HR). If the HR is above a certain threshold, it send a request to set an alarm. 
When the alarm is set, an HR graph is created and saved to your Google Drive. 
On the mobile side, the Automate app continuously synchronizes your watch with the phone, so the latest data would be available on the Fitbit api.

### 1) Fitbit api
To obtain Fitbit credentials you need to create a Fitbit app following [this link](https://dev.fitbit.com/apps/new). All the instructions are in the image below.
![Create an app for Fitbit](https://github.com/DavidBoja/Fitbit-smart-alarm/blob/master/images/fitbit_api_register_app.png)
After creating the app, you obtain the client ID and Client Secret, which will be used to make api requests.

### 2) Heroku
The python script "smart_alarm.py" does all the work on a Heroku server.

To setup your Heroku app, you firstly need to create a [Heroku](https://heroku.com) account. 
Use the Heroku CLI to create your app by following [these steps](https://devcenter.heroku.com/articles/heroku-cli).

Next, download this repository by following [this link](https://help.github.com/en/articles/cloning-a-repository). Instead of cloning it from the terminal, it may be easier to download it as a ZIP and extract it to the Heroku app folder.

Next, we need to setup a environment variables and the Heroku scheduler.
Login with your account to [Heroku.com](https://dashboard.heroku.com/apps) and find the Settings tab in your app.
There, you need to add the following variables (listed as key:value):
1. CHROMEDRIVER_PATH: /app/.chromedriver/bin/chromedriver
2. CLIENT_ID: the Fitbit Client ID obtained from step 1)
3. CLIENT_SECRET: the Fitbit Client Secret obtained from step 1)
4. EMAIL: Fitbit login email
5. FITBIT_AUTHORIZATION:
6. 
SLIKA ENV VARS
Scrolling down, you need to add 2 buildpacks in the Buildpacks section by oressing Add buildpack and pasting the following two repos one at a time:
1. https://github.com/heroku/heroku-buildpack-chromedriver.git
2. https://github.com/heroku/heroku-buildpack-google-chrome.git

### 3) Google Drive (OPTIONAL)
After the alarm has been set, an HR graph is created and saved to your Google Drive.
To be able to use Google Drive, you need to 
For the first time, you might need to run 

### 4) Automate app

### 5) Fitbit app

### 6) Usage
