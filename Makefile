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

DATE=$(shell date +"%Y-%b-%d %H:%M:%S")
VERSION=1.3.2

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

MPYFILES := \
	real.mpy \
	httpserver.mpy \
	request.mpy \
	content.mpy \
	ds18b20.mpy \
	config.mpy \
	register.mpy \
	#display.mpy \

%.mpy: %.py
	$(MPYCROSS) $<

O=config
o: $(O).mpy
	for f in $^ ; \
	do \
	    echo installing $$f ;\
		$(AMPY) put $$f ;\
	done;

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

flash:
	@echo "Be sure about MEMORY SIZE"
	$(ESPTOOL) --port $(PORT) --baud 115200 write_flash --verify --flash_size=32m --flash_mode=qio 0x00000 $(FIRMWARE)
	@echo 'Power device again'

# Upload all
install: $(MPYFILES) $(TEXT) main.py
	sed -i -e "s/Version.*--/Version ${VERSION} ${DATE}--/" footer.txt
	for f in $^ ; \
	do \
	    echo installing $$f ;\
	    $(AMPY) put $$f ;\
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
