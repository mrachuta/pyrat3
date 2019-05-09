## Project name
pyrat3 - python remote access tool - client app and server app.  
Previous versions (1.0 and 2.0) are available in other repos.

## Table of contents
* [General info](#general-info)
* [Technologies](#technologies)
* [Setup](#setup)
* [Using](#using)
* [Thanks](#thanks)

## General info
pyrat3 is a continuation of previous project (available in separate repository).

This tool was created for training purposes only, never was and will be used as unwanted software 
(there is no hidding, autostart of script etc).

Some of previously goals was achieved:

- Client:  
a) still limited number of imported modules (due to this, some functions looking ugly). This allow to
keep .exe file (after conversion from .py) in acceptable size,  
b) safe data transfer can be performed through SSL connection (if server support it),  
c) client is persistent - if there are some problems with connection, they re-run itself.  
  
- Server:  
a) simplified code vs. previous release (finally Django's one of most advantages was used - models),  
b) easy implementing of new jobs,  
c) communication basing on REST-API,  
d) minimal visual layer,  
e) JS is simplified using jQuery.  


## Technologies
- Client:  
a) Python3.  
- Server:  
a) Backend: Python3,  
b) Frontend: HTML5+CSS,  
c) Scripts: JavaScript and JQuery library,  
d) Database: SQLite.

Code was tested on following platforms:
- Server:  
a) Ubuntu 16.04.1 LTS (GNU/Linux 2.6.32-openvz-042stab125.5-amd64 x86_64) with Python 3.5.2  
- Client:  
a) Windows 8.1 (PL-PL) (x64) with Python 3.7.1  
b) Windows 8.1 (EN-US) (x64) with Python 3.6.4  

Used libraries:
* altgraph==0.16.1
* bottle==0.12.13
* certifi==2018.10.15
* cffi==1.11.5
* chardet==3.0.4
* Django==2.1.7
* djangorestframework==3.9.2
* future==0.17.1
* greenlet==0.4.15
* idna==2.7
* macholib==1.11
* pefile==2018.8.8
* pip-autoremove==0.9.1
* pycparser==2.19
* PyInstaller==3.4
* pytz==2018.9
* pywin32-ctypes==0.2.0
* requests==2.21.0
* urllib3==1.24.1
## Setup

- Client:  

  Script was designed for running as client on Windows platform.
  1. Clone git repo to localhost,
  2. Install required packages,
  3. Set correct value for server (client.py, line 15; if you will test app locally, 
  you can left it unchanged).  
    
      ```
      HOME = 'http://127.0.0.1:8000/pyrat3_server/api/'
      ```
      Remember, you will need to setup and run server first! Otherwise, client will be unusable.
  
- Server:  

  For testing on localhost:
  1. Clone git repo to localhost,
  2. Install required packages,  
  3. Create file secrets in the same directory as settings.py, 
  with following data (without < and >):  
    
      ```
      <secret_key>
      ```
  4. Initiate as standard Django-app (superuser, database, migrations etc).

## Using

- Client:  

  to run, perform:
  ```
  python client.py
  ```
- Server:  

  to run, perform:
  ```
  python manage.py runserver
  ```
  next, open browser and enter following adress:
  ```
  http://127.0.0.1:8000/pyrat3_server/index/
  ```
  To login, use previously created, super-user credentials.

## Thanks

For Django authors -- this framework is awesome!   
As always, many thanks to my fantastic
girlfriend for support and tests!