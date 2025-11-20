from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal

from .models import Run, StravaAuth, GarminAuth
from .forms_manual import ManualRunForm
from accounts.models import Profile

User = get_user_model()


class StravaAuthModelTests(TestCase):
    """Tests pour le modèle StravaAuth"""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
    
    def test_strava_auth_creation(self):
        """Test de création d'une autorisation Strava"""
        expires_at = timezone.now() + timedelta(hours=6)
        strava_auth = StravaAuth.objects.create(
            user=self.user,
            athlete_id=12345678,
            access_token="test_access_token",
            refresh_token="test_refresh_token",
            token_expires_at=expires_at
        )
        
        self.assertEqual(strava_auth.user, self.user)
        self.assertEqual(strava_auth.athlete_id, 12345678)
        self.assertEqual(str(strava_auth), f"Strava auth de {self.user.username}")
    
    def test_strava_auth_one_to_one(self):
        """Test de la relation OneToOne avec User"""
        expires_at = timezone.now() + timedelta(hours=6)
        StravaAuth.objects.create(
            user=self.user,
            athlete_id=12345678,
            access_token="test_access_token",
            refresh_token="test_refresh_token",
            token_expires_at=expires_at
        )
        
        # Verify we can access via user.strava_auth
        self.assertTrue(hasattr(self.user, 'strava_auth'))
        self.assertEqual(self.user.strava_auth.athlete_id, 12345678)


class GarminAuthModelTests(TestCase):
    """Tests pour le modèle GarminAuth"""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
    
    def test_garmin_auth_creation(self):
        """Test de création d'une autorisation Garmin"""
        garmin_auth = GarminAuth.objects.create(
            user=self.user,
            email="test@garmin.com",
            password="encrypted_password",
            is_active=True
        )
        
        self.assertEqual(garmin_auth.user, self.user)
        self.assertEqual(garmin_auth.email, "test@garmin.com")
        self.assertTrue(garmin_auth.is_active)
        self.assertEqual(str(garmin_auth), f"Garmin auth de {self.user.username}")
    
    def test_garmin_auth_one_to_one(self):
        """Test de la relation OneToOne avec User"""
        GarminAuth.objects.create(
            user=self.user,
            email="test@garmin.com",
            password="encrypted_password"
        )
        
        # Verify we can access via user.garmin_auth
        self.assertTrue(hasattr(self.user, 'garmin_auth'))
        self.assertEqual(self.user.garmin_auth.email, "test@garmin.com")


