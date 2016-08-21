# uPython-esp8266-httpserver

This is a General Purpose http server for ESP8266 written in uPython

It is mainly a temperature web server. For devices like ESP8266 and with temperature sensors based on DS18b20. 

- the http server is general purpose and is easy to customize

- the Makefile is pretty powerful and automatize upload and reset by means of espsend.py which should be installed or configured in the proper directory

- It uses other tools such as webrepl 

# USAGE
Server can be called with: http://192.168.1.123:8805/help 


## STATIC FILES
HTML files can be added/uploaded into FLASH memory of device and will be served.

For example if you upload your example.html file and request: http://192.168.1.123:8805/example.html

## DYNAMIC BEHAVIOURS
Can be configured in the main loop to serve dynamically generated contents
Conventionally contents are kept in cb_xyz() in content.py

## TEMPERATURE SERVER WITH DS18b20
A Dallas DS18b20 temperature sensor must be installed on device. On WeMos default GPIO for reading is = 12 

    D6	GPIO12	machine.Pin(12)

## Implementation

I use a configurator that reads and saves variables into json files

Server http is a class object with a main loop to serve requests.

The parser of requests works only on first line that has the request from browser:
    GET /example/?var1=value1&var2=value2 HTTP/1.1

Contents are produced with embedded html commands

It uses BOOTSTRAP for css/js. I have made shortcuts url for the cdn repository:
        https://goo.gl/EWKTqQ = https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js        
        http://goo.gl/E7UCvM =  http://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css


## Installation

This is a little tricky and I developed the espsend.py to automatize the uploading and to have a very fast cycle of edit-deploy-run-test

I use the following tools to develop:

    esp-open-sdk # git clone https://github.com/pfalcon/esp-open-sdk.git 
    micropython # git clone https://github.com/micropython/micropython.git
    webrepl # git clone https://github.com/micropython/webrepl.git
    esptool # git clone https://github.com/themadinventor/esptool.git
    ESPlorer   # see http://esp8266.ru/esplorer/ 

Let's start with a bare ESP8266 device like WeMos.

- Install latest version of micropython
- Reset device
- Connect to device with picocom (or other)
    picocom -b 115200
- Set up first time webrepl with your own password
    import webrepl; webrepl.start()
- open a browser with page webrepl.html in webrepl folder and configure for password
- Upload sources with webrepl from browser
- Fast Alternative use Makefile to upload
    make all

## Discussion
A number of tricks are used to keep memory allocation low. 

See thread http://forum.micropython.org/viewtopic.php?f=16&t=2266
for a discussion



