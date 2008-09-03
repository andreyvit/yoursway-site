from datetime import datetime as dt

from django.contrib.sitemaps import Sitemap

from blog.models import Post
from lib.helpers import reverse

class BlogSitemap(Sitemap):
    changefreq = "never"
    priority = 0.8

    def items(self):
        return Post.objects.exclude(date__gt=dt.now())

    def lastmod(self, obj):
        return obj.date


class IndexSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.6

    def items(self):
        return ["post_list"]

    def location(self, obj):
        return reverse(obj)

    def lastmod(self, obj):
        if obj == "post_list":
            return Post.objects.exclude(date__gt=dt.now()).latest('date').date