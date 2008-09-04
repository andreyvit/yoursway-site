from django.conf.urls.defaults import *
from django.views.generic.list_detail import object_list
from apps.blog.models import Post

urlpatterns = patterns('',
      (r'^$', object_list, {'queryset':Post.objects.all().order_by('-pub_date')}),
)
