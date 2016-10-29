######################################################################
# User configuration
######################################################################
# CHANGE DEVICE BEFORE BEGIN
D=149
DEV=192.168.1.$(D)

# Path to uploader 
UPLOADER=/opt/ESP8266/webrepl/webrepl_cli.py
ESPTOOL=/opt/ESP8266/esp-open-sdk/esptool/esptool.py
ESPSEND=/usr/local/bin/espsend.py
MPYCROSS=/opt/ESP8266/micropython/mpy-cross/mpy-cross

DATE=$(shell date +"%Y-%b-%d %H:%M:%S")
VERSION=1.3.2


# Serial port
#PORT=/dev/cu.SLAB_USBtoUART
PORT=/dev/ttyUSB0
SPEED=115200


######################################################################
# End of user config
######################################################################
FILES := \
	main.py \
	realmain.py \
	ds18b20.py \
	request.py \
	content.py \
	config.py \
	httpserver.py \
	register.py \

TEXT:= \
	boot.py \
	help.txt \
	header.txt \
	footer.txt \
	index.txt \
	config.txt \

MPYFILES := \
	realmain.mpy \
	httpserver.mpy \
	request.mpy \
	content.mpy \
	ds18b20.mpy \
	config.mpy \
	register.mpy \

%.mpy: %.py
	$(MPYCROSS) $<

instruction:
	@echo "How to install:"
	@echo "1) make erase 2) make flash 3) make initmicro 4) make install"
	@echo 'DONT FORGET TO CHANGE DEVICE IP ADDRESS or use D=192.168.1.123'
	@echo 'picocom -b 115200 /dev/ttyUSB0'
	@echo 'import webrepl; webrepl.start()'

check: $(MPYCROSS)
	python3 -m py_compile *.py
	rm -rf __pycache__
	rm -f *.pyc

# To flash firmware 1) make erase 2) make flash 3) make initmicro 4) make install
erase:
	$(ESPTOOL) --port $(PORT) erase_flash 

flash:
	$(ESPTOOL) --port $(PORT) --baud 115200 write_flash --verify --flash_size=32m --flash_mode=qio 0x00000 /opt/ESP8266/micropython/esp8266/build/firmware-combined.bin
	@echo 'Power device again'

initmicro:
	$(ESPSEND) -p $(PORT) -c 
	$(ESPSEND) -p $(PORT) --file net.py --target main.py
	$(ESPSEND) -p $(PORT) -r 

# Upload all
install: main.py $(MPYFILES) $(TEXT)
	sed -i -e "s/Version.*--/Version ${VERSION} ${DATE}--/" footer.txt
	$(ESPSEND) -p $(PORT) -c -w
	for f in $^ ; \
	do \
		$(UPLOADER) $$f $(DEV):/$$f ;\
	done;
	$(ESPSEND) -p $(PORT) -r

few: realmain.mpy content.mpy ds18b20.mpy ds18x20_et.mpy
	$(ESPSEND) -p $(PORT) -r
	$(ESPSEND) --rm realmain.mpy
	$(ESPSEND) -p $(PORT) -c -w
	for f in $^ ; \
	do \
		$(UPLOADER) $$f $(DEV):/$$f ;\
	done;
	$(ESPSEND) -p $(PORT) -r

reset: check
	$(ESPSEND) -p $(PORT) -c -r

webrepl:
	/opt/google/chrome/chrome file:///opt/ESP8266/webrepl/webrepl.html

git:
	git commit -m 'update ${DATE}' -a
	git push

vi:
	gvim $(FILES)

clean:
	rm -f *.pyc
	rm -f *.mpy
