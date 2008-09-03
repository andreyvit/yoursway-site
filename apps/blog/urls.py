from django.conf.urls.defaults import *
from django.conf import settings
from django.views.generic import date_based

from blog import views
from blog.models import Post

info = {
    'paginate_by': settings.PAGINATE_BY,
    }

info_dict_year = {
    'queryset': Post.plain_manager.filter(is_draft=False),
    'date_field': 'date',
    'template_name': 'blog/post_archive_year.html',
}

info_dict = {
    'queryset': Post.objects.all(),
    'date_field': 'date',
    'month_format': '%m',
    'template_name': 'blog/post_list.html',
    'allow_empty': True,
}

urlpatterns = patterns(
    '',
    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(?P<slug>[-\w]+)/$', views.post_detail, name="post_detail"),
    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/$', date_based.archive_day, info_dict, name="day_archive"),
    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/$', date_based.archive_month, info_dict, name="month_archive"),
    url(r'^(?P<year>\d{4})/$', date_based.archive_year,  info_dict_year, name="year_archive"),
    url(r'^tag/(?P<tag>[\w \.\-\+\|]+)/$', views.by_tag, info, name="post_by_tag"),
    url(r'^$', views.post_list, info, name="post_list"),
    url(r'^comment-edit/(?P<object_id>\d+)/$', views.comment_edit, name="comment_edit"),
    url(r'^comment-delete/(?P<object_id>\d+)/$', views.comment_delete, name="comment_delete"),
    url(r'^preview/$', views.preview, name="comment_preview"),
    url(r'^processed_js/$', views.processed_js, name="processed_js"),
    url(r'^wysiwyg_js/$', views.wysiwyg_js, name="wysiwyg_js"),
    url(r'^featured/$', views.featured, name="featured_posts"),
    )
