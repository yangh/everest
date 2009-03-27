class SourceURI:
    def __init__ (self, uri = '', source = None):
        self._uri = uri
        self._source = source
    
    def parse_uri (self, suri = None, dicts = None):
        import re
        import string
        
        if not suri:
            uristr = self._uri
        else:
            uristr = suri
        print "parse uri: %s" % uristr
        exp = re.compile (r"\%\{[a-zA-Z0-9_]*.\}")
        result = exp.findall (uristr)
        if result:
            for item in result:
                key = item[2:-1]
                if dicts and dicts[key]:
                    value = dicts[key]
                    print "%s from dicts %s" % (key, value)
                elif self._source[key]:
                    value = self._source[key]
                    print "%s from self source %s" % (key, value)
                uristr = string.replace (uristr, item, value)
        
        return uristr
    
    def remote_available (self, suri = None):
        import urllib2
        
        if suri:
            uristr = suri
        else:
            uristr = self._uri
        ava = False
        
        print uristr
        req = urllib2.Request (uristr)
        try:
            f = urllib2.urlopen (req)
            ava = True
        except urllib2.URLError, e:
            print "Cann't open URL %s" % uristr
        
        return ava
    
    def get_timestamp (self):
        import datetime
        
        now = datetime.datetime.now ()
        
        return now.strftime("%Y-%m-%d %H:%M")
    
    def get_upstream (self):
         import string
         
         ups = []
         src = self._source
         
         while True:
             try:
                 orig = src['version'].split('.')
                 orig[-1] = str (int (orig[-1]) + 1)
                 src['version'] = string.join (orig, '.')
                 print src
             except:
                 print "Cann't auto increase version"
                 break
                 
             uri = self.parse_uri (self._uri, src)
             print "Upstream: %s" % uri
             if self.remote_available (uri):
                 up = {}
                 up['module_id'] = src['module_id']
                 up['source_id'] = src['id']
                 up['version'] = src['version']
                 up['uri'] = uri
                 up['timestamp'] = self.get_timestamp()
                 ups.append (up)
             else:
                 break
         
         return ups
