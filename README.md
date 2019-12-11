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
* available in requirements.txt

## Setup

- Client:  

  Script was designed for running as client on Windows platform.
  1. Clone git repo to localhost,
  2. Install required packages,
  3. Set correct value for server (client.py, line 15; if you will test app locally, 
  you can left it unchanged).  
    
      ```
      HOME = 'http://127.0.0.1:8000/pyrserver/api/'
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
  next, open browser and enter following address:
  ```
  http://127.0.0.1:8000/pyrgui/index/
  ```
  To login, use previously created, super-user credentials.
  
- Online version of server is available via:
  ```
  http://pyrat.thinkbox.pl/
  ```
  Credentials:
  ```
  login: root / pass: toor12345
  ```
  Don't forget to change HOME value in *client.py* to:
  ```
  https://pyrat.pythonanywhere.com/pyrserver/api/
  ```
  After tests, be sure that your host is deleted from client list!

## Thanks

For Django authors -- this framework is awesome!   
As always, many thanks to my fantastic
girlfriend for support and tests!