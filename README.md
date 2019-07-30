# Fitbit-smart-alarm

This is a "hacky" implementation of a Fitbit smart alarm for older Fitbit devices which do not come with one.
A smart alarm is an alarm that tries to wake you up in between times t1 and t2, when it deems you are the most awake.

The overall implementation looks like:
SLIKA
The smart alarm is implemented on Heroku; a server which, among many other things, let's you run a scheduled python script for free.
The app continuously asks the Fitbit api for your current heart rate (HR). If the HR is above a certain threshold, it send a request to set an alarm. 
When the alarm is set, an HR graph is created and saved to your Google Drive. 
On the mobile side, the Automate app continuously synchronizes your watch with the phone, so the latest data would be available on the Fitbit api.

### 1) Fitbit api
To obtain Fitbit credentials you need to create a Fitbit app following this link. All the instructions are in the image below.
SLIKA CREDENTIALSA

### 2) Heroku
The python script "smart_alarm.py" does all the work on a Heroku server.

To setup your Heroku app, you firstly need to create a Heroku account. 
Use the Heroku CLI to setup your app: LINK TO INSTALL HEROKU, LINK TO CREATE APP.

Next, download this repository by following this link (https://help.github.com/en/articles/cloning-a-repository). Instead of cloning it, it may be easier to download it as a ZIP and extract it to the Heroku app folder.

Next, we need to setup a environment variables and the Heroku scheduler.

### 3) Google Drive
