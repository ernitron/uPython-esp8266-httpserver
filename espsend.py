#!/usr/bin/python

import serial
import time
import sys

class ESPserial:
    def __init__(self, port='/dev/ttyUSB0', baud=115200):
        self._port = serial.Serial(port)
        # setting baud rate in a separate step is a workaround for
        # CH341 driver on some Linux versions (this opens at 9600 then
        # sets), shouldn't matter for other platforms/drivers. See
        # https://github.com/themadinventor/esptool/issues/44#issuecomment-107094446
        self._port.baudrate = baud

    def write(self, packet):
        self._port.write(packet)

    def sendfile2(self, file):
        self.write('\x03') # Send ^C
        time.sleep(1.0)

        with open(file, 'r') as f:
            lines = f.readlines()
        self.write('import gc; gc.enable()\r' )
        self.write('gc.collect()\r' )
        self.write('\x05') # Send ^E
        self.write('import gc; gc.enable()\r' )
        self.write('f=open("%s", "wb")\r' % file)
        time.sleep(0.02)
        count = 0
        for l in lines:
           if l[0] == '#':
               print('Skip comment')
               continue
           #l = l.split('#', 1)[0]
           if len(l) <= 1:
               continue
           l = l.strip('\n')
           #self.write("a=b'''%s\\n''' #%d\r" % (l, count))
           self.write("a=b'''%s\\n'''\r" % (l))
           count += 1
           #self.write("f.write(a) #%d\r" % count)
           self.write("f.write(a)\r")
           count += 1
           time.sleep(0.10)
        self.write("f.close()\r")
        time.sleep(0.10)
        self.write('\x04') # Send ^D

    def sendfile(self, file1, target):
        self.write('\x03') # Send ^C
        time.sleep(1.0)

        with open(file1, 'r') as f:
            lines = f.readlines()
        self.write('import gc; gc.enable()\r' )
        self.write('gc.collect()\r' )
        self.write('\x05') # Send ^E
        self.write('import gc; gc.enable()\r' )
        time.sleep(0.02)
        self.write("a=b'''")
        for l in lines:
           if l[0] == '#':
               print('Skip comment')
               continue
           #l = l.split('#', 1)[0]
           if len(l) <= 1:
               continue
           l = l.strip('\n')
           l = l.replace('\\n', '\\\\n')
           l = l.replace('\\ ', '\\\\r')
           self.write("%s\\n" % (l))
           time.sleep(0.05)
        self.write("'''\r")
        self.write('f=open("%s", "wb")\r' % target)
        self.write("f.write(a)\r")
        self.write("f.close()\r")
        time.sleep(0.10)
        self.write('\x04') # Send ^D

    def readfile(self, file):
        self.write('\x03') # Send ^C
        self.write('f=open("%s", "r")\r' % file)
        self.write('lines = f.readlines()\r')
        self.write('for l in lines:\r' )
        self.write(' print(l)\r')
        self.write('\x08') # Send  Backspace
        self.write('\r\n')

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--baud', action="store", default=115200)
    #parser.add_argument('-p', '--port', action="store", default='/dev/ttyUSB0')
    parser.add_argument('-p', '--port', action="store", default='')
    parser.add_argument('-a', '--read', action="store", default='')
    parser.add_argument('-d', '--rm',  action="store", default='')
    parser.add_argument('-f', '--file', action="store", default='')
    parser.add_argument('-t', '--target', action="store", default='')
    # Boolean
    parser.add_argument('-c', '--controlc', action="store_true", default=False)
    parser.add_argument('-r', '--reset', action="store_true", default=False)
    parser.add_argument('-l', '--list', action="store_true", default=False)
    parser.add_argument('-m', '--mem', action="store_true", default=False)
    parser.add_argument('-k', '--check', action="store_true", default=False)
    parser.add_argument('-w', '--webrepl', action="store_true", default=False)
    args = parser.parse_args()

    if args.port == '':
        for i in range(0, 2):
            port = '/dev/ttyUSB' + str(i)
            try:
                esp = ESPserial(port, baud=int(args.baud))
                print ('Opened succesfully port %s' % port)
                break
            except:
                pass
    else:
      try:
        esp = ESPserial(port=args.port, baud=int(args.baud))
      except:
        sys.exit()

    if args.controlc == True:
        print("Sending Control-c")
        esp.write('\x03')

    if args.webrepl == True:
        print("Enabling Webrpl")
        esp.write('import webrepl; webrepl.start()\r\n')

    if args.list == True:
        print("Listing files on machine ")
        esp.write('import os; os.listdir()\r\n')

    if args.file != '':
        if args.target != '':
            target = args.target
        else:
            target = args.file
        print("Sending File %s as %s" % (args.file, target))
        esp.sendfile(args.file, target)

    if args.read != '':
        print("Reading File %s" % args.read)
        esp.readfile(args.read)

    if args.rm != '':
        print("Removing file %s " % args.rm)
        esp.write('import os; os.remove("%s")\r\n' % args.rm)

    if args.check == True:
        print("Check FW on machine ")
        esp.write('import esp; esp.check_fw()\r\n')

    if args.mem == True:
        print("Listing mem on machine ")
        esp.write('import esp; esp.meminfo()\r\n')
        esp.write('import micropython; micropython.mem_info()\r\n')
        esp.write('import gc\r\n')
        esp.write('gc.mem_alloc()\r\n')
        esp.write('gc.mem_free()\r\n')


    if args.reset == True:
        print("Restarting machine ")
        esp.write('\x03')
        esp.write('import machine; machine.reset()\r\n')

    time.sleep(1)

''' APPENDIX CONTROL CHARS '''
'''
Dec	Hex	ASCII	Key
0	00	NUL (null)	        ctrl @
1	01	SOH (start of heading)	ctrl A
2	02	STX (start of text)	ctrl B
3	03	ETX (end of text)	ctrl C
4	04	EOT (end of transmiss)	ctrl D
5	05	ENQ (enquiry)	        ctrl E
6	06	ACK (acknowledge)	ctrl F
7	07	BEL (bell)	        ctrl G
8	08	BS (backspace)	        ctrl H
9	09	HT (horizontal tab)	ctrl I
10	0A	LF (line feed)	        ctrl J
11	0B	VT (vertical tab)	ctrl K
12	0C	FF (form feed)	        ctrl L
13	0D	CR (carriage return)	ctrl M
14	0E	SO (shift out)	        ctrl N
15	0F	SI (shift in)	        ctrl O
16	10	DLE (data link escape)	ctrl P
17	11	DC1 (device control 1)	ctrl Q
18	12	DC2 (device control 2)	ctrl R
19	13	DC3 (device control 3)	ctrl S
20	14	DC4 (device control 4)	ctrl T
21	15	NAK (negative ack)	ctrl U
22	16	SYN (synchronous idle)	ctrl V
23	17	ETB (end of transm block)	ctrl W
24	18	CAN (cancel)	        ctrl X
25	19	EM (end of medium)	ctrl Y
26	1A	SUB (substitute)	ctrl Z
27	1B	ESC (escape)	        ctrl
28	1C	FS (file separator)	ctrl \
29	1D	GS (group separator)	ctrl [
30	1E	RS (record separator)	ctrl ^
31	1F	US (unit separator)	ctrl _
'''
