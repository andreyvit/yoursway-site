from os import path
import os
import urllib
import pickle
import time
import re

class Sape(object):
    """
    Class for working with sape.ru
    """

    def __init__(self,**kwargs):
        """
        Required arguments:
            user - sape account ID
            host - hostname of the website
            dir - directory for storing sape directory
            uri - requested uri
        Optional arguments:
            charset - character set of resulting html, if None return in unicode
            sape_server - server for requests
            cache_lifetime - links db older than this value should be
                refreshed
            cache_reloadtime - minimal time between requests to sape server
        """
        self.user = kwargs['user']
        self.host = kwargs['host']
        if -1 != self.host.find('www.'):
            self.host = self.host[4:]
        self.dir = kwargs['dir']
        self.uri = kwargs['uri']
        prefix = re.sub(r'(?i)[^-a-z0-9]','_',self.host)
        self.file = '%s/sape.links/%s.links.db' % (
            self.dir,prefix)
        self.links_delimiter = ''
        self.error = None

        self.charset = None
        self.sape_server = 'dispenser-01.sape.ru'
        self.cache_lifetime = 3600
        self.cache_reloadtime = 600

        for key in ['charset','sape_server','cache_lifetime',\
            'cache_reloadtime']:
            if kwargs.has_key(key):
                setattr(self,key,kwargs[key])

        self.links = self.loadLinks()
        #print 'self.links.keys():'
        #print '\n'.join(self.links.keys())
        #print 'Uri: `%s`' % self.uri
        if self.links.has_key(self.uri):
            print 'yes'
            self.page_links = self.links[self.uri]
        elif self.links.has_key('__sape_new_url__') and \
            len(self.links['__sape_new_url__']):
            print 'no'
            self.page_links = self.links['__sape_new_url__']
        else:
            self.page_links = []

    def loadLinks(self):
        """Get links from database"""

        if not path.exists(self.file):
            try:
                open(self.file,'w').write('')
            except IOError:
                self.error = 'Could not open file %s for writing' %\
                    self.file
                return {}

        if path.getmtime(self.file) < time.time() - self.cache_lifetime or\
            0 == path.getsize(self.file):
            os.utime(self.file,None)
            data = self.fetchLinks()
            if data is None:
                return {}
            links = self.parseLinks(data)
            # __sape_new_url__ should be in the parsed links
            if links['__sape_new_url__']:
                self.writeToFile(self.file,links)
            else:
                self.error = 'Network error. Incorrect data.'
                return {}

        if path.getsize(self.file):
            links = self.readFromFile(self.file)
        else:
            links = {}
        if links.has_key('__sape_delimiter__'):
            self.links_delimiter = links['__sape_delimiter__']
        return links

    def parseLinks(self,data):
        """Parse links from data retrieved from sape server"""

        links = {}
        data = data.decode('windows-1251')
        data = data.split('\n',2)
        links['__sape_delimiter__'] = data[1]
        for block in data[2].split('\n'):
            slices = block.split('||SAPE||')
            links[slices[0]] = slices[1:]
        return links

    def returnLinks(self, number=None, join=True):
        """Return html code"""

        if self.page_links:
            if not number or number > len(self.page_links):
                number = len(self.page_links)
            data = self.page_links[0:number]
            del self.page_links[0:number]
            if join:
                data = self.links_delimiter.join(data)
        else:
            if join:
                data = u''
            else:
                data = []
        if self.charset:
            if isinstance(data, list):
                for iter in data:
                    iter = iter.encode(self.charset)
            else:
                data = data.encode(self.charset)
        return data
        
    def writeToFile(self,filename,obj):
        """Lock file and write into it"""
        import fcntl
        data = pickle.dumps(obj)
        f = open(filename,'w')
        fcntl.lockf(f,fcntl.LOCK_EX)
        f.write(data)
        fcntl.lockf(f,fcntl.LOCK_UN)
        f.close()

    def readFromFile(self,filename):
        """Lock file and read it"""
        import fcntl
        f = open(filename,'r')
        fcntl.lockf(f,fcntl.LOCK_SH)
        data = f.read()
        fcntl.lockf(f,fcntl.LOCK_UN)
        f.close()
        try:
            data = pickle.loads(data)
        except:
            data = ''
        return data

    def fetchLinks(self):
        """Fetch links from sape server"""

        url = 'http://%s/code.php?user=%s&host=%s&charset=windows-1251&as_txt=true' % (
            self.sape_server,self.user,self.host)
        print url
        try:
            data = urllib.urlopen(url).read()
        except IOError, err:
            self.error = 'Network error: %s' % err
            return None
        return data

