from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from decimal import Decimal
from .models import (
    SportCategory, Exercise, WorkoutTemplate, TemplateItem, 
    WorkoutSession, SetLog, PR
)
from .views import update_prs_for_session

User = get_user_model()


class SportCategoryModelTests(TestCase):
    """Tests pour le modèle SportCategory"""
    
    def test_sport_category_creation(self):
        """Test de création d'une catégorie de sport"""
        category = SportCategory.objects.create(
            name="Musculation",
            slug="musculation",
            icon="🏋️",
            description="Sports de force",
            order=1
        )
        
        self.assertEqual(category.name, "Musculation")
        self.assertEqual(str(category), "🏋️ Musculation")
    
    def test_sport_category_ordering(self):
        """Test de l'ordre d'affichage"""
        cat1 = SportCategory.objects.create(name="Cat1", slug="cat1", order=2)
        cat2 = SportCategory.objects.create(name="Cat2", slug="cat2", order=1)
        
        categories = list(SportCategory.objects.all())
        self.assertEqual(categories[0], cat2)
        self.assertEqual(categories[1], cat1)


class ExerciseModelTests(TestCase):
    """Tests pour le modèle Exercise"""
    
    def setUp(self):
        self.category = SportCategory.objects.create(
            name="Musculation",
            slug="musculation"
        )
    
    def test_exercise_creation(self):
        """Test de création d'un exercice"""
        exercise = Exercise.objects.create(
            name="Développé couché",
            slug="dev-couche",
            muscle_group="chest",
            equipment="barbell",
            difficulty=3,
            sport_category=self.category
        )
        
        self.assertEqual(exercise.name, "Développé couché")
        self.assertFalse(exercise.is_time_based)
        self.assertEqual(str(exercise), "Développé couché")
    
    def test_time_based_exercise(self):
        """Test d'un exercice basé sur le temps"""
        plank = Exercise.objects.create(
            name="Plank",
            slug="plank",
            muscle_group="core",
            equipment="bodyweight",
            difficulty=2,
            is_time_based=True
        )
        
        self.assertTrue(plank.is_time_based)


class WorkoutTemplateModelTests(TestCase):
    """Tests pour le modèle WorkoutTemplate"""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.exercise = Exercise.objects.create(
            name="Squat",
            slug="squat",
            muscle_group="legs",
            equipment="barbell",
            difficulty=3
        )
    
    def test_template_creation(self):
        """Test de création d'un template"""
        template = WorkoutTemplate.objects.create(
            owner=self.user,
            name="PPL Push",
            is_public=False
        )
        
        self.assertEqual(template.name, "PPL Push")
        self.assertFalse(template.is_public)
        self.assertEqual(str(template), "PPL Push")
    
    def test_template_with_items(self):
        """Test d'un template avec des exercices"""
        template = WorkoutTemplate.objects.create(
            owner=self.user,
            name="Legs Day"
        )
        
        item1 = TemplateItem.objects.create(
            template=template,
            exercise=self.exercise,
            order=1,
            sets=4,
            reps=8,
            rest_seconds=120
        )
        
        self.assertEqual(template.items.count(), 1)
        self.assertEqual(template.items.first().exercise, self.exercise)


class SetLogModelTests(TestCase):
    """Tests pour le modèle SetLog"""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        
        self.reps_exercise = Exercise.objects.create(
            name="Bench Press",
            slug="bench-press",
            muscle_group="chest",
            equipment="barbell",
            difficulty=3,
            is_time_based=False
        )
        
        self.time_exercise = Exercise.objects.create(
            name="Plank",
            slug="plank",
            muscle_group="core",
            equipment="bodyweight",
            difficulty=2,
            is_time_based=True
        )
        
        self.session = WorkoutSession.objects.create(
            owner=self.user,
            duration_minutes=45
        )
    
    def test_setlog_volume_with_reps(self):
        """Test du calcul du volume avec reps"""
        log = SetLog.objects.create(
            session=self.session,
            exercise=self.reps_exercise,
            set_number=1,
            reps=10,
            weight_kg=Decimal('80.00')
        )
        
        expected_volume = 80.0 * 10
        self.assertEqual(log.volume, expected_volume)
    
    def test_setlog_volume_time_based(self):
        """Test du calcul du volume pour exercice basé sur le temps"""
        log = SetLog.objects.create(
            session=self.session,
            exercise=self.time_exercise,
            set_number=1,
            duration_seconds=60,
            weight_kg=Decimal('0.00')
        )
        
        self.assertEqual(log.volume, 0.0)
    
    def test_display_performance_reps(self):
        """Test de l'affichage de la performance avec reps"""
        log = SetLog.objects.create(
            session=self.session,
            exercise=self.reps_exercise,
            set_number=1,
            reps=12,
            weight_kg=Decimal('70.00')
        )
        
        self.assertEqual(log.display_performance, "12")
    
    def test_display_performance_time_seconds(self):
        """Test de l'affichage du temps en secondes"""
        log = SetLog.objects.create(
            session=self.session,
            exercise=self.time_exercise,
            set_number=1,
            duration_seconds=45,
            weight_kg=Decimal('0.00')
        )
        
        self.assertEqual(log.display_performance, "45s")
    
    def test_display_performance_time_minutes(self):
        """Test de l'affichage du temps en minutes:secondes"""
        log = SetLog.objects.create(
            session=self.session,
            exercise=self.time_exercise,
            set_number=1,
            duration_seconds=125,  # 2:05
            weight_kg=Decimal('0.00')
        )
        
        self.assertEqual(log.display_performance, "2:05")


