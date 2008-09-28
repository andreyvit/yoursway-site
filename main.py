#!/usr/bin/env python
# -*- coding: utf-8 -*-

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from yshome.base import prolog, BaseHandler
from yshome.menu import menu

class PageHandler(BaseHandler):
  
  @prolog()
  def get(self, path):
    if path == '':
      path = 'index'
    
    self.data.update(**menu(path))
    
    self.render_and_finish('site/' + path.lstrip('/').rstrip('/') + '.html')

url_mapping = [
  ('^/([a-z0-9/-]*)$', PageHandler),
]

application = webapp.WSGIApplication(url_mapping, debug=True)

def main():
  run_wsgi_app(application)

if __name__ == '__main__':
  main()
