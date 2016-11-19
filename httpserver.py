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
from content import cb_index, cb_status, cb_help, cb_setparam, cb_resetconf, cb_listssid
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
     self.footer = None

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
     self.socket = socket.socket()
     self.socket.settimeout(10.0) # otherwise it will wait forever
     try:
         self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
         print("Server ", self.host, ":",self.port)
         self.socket.bind((self.host, self.port))
     except Exception as e:
         print("No port: ", self.port)
         #self.socket.shutdown(socket.SHUT_RDWR) # is this implemented in uPython?
         return
     self.footer = httpfooter()

  def wait_connections(self):
     # Main loop awaiting connections
     self.socket.listen(1) # maximum number of queued connections
     refresh30 = '<meta http-equiv="refresh" content="300">\n'
     error404 = '404 - Error'

     counting = 0
     while True:
         counting += 1
         print ("Wait ", counting)
         try:
            self.conn, self.addr = self.socket.accept()
         except KeyboardInterrupt:
            return
         except: # Timeout
            continue

         req = self.conn.readline()
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
             self.http_send(header, content, self.footer)
         elif r['uri'] == b'/index' :
             header = httpheader(200, self.title, refresh=refresh30)
             self.http_send(header, cb_index(), self.footer)
         elif r['uri'] == b'/temperature' or r['uri'] == b'/' :
             content = cb_temperature()
             header = httpheader(200, self.title, refresh=refresh30)
             self.http_send(header, content, self.footer)
         elif r['uri'] == b'/j' :
             content = cb_temperature_json()
             header = httpheader(200, self.title, extension='j')
             self.http_send(header, content, [])
         elif r['uri'] == b'/help':
             content = cb_help()
             header = httpheader(200, self.title)
             self.http_send(header, content, self.footer)
         elif r['uri'] == b'/status':
             header = httpheader(200, self.title)
             self.http_send(header, cb_status(), self.footer)
         elif b'/conf' in r['uri']:
             if 'key' in r['args'] and 'value' in r['args']:
               header = httpheader(302, self.title)
               content = cb_setparam(r['args']['key'], r['args']['value'])
             elif 'key' in r['args'] :
               header = httpheader(200, self.title)
               content = cb_setparam(r['args']['key'], None)
             else:
               header = httpheader(200, self.title)
               content = cb_setparam(None, None)
             self.title = config.get_config('place') # just in case
             self.http_send(header, content, self.footer)

         elif r['uri'] == b'/ssid' :
             header = httpheader(200, self.title)
             content = cb_listssid()
             self.http_send(header, content, self.footer)

         elif r['uri'] == b'/setconf' :
             header = httpheader(200, self.title)
             content = cb_setconf()
             self.http_send(header, content, self.footer)
         elif r['uri'] == b'/reboot' :
             header = httpheader(200, self.title)
             content = '<h2><a href="/">Reboot in 2\"</a></h2></div>'
             self.http_send(header, content, self.footer)
             time.sleep(2)
             import machine
             machine.reset()
         elif r['file'] != b'':
             myfile = r['file']
             try:
                if myfile == b'port_config.py': raise Exception
                with open(myfile, 'r') as f:
                    content = f.readlines()
                header = httpheader(200, self.title)
             except:
                header = httpheader(404, self.title)
                content = 'No such file %s' % myfile
             self.http_send(header, content, self.footer)
         else:
             header = httpheader(404, self.title)
             content = error404
             self.http_send(header, content, self.footer)

         # At end of loop just close socket and collect garbage
         self.conn.close()
         gc.collect()

