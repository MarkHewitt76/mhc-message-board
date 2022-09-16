from django.urls import path
from . import views

urlpatterns = [
    path('', views.PostList.as_view(), name='boards_home'),
    path('<slug:slug>/', views.FullPost.as_view(), name='boards-post'),
]
