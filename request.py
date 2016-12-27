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
    table = {'%21':'!' ,'%23':'#' ,'%24':'$' ,'%26':'&' ,'%27':"'" ,'%28':'(' ,'%29':')' ,'%2F':'/' ,'%3A':':', '+':' '}
    for k, v in table.items():
        s = s.replace(k, v)
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

   Methods = b'GET HEAD POST post PUT'
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

