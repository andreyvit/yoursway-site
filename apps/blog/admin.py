from django.contrib import admin
from apps.blog.models import Post

class PostAdmin(admin.ModelAdmin):
    list_display = ['name', 'pub_date', 'upd_date']

admin.site.register(Post, PostAdmin)