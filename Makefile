######################################################################
# User configuration
######################################################################
# Path to uploader 
UPLOADER=/opt/ESP8266/webrepl/webrepl_cli.py
# Serial port
#PORT=/dev/cu.SLAB_USBtoUART
PORT=/dev/ttyUSB0
SPEED=115200

ESPDEV=192.168.1.144
ESPDEV=192.168.1.121
ESPDEV=192.168.1.128


######################################################################
# End of user config
######################################################################
FILES := \
	main.py \
	ds18b20.py \
	request.py \
	content.py \
	help.txt \
	httpserver.py \

help: 
	@echo 'picocom -b 115200'
	@echo 'import webrepl; webrepl.start()'

check:
	python -m py_compile *.py
	rm -f *.pyc

# To flash firmware
flash:
	export PATH="/opt/ESP8266/esp-open-sdk/xtensa-lx106-elf/bin/:$$PATH" ;\
	/opt/ESP8266/esp-open-sdk/esptool/esptool.py --port $(PORT) erase_flash ;\
	cd /opt/ESP8266/micropython/esp8266 ;\
	make PORT=$(PORT) deploy

# Upload all
all: $(FILES) 
	@echo 'REMEMBER: import webrepl; webrepl.start()'
	@python espsend.py -c -w
	for f in $(FILES); \
	do \
		python $(UPLOADER) $$f $(ESPDEV):/$$f ;\
	done;
	@python espsend.py -r

m: main.py
	@echo 'REMEMBER: import webrepl; webrepl.start()'
	python espsend.py -c -w
	python $(UPLOADER) $^ $(ESPDEV):/$^
h: httpserver.py
	@echo 'REMEMBER: import webrepl; webrepl.start()'
	python espsend.py -c -w
	python $(UPLOADER) $^ $(ESPDEV):/$^
	python espsend.py -r
c: content.py
	@echo 'REMEMBER: import webrepl; webrepl.start()'
	python espsend.py -c -w
	python $(UPLOADER) $^ $(ESPDEV):/$^
f: config.py
	@echo 'REMEMBER: import webrepl; webrepl.start()'
	python espsend.py -c -w
	python $(UPLOADER) $^ $(ESPDEV):/$^
d: ds18b20.py
	@echo 'REMEMBER: import webrepl; webrepl.start()'
	python espsend.py -c -w
	python $(UPLOADER) $^ $(ESPDEV):/$^
q: request.py
	python espsend.py -c -w
	python $(UPLOADER) $^ $(ESPDEV):/$^
r: 
	python espsend.py -c -r

reset: 
	python espsend.py -c -r

# Print usage
usage:
	@echo "make upload FILE=<file>  to upload a specific file (i.e make upload FILE:=request.py)"
	@echo "make all           		to upload all"
	@echo "make <x>                 where <x> is the initial of source file "

