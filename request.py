def get_args(uri):
   answer = {}
   if uri == None or uri == b'' :
       return answer
   uri = bytes.decode(uri)
   if '?' in uri:
       params = uri.split('?')[1]
       if '=' in uri:
           answer = dict(item.split('=') for item in params.split('&'))
   return answer

# Parses the client's request.
# Returns a dictionary containing pretty much everything
# the server needs to know about the uri.
def parse_request(req):
   if b'\r\n' not in req :
       return None

   r = {}
   line, rest = req.split(b'\n', 1)
   method, uri, http = line.split(b' ')

   Methods = b'GET HEAD POST PUT DELETE'
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

