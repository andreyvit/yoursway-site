from django.template import Library
import re

from discussion.models import CommentNode
from blog.models import Post
from lib.db import load_content_objects
#from blogroll.models import Link

register = Library()

@register.inclusion_tag('blog/sidebar.html', takes_context=True)
def sidebar(context):
    comments = CommentNode.objects.filter(approved=True).select_related().order_by('-pub_date')[:5]
    #comments = load_content_objects(comments, cache_field='object')
    last_posts = Post.objects.all().order_by('-date')[:5]
    #blogroll_links = Link.objects.all()
    # TODO: return all variables from RequestContext dictionary
    return {
            'STATIC_URL': context['STATIC_URL'],
            'request': context['request'],
            'last_posts': last_posts,
            'settings': context['settings'],
            'comments': comments,
            #'blogroll_links': blogroll_links,
            }
