from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile


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
        fields = ['image']
