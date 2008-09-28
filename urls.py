# Custom patches
from os.path import join, dirname

from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib import admin
from django.contrib.sitemaps import FlatPageSitemap, GenericSitemap
from django.http import HttpResponseServerError
from django.template.context import RequestContext, Context
from django.template.loader import render_to_string

from blog.sitemaps import BlogSitemap, IndexSitemap
from tagging.models import Tag
import watchlist.mail
from django.shortcuts import render_to_response
import patches

def index(request):
    return render_to_response('site/index.html',RequestContext(request))

def pages(request, url):
    url = url.rstrip('/')
    return render_to_response('site/%s.html' % url, RequestContext(request))

def subpages(request, url1, url2):
    return render_to_response('site/%s/%s.html' % (url1, url2), RequestContext(request))

 