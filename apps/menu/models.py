from django.db.models.base import Model
from django.db.models.fields import CharField
from django.db.models.fields import IntegerField

class Menu(Model):
    class Meta: 
        verbose_name = 'menu item'
    class Admin: 
        list_display = ['name', 'url', 'order']
        ordering = ('order',)
    
    name = CharField(max_length=100)
    url = CharField(max_length=100)
    order = IntegerField()
