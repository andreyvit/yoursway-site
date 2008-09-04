"""
Models for generic tagging.
"""
from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _
from django.contrib import admin

from tagging.managers import TagManager, TaggedItemManager
from tagging.validators import isTag
from lib.helpers import reverse


class Tag(models.Model):
    """
    A tag.
    """
    name = models.CharField(_('name'), max_length=50, unique=True, db_index=True, validator_list=[isTag])
    translation = models.CharField(_('name translation'), max_length=50, blank=True)

    objects = TagManager()

    class Meta:
        db_table = 'tag'
        ordering = ('name',)
        verbose_name = _('tag')
        verbose_name_plural = _('tags')

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('post_by_tag', tag=self.name)

    def get_name(self):
        if self.translation:
            return self.translation
        else:
            return self.name


class TaggedItem(models.Model):
    """
    Holds the relationship between a tag and the item being tagged.
    """
    tag = models.ForeignKey(Tag, verbose_name=_('tag'), related_name='items')
    content_type = models.ForeignKey(ContentType, verbose_name=_('content type'))
    object_id = models.PositiveIntegerField(_('object id'), db_index=True)
    object = generic.GenericForeignKey('content_type', 'object_id')

    objects = TaggedItemManager()

    class Meta:
        db_table = 'tagged_item'
        verbose_name = _('tagged item')
        verbose_name_plural = _('tagged items')
        # Enforce unique tag association per object
        unique_together = (('tag', 'content_type', 'object_id'),)

    def __unicode__(self):
        return u'%s [%s]' % (self.object, self.tag)


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'translation')

admin.site.register(Tag, TagAdmin)
admin.site.register(TaggedItem)
