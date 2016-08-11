
def get_args(uri):
   answer = {}
   if uri == None or uri == '' :
       return answer
   if '?' in uri:
       params = uri.split('?')[1]
       if '=' in uri:
           answer = dict(item.split('=') for item in params.split('&'))
   return answer

# Parses the client's request.
# Returns a dictionary containing pretty much everything
# the server needs to know about the uri.
def parse_request(req):
   if "\r\n" not in req :
       return None

   r = {}
   line, rest = req.split('\n', 1)
   method, uri, http = line.split()

   Methods = 'GET HEAD POST PUT DELETE'
   if method in Methods:
       r['uri'] = uri
       r['method'] = method
       r['http'] = http
       r['args'] = get_args(uri)
       uri = uri.replace('/', '')
       if '?' in uri: endpos = uri.find('?')
       else: endpos = len(uri)
       r['file'] = uri[:endpos]

   return r

