from django.contrib import admin
from apps.menu.models import Menu

class MenuAdmin(admin.ModelAdmin):
    list_display = ['name', 'url', 'order']
    ordering = ('order',)

admin.site.register(Menu, MenuAdmin)