from django.urls import path
from . import views

urlpatterns = [
    path('', views.PostList.as_view(), name='boards_home'),
    path('post/<slug:slug>/', views.FullPost.as_view(), name='boards_post'),
]
