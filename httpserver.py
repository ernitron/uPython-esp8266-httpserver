# Micropython Http Server
# Erni Tron ernitron@gmail.com
# Copyright (c) 2016

# Global import
import socket  # Networking support
import time    # Current time
import gc      # Current time

# Local import
from request import parse_request
from config import set_config, get_config
from content import cb_index, cb_status, cb_setplace, cb_setplace, cb_setwifi, cb_help
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
    with open('footer.txt', 'r') as f:
        return f.readlines()

# A simple HTTP server
class Server:
  def __init__(self, port=80, title='uServer'):
     # Constructor
     self.host = '0.0.0.0' # <-- works on all avaivable network interfaces
     self.port = port
     self.title = get_config('place')
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

  def activate_server(self):
     # Attempts to aquire the socket and launch the server
     self.socket = socket.socket()
     try:
         self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
         print("Server ", self.host, ":",self.port)
         self.socket.bind((self.host, self.port))
     except Exception as e:
         print("No port: ", self.port)
         #self.socket.shutdown(socket.SHUT_RDWR) # is this implemented in uPython?
         return
     self.wait_for_connections()

  def wait_for_connections(self):
     # Main loop awaiting connections
     self.socket.listen(1) # maximum number of queued connections
     refresh30 = '<meta http-equiv="refresh" content="300">\n'
     error404 = '404 - Error'

     while True:
         print ("Wait..")
         self.conn, self.addr = self.socket.accept()
         # conn - socket to client // addr - clients address
         req = self.conn.readline()
         while True:
             h = self.conn.readline()
             if not h or h == b'\r\n':
                 break

         self.footer = httpfooter()
         # determine request method (GET / POST are supported)
         self.title = get_config('place')
         r = parse_request(req)
         if r == None:
             header = httpheader(404, self.title)
             content = error404
             self.http_send(header, content, self.footer)
         elif r['uri'] == b'/' or r['uri'] == b'/index' :
             header = httpheader(200, self.title, refresh=refresh30)
             content = cb_index(self.title)
             self.http_send(header, content, self.footer)
         elif r['uri'] == b'/temperature' :
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
             if 'param' in r['args'] and 'value' in r['args']:
               header = httpheader(302, self.title)
               content = cb_setparam(r['args']['param'], r['args']['value'])
             else:
               header = httpheader(200, self.title)
               content = cb_setparam(None, None) #with void arguments
             self.http_send(header, content, self.footer)
         elif r['uri'] == b'/reinit' :
             header = httpheader(200, self.title)
             content = '<h2><a href="/">Restart in 2\"</a></h2></div>'
             self.http_send(header, content, self.footer)
             time.sleep(2)
             import machine
             machine.reset()
         elif r['file'] != b'':
             myfile = r['file']
             try:
                with open(myfile, 'r') as f:
                    content = f.readlines()
             except:
                content = 'No file %s' % myfile
             header = httpheader(200, self.title)
             self.http_send(header, content, self.footer)
         else:
             header = httpheader(404, self.title)
             content = error404
             self.http_send(header, content, self.footer)

         # At end of loop just close socket and collect garbage
         self.conn.close()
         gc.collect()

