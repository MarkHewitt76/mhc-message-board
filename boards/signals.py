"""Signals configuration
----------------
Django signals model post_save method
Standard Django User model
Django receiver decorator
boards UserProfile model
"""
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import UserProfile


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """
    Creates a user profile instance automatically upon creation of
    a user model instance.
    The post_save signal is fired when a user is created. User model is
    the sender of the 'instance' and 'created' arguments to this receiver
    function, which creates the related user profile instance.
    """

    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    """
    Receiver function to save an instance of the user profile when the
    post_save signal is sent by the User model.
    """

    instance.user_profile.save()
