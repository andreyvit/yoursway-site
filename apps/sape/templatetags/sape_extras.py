from django import template
from django.conf import settings

from sape import Sape

register = template.Library()

def sape_init(request):
    uri = '%s%s%s' % (
        request.path,
        len(request.META['QUERY_STRING']) and '?' or '',
        request.META['QUERY_STRING'])
    if hasattr(settings, 'SAPE_DOMAIN'):
        host = settings.SAPE_DOMAIN
    else:
        host = request.META['HTTP_HOST']
    sape = Sape(
        user=settings.SAPE_USER,
        host=host,
        uri=uri,
        dir=settings.SAPE_DIR)
    return sape

@register.simple_tag
def sape_links(request):
    sape = sape_init(request)
    return sape.returnLinks()

@register.simple_tag
def sape_links_list(request):
    sape = sape_init(request)
    return '\n'.join([u'<li>%s</li>' % x for x in sape.returnLinks(join=False)])
