from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.PostList.as_view(), name='boards_home'),
    path(
        'posts/user/<str:username>/',
        views.UserPostList.as_view(),
        name='user_posts'),
    path(
        'posts/category/<str:category>/',
        views.CategoryList.as_view(),
        name='category_posts'),
    path('post/<slug:slug>/', views.FullPost.as_view(), name='boards_post'),
    path('like/<slug:slug>/', views.PostLike.as_view(), name='post_like'),
    path('register/', views.register, name='register'),
    path('user/profile/', views.profile, name='profile'),
    path('login/', auth_views.LoginView.as_view(
        template_name='login.html'
        ),
        name='login'),
    path('logout/', auth_views.LogoutView.as_view(
        template_name='logout.html'
        ),
        name='logout'),
    path('password-reset/',
         auth_views.PasswordResetView.as_view(
            template_name='password_reset.html'
         ),
         name='password_reset'),
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
            template_name='password_reset_done.html'
         ),
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
            template_name='password_reset_confirm.html'
         ),
         name='password_reset_confirm'),
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='password_reset_complete.html'
         ),
         name='password_reset_complete'),
    path('new/', views.CreatePost.as_view(
        template_name='post_form.html'
        ),
        name='create_post'),
    path('post/<slug:slug>/update/', views.UpdatePost.as_view(
        template_name='post_form.html'
        ),
        name='update_post'),
    path('post/<slug:slug>/delete/', views.DeletePost.as_view(
        template_name='post_confirm_delete.html'
        ),
        name='delete_post'),
    path('contact/', views.ContactFormView.as_view(), name='contact_form'),
]
