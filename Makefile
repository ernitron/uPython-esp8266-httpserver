######################################################################
# User configuration
######################################################################

# Serial port
# Windows
#PORT=/dev/cu.SLAB_USBtoUART
# MAC
#PORT=/dev/ttyACM0
# Linux Debian/Ubuntu
PORT=/dev/ttyUSB0

SPEED=115200

# Path to programs
MPYCROSS=/opt/ESP8266/micropython/mpy-cross/mpy-cross
ESPTOOL=/opt/ESP8266/esp-open-sdk/esptool/esptool.py
# Install with sudo pip2 install adafruit-ampy
AMPY=ampy -p $(PORT)
FIRMWARE=/opt/ESP8266/micropython/esp8266/build/firmware-combined.bin
#FIRMWARE=./build/firmware-combined.bin

# OTA via uploader
DEV=192.168.1.147
UPLOADER=/opt/ESP8266/webrepl/webrepl_cli.py

DATE=$(shell date +"%Y-%b-%d %H:%M:%S")
VERSION=2.1.2-deepsleep
BUILDDIR=BUILD


######################################################################
# End of user config
######################################################################
FILES := \
	main.py \
	real.py \
	ds18b20.py \
	request.py \
	content.py \
	config.py \
	httpserver.py \
	register.py \

TEXT:= \
	help.txt \
	header.txt \
	footer.txt \
	index.txt \
	config.txt \
	webrepl_cfg.py \

MPYFILES := \
	$(BUILDDIR)/real.mpy \
	$(BUILDDIR)/httpserver.mpy \
	$(BUILDDIR)/request.mpy \
	$(BUILDDIR)/content.mpy \
	$(BUILDDIR)/ds18b20.mpy \
	$(BUILDDIR)/config.mpy \
	$(BUILDDIR)/register.mpy \
	$(BUILDDIR)/gotosleep.mpy \
	$(BUILDDIR)/display.mpy \

$(BUILDDIR)/%.mpy: %.py
	$(MPYCROSS) $< -o $@

O=httpserver
o: $(BUILDDIR)/$(O).mpy
	@echo installing $^
	$(AMPY) put $^

w:  $(BUILDDIR)/$(O).mpy
	$(UPLOADER) $^ $(DEV):/$(O).mpy

p:  $(O)
	$(UPLOADER) $^ $(DEV):/$(O)

instruction:
	@echo "How to install:"
	@echo "1) make erase 2) make flash 3) make install"

compile: $(MPYFILES)
	@echo "compile all to be compiled"

check:
	python3 -m py_compile *.py
	rm -rf __pycache__
	rm -f *.pyc

erase:
	$(ESPTOOL) --port $(PORT) erase_flash 

ESPIFSDK=/opt/ESP8266/nodemcu-firmware/sdk/esp_iot_sdk_v1.5.4.1/bin/esp_init_data_default.bin
ESPIFADX=0x3fc000 

flash:
	@echo "Be sure about MEMORY SIZE"
	$(ESPTOOL) --port $(PORT) --baud 115200 write_flash --verify --flash_size=32m --flash_mode=qio 0x00000 $(FIRMWARE) $(ESPIFADX) $(ESPIFSDK) 
	@echo 'Power device again'

# Upload all
install: $(MPYFILES) $(TEXT) main.py
	sed -i -e "s/Version.*--/Version ${VERSION} ${DATE}--/" footer.txt
	for f in $^ ; \
	do \
	    echo installing $$f ;\
	    $(AMPY) put $$f ;\
	done;

webinstall: $(MPYFILES) $(TEXT) main.py
	for f in $^ ; \
       do $(UPLOADER) $$f $(DEV):/$$f ;\
    done;

reset:
	$(AMPY) reset

git:
	git commit -m 'update ${DATE}' -a
	git push

vi:
	gvim $(FILES)

clean:
	rm -f *.pyc
	rm -f *.mpy
