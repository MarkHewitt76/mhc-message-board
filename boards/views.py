from django.shortcuts import render
from django.views import generic
from .models import Post
# from django.http import HttpResponse


class PostList(generic.ListView):
    """
    View for all published posts, in descending order, using
    Post model and inheriting from generic list view model.
    To be used on homepage.
    """

    model = Post
    queryset = Post.objects.filter(status=1).order_by('-created_on')
    template_name = 'index.html'

# def home(request):
#     return HttpResponse('<h1>Homepage</h1>')


# def about(request):
#     return HttpResponse('<h1>About page</h1>')
