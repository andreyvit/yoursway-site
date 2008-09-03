# This module must be imported somewhere to work

import settings
import traceback

from django.db.models import signals
from django.template import Context, loader, Template, TemplateDoesNotExist
from django.core.mail import mail_admins
from django.contrib.sites.models import Site
from django.contrib.auth.models import User

from discussion.models import CommentNode
from blog.models import Post
from watchlist.models import Subscription


DEFAULT_COMMENT_SUBJECT = '''New comment for {{ comment.content_type }} "{{ obj.name }}" by "{{ comment.user.first_name }}"'''
DEFAULT_COMMENT_BODY = '''Author: {{ comment.user }}

Comment text:
{{ comment.body }}

Reply: {{ site_url }}{{ comment.get_absolute_url }}

You can unsubscribe at: {% load watchlist_tags %}{{ site_url }}{% unsubscribe_url comment.object %}'''


def send_comment_by_mail(instance, created, **kwargs):
    if not created:
        return
    comment = instance
    obj = comment.object
    if getattr(obj, 'is_draft', False):
        return

    # use templates for mail subject and body
    try:
        subject_tmp = loader.get_template("comment_subject.txt")
    except TemplateDoesNotExist:
        subject_tmp = Template(DEFAULT_COMMENT_SUBJECT)
    try:
        body_tmp = loader.get_template("comment_body.txt")
    except TemplateDoesNotExist:
        body_tmp = Template(DEFAULT_COMMENT_BODY)

    current_domain = Site.objects.get_current()
    site_url = '%s://%s' % (settings.SITE_PROTOCOL, current_domain)
    ctx = Context({'obj': obj, 'comment': comment, 'site_url': site_url})
    subject = subject_tmp.render(ctx).strip()
    body = body_tmp.render(ctx).strip()

    # send email to the user
    try:
        for user in Subscription.objects.get_subscribers(obj, exclude=(comment.user, )):
            if user.email:
                user.email_user(subject, body)
    except UnicodeEncodeError:
        if not settings.DEBUG:
            mail_admins("Trouble while sending email", traceback.format_exc())
        else:
            raise


signals.post_save.connect(send_comment_by_mail, sender=CommentNode)
