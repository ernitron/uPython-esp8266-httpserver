# uPython-esp8266-httpserver

This is a General Purpose http server for ESP8266 written in uPython

It is mainly a temperature web server. For devices like ESP8266 and with temperature sensors based on DS18b20. 

- the http server is general purpose and is easy to customize

- the Makefile is pretty powerful and automatize upload and reset by means of espsend.py which should be installed or configured in the proper directory

- It uses other tools such as webrepl 

Server can be called with

    http://192.168.1.123:8805/help

help.txt must be present

= USAGE
STATIC FILES:
HTML files can be added/uploaded into FLASH memory of device and will be served

DYNAMIC BEHAVIOURS:
Can be configured in the main loop to serve dynamically generated contents
Conventionally contents are kept in cb_xyz() in content.py

== Implementation
It uses BOOTSTRAP for css/js. 

== Installation
This is a little tricky and I developed the espsend.py to automatize the uploading and to have a very fast cycle of edit-deploy-run-test

I use the following tools to develop:

    ESPlorer   # see http://esp8266.ru/esplorer/ 
    esp-open-sdk # git clone https://github.com/pfalcon/esp-open-sdk.git 
    esptool # git clone https://github.com/themadinventor/esptool.git
    micropython.1.8.2 # git clone https://github.com/micropython/micropython.git
    webrepl # git clone https://github.com/micropython/webrepl.git

Let's start with a bare ESP8266 device like WeMos.

- Install latest version of micropython
- reset device
- Connect to device with picocom (or other)
    picocom -b 115200
- Set up first time webrepl with your own password
    import webrepl; webrepl.start()
- open a browser with page 

- Fast Alternative use Makefile to upload
    make all

== Discussion
A number of tricks are used to keep memory allocation low. 

See thread http://forum.micropython.org/viewtopic.php?f=16&t=2266
for a discussion



