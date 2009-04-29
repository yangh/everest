import string

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
        #print "parse uri: %s" % uristr
        exp = re.compile (r"\%\{[a-zA-Z0-9_]*.\}")
        result = exp.findall (uristr)
        if result:
            for item in result:
                key = item[2:-1]
                if dicts and dicts[key]:
                    value = dicts[key]
                    #print "%s from dicts %s" % (key, value)
                elif self._source[key]:
                    value = self._source[key]
                    #print "%s from self source %s" % (key, value)
                uristr = string.replace (uristr, item, value)
        
        return uristr
    
    def remote_available (self, suri = None):
        import urllib2
        
        if suri:
            uristr = suri
        else:
            uristr = self._uri
        ava = False
        
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
    
    def new_upstream (self, src, uri):
        up = {}
        up['module_id'] = src['module_id']
        up['source_id'] = src['id']
        up['version'] = src['version']
        up['uri'] = uri
        up['timestamp'] = self.get_timestamp()
        
        return up
    
    def build_upstream_version (self, version):
        up_version = ''
        try:
            orig = version.split('.')
            orig[-1] = str (int (orig[-1]) + 1)
            up_version = string.join (orig, '.')
        except:
            print "Cann't auto increase version"
        
        return up_version
    
    def check_and_add_upstream (self, src, ruri, version, check_sub = False):
        ups = []
        
        src['version'] = version
        uri = self.parse_uri (ruri, src)
        print "Testing upstream: %s" % uri
        if self.remote_available (uri):
            ups.append (self.new_upstream(src, uri))
            added = True
            if not check_sub:
                return ups
            
            # check sub version
            for v in range (1, 10):
                sub_version = version + "." + str(v)
                subups = self.check_and_add_upstream (src, ruri, sub_version, False)
                if len (subups) > 0:
                    ups += subups
                else:
                    src['version'] = version
                    break
        
        return ups
    
    def get_upstream (self, exists_ups = []):
         ups = []
         src = self._source
         
         while True:
             version = self.build_upstream_version (src['version'])
             if (len(version) < 1):
                 break;
             
             if version in exists_ups:
                 print "Pass exists upstream: %s" % version
                 src['version'] = version
                 continue
             
             subups = self.check_and_add_upstream (src, self._uri, version, True)
             if len (subups) > 0:
                 ups += subups
             else:
                 break
         
         return ups
