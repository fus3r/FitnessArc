from django.test import TestCase
from django.contrib.auth import get_user_model
from accounts.models import Profile

class ProfileSignalTests(TestCase):
    def test_profile_auto_created(self):
        User = get_user_model()
        u = User.objects.create_user(username='toto', password='x')
        self.assertTrue(Profile.objects.filter(user=u).exists())
        # Accès direct via la relation inversée
        self.assertIsNotNone(u.profile.pk)

