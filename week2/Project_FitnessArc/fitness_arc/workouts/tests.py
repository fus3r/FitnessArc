from django.test import TestCase

# Create your tests here.
from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Exercise, WorkoutTemplate, TemplateItem, WorkoutSession, SetLog

User = get_user_model()

class WorkoutsSmokeTest(TestCase):
    def setUp(self):
        self.u = User.objects.create_user(username="u", password="x")
        self.ex = Exercise.objects.create(
            name="Développé couché", slug="dev-couche", muscle_group="chest",
            equipment="barbell", difficulty=3
        )

    def test_create_template_and_session(self):
        tpl = WorkoutTemplate.objects.create(owner=self.u, name="PPL")
        TemplateItem.objects.create(template=tpl, exercise=self.ex, order=1, sets=3, reps=8)
        sess = WorkoutSession.objects.create(owner=self.u, from_template=tpl)
        SetLog.objects.create(session=sess, exercise=self.ex, set_number=1, reps=8, weight_kg=80)
        self.assertGreater(sess.total_volume, 0)
