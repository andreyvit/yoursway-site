from datetime import datetime, timedelta

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.utils.html import strip_tags
from django.contrib.contenttypes import generic
from django.contrib import admin

from lib.helpers import reverse
from render import render
from blog.managers import PostManager, PublicPostManager, FeaturedPostManager
from discussion.models import CommentNode
from tagging.models import Tag
from tagging.fields import TagField
from pingback import Pingback, create_ping_func
from pingback import ping_external_links, ping_directories
import xmlrpc

RENDER_METHODS = (
    ('markdown', 'Markdown'),
    ('bbcode', 'BB code'),
    ('html', 'HTML'),
    ('html_br', 'Text+HTML (livejournal)'),
    ('text', 'Plain text')
)


class Post(models.Model):
    author = models.ForeignKey(User, related_name='posts')
    name = models.CharField(_(u'Name'), max_length=settings.NAME_LENGTH)
    slug = models.SlugField(_(u'Slug'), max_length=settings.NAME_LENGTH, blank=True,
                            unique_for_date="date")
    teaser = models.TextField(_(u'Post teaser'), blank=True)
    text = models.TextField(_(u'Text'))
    render_method = models.CharField(_(u'Render method'), max_length=15, choices=RENDER_METHODS, default=settings.RENDER_METHOD)
    html = models.TextField(_(u'HTML'), editable=False, blank=True)
    date = models.DateTimeField(_(u'Date'), default=datetime.now)
    upd_date = models.DateTimeField(_(u'Date'), auto_now=True, editable=False)
    is_draft = models.BooleanField(verbose_name=u'Post would act as draft', default=False)
    is_featured = models.BooleanField(verbose_name=u'Featured post', default=False)
    enable_comments = models.BooleanField(default=True)
    tags = TagField()

    comments = generic.GenericRelation(CommentNode)
    pingbacks = generic.GenericRelation(Pingback)

    all_objects = PostManager()
    objects = PublicPostManager()
    featured_objects = FeaturedPostManager()
    plain_manager = models.Manager()

    class Meta:
        db_table = 'blog_post'
        ordering = ['-date']
        get_latest_by = 'date'

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('post_detail', year=self.date.year, month=self.date.strftime('%m'), day=self.date.strftime('%d'), slug=self.slug)

    def save(self):
        if not self.slug:
            from pytils.translit import slugify
            self.slug = slugify(self.name)
        self.text = self.text.strip()
        self.html = render(self.text, self.render_method, unsafe=True)
        super(Post, self).save()

    def comments_open(self):
        if settings.COMMENTS_EXPIRE_DAYS:
            return self.enable_comments and (datetime.today() - timedelta(settings.COMMENTS_EXPIRE_DAYS)) <= self.date
        else:
            return self.enable_comments
    comments_open.boolean = True

    def _get_tags(self):
        return Tag.objects.get_for_object(self)

    def _set_tags(self, tag_list):
        Tag.objects.update_tags(self, tag_list)

    #tags = property(_get_tags, _set_tags)

    def get_tags(self):
        return [value.strip(' ,') for value in self.tags.split()]

    @property
    def html_short(self):
        from render.clean import normalize_html
        if self.shortable:
            head = self.html.split('<!--more-->', 1)[0]
            head = normalize_html(head)
            return head
        else:
            return self.html

    @property
    def shortable(self):
        return '<!--more-->' in self.html

    def view_link(self):
        return u'<a href="%s">%s</a>' % (self.get_absolute_url(), _('view'))
    view_link.allow_tags = True


class PostAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name', )}
    list_display = ('name', 'date', 'author', 'enable_comments', 'comments_open', 'is_draft', 'view_link')
    search_fields = ('name', 'text')
    list_filter = ('date', )
    fieldsets = (
        (None, {'fields': ('author', ('name', 'slug'), 'tags', 'text', 'render_method', 'date', ('is_draft', 'enable_comments'))}),
        ('Featured post', {'classes': ('collapse', ), 'fields': ('is_featured', 'teaser')}),
        )
    class Media:
        if settings.WYSIWYG_ENABLE:
            js = (
                settings.STATIC_URL + 'js/jquery.js',
                settings.STATIC_URL + 'js/wymeditor/jquery.wymeditor.pack.js',
                '/' + settings.BLOG_URLCONF_ROOT + 'wysiwyg_js/',
                )

admin.site.register(Post, PostAdmin)


# Pingback and directory ping handling
def pingback_blog_handler(year, month, day, slug, **kwargs):
    from datetime import time, date, datetime
    from time import strptime
    d = date(*strptime(year + month + day, '%Y%b%d')[:3])
    r = (datetime.combine(d, time.min), datetime.combine(d, time.max))
    return Post.objects.filter(date__range=r).get(slug=slug)

ping_details = {'post_detail': pingback_blog_handler}

xmlrpc.dispatcher.register_function(create_ping_func(**ping_details), 'pingback.ping')


if settings.ENABLE_PINGBACK:
    models.signals.post_save.connect(
        ping_external_links(content_attr='html', url_attr='get_absolute_url'),
        sender=Post)
if settings.ENABLE_DIRECTORY_PING:
    models.signals.post_save.connect(
        ping_directories(content_attr='html', url_attr='get_absolute_url'),
        sender=Post)
