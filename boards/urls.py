from django.urls import path
from . import views

urlpatterns = [
    path('', views.PostList.as_view(), name='boards_home'),
    # path('about/', views.about, name='boards-about'),
]
