from django.conf.urls.defaults import *
from django.shortcuts import render_to_response
from django.template.context import RequestContext

def index(request):
    return render_to_response('main.html',RequestContext(request))

urlpatterns = patterns('',
    # Example:
    # (r'^yoursway/', include('yoursway.foo.urls')),
      (r'^$', index),
      (r'^blog/', include('apps.blog.urls')),
    # Uncomment this for admin:
      (r'^admin/', include('django.contrib.admin.urls')),
)
