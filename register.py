import socket
from ds18b20 import sensor
import json

def register(url, auth):
    # get the sensor status dictionary
    T = sensor.status()
    content = json.dumps(T)
    header = 'Content-Type: application/json\r\nAuthorization: Basic %s\r\n' % auth
    http_post(url, header, content)
    print('register sent to url')

def http_post(url, header, content):
    _, __, host, path = url.split('/', 3)
    if ':' in host:
        host, port = host.split(':')
        port = int(port)
    else:
        port = 80
    addr = socket.getaddrinfo(host, port)[0][-1]
    s = socket.socket()
    s.settimeout(4) # otherwise it will wait forever
    try:
        s.connect(addr)
        l = len(content)
        xmsg = bytes('POST /%s HTTP/1.1\r\nHost: relayserver\r\nContent-Length:%d\r\n%s\r\n' % (path, l, header), 'utf8')
        s.send(xmsg)
        s.sendall(content)
        s.close()
    except:
        pass
