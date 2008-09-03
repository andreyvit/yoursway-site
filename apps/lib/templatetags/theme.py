from time import localtime, strftime
from os.path import join, exists, isdir, getmtime

from django.template import Library
from django.conf import settings

def gettime(filename):
    time = localtime(getmtime(filename))
    return strftime('%Y%m%d%H%M', time)

def theme_static(kind, filename):
    candidates = [[settings.THEME, kind, '%s.%s' % (filename, kind)],
                  [kind, '%s.%s' % (filename, kind)]]

    for candidate in candidates:
        full_path = join(settings.STATIC_ROOT, *candidate)
        if exists(full_path) and not isdir(full_path):
            url = '/'.join(candidate)
            if settings.APPEND_MTIME_TO_STATIC:
                url = '%s?%s' % (url, gettime(full_path))
            return {'STATIC_URL': settings.STATIC_URL, 'include': True, 'url': url}

    return {'include': False}

register = Library()

@register.inclusion_tag('templatetags/css.html')
def theme_css(filename='main'):
    return theme_static('css', filename)

@register.inclusion_tag('templatetags/js.html')
def theme_js(filename='main'):
    return theme_static('js', filename)

