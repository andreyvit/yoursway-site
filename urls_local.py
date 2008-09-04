from django.conf.urls.defaults import *

urlpatterns = patterns(
    '',
    url('^hab$', 'django.views.generic.simple.redirect_to', {'url': '/'}, name='redirect_to_main'),
)