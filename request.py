def get_args(uri):
   answer = {}
   if uri == None or uri == b'' :
       return answer
   if b'?' in uri:
       params = uri.split(b'?')[1]
       if b'=' in uri:
           answer = dict(item.split(b'=') for item in params.split(b'&'))
   return answer

# Parses the client's request.
# Returns a dictionary containing pretty much everything
# the server needs to know about the uri.
def parse_request(req):
   if b"\r\n" not in req :
       return None

   r = {}
   line, rest = req.split(b'\n', 1)
   method, uri, http = line.split()

   Methods = b'GET HEAD POST PUT DELETE'
   if method in Methods:
       r['uri'] = uri
       r['method'] = method
       r['http'] = http
       r['args'] = get_args(uri)
       uri = uri.replace(b'/', b'')
       if b'?' in uri: endpos = uri.find(b'?')
       else: endpos = len(uri)
       r['file'] = uri[:endpos]

   return r

