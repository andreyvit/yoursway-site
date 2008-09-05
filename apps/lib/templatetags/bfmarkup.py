"""
Byteflow's own markup filters to avoid using of django's currently broken
as of 12.02.2008.
For status see http://code.djangoproject.com/ticket/6387
"""
from django import template
from django.conf import settings
from django.utils.encoding import smart_str, force_unicode
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def strong_spaces(value):
    return mark_safe(value.replace(u' ',u'&nbsp;'))
strong_spaces.is_safe = True


@register.filter
def markdown(value, arg=''):
    """
    Runs Markdown over a given value, optionally using various
    extensions python-markdown supports.

    Syntax::

        {{ value|markdown:"extension1_name,extension2_name..." }}

    To enable safe mode, which strips raw HTML and only returns HTML
    generated by actual Markdown syntax, pass "safe" as the first
    extension in the list.

    If the version of Markdown in use does not support extensions,
    they will be silently ignored.

    """
    try:
        import markdown
    except ImportError:
        if settings.DEBUG:
            raise template.TemplateSyntaxError, "Error in {% markdown %} filter: The Python markdown library isn't installed."
        return force_unicode(value)
    else:
        # markdown.version was first added in 1.6b. The only version of markdown
        # to fully support extensions before 1.6b was the shortlived 1.6a.
        if hasattr(markdown, 'version'):
            extensions = [e for e in arg.split(",") if e]
            if len(extensions) > 0 and extensions[0] == "safe":
                extensions = extensions[1:]
                safe_mode = True
            else:
                safe_mode = False
            # markdown 1.6 was the first to add proper unicode support
            if markdown.version_info < (1,6):
                return mark_safe(force_unicode(markdown.markdown(smart_str(value), extensions, safe_mode=safe_mode)))
            else:
                return mark_safe(markdown.markdown(force_unicode(value), extensions, safe_mode=safe_mode))
        else:
            return mark_safe(force_unicode(markdown.markdown(smart_str(value))))
markdown.is_safe = True


@register.filter
def cond_display(value, variants):
    return mark_safe(variants.split(',')[bool(value)])


@register.filter
def list_attr(value, attr_name):
    def get_attr(item):
        attr = getattr(item, attr_name, None)
        if callable(attr):
            return attr()
        return attr
    return [get_attr(item) for item in value]