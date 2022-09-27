"""
Form configuration for boards app
"""
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django_summernote.widgets import SummernoteWidget
from .models import UserProfile, Post, Comment


class UserRegistrationForm(UserCreationForm):
    """
    Registration form class which inherits django UserCreationForm.
    For inheritance by form views.
    Inherits UserCreationForm and email field from django
    forms library and operates on User model.
    """

    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class UserUpdateForm(forms.ModelForm):
    """
    Model form class which inherits the ModelForm object from forms.
    Will allow the user to update their info in the User model
    from the front end.
    """

    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']


class ProfileUpdateForm(forms.ModelForm):
    """
    Model form class which inherits the ModelForm object from forms.
    Will allow the user to upload a profile picture to the UserProfile
    model from the front end.
    """
    class Meta:
        model = UserProfile
        fields = ['profile_image']


class PostForm(forms.ModelForm):
    """
    Model form class which inherits the ModelForm object from forms.
    Will add the Summernote WYSIWYG editor to the CreatePost and UpdatePost
    views so that the user can avail of rich text formatting when
    posting/updating messages.
    """

    class Meta:
        model = Post
        fields = ['title', 'category', 'content', 'post_image']
        widgets = {
            'content': SummernoteWidget(),
        }


class CommentForm(forms.ModelForm):
    """
    Comment form to be displayed below posts if user is logged in.
    """

    class Meta:
        model = Comment
        fields = ('body',)
        widgets = {
          'body': forms.Textarea(attrs={'rows': 3, 'cols': 150}),
        }


class ContactForm(forms.Form):
    """
    Simple contact form to be displayed from 'Contact Admin' links.
    """

    name = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    subject = forms.CharField(required=True)
    message = forms.CharField(widget=forms.Textarea)