class RunModelTests(TestCase):
    """Tests pour le modèle Run"""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        Profile.objects.get_or_create(
            user=self.user,
            defaults={'weight_kg': Decimal('70.00')}
        )
    
    def test_run_creation_manual(self):
        """Test de création d'une course manuelle"""
        run = Run.objects.create(
            user=self.user,
            source='manual',
            name="Course matinale",
            distance_m=5000,
            moving_time_s=1500,  # 25 minutes
            elapsed_time_s=1560,  # 26 minutes
            start_date=timezone.now()
        )
        
        self.assertEqual(run.user, self.user)
        self.assertEqual(run.source, 'manual')
        self.assertEqual(run.distance_m, 5000)
    
    def test_run_creation_strava(self):
        """Test de création d'une course depuis Strava"""
        run = Run.objects.create(
            user=self.user,
            source='strava',
            strava_id=123456789,
            name="Run Strava",
            distance_m=10000,
            moving_time_s=3000,
            elapsed_time_s=3120,
            start_date=timezone.now(),
            elevation_gain_m=50.0
        )
        
        self.assertEqual(run.source, 'strava')
        self.assertEqual(run.strava_id, 123456789)
    
    def test_run_creation_garmin(self):
        """Test de création d'une course depuis Garmin"""
        run = Run.objects.create(
            user=self.user,
            source='garmin',
            garmin_id=987654321,
            name="Run Garmin",
            distance_m=8000,
            moving_time_s=2400,
            elapsed_time_s=2500,
            start_date=timezone.now()
        )
        
        self.assertEqual(run.source, 'garmin')
        self.assertEqual(run.garmin_id, 987654321)
    
    def test_distance_km_property(self):
        """Test de la propriété distance_km"""
        run = Run.objects.create(
            user=self.user,
            source='manual',
            name="Test",
            distance_m=5000,
            moving_time_s=1500,
            elapsed_time_s=1500,
            start_date=timezone.now()
        )
        
        self.assertEqual(run.distance_km, 5.0)
    
    def test_moving_time_hms_property_minutes(self):
        """Test de la propriété moving_time_hms (format minutes)"""
        run = Run.objects.create(
            user=self.user,
            source='manual',
            name="Test",
            distance_m=5000,
            moving_time_s=2533,  # 42m13s
            elapsed_time_s=2533,
            start_date=timezone.now()
        )
        
        self.assertEqual(run.moving_time_hms, "42m13s")
    
    def test_moving_time_hms_property_hours(self):
        """Test de la propriété moving_time_hms (format heures)"""
        run = Run.objects.create(
            user=self.user,
            source='manual',
            name="Test",
            distance_m=20000,
            moving_time_s=3800,  # 1h03m20s
            elapsed_time_s=3800,
            start_date=timezone.now()
        )
        
        self.assertEqual(run.moving_time_hms, "1h03m20s")
    
    def test_pace_min_per_km_property(self):
        """Test de la propriété pace_min_per_km"""
        run = Run.objects.create(
            user=self.user,
            source='manual',
            name="Test",
            distance_m=5000,
            moving_time_s=1500,  # 25 minutes
            elapsed_time_s=1500,
            start_date=timezone.now()
        )
        
        # 1500 secondes / 5 km = 300 secondes/km = 5:00 /km
        self.assertEqual(run.pace_min_per_km, "5:00 /km")
    
    def test_estimate_calories_with_profile_weight(self):
        """Test de l'estimation des calories avec le poids du profil"""
        profile = self.user.profile
        profile.weight_kg = Decimal('75.00')
        profile.save()
        
        run = Run(
            user=self.user,
            source='manual',
            name="Test",
            distance_m=10000,  # 10 km
            moving_time_s=3000,
            elapsed_time_s=3000,
            start_date=timezone.now()
        )
        
        # 75 kg × 10 km × 1.036 = 777 kcal
        calories = run.estimate_calories()
        self.assertAlmostEqual(calories, 777.0, places=0)
    
    def test_estimate_calories_default_weight(self):
        """Test de l'estimation des calories avec poids par défaut"""
        # Supprimer le poids du profil
        profile = self.user.profile
        profile.weight_kg = None
        profile.save()
        
        run = Run(
            user=self.user,
            source='manual',
            name="Test",
            distance_m=5000,  # 5 km
            moving_time_s=1500,
            elapsed_time_s=1500,
            start_date=timezone.now()
        )
        
        # 70 kg (default) × 5 km × 1.036 = 362.6 kcal
        calories = run.estimate_calories()
        self.assertAlmostEqual(calories, 362.6, places=0)
    
    def test_auto_calculate_speed_and_pace_on_save(self):
        """Test du calcul automatique de la vitesse et de l'allure à la sauvegarde"""
        run = Run.objects.create(
            user=self.user,
            source='manual',
            name="Test",
            distance_m=10000,  # 10 km
            moving_time_s=3000,  # 50 minutes
            elapsed_time_s=3000,
            start_date=timezone.now()
        )
        
        # Vitesse moyenne: 10000m / 3000s = 3.33 m/s
        self.assertAlmostEqual(run.average_speed, 3.33, places=2)
        
        # Allure moyenne: 3000s / 10km = 300 s/km
        self.assertAlmostEqual(run.average_pace_s_per_km, 300.0, places=1)
    
    def test_auto_calculate_calories_on_save(self):
        """Test du calcul automatique des calories à la sauvegarde"""
        run = Run.objects.create(
            user=self.user,
            source='manual',
            name="Test",
            distance_m=5000,
            moving_time_s=1500,
            elapsed_time_s=1500,
            start_date=timezone.now()
        )
        
        # Should have automatically calculated calories
        self.assertIsNotNone(run.calories_burned)
        self.assertGreater(run.calories_burned, 0)
    
    def test_run_ordering(self):
        """Test de l'ordre par défaut (start_date DESC)"""
        date1 = timezone.now()
        date2 = date1 + timedelta(days=1)
        date3 = date2 + timedelta(days=1)
        
        run1 = Run.objects.create(
            user=self.user, source='manual', name="Run 1",
            distance_m=5000, moving_time_s=1500, elapsed_time_s=1500,
            start_date=date1
        )
        run2 = Run.objects.create(
            user=self.user, source='manual', name="Run 2",
            distance_m=5000, moving_time_s=1500, elapsed_time_s=1500,
            start_date=date2
        )
        run3 = Run.objects.create(
            user=self.user, source='manual', name="Run 3",
            distance_m=5000, moving_time_s=1500, elapsed_time_s=1500,
            start_date=date3
        )
        
        runs = list(Run.objects.all())
        self.assertEqual(runs[0], run3)  # Most recent first
        self.assertEqual(runs[1], run2)
        self.assertEqual(runs[2], run1)
    
    def test_run_str_representation(self):
        """Test de la représentation string"""
        run = Run.objects.create(
            user=self.user,
            source='manual',
            name="Course matinale",
            distance_m=5000,
            moving_time_s=1500,
            elapsed_time_s=1500,
            start_date=timezone.now()
        )
        
        self.assertEqual(str(run), "Course matinale (5.0 km)")


