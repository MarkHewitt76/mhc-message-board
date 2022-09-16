from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin
from .models import Post

# admin.site.register(Post)


@admin.register(Post)
class PostAdmin(SummernoteModelAdmin):
    """
    Adds Post model to admin page with search bar,
    Summernote WYSIWYG editor, formatted fields and
    filter panels. Slug field prepopulated from title.
    """

    list_display = ('title', 'slug', 'status', 'created_on')
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}
    list_filter = ('status', 'created_on')
    summernote_fields = ('content')
