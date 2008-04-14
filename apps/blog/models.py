from django.db.models.fields import CharField
from django.db.models.base import Model
from django.db.models.fields import SlugField
from django.db.models.fields import TextField
from django.db.models.fields import DateTimeField

class Post(Model):
    class Admin: list_display = ['name', 'pub_date', 'upd_date']

    name = CharField(max_length=100)
    slug = SlugField(max_length=100)
    text = TextField()
    pub_date = DateTimeField(editable=True)
    upd_date = DateTimeField(auto_now=True, editable=False)