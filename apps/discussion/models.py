import datetime
import md5

from django.conf import settings
from django.db import backend, connection, models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.utils.html import strip_tags
from django.contrib import admin

from blog.templatetags.nofollow import nofollow
from render import render


class CommentNodeManager(models.Manager):
    def for_object(self, obj):
        """
        Create a ``QuerySet`` containing all comments for the given
        object.
        """
        ctype = ContentType.objects.get_for_model(obj)
        return self.filter(content_type__pk=ctype.id, object_id=obj.id)

    def tree_for_object(self, obj, filters=None):
        """
        Get the entire comment tree for an object, with a ``level`
        attribute added to each comment indicating the level at which
        it sits in the tree, starting at ``0`` for root comments.
        """
        comments = self.for_object(obj).select_related().order_by('lft')
        if filters:
            comments = comments.filter(**filters)
        stack = []
        for comment in comments:
            # [:] is used to create a copy of the stack, as the stack will be
            # modified during iteration.
            stack_copy = stack[:]
            for j in stack_copy:
                if j < comment.rght:
                    stack.pop()
            stack_size = len(stack)
            comment.level = stack_size
            stack.append(comment.rght)
        return comments

    def get_counts_in_bulk(self, objects):
        """
        Get a dictionary mapping object ids to the total number of
        comments made against each object.
        """
        query = """
SELECT object_id, COUNT(object_id)
FROM %s
WHERE content_type_id = %%s
  AND object_id IN (%s)
GROUP BY object_id""" % (
            backend.quote_name(self.model._meta.db_table),
            ','.join(['%s'] * len(objects))
        )
        ctype = ContentType.objects.get_for_model(objects[0])
        cursor = connection.cursor()
        cursor.execute(query, [ctype.id] + [obj.id for obj in objects])
        results = cursor.fetchall()
        return dict([(object_id, num_comments) \
                     for object_id, num_comments in results])


class ApprovedCommentNodeManager(CommentNodeManager):
    def get_query_set(self):
        return super(ApprovedCommentNodeManager, self).get_query_set().filter(approved=True)

class CommentNode(models.Model):
    """
    A comment about any ``Model`` instance, which is also a node in
    a tree of comments.
    """
    # Comment fields
    user = models.ForeignKey(User, related_name='comments')
    pub_date = models.DateTimeField(_(u'Publishing date'), editable=False,
                                    default=datetime.datetime.now)
    upd_date = models.DateTimeField(_(u'Date'), auto_now=True, editable=False)
    body = models.TextField(_(u'Body'))
    body_html = models.TextField(_(u'Body HTML'), editable=False)
    reply_to_id = models.PositiveIntegerField(editable=False, null=True, blank=True)
    approved = models.BooleanField(default=False)

    # Generic relation to the object being commented on
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField(db_index=True)
    object = generic.GenericForeignKey('content_type', 'object_id')

    # Tree fields
    lft = models.PositiveIntegerField(db_index=True, editable=False)
    rght = models.PositiveIntegerField(editable=False)

    all_objects = CommentNodeManager()
    objects = ApprovedCommentNodeManager()

    class Meta:
        db_table = 'comment_nodes'

    def __unicode__(self):
        return self.body[:50]

    def get_clean_html(self):
        return strip_tags(self.body_html)[:50]
    get_clean_html.allow_tags = True

    def save(self):
        if self.body:
            self.body = self.body.strip()
            self.body_html = nofollow(render(self.body, 'markdown'))
        if not self.id:
            # Get the object being commented on
            comment_on = self.content_type.get_object_for_this_type(pk=self.object_id)

            if isinstance(comment_on, CommentNode):
                # This is a reply to another comment - adopt its content type
                # and object id so this comment is associated with the correct
                # object.
                self.reply_to_id = self.object_id
                self.content_type = comment_on.content_type
                self.object_id = comment_on.object_id

                # We need to update the whole tree to the right of the comment
                target_rght = comment_on.rght - 1
                cursor = connection.cursor()
                cursor.execute("""
                UPDATE comment_nodes
                SET rght = rght + 2
                WHERE content_type_id = %s
                  AND object_id = %s
                  AND rght > %s""" % (self.content_type.id, self.object_id, target_rght))
                cursor.execute("""
                UPDATE comment_nodes
                SET lft = lft + 2
                WHERE content_type_id = %s
                  AND object_id = %s
                  AND lft > %s""" % (self.content_type.id, self.object_id, target_rght))
                self.lft = target_rght + 1
                self.rght = target_rght + 2
            else:
                # This is a new root comment
                cursor = connection.cursor()
                cursor.execute("""
                SELECT MAX(rght)
                FROM comment_nodes
                WHERE content_type_id = %s
                  AND object_id = %s""", (self.content_type.id, self.object_id))
                row = cursor.fetchone()
                current_max_rght = row[0]
                if current_max_rght is None:
                    # There are no comments for the content object so far
                    self.lft = 1
                    self.rght = 2
                else:
                    # Put this comment at the top level
                    self.lft = current_max_rght + 1
                    self.rght = current_max_rght + 2
        super(CommentNode, self).save()

    def get_absolute_url(self):
        return '%s#c%s' % (self.object.get_absolute_url(), self.id)

    def get_gravatar_url(self):
        gravatar_id = md5.md5(self.user.email).hexdigest()
        default_addr = settings.DEFAULT_AVATAR_PATH + settings.DEFAULT_AVATAR_IMG
        #gravatar_url = 'http://www.gravatar.com/avatar.php?gravatar_id=%s&default=%s&size=%i' % (gravatar_id, default_addr, settings.DEFAULT_AVATAR_SIZE)
        gravatar_url = 'http://www.gravatar.com/avatar.php?gravatar_id=%s&default=%s&size=%i' % (gravatar_id, "", settings.DEFAULT_AVATAR_SIZE)
        return gravatar_url


class CommentNodeAdmin(admin.ModelAdmin):
    list_display = ('get_clean_html', 'user', 'pub_date', 'content_type', 'object_id', 'reply_to_id', 'approved')

admin.site.register(CommentNode, CommentNodeAdmin)

