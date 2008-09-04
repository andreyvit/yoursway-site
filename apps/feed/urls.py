from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib.syndication.views import feed

from feed import blog_feeds

# Be careful, names of this keys are also used in templates and in feeds.py!
atom_feeds = {
    'blog': blog_feeds.AtomBlogEntries,
    'comments': blog_feeds.AtomCommentEntries,
    'tag': blog_feeds.AtomPostsByTag,
    'featured': blog_feeds.AtomFeaturedBlogEntries,
    }

rss_feeds = {
    'blog': blog_feeds.RssBlogEntries,
    'comments': blog_feeds.RssCommentEntries,
    'tag': blog_feeds.RssPostsByTag,
    'featured': blog_feeds.RssFeaturedBlogEntries,
    }

def redirect_to_feed(request, url):
    from django.views.generic.simple import redirect_to
    from lib.helpers import reverse
    return redirect_to(request, url=reverse('feed', url=url))

urlpatterns = patterns(
    '',
    url(r'^rss/(?P<url>.*)/$', feed, {'feed_dict': rss_feeds}, name=settings.USE_ATOM and "rss_feed" or "feed"),
    url(r'^atom/(?P<url>.*)/$', feed, {'feed_dict': atom_feeds}, name=settings.USE_ATOM and "feed" or "atom_feed"),
    url(r'^(?P<url>.*)/$', redirect_to_feed),
)
