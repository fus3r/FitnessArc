# nutrition/tests.py

from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from decimal import Decimal
from django.utils import timezone
from .models import Food, FoodLog

class NutritionModelTests(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        # Créer un utilisateur de test (dépend du modèle Profile de l'app accounts)
        # On suppose que l'app accounts est mergée et crée automatiquement le Profile
        cls.user = User.objects.create_user(username='testuser', password='password123')
        cls.date_today = timezone.now().date()
        
        # Créer les aliments de base
        # Food 1: Riz blanc (130 kcal, 2.7g P, 28g C, 0.3g F)
        cls.rice = Food.objects.create(
            name="Riz Blanc", slug="riz-blanc",
            kcal_per_100g=Decimal('130.00'), protein_per_100g=Decimal('2.70'), 
            carbs_per_100g=Decimal('28.00'), fat_per_100g=Decimal('0.30')
        )
        # Food 2: Poulet (165 kcal, 31g P, 0g C, 3.6g F)
        cls.chicken = Food.objects.create(
            name="Poulet", slug="poulet",
            kcal_per_100g=Decimal('165.00'), protein_per_100g=Decimal('31.00'), 
            carbs_per_100g=Decimal('0.00'), fat_per_100g=Decimal('3.60')
        )

    def test_food_log_creation_and_calories_calculation(self):
        """
        Teste si la création d'un FoodLog est correcte et si les propriétés calculées (kcal, macros) fonctionnent.
        (Couvre un des tests unitaires clés Must-have pour la nutrition )
        """
        # Log 1: 200g de Riz
        grams_rice = Decimal('200.00')
        log1 = FoodLog.objects.create(
            owner=self.user, date=self.date_today, food=self.rice, grams=grams_rice, meal_type='lunch'
        )

        # Vérification des totaux calculés pour 200g de Riz :
        # Kcal: (130 * 200) / 100 = 260
        # Prot: (2.7 * 200) / 100 = 5.4
        self.assertEqual(log1.kcal, Decimal('260.00'))
        self.assertEqual(log1.protein, Decimal('5.40'))
        self.assertEqual(log1.carbs, Decimal('56.00')) # (28 * 200) / 100
        self.assertEqual(log1.fat, Decimal('0.60'))    # (0.3 * 200) / 100
        
    def test_daily_totals_aggregation(self):
        """
        Teste si l'agrégation des totaux journaliers (dans la vue) fonctionne sur plusieurs logs.
        (Critère d'acceptation: Totaux journaliers se mettent à jour immédiatement [cite: 55, 127])
        """
        # Log 1: 150g de Poulet (Midi)
        grams_chicken = Decimal('150.00')
        FoodLog.objects.create(
            owner=self.user, date=self.date_today, food=self.chicken, grams=grams_chicken, meal_type='lunch'
        )
        
        # Log 2: 100g de Riz (Midi)
        grams_rice = Decimal('100.00')
        FoodLog.objects.create(
            owner=self.user, date=self.date_today, food=self.rice, grams=grams_rice, meal_type='lunch'
        )

        # Récupération de tous les logs du jour pour l'utilisateur
        logs = FoodLog.objects.filter(owner=self.user, date=self.date_today)
        
        # Calcul des totaux basés sur le code de la vue (somme des propriétés)
        total_kcal = sum(log.kcal for log in logs)
        total_protein = sum(log.protein for log in logs)
        
        # Calcul attendu :
        # Poulet (150g): Kcal=247.5, Prot=46.5
        # Riz (100g): Kcal=130.0, Prot=2.7
        # Total Kcal attendu: 247.5 + 130.0 = 377.5
        # Total Prot attendu: 46.5 + 2.7 = 49.2
        
        self.assertEqual(round(total_kcal, 2), Decimal('377.50'))
        self.assertEqual(round(total_protein, 2), Decimal('49.20'))


    def test_grams_validation_rule(self):
        """
        Teste si la validation 'grams > 0' (Règle #10) est respectée.
        """
        # Le champ 'grams' dans le modèle doit être positif (> 0) [cite: 57, 129]
        from django.core.exceptions import ValidationError
        
        # Tentative de créer un log avec 0 gramme
        with self.assertRaises(ValidationError):
            log = FoodLog(
                owner=self.user, date=self.date_today, food=self.rice, grams=Decimal('0.00'), meal_type='lunch'
            )
            # Une validation complète doit être forcée
            log.full_clean() 

class NutritionViewTests(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', password='password123')
        cls.food = Food.objects.create(
            name="Test Food", slug="test-food",
            kcal_per_100g=Decimal('100.00'), protein_per_100g=Decimal('10.00'), 
            carbs_per_100g=Decimal('10.00'), fat_per_100g=Decimal('10.00')
        )
        cls.url = reverse('nutrition_today')
        
    def setUp(self):
        # Se connecter avant chaque test de vue (nécessaire à cause de @login_required)
        self.client.login(username='testuser', password='password123')

    def test_nutrition_today_view_success(self):
        """Teste si la vue est accessible et rend le template correct."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'nutrition/nutrition_today.html')
        
    def test_nutrition_today_post_data_addition(self):
        """Teste si l'ajout de données (POST) via le formulaire fonctionne."""
        initial_log_count = FoodLog.objects.count()
        
        response = self.client.post(self.url, {
            'food': self.food.pk,
            'grams': 100,
            'meal_type': 'dinner'
        }, follow=True) # follow=True suit la redirection
        
        # Vérifie si le log a été créé et si la redirection a eu lieu (status 200)
        self.assertEqual(FoodLog.objects.count(), initial_log_count + 1)
        self.assertRedirects(response, self.url)
        
        # Vérifie si la donnée s'affiche dans la page après redirection
        self.assertContains(response, "Test Food")
        
        
    def test_nutrition_today_post_invalid_data(self):
        """Teste si la soumission de données invalides est rejetée."""
        initial_log_count = FoodLog.objects.count()
        
        response = self.client.post(self.url, {
            'food': self.food.pk,
            'grams': 'invalid_text', # Invalide
            'meal_type': 'dinner'
        })
        
        # Vérifie que le statut est 200 (re-rendu de la page avec erreurs)
        self.assertEqual(response.status_code, 200)
        # Vérifie qu'aucun log n'a été créé
        self.assertEqual(FoodLog.objects.count(), initial_log_count)
        # Vérifie que la page contient des messages d'erreur du formulaire
        self.assertFormError(response.context['form'], 'grams', 'Entrez un nombre.')
