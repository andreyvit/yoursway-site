# -*- coding: utf-8
import unittest
from sape import Sape
import pickle
import os
import time
import sys

args = {
    'user': '74947f25f25d6eb17e910005cbeaa8e6',
    'host': 'allsubmitter.org',
    'dir': '/tmp',
    'uri': '/',
}

class SapeTestCase(unittest.TestCase):
    def setUp(self):
        self.sape = Sape(**args)
        self.data = u'b33628e5e3121e6a77a47249bbbfaa23' + u'\n' +\
            u'@' + u'\n' +\
            u'/||SAPE||foobar||SAPE||toor' + u'\n' +\
            u'/index.html||SAPE||коза' + u'\n' +\
            u'__sape_new_url__||SAPE||nah_code'
        self.data = self.data.encode('windows-1251')

    def testInit(self):
        sape_instance = Sape(**args)
        self.assertEqual(args['user'],sape_instance.user)
        self.assertEqual(args['host'],sape_instance.host)
        self.assertEqual(args['dir'],sape_instance.dir)
        self.assertEqual(3600,sape_instance.cache_lifetime)
        self.assertEqual('/tmp/74947f25f25d6eb17e910005cbeaa8e6/links.db',
            sape_instance.file)

    def testReadFromFile(self):
        test_data = {'foo': 'bar'}
        test_file = '/tmp/sape-test'
        open(test_file,'w').write('trash')
        self.assertEqual('',self.sape.readFromFile(test_file))
        open(test_file,'w').write(pickle.dumps(test_data))
        self.assertEqual(test_data,self.sape.readFromFile(test_file))

    def testWriteToFile(self):
        test_data = {'foo': 'bar'}
        test_file = '/tmp/sape-test'
        self.sape.writeToFile(test_file,test_data)
        self.assertEqual(test_data,self.sape.readFromFile(test_file))

    def testParseLocalLinks(self):
        links = self.sape.parseLinks(self.data)
        self.assertEqual('@',links['__sape_delimiter__'])
        self.assertEqual(set(['foobar','toor']),set(links['/']))
        self.assertEqual([u'коза'],
            links['/index.html'])
        self.assertEqual(set(['nah_code']),
            set(links['__sape_new_url__']))

    def testFetchLinks(self):
        data = self.sape.fetchLinks()
        self.assert_(0 < len(data))

    def testParseRemoteLinks(self):
        data = self.sape.fetchLinks()
        links = self.sape.parseLinks(data)
        self.assertTrue(links.has_key('__sape_new_url__'))

    def testLoadLinks(self):
        self.makeFakeLinks()
        links = self.sape.loadLinks()
        self.assertEqual(set(['foobar','toor']),set(links['/']))
        self.assertFalse(links.has_key('/links.html'))

        self.makeFakeLinks()
        ftime = int(time.time()) - self.sape.cache_lifetime
        os.utime(self.sape.file,(ftime,ftime))
        links = self.sape.loadLinks()
        self.assertNotEqual(set(['foobar','toor']),set(links['/']))
        self.assertTrue(links.has_key('/links.html'))

        self.makeFakeLinks()
        ftime = int(time.time()) - self.sape.cache_reloadtime / 2
        os.utime(self.sape.file,(ftime,ftime))
        links = self.sape.loadLinks()
        self.assertEqual(set(['foobar','toor']),set(links['/']))
        self.assertFalse(links.has_key('/links.html'))

    def testReturnLinks(self):
        self.makeFakeLinks()
        links_html = self.sape.returnLinks()
        self.assertEqual('foobar@toor',links_html)

        self.makeFakeLinks()
        self.sape = Sape(**args)
        links_html = self.sape.returnLinks(1)
        self.assertEqual('foobar',links_html)
        links_html = self.sape.returnLinks(1)
        self.assertEqual('toor',links_html)

    def makeFakeLinks(self):
        self.sape.writeToFile(self.sape.file,
            self.sape.parseLinks(self.data))
        os.utime(self.sape.file,None)