class WorkoutSessionModelTests(TestCase):
    """Tests pour le modèle WorkoutSession"""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.exercise = Exercise.objects.create(
            name="Deadlift",
            slug="deadlift",
            muscle_group="back",
            equipment="barbell",
            difficulty=4
        )
    
    def test_session_creation(self):
        """Test de création d'une session"""
        session = WorkoutSession.objects.create(
            owner=self.user,
            duration_minutes=60
        )
        
        self.assertEqual(session.owner, self.user)
        self.assertFalse(session.is_completed)
    
    def test_total_volume_calculation(self):
        """Test du calcul du volume total"""
        session = WorkoutSession.objects.create(
            owner=self.user,
            duration_minutes=45
        )
        
        SetLog.objects.create(
            session=session,
            exercise=self.exercise,
            set_number=1,
            reps=5,
            weight_kg=Decimal('100.00')
        )
        
        SetLog.objects.create(
            session=session,
            exercise=self.exercise,
            set_number=2,
            reps=5,
            weight_kg=Decimal('120.00')
        )
        
        expected_volume = (100 * 5) + (120 * 5)
        self.assertEqual(session.total_volume, expected_volume)
    
    def test_estimated_calories_burned(self):
        """Test du calcul des calories brûlées"""
        session = WorkoutSession.objects.create(
            owner=self.user,
            duration_minutes=30
        )
        
        # 30 minutes * 5 kcal/min = 150 kcal
        self.assertEqual(session.estimated_calories_burned, 150)
    
    def test_estimated_calories_burned_zero_duration(self):
        """Test des calories avec durée nulle"""
        session = WorkoutSession.objects.create(
            owner=self.user,
            duration_minutes=0
        )
        
        self.assertEqual(session.estimated_calories_burned, 0)


class PRModelTests(TestCase):
    """Tests pour le modèle PR (Personal Records)"""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.exercise = Exercise.objects.create(
            name="Squat",
            slug="squat",
            muscle_group="legs",
            equipment="barbell",
            difficulty=3
        )
    
    def test_pr_creation(self):
        """Test de création d'un PR"""
        pr = PR.objects.create(
            owner=self.user,
            exercise=self.exercise,
            metric="max_weight",
            value=Decimal('150.00')
        )
        
        self.assertEqual(pr.metric, "max_weight")
        self.assertEqual(pr.value, Decimal('150.00'))
    
    def test_pr_unique_together(self):
        """Test de la contrainte unique owner+exercise+metric"""
        PR.objects.create(
            owner=self.user,
            exercise=self.exercise,
            metric="max_weight",
            value=Decimal('150.00')
        )
        
        # Attempting to create a duplicate should fail
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            PR.objects.create(
                owner=self.user,
                exercise=self.exercise,
                metric="max_weight",
                value=Decimal('160.00')
            )


