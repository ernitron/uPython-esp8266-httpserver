# uPython-esp8266-httpserver

This is a General Purpose http server for ESP8266 written in micropython (www.micropython.org)
It just serves static html files. Simply upload into flash any html files and she will serve them. 
As an example put your index.html with just "hello world!" in it and you have the K&R standard greetings.

It is highly configurable with parameters for SSID, PWD, AP SSID and many others. It is virually unlimited as the configuration parameters are kept into a json array of {'key', 'value'} and the server can simply store as many as possible.

It is mainly a temperature web server. For devices like ESP8266 and with temperature sensors based on DS18b20. 

*  the http server is general purpose and is easy to customize and configure
*  the Makefile is pretty powerful and automatize a lot of common tasks upload and reset using the script espsend.py 
which should be installed or configured in the proper directory
*  It uses other tools such as webrepl 


# Requirements

Software: based on micropython version 1.8.5. Probably latest and bleeding version works best.

    # git clone https://github.com/micropython/micropython.git

Hardware: Tested on Wemos D1 and Lolin V3 with ESP8266 chipset. For temperature a Dallas DS18b20 is needed wired to the device.


# DIFY (Do It Fu**ing Yourself)

Acutally I assemble all the stuff into a microappliance and I disseminate my places to track temperatures all around.
Look at the pictures. 


## BOM (Billing of Materials)

You can easily find all this stuff very cheap on aliexpress... just shop around ;)

* Wemos D1 mini (around 3$)
* Cheap Charger (< 1$)
* Micro USB Cable 5cm (< 1$)
* Sensor DS18b20 (< 1$)

Expect to afford 6US$ !!!
Isn't it fu**ing amazing?  https://www.dropbox.com/s/mw0tacnw87kg23v/IMG_0580.JPG?dl=0

I suggest to solder the 3 wires of the DS18B20 sensor directly on the Wemos D1 pins: 5V-GND-D4 i
They are contiguous.

No resistor is needed then (but check the code for the right PIN which is PIN=2).

# USAGE
Server can be called with: http://192.168.1.123:8805/help 

Many other configurations are possible

For instance if you want to upload data to the cloud there is a asynchronous routine called 'register' that push into a server values with json format. The server that holds data can be found here:
    https://github.com/ernitron/temperature-server

## STATIC FILES
HTML files can be added/uploaded into FLASH memory of device and will be served.

For example if you upload your example.html file and request: http://192.168.1.123:8805/example.html

## DYNAMIC BEHAVIOR
Can be configured in the main loop to serve dynamically generated contents
Conventionally contents are kept in cb_xyz() in content.py

## TEMPERATURE SERVER WITH DS18b20
A Dallas DS18b20 temperature sensor must be installed on device. 
On WeMos default GPIO for reading is either 12 or 2 as it has its own pullup resistor

*   D6	GPIO12	machine.Pin(12)
*   D4	GPIO2	machine.Pin(2)

## Implementation

I use a configurator that reads and saves variables into json files. Pretty cunny ;)

Server http is a class object with a main loop to serve requests.

The parser of requests works only on first line that has the request from browser:
    GET /example/?var1=value1&var2=value2 HTTP/1.1

Contents are produced with embedded html commands

It uses BOOTSTRAP for css/js. I have made shortcuts url for the cdn repository:
* https://goo.gl/EWKTqQ = https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js        
* http://goo.gl/E7UCvM =  http://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css

note: they are no more useful as files with html header are stored in flash and there is no need to shortcut them


## Installation

This is a little tricky and I developed the espsend.py to automatize the uploading and to have a very fast cycle of edit-deploy-run-test

I use the following tools to develop:

*   esp-open-sdk # git clone https://github.com/pfalcon/esp-open-sdk.git 
*   micropython # git clone https://github.com/micropython/micropython.git
*   webrepl # git clone https://github.com/micropython/webrepl.git
*   esptool # git clone https://github.com/themadinventor/esptool.git 
*   espsend.py # this is the script that goes on UART and make basic installation tasks.

Let's start with a bare ESP8266 device like WeMos.

* Install latest version of micropython
* Reset device
* Connect to device with picocom (or other)
    picocom -b 115200
* Set up first time webrepl with your own password
    import webrepl; webrepl.start()
* open a browser with page webrepl.html in webrepl folder and configure for password
* Upload sources with webrepl from browser

* Fast alternative use Makefile to make all.

**    make erase
**    make flash
**    make initmicro
**    make install

## Development

There is plenty of space for development

## Discussion

A number of tricks are used to keep memory allocation low. 

See thread http://forum.micropython.org/viewtopic.php?f=16&t=2266 for a discussion



