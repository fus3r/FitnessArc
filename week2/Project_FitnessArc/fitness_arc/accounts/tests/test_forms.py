from django.test import TestCase
from django.contrib.auth import get_user_model
from accounts.forms import SignupForm, ProfileForm
from accounts.models import Profile


class SignupFormTests(TestCase):
    def test_signup_form_valid(self):
        form = SignupForm(
            data={
                "username": "newuser",
                "email": "new@example.com",
                "goal": "bulk",
                "sex": "M",
                "height_cm": 180,
                "weight_kg": 75,
                "password1": "StrongPass123",
                "password2": "StrongPass123",
            }
        )
        self.assertTrue(form.is_valid(), form.errors)
        user = form.save()
        self.assertIsNotNone(user.pk)
        self.assertTrue(user.check_password("StrongPass123"))
        # profil créé et goal appliqué
        self.assertTrue(Profile.objects.filter(user=user, goal="bulk").exists())

    def test_signup_form_invalid_password_mismatch(self):
        form = SignupForm(
            data={
                "username": "oops",
                "email": "",
                "goal": "cut",
                "password1": "abc12345",
                "password2": "different123",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)


class ProfileFormTests(TestCase):
    def test_profile_form_validation_negative_height(self):
        User = get_user_model()
        u = User.objects.create_user(username="pierre", password="x")
        form = ProfileForm(
            data={
                "sex": "M",
                "height_cm": 0,             # invalide
                "weight_kg": "72.5",
                "goal": "maintain",
            },
            instance=u.profile,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("height_cm", form.errors)
