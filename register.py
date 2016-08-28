import socket
from content import cb_temperature_json
from config import get_config
from machine import Timer

def register(url, authorization):
    content = cb_temperature_json()
    header = 'Content-Type: application/json\r\n' + authorization + '\r\n'
    http_post(url, header, content)

def http_post(url, header, content):
    _, _, host, path = url.split('/', 3)
    if ':' in host:
        host, port = host.split(':')
        port = int(port)
    else:
        port = 80
    addr = socket.getaddrinfo(host, port)[0][-1]
    s = socket.socket()
    s.connect(addr)
    l = len(content)
    xmsg = bytes('POST /%s HTTP/1.1\r\nHost: relayserver\r\nContent-Length:%d\r\n%s\r\n' % (path, l, header), 'utf8')
    s.send(xmsg)
    s.sendall(content)
    s.close()

    #while True:
    #    data = s.recv(100)
    #    if data:
    #        print(str(data, 'utf8'), end='')
    #    else:
    #        break
