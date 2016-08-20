#!/usr/bin/python

# Global import
import socket  # Networking support
import time    # Current time
import network # Network IF

# Local import
from request import parse_request
from content import httpheader, httpfooter, cb_status, cb_setplace, cb_setplace, cb_setwifi, cb_temperature_init, cb_temperature, cb_temperature_json

# A simple HTTP server
class Server:
  def __init__(self, port=80, title='ESPserver'):
     # Constructor
     self.host = '0.0.0.0' # <-- works on all avaivable network interfaces
     self.port = port
     self.title = title
     self.conn = None
     self.addr = None
     self.footer = httpfooter()

  def http_send(self, header, content, footer):
    for c in header:
        self.conn.send(c)
    #if type(content) is list or type(content) is tuple:
    if type(content) is list :
       for c in content:
          self.conn.send(c)
    elif content != '':
       self.conn.send(content)
    if footer != '': self.conn.sendall(footer)

  def activate_server(self):
     # Attempts to aquire the socket and launch the server
     self.socket = socket.socket()
     try:
         self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
         print("HTTP server ", self.host, ":",self.port)
         self.socket.bind((self.host, self.port))
     except Exception as e:
         print("No port: " , self.port)
         #self.socket.shutdown(socket.SHUT_RDWR) # is this implemented in uPython?
         return
     self.wait_for_connections()

  def wait_for_connections(self):
     # Main loop awaiting connections
     self.socket.listen(1) # maximum number of queued connections
     refresh30 = '<meta http-equiv="refresh" content="300">\n'

     while True:
         print ("Awaiting...")
         self.conn, self.addr = self.socket.accept()
         # conn - socket to client // addr - clients address
         req = self.conn.readline()
         while True:
             h = self.conn.readline()
             if not h or h == b'\r\n':
                 break

         # determine request method (GET / POST are supported)
         r = parse_request(req)
         if r == None:
            header = httpheader(404, self.title)
            content = '404 - Error'
            self.http_send(header, content, self.footer)
         elif r['uri'] == b'/' or r['uri'] == b'/index' :
            header = httpheader(200, self.title, refresh=refresh30)
            content = '<h2>Server Ready %s</h2>' % self.title + cb_status()
            self.http_send(header, content, self.footer)
         elif r['uri'] == b'/temperature' :
            content = cb_temperature()
            header = httpheader(200, self.title, refresh=refresh30)
            self.http_send(header, content, self.footer)
         elif r['uri'] == b'/j' :
            content = cb_temperature_json(12)
            header = httpheader(200, self.title, extension='j')
            self.http_send(header, content, '')
         elif r['uri'] == b"/help":
            try:
                with open('help.txt', 'r') as f:
                    content = f.readlines()
            except:
                content = ''
            header = httpheader(200, self.title)
            self.http_send(header, content, self.footer)
         elif r['uri'] == b'/status':
            header = httpheader(200, self.title)
            self.http_send(header, cb_status(), self.footer)
         elif b'/setname' in r['uri']:
            try:
               self.title = r['args']['name']
               header = httpheader(302, self.title, refresh='<meta http-equiv="refresh" content="2; url=/"/>')
               content = cb_setplace(self.title)
            except:
               header = httpheader(200, self.title)
               content = '<p><form action="/setname">' \
                         'Name <input type="text" name="name"> ' \
                         '<input type="submit" value="Submit">' \
                         '</form></p></div>'
            self.http_send(header, content, self.footer)
         elif b"/setwifi" in r['uri']:
            try:
                ssid = r['args']['ssid']
                pwd = r['args']['pwd']
                content = cb_setwifi(ssid, pwd)
            except:
                content = '<p><form action="/setwifi">' \
                          'SSID <input type="text" name="ssid"> ' \
                          'PASS <input type="text" name="pwd"> ' \
                          '<input type="submit" value="Submit">' \
                          '</form></p></div>'
            header = httpheader(200, self.title)
            self.http_send(header, content, self.footer)
         elif r['uri'] == b'/reinit' :
            header = httpheader(200, self.title)
            content = '<h2><a href="/">Machine restarts in 2 secs...</a></h2></div>'
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
                content = 'No such file %s' % myfile
            header = httpheader(200, self.title)
            self.http_send(header, content, self.footer)
         else:
            header = httpheader(404, self.title)
            content = '404 - Error'
            self.http_send(header, content, self.footer)

         # At end of loop just close socket and collect garbage
         self.conn.close()