class UpdatePRsFunctionTests(TestCase):
    """Tests pour la fonction update_prs_for_session"""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.exercise = Exercise.objects.create(
            name="Bench Press",
            slug="bench-press",
            muscle_group="chest",
            equipment="barbell",
            difficulty=3
        )
        self.session = WorkoutSession.objects.create(
            owner=self.user,
            duration_minutes=45
        )
    
    def test_update_prs_max_weight(self):
        """Test de mise à jour du PR de charge max"""
        SetLog.objects.create(
            session=self.session,
            exercise=self.exercise,
            set_number=1,
            reps=5,
            weight_kg=Decimal('100.00')
        )
        
        SetLog.objects.create(
            session=self.session,
            exercise=self.exercise,
            set_number=2,
            reps=3,
            weight_kg=Decimal('110.00')
        )
        
        update_prs_for_session(self.session)
        
        pr = PR.objects.get(
            owner=self.user,
            exercise=self.exercise,
            metric="max_weight"
        )
        
        self.assertEqual(pr.value, Decimal('110.00'))
    
    def test_update_prs_max_reps(self):
        """Test de mise à jour du PR de reps max"""
        SetLog.objects.create(
            session=self.session,
            exercise=self.exercise,
            set_number=1,
            reps=15,
            weight_kg=Decimal('60.00')
        )
        
        update_prs_for_session(self.session)
        
        pr = PR.objects.get(
            owner=self.user,
            exercise=self.exercise,
            metric="max_reps"
        )
        
        self.assertEqual(pr.value, Decimal('15'))
    
    def test_update_prs_improvement(self):
        """Test de l'amélioration d'un PR existant"""
        # Create an initial PR
        PR.objects.create(
            owner=self.user,
            exercise=self.exercise,
            metric="max_weight",
            value=Decimal('100.00')
        )
        
        # New session with higher weight
        SetLog.objects.create(
            session=self.session,
            exercise=self.exercise,
            set_number=1,
            reps=5,
            weight_kg=Decimal('120.00')
        )
        
        update_prs_for_session(self.session)
        
        pr = PR.objects.get(
            owner=self.user,
            exercise=self.exercise,
            metric="max_weight"
        )
        
        self.assertEqual(pr.value, Decimal('120.00'))


