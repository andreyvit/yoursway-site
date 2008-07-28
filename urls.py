from django.conf.urls.defaults import *
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.conf import settings
from django.contrib import admin
import apps.blog.admin

def index(request):
    return render_to_response('site/index.html',RequestContext(request))

def pages(request, url):
    url = url.rstrip('/')
    return render_to_response('site/%s.html' % url, RequestContext(request))

urlpatterns = patterns('',
    # Example:
    # (r'^yoursway/', include('yoursway.foo.urls')),
      (r'^blog/', include('apps.blog.urls')),
    # Uncomment this for admin:
      (r'^admin/(.*)$', admin.site.root),
      (r'^$', index),
      (r'^([^/]*)/?$', pages),
)

admin.autodiscover()

if settings.DEBUG:    
    urlpatterns += patterns('',
    (r'^media/(.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
)
