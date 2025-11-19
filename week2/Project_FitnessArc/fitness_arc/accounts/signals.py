from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from .models import Profile

User = get_user_model()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Crée automatiquement un Profile à la création d'un utilisateur (sauf superusers)."""
    if created and not instance.is_superuser and not instance.is_staff:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def ensure_and_save_profile(sender, instance, **kwargs):
    """
    Garantit qu'un Profile existe (utile avec des fixtures) puis sauvegarde.
    Ignore les superusers et staff.
    """
    if not instance.is_superuser and not instance.is_staff:
        Profile.objects.get_or_create(user=instance)
        instance.profile.save()
