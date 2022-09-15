from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='boards-home'),
    path('about/', views.about, name='boards-about'),
]
