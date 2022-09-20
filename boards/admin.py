from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin
from .models import Category, Post, Comment, UserProfile


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


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """
    Adds Comment model to admin page with search bar,
    customised fields and filter panel.
    """

    list_display = ('name', 'body', 'post', 'created_on')
    list_filter = ('created_on',)
    search_fields = ['name', 'email', 'body']


admin.site.register(Category)

admin.site.register(UserProfile)
