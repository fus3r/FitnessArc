from django.test import TestCase

# Create your tests here.
from datetime import date, timedelta
from django.contrib.auth import get_user_model
from django.urls import reverse
from workouts.models import WorkoutSession
from dashboard.services import get_dashboard_data
from dashboard.templatetags.time_format import duration_hm
from django.test import SimpleTestCase

User = get_user_model()


class DashboardServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )

    def test_weekly_training_time_uses_minutes(self):
        today = date.today()

        # 2 sessions in the last 7 days
        WorkoutSession.objects.create(
            owner=self.user,
            date=today,
            duration_minutes=30,
            is_completed=True,
        )
        WorkoutSession.objects.create(
            owner=self.user,
            date=today - timedelta(days=2),
            duration_minutes=45,
            is_completed=True,
        )

        data = get_dashboard_data(self.user)

        # service returns 75 minutes
        self.assertEqual(data["weekly_training_time"], 75)
        self.assertEqual(data["weekly_training_hours"], 1)
        self.assertEqual(data["weekly_training_min"], 15)


class DurationHmFilterTests(SimpleTestCase):
    def test_only_minutes(self):
        self.assertEqual(duration_hm(45), "45min")

    def test_exact_hours(self):
        self.assertEqual(duration_hm(120), "2h")

    def test_hours_and_minutes(self):
        self.assertEqual(duration_hm(63), "1h03min")

    def test_none_value(self):
        self.assertEqual(duration_hm(None), "0min")

    def test_invalid_value(self):
        self.assertEqual(duration_hm("abc"), "0min")

class DashboardViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="viewer",
            email="viewer@example.com",
            password="testpass123",
        )

    def test_dashboard_requires_login(self):
        url = reverse("dashboard:index")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/accounts/login", resp["Location"])

    def test_dashboard_renders_for_logged_user(self):
        self.client.force_login(self.user)
        url = reverse("dashboard:index")
        resp = self.client.get(url)

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "dashboard/index.html")

        # basic keys exist in context
        self.assertIn("weekly_training_time", resp.context)
        self.assertIn("calendar_weeks", resp.context)