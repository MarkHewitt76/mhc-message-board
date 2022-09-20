from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.PostList.as_view(), name='boards_home'),
    path('post/<slug:slug>/', views.FullPost.as_view(), name='boards_post'),
    path('register/', views.register, name='register'),
    path('user/profile/', views.profile, name='profile'),
    path('login/', auth_views.LoginView.as_view(
        template_name='login.html'
        ),
        name='login'
    ),
    path('logout/', auth_views.LogoutView.as_view(
        template_name='logout.html'
        ),
        name='logout'
    ),
    path('new/', views.CreatePost.as_view(
        template_name='post_form.html'
        ),
        name='create_post'
    ),
    path('post/<slug:slug>/update/', views.UpdatePost.as_view(
        template_name='post_form.html'
        ),
        name='update_post'
    ),
    path('post/<slug:slug>/delete/', views.DeletePost.as_view(
        template_name='post_confirm_delete.html'
        ),
        name='delete_post'
    ),
]
