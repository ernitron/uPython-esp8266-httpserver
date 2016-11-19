# Micropython Http Server
# Erni Tron ernitron@gmail.com
# Copyright (c) 2016

def get_args(uri):
   answer = {}
   if uri == None or uri == b'' :
       return answer
   uri = bytes.decode(uri)
   uri = urldecode(uri)
   if '?' in uri:
       params = uri.split('?')[1]
       if '=' in uri:
           answer = dict(item.split('=') for item in params.split('&'))
   return answer

def urldecode(s):
    s = s.replace('%21','!')
    s = s.replace('%23','#')
    s = s.replace('%24','$')
    s = s.replace('%26','&')
    s = s.replace('%27',"'")
    s = s.replace('%28','(')
    s = s.replace('%29',')')
    s = s.replace('%2F','/')
    s = s.replace('%3A',':')
    return s

# Parses the client's request.
# Returns a dictionary containing pretty much everything
# the server needs to know about the uri.
def parse_request(req):
   if b'\r\n' not in req :
       return None

   r = {}
   line, rest = req.split(b'\n', 1)
   method, uri, http = line.split(b' ')

   Methods = b'GET HEAD POST PUT'
   if method in Methods:
       r['uri'] = uri
       r['method'] = method
       r['http'] = http
       uri = uri.replace(b'/', b'')
       r['args'] = get_args(uri)
       if b'?' in uri: endpos = uri.find(b'?')
       else: endpos = len(uri)
       r['file'] = uri[:endpos]

   return r

