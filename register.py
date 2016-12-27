import socket
import time

class Register():
  def __init__(self, url, auth):
    if not url :
        self.host = None
        return

    try:
        _, __, self.host, self.path = url.split('/', 3)
    except:
        self.host = None
        return

    if ':' in self.host:
        self.host, self.port = self.host.split(':')
        self.port = int(self.port)
    else:
        self.port = 80

    self.header = 'Content-Type: application/json\r\n'
    if auth:
        self.header += 'Authorization: Basic %s\r\n' % auth

  def http_post(self, content):
    if not self.host : return
    print (self.host, self.port, self.path)

    import json
    jsondata = json.dumps(content)
    addr = socket.getaddrinfo(self.host, self.port)[0][-1]
    s = socket.socket()
    s.settimeout(10) # otherwise it will wait forever
    l = len(jsondata)
    msg = b'POST /%s HTTP/1.1\r\nHost: espserver\r\nContent-Length:%d\r\n%s\r\n' % (self.path, l, self.header)
    try:
        s.connect(addr)
        s.send(msg)
        s.sendall(jsondata)
    except Exception as e: # most probably a timeout
        print(e)
    s.close()

# Register class initialized to None
register = None
