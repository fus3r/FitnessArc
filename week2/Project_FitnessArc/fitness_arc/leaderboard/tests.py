from django.test import TestCase

# Create your tests here.
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class LeaderboardTests(TestCase):
    def setUp(self):
        # Create temporary test users
        self.user = User.objects.create_user("user1", password="123")
        self.friend = User.objects.create_user("user2", password="123")
        self.admin = User.objects.create_superuser("admin", password="123")

    def test_leaderboard_hides_admin(self):
        self.client.login(username="user1", password="123")
        response = self.client.get(reverse("leaderboard:index"))

        html = response.content.decode()

        self.assertIn("user1", html)
        self.assertIn("user2", html)
        self.assertNotIn("admin", html)