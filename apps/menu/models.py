from django.db.models.base import Model
from django.db.models.fields import CharField
from django.db.models.fields import IntegerField

class Menu(Model):
    class Meta: 
        verbose_name = 'menu item'
    
    name = CharField(max_length=100)
    url = CharField(max_length=100)
    order = IntegerField()
