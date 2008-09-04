from django.db import models

SELECT_SQL = {
    'approved_comments_count': 'SELECT COUNT(*) FROM comment_nodes, django_content_type ' \
        'WHERE comment_nodes.content_type_id = django_content_type.id ' \
        'AND django_content_type.model = \'post\' ' \
        'AND comment_nodes.object_id = blog_post.id ' \
        'AND comment_nodes.approved',
    'pingback_count': 'SELECT COUNT(*) FROM pingback, django_content_type ' \
        'WHERE pingback.content_type_id = django_content_type.id ' \
        'AND django_content_type.model = \'post\' ' \
        'AND pingback.object_id = blog_post.id'
    }


class PostManager(models.Manager):
    def get_query_set(self):
        qs = super(PostManager, self).get_query_set()
        qs = qs.extra(select=SELECT_SQL, params=[])
        return qs


class PublicPostManager(PostManager):
    def get_query_set(self):
        qs = super(PublicPostManager, self).get_query_set().filter(is_draft=False)
        return qs


class FeaturedPostManager(PublicPostManager):
    def get_query_set(self):
        qs = super(FeaturedPostManager, self).get_query_set().filter(is_featured=True)
        return qs

