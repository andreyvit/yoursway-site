# -*- encoding: utf-8 -*-
import time
from datetime import time as t, date as d, datetime as dt

from django.views.generic.list_detail import object_list
from django.shortcuts import get_object_or_404, render_to_response, get_list_or_404
from django.http import HttpResponseRedirect, Http404
from django.contrib.sites.models import Site
from django.conf import settings
from django.utils.translation import ugettext as _

from lib.forms import build_form
from lib.exceptions import RedirectException
from lib.decorators import render_to, ajax_request
from lib.helpers import get_object_or_404_ajax
from lib.http import render_response

from accounts.models import ActionRecord
from accounts.views import _login
from discussion.forms import CommentForm, AnonymousCommentForm
from discussion.models import CommentNode
from blog.models import Post
from tagging.views import tagged_object_list
from render import render

def _get_reply_to(request):
    try:
        return int(request.GET.get('reply_to', None))
    except (ValueError, TypeError):
        return None


def _get_date(date_str):
    try:
        return d(*time.strptime(date_str, '%Y%m%d')[:3])
    except ValueError:
        raise Http404


def post_list(request, *args, **kwargs):
    """Post listing. Only shows posts that are older than now()"""
    kwargs['queryset'] = Post.objects.exclude(date__gt=dt.now())
    return object_list(request, *args, **kwargs)


def by_tag(request, tag, *args, **kwargs):
    """Post listing. Only shows posts that are older than now() and belongs to specified tags"""
    queryset = Post.objects.filter(date__lte=dt.now())
    if not kwargs.has_key('extra_context'):
        kwargs['extra_context'] = {}
    kwargs['extra_context']['feedurl'] = 'tag/%s' % tag
    if '+' in tag:
        return tagged_object_list(request, queryset, tag.split('+'), union=False, *args, **kwargs)
    else:
        return tagged_object_list(request, queryset, tag.split('|'), *args, **kwargs)


@render_to('blog/post_detail.html')
def post_detail(request, year, month, day, slug):
    reply_to = _get_reply_to(request)
    date = _get_date(year+month+day)
    today = (dt.combine(date, t.min), dt.combine(date, t.max))
    post = get_object_or_404(Post.all_objects.filter(date__range=today), slug=slug)
    if post.comments_open():
        Form = request.user.is_authenticated() and CommentForm or AnonymousCommentForm
        form = build_form(Form, request, remote_ip=request.META.get('REMOTE_ADDR'), post=post, user=request.user,
                          initial={'reply_to': reply_to})
        if form.is_valid():
            c, user_is_new = form.save()
            if not request.user.is_authenticated():
                if user_is_new:
                    c.user.backend = 'django.contrib.auth.backends.ModelBackend'
                    _login(request, c.user)
                    message = _('Please look in your mailbox for info about your account.')
                else:
                    ActionRecord.approvals.send_approval(c)
                    message = _('Please look in your mailbox for comment approval link.')
            else:
                message = None
            raise RedirectException(c.get_absolute_url(), notice_message=message)
    else:
        form = None
    return {
            'object': post,
            'form': form,
            'reply_to': reply_to,
            'feedurl': 'comments/%s' % post.id,
            'site': Site.objects.get_current(),
            'post_detail': True}


@ajax_request
def comment_edit(request, object_id):
    comment = get_object_or_404_ajax(CommentNode, pk=object_id)
    if request.user != comment.user:
        return {'error': {'type': 403, 'message': 'Access denied'}}
    if 'get_body' in request.POST:
        return {'body': comment.body}
    elif 'body' in request.POST:
        comment.body = request.POST['body']
        comment.save()
        return {'body_html': comment.body_html}
    else:
        return {'error': {'type': 400, 'message': 'Bad request'}}


@ajax_request
def comment_delete(request, object_id):
    if not request.user.is_staff:
        return {'error': {'type': 403, 'message': 'Access denied'}}
    comment = get_object_or_404_ajax(CommentNode, pk=object_id)
    if request.POST.get('delete'):
        comment.delete()
        return {'success': True, 'id': object_id}
    else:
        return {'error': {'type': 400, 'message': 'Bad request'}}


@ajax_request
def preview(request):
    return {'body_preview': render(request.POST['body'], settings.RENDER_METHOD)}


def process_root_request(request):
    return HttpResponseRedirect('/%s' % settings.BLOG_URLCONF_ROOT)


@render_to('processed.js')
def processed_js(request):
    return {}


@render_to('wysiwyg.js')
def wysiwyg_js(request):
    return {}


@render_to('blog/featured.html')
def featured(request):
    featured_list = Post.featured_objects.all()
    return {'object_list': featured_list}