class WorkoutViewTests(TestCase):
    """Tests pour les vues de l'app workouts"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.client.login(username='testuser', password='password123')
        
        self.exercise = Exercise.objects.create(
            name="Pull Up",
            slug="pull-up",
            muscle_group="back",
            equipment="bodyweight",
            difficulty=3
        )
        
        self.template = WorkoutTemplate.objects.create(
            owner=self.user,
            name="Upper Body"
        )
    
    def test_exercise_list_view(self):
        """Test de la vue liste d'exercices"""
        url = reverse('workouts:exercise_list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('exercises', response.context)
    
    def test_template_list_view_requires_login(self):
        """Test que la liste de templates nécessite une authentification"""
        self.client.logout()
        url = reverse('workouts:template_list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)
    
    def test_template_list_view(self):
        """Test de la vue liste de templates"""
        url = reverse('workouts:template_list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('my_templates', response.context)
    
    def test_template_create_view(self):
        """Test de création d'un template"""
        url = reverse('workouts:template_create')
        response = self.client.post(url, {'name': 'New Template'})
        
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            WorkoutTemplate.objects.filter(
                owner=self.user,
                name='New Template'
            ).exists()
        )
    
    def test_start_session_from_template(self):
        """Test de démarrage d'une session depuis un template"""
        url = reverse('workouts:start_session', args=[self.template.pk])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            WorkoutSession.objects.filter(
                owner=self.user,
                from_template=self.template
            ).exists()
        )
    
    def test_session_detail_add_set_reps(self):
        """Test d'ajout d'une série avec reps"""
        session = WorkoutSession.objects.create(
            owner=self.user,
            from_template=self.template
        )
        
        TemplateItem.objects.create(
            template=self.template,
            exercise=self.exercise,
            order=1
        )
        
        url = reverse('workouts:session_detail', args=[session.pk])
        response = self.client.post(url, {
            'duration_minutes': 30,
            'exercise_id': self.exercise.id,
            'set_number': 1,
            'reps': 10,
            'weight_kg': 0
        })
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(session.set_logs.count(), 1)
    
    def test_session_detail_add_set_time_based(self):
        """Test d'ajout d'une série avec durée"""
        plank = Exercise.objects.create(
            name="Plank",
            slug="plank",
            muscle_group="core",
            equipment="bodyweight",
            is_time_based=True
        )
        
        session = WorkoutSession.objects.create(
            owner=self.user,
            from_template=self.template
        )
        
        TemplateItem.objects.create(
            template=self.template,
            exercise=plank,
            order=1
        )
        
        url = reverse('workouts:session_detail', args=[session.pk])
        response = self.client.post(url, {
            'duration_minutes': 20,
            'exercise_id': plank.id,
            'set_number': 1,
            'duration_seconds': 60,
            'weight_kg': 0
        })
        
        self.assertEqual(response.status_code, 302)
        log = session.set_logs.first()
        self.assertEqual(log.duration_seconds, 60)
        self.assertIsNone(log.reps)
    
    def test_complete_session(self):
        """Test de finalisation d'une session"""
        session = WorkoutSession.objects.create(
            owner=self.user,
            duration_minutes=0
        )
        
        SetLog.objects.create(
            session=session,
            exercise=self.exercise,
            set_number=1,
            reps=8,
            weight_kg=Decimal('70.00')
        )
        
        url = reverse('workouts:complete_session', args=[session.pk])
        response = self.client.post(url, {
            'duration_minutes': 45
        })
        
        session.refresh_from_db()
        self.assertTrue(session.is_completed)
        self.assertEqual(session.duration_minutes, 45)
    
    def test_cancel_empty_session(self):
        """Test d'annulation d'une session vide"""
        session = WorkoutSession.objects.create(
            owner=self.user,
            duration_minutes=0
        )
        
        session_id = session.pk
        
        url = reverse('workouts:complete_session', args=[session.pk])
        response = self.client.post(url, {
            'duration_minutes': 0
        })
        
        # The session should be deleted
        self.assertFalse(
            WorkoutSession.objects.filter(pk=session_id).exists()
        )
    
    def test_session_delete(self):
        """Test de suppression d'une session"""
        session = WorkoutSession.objects.create(
            owner=self.user,
            duration_minutes=30,
            is_completed=True
        )
        
        SetLog.objects.create(
            session=session,
            exercise=self.exercise,
            set_number=1,
            reps=10,
            weight_kg=Decimal('80.00')
        )
        
        # Create a PR
        update_prs_for_session(session)
        
        session_id = session.pk
        
        url = reverse('workouts:session_delete', args=[session.pk])
        response = self.client.post(url)
        
        # The session should be deleted
        self.assertFalse(
            WorkoutSession.objects.filter(pk=session_id).exists()
        )
    
    def test_set_log_delete(self):
        """Test de suppression d'un set log"""
        session = WorkoutSession.objects.create(
            owner=self.user,
            duration_minutes=30
        )
        
        log = SetLog.objects.create(
            session=session,
            exercise=self.exercise,
            set_number=1,
            reps=10,
            weight_kg=Decimal('80.00')
        )
        
        url = reverse('workouts:set_log_delete', args=[session.pk, log.pk])
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, 302)
        self.assertFalse(SetLog.objects.filter(pk=log.pk).exists())
    
    def test_template_detail_add_item(self):
        """Test d'ajout d'un exercice à un template"""
        url = reverse('workouts:template_detail', args=[self.template.pk])
        response = self.client.post(url, {
            'exercise': self.exercise.id,
            'sets': 3,
            'reps': 10,
            'rest_seconds': 90
        })
        
        self.assertEqual(self.template.items.count(), 1)
    
    def test_template_item_delete(self):
        """Test de suppression d'un item de template"""
        item = TemplateItem.objects.create(
            template=self.template,
            exercise=self.exercise,
            order=1
        )
        
        url = reverse('workouts:template_item_delete', args=[self.template.pk, item.pk])
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, 302)
        self.assertFalse(TemplateItem.objects.filter(pk=item.pk).exists())
    
    def test_template_delete(self):
        """Test de suppression d'un template"""
        template_id = self.template.pk
        
        url = reverse('workouts:template_delete', args=[self.template.pk])
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            WorkoutTemplate.objects.filter(pk=template_id).exists()
        )
    
    def test_cannot_modify_other_user_template(self):
        """Test qu'on ne peut pas modifier le template d'un autre utilisateur"""
        other_user = User.objects.create_user(username='otheruser', password='password123')
        other_template = WorkoutTemplate.objects.create(
            owner=other_user,
            name="Other Template",
            is_public=True  # Template public visible
        )
        
        # Peut voir le template (GET)
        url = reverse('workouts:template_detail', args=[other_template.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['is_owner'])
        
        # Ne peut pas ajouter d'exercice (POST)
        response = self.client.post(url, {
            'exercise': self.exercise.id,
            'sets': 3,
            'reps': 10,
            'rest_seconds': 90
        })
        
        # Should be redirected and no item added
        self.assertEqual(response.status_code, 302)
        self.assertEqual(other_template.items.count(), 0)
