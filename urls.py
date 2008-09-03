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


def error500(request, template_name='500.html'):
    try:
        output = render_to_string(template_name, {}, RequestContext(request))
    except:
        output = "Critical error. Administrator was notified."
	#render_to_string(template_name, {}, Context())
    return HttpResponseServerError(output)

handler500 = 'urls.error500'

info_dict = { 'queryset': Tag.objects.all() }

sitemaps = {
    'blog': BlogSitemap,
    'flat': FlatPageSitemap,
    'tags': GenericSitemap(info_dict, priority=0.5, changefreq='daily'),
    'index': IndexSitemap,
    }

try:
    import urls_local
    urlpatterns = urls_local.urlpatterns
except ImportError:
    urlpatterns = patterns('',)

admin.autodiscover()

urlpatterns += patterns(
    '',
    url(r'^admin/(.*)', admin.site.root, name='admin'),
    url(r'^accounts/', include('accounts.urls')),
    url(r'^openid/', include('openidconsumer.urls')),
    url(r'^openidserver/', include('openidserver.urls')),
    url(r'^%s' % settings.BLOG_URLCONF_ROOT, include('blog.urls')),
    url(r'^sitemap.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),
    url(r'^xmlrpc/', include('xmlrpc.urls')),
    url(r'^captcha/', include('captcha.urls')),
    url(r'^robots.txt$', include('robots.urls')),
    url(r'^feeds/', include('feed.urls')),
    url(r'^watchlist/', include('watchlist.urls')),
    (r'^$', index),
    (r'^([^/]*)/?$', pages),
    (r'^([^/]*)/([^/]*)/?$', subpages),
    (r'^(?P<path>(styles|scripts|images|fonts|media|static)/.*)$', 'django.views.static.serve', {'document_root': settings.PROJECT_ROOT}),
    )

if settings.SET_URL_ROOT_HANDLER:
    urlpatterns += patterns('', url(r'^$', 'blog.views.process_root_request'))

# static urls will be disabled in production mode,
# forcing user to configure httpd
if settings.DEBUG:
    urlpatterns += patterns(
        '',
        url(r'^media/(.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
        url(r'^static/(.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
        url(r'^admin-media/(.*)$', 'django.views.static.serve', {'document_root': join(dirname(admin.__file__), 'media')}),
        )

if 'wpimport' in settings.INSTALLED_APPS:
    urlpatterns += patterns(
        '',
        url(r'^wpimport/', include('wpimport.urls')),
        )

if 'wbimport' in settings.INSTALLED_APPS:
    urlpatterns += patterns(
        '',
        url(r'^wbimport/', include('wbimport.urls')),
        )

if 'debug' in settings.INSTALLED_APPS:
    urlpatterns += patterns(
        '',
        url('', include('debug.urls')),
        )
