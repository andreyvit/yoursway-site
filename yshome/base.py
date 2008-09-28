# -*- coding: utf-8 -*-

import os
import logging
import urllib

from datetime import datetime, timedelta
from google.appengine.ext.webapp import template
from google.appengine.api import users
# from google.appengine.api import memcache
# from google.appengine.ext import db
from google.appengine.ext import webapp

template_path = os.path.join(os.path.dirname(__file__), '..', 'templates')
# template.register_template_library('myfilters')

class FinishRequest(Exception):
  pass
  
class prolog(object):
  def __init__(decor, path_components = [], fetch = []):
    decor.path_components = path_components
    decor.fetch = fetch
    pass

  def __call__(decor, original_func):
    def decoration(self, *args):
      try:
        # self.read_flash()
        # self.read_config(config_needed = decor.config_needed)
        # self.read_user()
        for func, arg in zip(decor.path_components, args):
          getattr(self, 'fetch_%s' % func)(arg)
        for func in decor.fetch:
          getattr(self, 'also_fetch_%s' % func)()
        return original_func(self, *args)
      except FinishRequest:
        pass
    decoration.__name__ = original_func.__name__
    decoration.__dict__ = original_func.__dict__
    decoration.__doc__  = original_func.__doc__
    return decoration

class BaseHandler(webapp.RequestHandler):
  def __init__(self):
    self.now = datetime.now()
    self.data = dict(now = self.now)
    
  def finish_request(self):
    raise FinishRequest

  def redirect_and_finish(self, url, flash = None):
    if flash:
      self.flash(flash)
    self.redirect(url)
    raise FinishRequest
    
  def render_and_finish(self, *path_components):
    self.response.out.write(template.render(os.path.join(template_path, *path_components), self.data))
    raise FinishRequest
    
  def access_denied(self, message = None, attemp_login = True):
    if attemp_login and self.user == None and self.request.method == 'GET':
      self.redirect_and_finish(users.create_login_url(self.request.uri))
    self.die(403, 'access_denied.html', message=message)

  def not_found(self, message = None):
    self.die(404, 'not_found.html', message=message)

  def invalid_request(self, message = None):
    self.die(400, 'invalid_request.html', message=message)
    
  def die(self, code, template, message = None):
    if message:
      logging.warning("%d: %s" % (code, message))
    self.error(code)
    self.data.update(message = message)
    self.render_and_finish('errors', template)
