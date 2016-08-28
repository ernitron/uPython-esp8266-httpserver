######################################################################
# User configuration
######################################################################
# Path to uploader 
UPLOADER=/opt/ESP8266/webrepl/webrepl_cli.py
ESPTOOL=/opt/ESP8266/esp-open-sdk/esptool/esptool.py
ESPSEND=/usr/local/bin/espsend.py
MPYCROSS=/opt/ESP8266/micropython/mpy-cross/mpy-cross

DATE=$(shell date +"%d %b %Y")

# Serial port
#PORT=/dev/cu.SLAB_USBtoUART
PORT=/dev/ttyUSB0
SPEED=115200

DEV=192.168.1.153

######################################################################
# End of user config
######################################################################
FILES := \
	main.py \
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

MPYFILES := \
	httpserver.mpy \
	request.mpy \
	content.mpy \
	ds18b20.mpy \
	config.mpy \
	register.mpy \

%.mpy: %.py
	$(MPYCROSS) $<

default: 
	@echo 'picocom -b 115200'
	@echo 'import webrepl; webrepl.start()'

check: $(MPYCROSS)
	python3 -m py_compile *.py
	rm -rf __pycache__
	rm -f *.pyc

# Upload all
all: main.py $(MPYFILES) $(TEXT)
	$(ESPSEND) -p $(PORT) -c -w
	for f in $^ ; \
	do \
		$(UPLOADER) $$f $(DEV):/$$f ;\
	done;
	$(ESPSEND) -p $(PORT) -r

# To flash firmware
flash:
	export PATH="/opt/ESP8266/esp-open-sdk/xtensa-lx106-elf/bin/:$$PATH" ;\
	$(ESPTOOL) --port $(PORT) erase_flash ;\
	cd /opt/ESP8266/micropython/esp8266 ;\
	make PORT=$(PORT) deploy

initmicro:
	$(ESPSEND) -p $(PORT) -c 
	$(ESPSEND) -p $(PORT) --file net.py --target main.py
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
