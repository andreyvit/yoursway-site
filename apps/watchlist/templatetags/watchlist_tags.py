from django import template
from django.contrib.contenttypes.models import ContentType

from lib.helpers import reverse
from watchlist.models import Subscription

register = template.Library()


@register.simple_tag
def unsubscribe_url(obj):
    ctype = ContentType.objects.get_for_model(obj)
    return reverse('wl_unsubscribe', content_type=ctype.model, object_id=obj.pk)

@register.simple_tag
def subscribe_url(obj):
    ctype = ContentType.objects.get_for_model(obj)
    return reverse('wl_subscribe', content_type=ctype.model, object_id=obj.pk)

@register.filter
def is_subscribed_to(user, obj):
    if not user.is_authenticated():
        return False
    ctype = ContentType.objects.get_for_model(obj)
    try:
        Subscription.objects.get(user=user, content_type=ctype, object_id=obj.pk)
        return True
    except Subscription.DoesNotExist:
        return False