class ManualRunFormTests(TestCase):
    """Tests pour le formulaire ManualRunForm"""
    
    def test_parse_time_seconds_only(self):
        """Test du parsing de temps (secondes uniquement)"""
        form = ManualRunForm()
        self.assertEqual(form.parse_time("30"), 30)
        self.assertEqual(form.parse_time("120"), 120)
    
    def test_parse_time_mm_ss(self):
        """Test du parsing de temps MM:SS"""
        form = ManualRunForm()
        self.assertEqual(form.parse_time("5:30"), 330)  # 5 min 30 sec
        self.assertEqual(form.parse_time("45:00"), 2700)  # 45 min
    
    def test_parse_time_hh_mm_ss(self):
        """Test du parsing de temps HH:MM:SS"""
        form = ManualRunForm()
        self.assertEqual(form.parse_time("1:30:00"), 5400)  # 1h 30min
        self.assertEqual(form.parse_time("2:15:45"), 8145)  # 2h 15min 45s
    
    def test_parse_time_text_format_hours(self):
        """Test du parsing de temps au format texte (heures)"""
        form = ManualRunForm()
        self.assertEqual(form.parse_time("1h30m"), 5400)  # 1h 30min
        self.assertEqual(form.parse_time("2h"), 7200)  # 2h
    
    def test_parse_time_text_format_minutes(self):
        """Test du parsing de temps au format texte (minutes)"""
        form = ManualRunForm()
        self.assertEqual(form.parse_time("45m"), 2700)  # 45 min
        self.assertEqual(form.parse_time("30m30s"), 1830)  # 30 min 30s
    
    def test_parse_time_text_format_seconds(self):
        """Test du parsing de temps au format texte (secondes)"""
        form = ManualRunForm()
        self.assertEqual(form.parse_time("45s"), 45)
        self.assertEqual(form.parse_time("120s"), 120)
    
    def test_parse_time_complex_format(self):
        """Test du parsing de temps au format complexe"""
        form = ManualRunForm()
        self.assertEqual(form.parse_time("1h30m45s"), 5445)  # 1h 30min 45s
    
    def test_form_valid_data(self):
        """Test de validation du formulaire avec données valides"""
        form_data = {
            'name': 'Course matinale',
            'start_date': '2025-11-20T08:30',
            'distance_m': 5000,
            'moving_time': '25:00',
            'elapsed_time': '26:30',
            'elevation_gain_m': 50,
            'calories_burned': 350
        }
        form = ManualRunForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_form_saves_correctly(self):
        """Test que le formulaire sauvegarde correctement"""
        user = User.objects.create_user(username='testuser', password='password123')
        
        form_data = {
            'name': 'Course test',
            'start_date': '2025-11-20T08:30',
            'distance_m': 5000,
            'moving_time': '25:00',
            'elapsed_time': '26:30',
            'elevation_gain_m': 50,
            'calories_burned': None
        }
        form = ManualRunForm(data=form_data)
        
        if form.is_valid():
            run = form.save(commit=False)
            run.user = user
            run.source = 'manual'
            run.save()
            
            self.assertEqual(run.moving_time_s, 1500)  # 25 minutes
            self.assertEqual(run.elapsed_time_s, 1590)  # 26.5 minutes
            self.assertEqual(run.elevation_gain_m, 50)


