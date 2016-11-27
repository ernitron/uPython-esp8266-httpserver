# Micropython Http Server
# Erni Tron ernitron@gmail.com
# Copyright (c) 2016

# Global import
import socket  # Networking support
import time    # Current time
import gc      # Current time

# Local import
from request import parse_request
from config import config
from content import cb_open, cb_status, cb_getconf, cb_setconf, cb_resetconf
from content import cb_temperature, cb_temperature_json

def httpheader(code, title, extension='h', refresh=''):
   mt = {'h': "text/html", 'j': "application/json"}
   codes = {200:" OK", 400:" Bad Request", 404:" Not Found", 302:" Redirect", 501:"Server Error" }
   head0 = 'HTTP/1.1 %s\r\nServer: tempserver\r\nContent-Type: %s\r\n'
   #head1 = 'Cache-Control: private, no-store\r\nConnection: close\r\n\r\n'
   head1 = 'Connection: close\r\n\r\n'
   head2 = ''

   if code not in codes: code = 501

   httpstatus = str(code) + codes[code]

   if extension not in mt: extension = 'h'
   mimetype = mt[extension]

   if extension == 'j':
       return [head0 % (httpstatus, mimetype), head1 ]
   else:
       with open('header.txt', 'r') as f:
           head2 = f.readlines()
       return [head0 % (httpstatus, mimetype), head1] + head2

def httpfooter():
    try:
        with open('footer.txt', 'r') as f:
            return f.readlines()
    except:
        return []

# A simple HTTP server
class Server:
  def __init__(self, port=80, title='uServer'):
     # Constructor
     self.host = '0.0.0.0' # <-- works on all avaivable network interfaces
     self.port = port
     self.title = config.get_config('place')
     self.conn = None
     self.addr = None

  def http_send(self, header, content, footer):
    for c in header:
        self.conn.send(c)
    # if type(content) is list or type(content) is tuple:
    if type(content) is list :
       for c in content:
          self.conn.send(c)
    elif content != '':
       self.conn.send(content)

    for c in footer:
        self.conn.sendall(c)

  def activate(self):
     # Attempts to aquire the socket and launch the server
     try:
         self.socket = socket.socket()
         self.socket.settimeout(5.0) # otherwise it will wait forever
         self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
         self.socket.bind((self.host, self.port))
         print("Server ", self.host, ":",self.port)
     except Exception as e:
         print(e)
     self.socket.listen(1) # maximum number of queued connections

  def wait_connections(self, sta_if):
     # Main loop awaiting connections
     refresh30 = '<meta http-equiv="refresh" content="300">\n'
     error404 = '404 - Error'
     footer = httpfooter()

     from register import register
     rurl = config.get_config('register')
     auth = config.get_config('authorization')

     counting = 0
     startime = time.time()
     while True:
         if not sta_if.isconnected():
             print('Disconnected...')
             return

         nowtime = time.time()
         if nowtime-startime > 299: # means every 60*5 = 300 sec == 5 mins
             register(rurl, auth)
             startime = time.time()

         counting += 1
         print("Wait ", counting)

         try:
            self.conn, self.addr = self.socket.accept()
         except KeyboardInterrupt:
            return
         except:
            print('Timeout')
            continue

         try:
            req = self.conn.readline()
         except:
            print('Timeout readline')
            continue

         # conn - socket to client // addr - clients address
         while True:
             h = self.conn.readline()
             if not h or h == b'\r\n':
                 break

         # determine request method (GET / POST are supported)
         r = parse_request(req)
         if r == None:
             header = httpheader(404, self.title)
             content = error404
         elif r['uri'] == b'/temperature' or r['uri'] == b'/' :
             header = httpheader(200, self.title, refresh=refresh30)
             content = cb_temperature()
         elif r['uri'] == b'/j' :
             header = httpheader(200, self.title, extension='j')
             content = cb_temperature_json()
             self.http_send(header, content, [])
             continue
         elif r['uri'] == b'/status':
             header = httpheader(200, self.title)
             content = cb_status()
         elif r['uri'] == b'/getconf':
             header = httpheader(200, self.title)
             content = cb_getconf()
         elif b'/setconf' in r['uri']:
             if 'key' in r['args'] and 'value' in r['args']:
               header = httpheader(302, self.title)
               content = cb_setconf(r['args']['key'], r['args']['value'])
             elif 'key' in r['args'] :
               header = httpheader(200, self.title)
               content = cb_setconf(r['args']['key'], None)
             else:
               header = httpheader(200, self.title)
               content = cb_setconf(None, None)
             self.title = config.get_config('place') # just in case
         elif r['uri'] == b'/reboot' :
             header = httpheader(200, self.title)
             content = '<h2>Reboot</h2></div>'
             self.http_send(header, content, footer)
             return
         elif r['file'] != b'':
             myfile = r['file']
             header = httpheader(200, self.title)
             content = cb_open(myfile)
         else:
             header = httpheader(404, self.title)
             content = error404

         # At end of loop just close socket and collect garbage
         self.http_send(header, content, footer)
         self.conn.close()
         gc.collect()

