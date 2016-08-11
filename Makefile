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
	@echo "make upload FILE:=<file>  to upload a specific file (i.e make upload FILE:=request.py)"
	@echo "make upload_server        to upload the server code "
	@echo "make upload_all           to upload all"
	@echo $(TEST)

# Upload one files only
upload:
	@python $(UPLOADER) -b $(SPEED) -p $(PORT) upload $(FILE)

# Upload HTTP files only
upload_http: $(HTTP_FILES)
	@python $(UPLOADER) -b $(SPEED) -p $(PORT) upload $(foreach f, $^, $(f))

# Upload httpserver files (init and server module)
upload_server: $(LUA_FILES)
	@python $(UPLOADER) -b $(SPEED) -p $(PORT) upload $(foreach f, $^, $(f))