class RunningViewTests(TestCase):
    """Tests pour les vues de l'app running"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.profile, _ = Profile.objects.get_or_create(
            user=self.user,
            defaults={'running_data_source': 'manual', 'weight_kg': Decimal('70.00')}
        )
        self.client.login(username='testuser', password='password123')
    
    def test_my_runs_view_requires_login(self):
        """Test que la vue my_runs nécessite une authentification"""
        self.client.logout()
        url = reverse('running:my_runs')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)
    
    def test_my_runs_view(self):
        """Test de la vue my_runs"""
        Run.objects.create(
            user=self.user,
            source='manual',
            name="Test Run",
            distance_m=5000,
            moving_time_s=1500,
            elapsed_time_s=1500,
            start_date=timezone.now()
        )
        
        url = reverse('running:my_runs')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('runs', response.context)
        self.assertEqual(response.context['runs'].count(), 1)
        self.assertIn('running_data_source', response.context)
    
    def test_manual_run_add_view_requires_manual_source(self):
        """Test que l'ajout manuel nécessite le mode manuel dans le profil"""
        self.profile.running_data_source = 'strava'
        self.profile.save()
        
        url = reverse('running:manual_run_add')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 302)
        messages = list(response.wsgi_request._messages)
        self.assertTrue(any('manuel' in str(m).lower() for m in messages))
    
    def test_manual_run_add_view_get(self):
        """Test de l'accès GET au formulaire d'ajout manuel"""
        url = reverse('running:manual_run_add')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
    
    def test_manual_run_add_view_post_success(self):
        """Test de l'ajout d'une course manuelle via POST"""
        url = reverse('running:manual_run_add')
        
        form_data = {
            'name': 'Course matinale',
            'start_date': '2025-11-20T08:30',
            'distance_m': 5000,
            'moving_time': '25:00',
            'elapsed_time': '26:30',
            'elevation_gain_m': 50,
            'calories_burned': 350
        }
        
        response = self.client.post(url, data=form_data)
        
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Run.objects.filter(user=self.user, name='Course matinale').exists())
        
        run = Run.objects.get(user=self.user, name='Course matinale')
        self.assertEqual(run.source, 'manual')
        self.assertEqual(run.distance_m, 5000)
    
    def test_manual_run_add_view_post_invalid(self):
        """Test de l'ajout d'une course avec données invalides"""
        url = reverse('running:manual_run_add')
        
        form_data = {
            'name': '',  # Nom vide (invalide)
            'distance_m': -100,  # Negative distance (invalid)
            'moving_time': 'invalid',
            'elapsed_time': 'invalid'
        }
        
        response = self.client.post(url, data=form_data)
        
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Run.objects.filter(user=self.user).exists())
    
    def test_runs_filtered_by_user(self):
        """Test que chaque utilisateur ne voit que ses propres courses"""
        other_user = User.objects.create_user(username='otheruser', password='password123')
        
        Run.objects.create(
            user=self.user,
            source='manual',
            name="My Run",
            distance_m=5000,
            moving_time_s=1500,
            elapsed_time_s=1500,
            start_date=timezone.now()
        )
        
        Run.objects.create(
            user=other_user,
            source='manual',
            name="Other Run",
            distance_m=10000,
            moving_time_s=3000,
            elapsed_time_s=3000,
            start_date=timezone.now()
        )
        
        url = reverse('running:my_runs')
        response = self.client.get(url)
        
        runs = response.context['runs']
        self.assertEqual(runs.count(), 1)
        self.assertEqual(runs.first().name, "My Run")
