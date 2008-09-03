import os.path

from django.conf import settings
from django.contrib.sites.models import Site
from blog.models import Post

def settings_vars(request):
    return {
        'STATIC_URL': settings.STATIC_URL,
        'THEME_STATIC_URL': settings.THEME_STATIC_URL,
        'settings': settings,
        }

def featured_posts(request):
    return {
        'featured_posts': Post.featured_objects.all()
    }
