from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from accounts.models import Profile


class AccountsViewsTests(TestCase):
    def test_signup_creates_user_profile_and_redirects(self):
        url = reverse("accounts:signup")
        resp = self.client.post(
            url,
            data={
                "username": "john",
                "email": "john@example.com",
                "goal": "maintain",
                "sex": "M",
                "height_cm": 175,
                "weight_kg": 70,
                "password1": "StrongPass123",
                "password2": "StrongPass123",
            },
        )
        # Redirige vers /accounts/signup/done/ (activation_sent)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, reverse("accounts:activation_sent"))

        # User + profile created
        User = get_user_model()
        self.assertTrue(User.objects.filter(username="john").exists())
        u = User.objects.get(username="john")
        self.assertTrue(Profile.objects.filter(user=u).exists())

    def test_profile_edit_requires_login_redirects_to_login(self):
        url = reverse("accounts:profile_edit")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 302)
        expected_login = f"{reverse('accounts:login')}?next={url}"
        self.assertEqual(resp.url, expected_login)

    def test_profile_detail_requires_login_redirects_to_login(self):
        url = reverse("accounts:profile")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 302)
        expected_login = f"{reverse('accounts:login')}?next={url}"
        self.assertEqual(resp.url, expected_login)

    def test_profile_edit_updates_profile_when_logged_in(self):
        # create & login a user
        User = get_user_model()
        u = User.objects.create_user(username="maria", password="pass12345")
        logged = self.client.login(username="maria", password="pass12345")
        self.assertTrue(logged)

        url = reverse("accounts:profile_edit")
        resp = self.client.post(
            url,
            data={
                "sex": "F",
                "height_cm": 170,
                "weight_kg": "60.0",
                "goal": "cut",
                "running_data_source": "manual",
            },
        )
        # redirect to profile page after success
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, reverse("accounts:profile"))

        u.refresh_from_db()
        self.assertEqual(u.profile.sex, "F")
        self.assertEqual(u.profile.height_cm, 170)
        self.assertEqual(str(u.profile.weight_kg), "60.00")
        self.assertEqual(u.profile.goal, "cut")
