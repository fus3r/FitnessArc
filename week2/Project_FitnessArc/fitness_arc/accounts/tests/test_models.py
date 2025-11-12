from django.test import TestCase
from django.contrib.auth import get_user_model
from accounts.models import Profile


class ProfileModelTests(TestCase):
    def test_profile_auto_created_on_user_creation(self):
        User = get_user_model()
        u = User.objects.create_user(username="bob", password="x")
        self.assertTrue(Profile.objects.filter(user=u).exists())
        # accès relation inverse sans erreur
        self.assertIsNotNone(u.profile.pk)

    def test_profile_str(self):
        User = get_user_model()
        u = User.objects.create_user(username="alice", password="x")
        self.assertEqual(str(u.profile), f"Profile<{u.username}>")
