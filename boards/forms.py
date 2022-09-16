from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class UserRegistrationForm(UserCreationForm):
    """
    Registration form class. For inheritance by form views.
    Inherits UserCreationForm and email field from django
    forms library and operates on User model.
    """

    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']