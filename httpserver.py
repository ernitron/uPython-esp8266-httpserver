#!/usr/bin/python

# Global import
import socket  # Networking support
import time    # Current time
import gc      # Garbage collector
import network # Network IF
import machine

# Local import
from request import parse_request
from content import *


# A simple HTTP server
class Server:
  def __init__(self, port=80, title='ESP Server'):
     # Constructor
     self.host = '0.0.0.0' # <-- works on all avaivable network interfaces
     self.port = port
     self.title = title
     self.footer = httpfooter()

  def http_send(self, cl, header, content, footer):
    cl.send(header)
    #if type(content) is list or type(content) is tuple:
    if type(content) is list :
       for c in content:
          cl.send(c)
    elif content != '':
       cl.send(content)
    if footer != '': cl.sendall(footer)

  def activate_server(self):
     # Attempts to aquire the socket and launch the server
     self.socket = socket.socket()
     try:
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

     while True:
         print ("Awaiting... ")
         conn, addr = self.socket.accept()
         # conn - socket to client // addr - clients address
         data = conn.recv(512) # it would be better a 1024 buffer
         string = bytes.decode(data)

         # determine request method (GET / POST are supported)
         r = parse_request(string)
         if r == None:
            header = httpheader('404', 'html', self.title, '')
            content = '404 - Error'
            self.http_send(conn, header, content, self.footer)
         elif r['uri'] == '/' or r['uri'] == '/index' :
            header = httpheader('200', 'html', self.title, '<meta http-equiv="refresh" content="300">\n')
            content = '<h2>Server Ready</h2>' + cb_status()
            self.http_send(conn, header, content, self.footer)
         elif r['uri'] == '/temperature' :
            content = cb_temperature()
            header = httpheader('200', 'html', self.title, '<meta http-equiv="refresh" content="300">\n')
            self.http_send(conn, header, content, self.footer)
         elif r['uri'] == '/j' :
            content = cb_temperature_json(12)
            header = httpheader('200', 'json', self.title, '')
            self.http_send(conn, header, content, '')
         elif r['uri'] == "/help":
            print('Setname')
            try:
                with open('help.txt', 'r') as f:
                    content = f.readlines()
            except:
                content = ''
            header = httpheader('200', 'html', self.title, '')
            self.http_send(conn, header, content, self.footer)
         elif r['uri'] == "/status":
            header = httpheader('200', 'html', self.title, '<meta http-equiv="refresh" content="300">\n')
            self.http_send(conn, header, cb_status(), self.footer)
         elif "/setname" in r['uri']:
            try:
               self.title = r['args']['name']
               header = httpheader('302', 'html', self.title, '<meta http-equiv="refresh" content="0; url=/"/>')
               content = cb_setplace(self.title)
            except:
               header = httpheader('200', 'html', self.title, '')
               content = '<p><form action="/setname">' \
                         'Name <input type="text" name="name"> ' \
                         '<input type="submit" value="Submit">' \
                         '</form></p></div>'
            self.http_send(conn, header, content, self.footer)
         elif "/setwifi" in r['uri']:
            print('Setwifi')
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
            header = httpheader('200', 'html', self.title, '')
            self.http_send(conn, header, content, self.footer)
         elif r['uri'] == '/reinit' :
            header = httpheader('200', 'html', self.title, '')
            content = '<h2><a href="/">Machine restarts in 2 secs...</a></h2></div>'
            self.http_send(conn, header, content, self.footer)
            time.sleep(2)
            machine.reset()
         elif r['file'] != '':
            myfile = r['file']
            try:
                with open(myfile, 'r') as f:
                    content = f.readlines()
            except:
                content = 'No Such file %s' % myfile
            header = httpheader('200', 'html', self.title, '')
            self.http_send(conn, header, content, self.footer)
         else:
            header = httpheader('404', 'html', self.title, '')
            content = 'Error 404'
            self.http_send(conn, header, content, self.footer)

         # At end of loop just close socket and collect garbage
         conn.close()


