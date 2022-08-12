# Books2Notion
**Python script for syncing Google Play Books Highlights to Notion**
#### **[Demo Notion pages with highlights](https://quark-plane-15f.notion.site/4bd2a74b373a48f488a6ba86eb2b309c?v=4d15601367de4de3a72c8ac903cce14a "Notion pages containing highlights")**
[![Google Play Books](https://i.imgur.com/42ozIyz.png "Google Play Books")](https://i.imgur.com/42ozIyz.png "Google Play Books")
[![Notion Notes](https://i.imgur.com/qgQUpSf.png "Notion Notes")](https://i.imgur.com/qgQUpSf.png "Notion Notes")

---

### Table of Contents
- [Books2Notion](#books2notion)
    + [Table of Contents](#table-of-contents)
  * [Usage](#usage)
      - [Sync Modes](#sync-modes)
    + [Automatic](#automatic)
    + [Run Manually](#run-manually)
  * [Installation and Setup](#installation-and-setup)
    + [1. Clone Git repo](#1-clone-git-repo)
    + [2.Install Python Modules](#2install-python-modules)
    + [3.Authorize Notion](#3authorize-notion)
      - [a. Get Notion Integration Token](#a-get-notion-integration-token)
      - [b. Duplicate template and share it to integration](#b-duplicate-template-and-share-it-to-integration)
    + [4. Authorize Google APIs](#4-authorize-google-apis)
      - [a. Create Google cloud project](#a-create-google-cloud-project)
      - [b. Create OAuth consent screen](#b-create-oauth-consent-screen)
      - [c. Create OAuth2.0 credentials](#c-create-oauth20-credentials)
      - [d. Enable APIs](#d-enable-apis)
    + [5. Get env variables](#5-get-env-variables)
      - [a. Get NOTION_DATABASE_ID](#a-get-notion_database_id)
      - [b. Get DRIVE_FOLDER_ID](#b-get-drive_folder_id)
      - [c. Get IMAGE_HOST_KEY](#c-get-image_host_key)
      - [d. Get TIME_OFFSET](#d-get-time_offset)
    + [6. Authorize script](#6-authorize-script)
    + [7. Schedule script](#7-schedule-script)
      - [Heroku](#heroku)
        * [a. Create Heroku Account](#a-create-heroku-account)
        * [b. Install Heroku cli](#b-install-heroku-cli)
        * [c. Heroku login](#c-heroku-login)
        * [d. Create  app](#d-create--app)
        * [e. Fill env variables](#e-fill-env-variables)
        * [f. add buildback](#f-add-buildback)
        * [g. deploy application](#g-deploy-application)
      - [Local](#local)

---

## Usage
Red highlights are reserved for saving new words, it gets added to 'New Words' database along with definition fetched from [Wiktionary](https://en.wiktionary.org/wiki/Wiktionary:Main_Page "Wiktionary")    
#### Sync Modes
1. `append` - appends new highlights and new words to notion, but won't sync highlights and new words from pages that have been synced before
2. `sync` - syncs complete highlights of the books to notion
3. `sync-full` - syncs complete highlights and new words

### Automatic
Follow [7. Schedule script](#7-schedule-script) to schedule .Script is scheduled to run every hour in `append` mode. Enable  _Full_Sync_ checkbox for books in the database if you want to  run  the script in `sync-full` mode in the next scheduled run. 
<img src=https://i.imgur.com/7DQVufc.png width=350px>

### Run Manually
Clone `manual` branch
```
git clone --single-branch --branch manual https://github.com/MohamedIrfanAM/books2notion.git
```
````
python3 books2notion.py --mode <mode>
````
Example: `python3 books2notion.py --mode sync-full`

## Installation and Setup
### 1. Clone Git repo
Make sure you have [git](https://git-scm.com/downloads "git") installed.
To schedule script, clone `deployment` branch  
```
git clone https://github.com/MohamedIrfanAM/books2notion.git
```
For running the script manually,  clone `manual` branch
```
git clone --single-branch --branch manual https://github.com/MohamedIrfanAM/books2notion.git
```

### 2.Install Python Modules
Install [Python](https://www.python.org/downloads/ "Python") and proceed to install following modules
```
pip install --upgrade google-api-python-client, google-auth-httplib2, google-auth-oauthlib
pip install Pillow
pip install schedule
```
### 3.Authorize Notion
#### a. Get Notion Integration Token
**Goto https://www.notion.so/my-integrations and make an integration, give it a name submit with default settings.**    
<img src=https://i.imgur.com/xVjkwlr.png width="300">       
<img src=https://i.imgur.com/GhAh9ew.png width="300">      
<img src=https://i.imgur.com/uQcKblG.png width="400">     

**Copy the integration token and save it somewhere.**   
#### b. Duplicate template and share it to integration
**Duplicate [ books template](https://quark-plane-15f.notion.site/4bd2a74b373a48f488a6ba86eb2b309c?v=4d15601367de4de3a72c8ac903cce14a " books template") and `share -> invite -> integration_name -> invite`**  
<img src=https://i.imgur.com/2mcGWGE.png width="450">        
<img src=https://i.imgur.com/Ynp1bld.png width="350">      
<img src=https://i.imgur.com/lTVMfxk.png width="350">      

### 4. Authorize Google APIs
#### a. Create Google cloud project
**Goto https://console.cloud.google.com/ then click 'select a project'**   
<img src=https://i.imgur.com/M2Gg9uO.png width="350">      
<img src=https://i.imgur.com/xMKy2Ug.png width="350">          

**Give the project a name and click create**        
<img src=https://i.imgur.com/sz1an2k.png width="350">    
 
#### b. Create OAuth consent screen    
<img src=https://i.imgur.com/8BDKHyU.png width="350">     
<img src=https://i.imgur.com/Duc8REO.png width="350">     

**Fill 'name' and 'user support email'**    
<img src=https://i.imgur.com/9zYBVhD.png width="350">     

**Scroll down fill in 'Email address' and continue**     
<img src=https://i.imgur.com/xeXx9zi.png width="350">         
**click 'save and continue' for 'Scopes' and 'Test Users', don't have to fill in anything**        
<img src=https://i.imgur.com/bmQhPrU.png width="350">     
**Publish app**     
<img src=https://i.imgur.com/8PJPZib.png width="350">   
<img src=https://i.imgur.com/55Lk6L9.png width="350">   
#### c. Create OAuth2.0 credentials    
<img src=https://i.imgur.com/NvgyNEj.png width="350">     
<img src=https://i.imgur.com/gfzNn26.png width="350">    
<img src=https://i.imgur.com/8kvKOpn.png width="350">    
<img src=https://i.imgur.com/caytldw.png width="350">    
<img src=https://i.imgur.com/Jl4tImE.png width="350">    
   
**Download file and save it as `credentials.json` in the `books2notion` folder we created in [1. Clone Git repo](#1-clone-git-repo)**      

#### d. Enable APIs  
**We have to enable `Books API`, `Google Drive API` and `Google Docs API`**    
<img src=https://i.imgur.com/yaV16Mi.png width="350">     
<img src=https://i.imgur.com/tuDy5LM.png width="350">   

**Search for each APIs mentioned above and enable it**   
<img src=https://i.imgur.com/4qa3m6r.png width="350">
<img src=https://i.imgur.com/NcZoROK.png width="350">
<img src=https://i.imgur.com/vqJaAP6.png width="350">

### 5. Get env variables
#### a. Get NOTION_DATABASE_ID
**Copy the url of database we duplicated in [Duplicate Notion template](#b-duplicate-template-and-share-it-to-integration)**   
**It should look like this**    
```
https://www.notion.so/lucas-gen/e32a031992f348aeae115fe6dee8353?v=1e75f5e2b07349f4b331e88c4ca3beac
```
![](https://maze-condor-4f8.notion.site/image/https%3A%2F%2Fs3-us-west-2.amazonaws.com%2Fsecure.notion-static.com%2F0a48c753-25ef-4b24-8a2b-ac05c1dbfc1c%2FUntitled.png?table=block&id=4ccddee5-b2f2-44e4-8c4f-6638ab9a88fc&spaceId=41d27f42-f75a-496d-bb9b-d18fbe56e71b&width=2000&userId=&cache=v2)    
**Save the databse id somewhere**   
#### b. Get DRIVE_FOLDER_ID  
**Select any book from your Play Books library and open to read, you will find an option to save annotations to google drive and enable it (only have to doit once,then it will be default for everybook).**      
<img src=https://i.imgur.com/5REwVar.png width="250">       
**Go to google drive and navigate to folder you selected for saving annotations and copy it's url.**    
**it should look like this - `https://drive.google.com/drive/folders/<folder id>`**    
**copy the folder id and save it somewhere**     
#### c. Get IMAGE_HOST_KEY
**goto https://freeimage.host/page/api?lang=en and save the api key somewhere**       
[![](https://i.imgur.com/NoaM5ix.png)](https://i.imgur.com/NoaM5ix.png)     
#### d. Get TIME_OFFSET
goto https://www.timeanddate.com/time/zone/ and find time offset from UTC    
Example `+05:30`,`-04:00`

### 6. Authorize script  
**Run the script for the first time `python3 schedule_sync.py` in the terminal, you will prompted to give access to application via browser. This script will create a `.env` file in `books2notion` folder.
You don't have to authorize everytime just first time only.**      
The `.env`  file generated by running above script should look something like this    
```
API_TOKEN=<google API token, filled by script>
REFRESH_TOKEN=<google refresh token, filled by script>
TOKEN_URI=<token URI, filled by script>
CLIENT_ID=<client id, filled by script>
CLIENT_SECRET=<client id, filled by script>
EXPIRY=<token expiry, filled by script>
NOTION_KEY=
NOTION_DATABASE_ID=
DRIVE_FOLDER_ID=
IMAGE_HOST_KEY=
TIME_OFFSET=
  ```
### 7. Schedule script  
#### Heroku
##### a. Create Heroku Account
goto https://heroku.com/ and make a free account       
##### b. Install Heroku cli
https://devcenter.heroku.com/articles/heroku-cli#install-the-heroku-cli
##### c. Heroku login
```
heroku login
```
##### d. Create  app
```
heroku create
```
##### e. Fill env variables
goto https://dashboard.heroku.com/apps and you find your app, it might not be named `books2notion`      
<img src=https://i.imgur.com/wDvRTcg.png width="500">      
**goto settings**      
<img src=https://i.imgur.com/7W8T9ld.png width="350">    
**Reveal config vars**    
<img src=https://i.imgur.com/tUEO567.png width="350">     
**Fill in env variables we saved from [3. Get Notion Integration Token](#a-get-notion-integration-token), [5. Get env variables](#5-get-env-variables), [6. Authorize script](#6-authorize-script)**     
<img src=https://i.imgur.com/QbIdcZL.png width="550">     
##### f. add buildback   
**croll down and you will find option to add buildpack**   
<img src=https://i.imgur.com/bjtJoW6.png width="550">   
<img src=https://i.imgur.com/w3T7KFq.png width="300">   
##### g. deploy application
```
git push heroku deployment:main
```
**Now that's it, we have successfully deployed application.**   

#### Local
**Sheduling locally in Mac and Linux (cron)**   
Follow this [article](https://towardsdatascience.com/how-to-schedule-python-scripts-with-cron-the-only-guide-youll-ever-need-deea2df63b4e "article")   
**Sheduling locally in Windows (windows task scheduler)**     
Follow this [article](https://www.jcchouinard.com/python-automation-using-task-scheduler/ "article")   
