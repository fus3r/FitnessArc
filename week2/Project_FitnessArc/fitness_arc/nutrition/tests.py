# nutrition/tests.py

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from decimal import Decimal
from django.utils import timezone
from .models import Food, FoodLog, Recipe, RecipeIngredient
from .views import calculate_daily_goal, normalize_string
from accounts.models import Profile

class FoodModelTests(TestCase):
    """Tests pour le modèle Food"""
    
    def setUp(self):
        self.food_grams = Food.objects.create(
            name="Riz Blanc",
            slug="riz-blanc",
            kcal_per_100g=Decimal('130.00'),
            protein_per_100g=Decimal('2.70'),
            carbs_per_100g=Decimal('28.00'),
            fat_per_100g=Decimal('0.30'),
            unit_type='g'
        )
        
        self.food_ml = Food.objects.create(
            name="Lait",
            slug="lait",
            kcal_per_100g=Decimal('64.00'),
            protein_per_100g=Decimal('3.40'),
            carbs_per_100g=Decimal('5.00'),
            fat_per_100g=Decimal('3.60'),
            unit_type='ml'
        )
        
        self.food_unit = Food.objects.create(
            name="Œuf",
            slug="oeuf",
            kcal_per_100g=Decimal('155.00'),
            protein_per_100g=Decimal('13.00'),
            carbs_per_100g=Decimal('1.10'),
            fat_per_100g=Decimal('11.00'),
            unit_type='unit'
        )
    
    def test_food_creation(self):
        """Test de création d'un aliment"""
        self.assertEqual(self.food_grams.name, "Riz Blanc")
        self.assertEqual(self.food_grams.unit_type, 'g')
        self.assertTrue(self.food_grams.is_public)
    
    def test_get_unit_label(self):
        """Test du label d'unité"""
        self.assertEqual(self.food_grams.get_unit_label(), 'Grammes (g)')
        self.assertEqual(self.food_ml.get_unit_label(), 'Millilitres (ml)')
        self.assertEqual(self.food_unit.get_unit_label(), 'Unité(s)')
    
    def test_food_str_representation(self):
        """Test de la représentation string"""
        self.assertEqual(str(self.food_grams), "Riz Blanc")


class FoodLogModelTests(TestCase):
    """Tests pour le modèle FoodLog"""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.date_today = timezone.now().date()
        
        self.rice = Food.objects.create(
            name="Riz Blanc", slug="riz-blanc",
            kcal_per_100g=Decimal('130.00'), protein_per_100g=Decimal('2.70'), 
            carbs_per_100g=Decimal('28.00'), fat_per_100g=Decimal('0.30')
        )
        
        self.chicken = Food.objects.create(
            name="Poulet", slug="poulet",
            kcal_per_100g=Decimal('165.00'), protein_per_100g=Decimal('31.00'), 
            carbs_per_100g=Decimal('0.00'), fat_per_100g=Decimal('3.60')
        )
    
    def test_food_log_creation(self):
        """Test de création d'un log alimentaire"""
        log = FoodLog.objects.create(
            owner=self.user,
            date=self.date_today,
            food=self.rice,
            quantity=Decimal('200.00'),
            meal_type='lunch'
        )
        
        self.assertEqual(log.owner, self.user)
        self.assertEqual(log.food, self.rice)
        self.assertEqual(log.quantity, Decimal('200.00'))
    
    def test_kcal_calculation(self):
        """Test du calcul des calories"""
        log = FoodLog.objects.create(
            owner=self.user,
            date=self.date_today,
            food=self.rice,
            quantity=Decimal('200.00'),
            meal_type='lunch'
        )
        
        expected_kcal = (Decimal('130.00') * Decimal('200.00')) / 100
        self.assertEqual(log.kcal, expected_kcal)
    
    def test_macros_calculation(self):
        """Test du calcul des macros"""
        log = FoodLog.objects.create(
            owner=self.user,
            date=self.date_today,
            food=self.chicken,
            quantity=Decimal('150.00'),
            meal_type='dinner'
        )
        
        expected_protein = (Decimal('31.00') * Decimal('150.00')) / 100
        expected_carbs = (Decimal('0.00') * Decimal('150.00')) / 100
        expected_fat = (Decimal('3.60') * Decimal('150.00')) / 100
        
        self.assertEqual(log.protein, expected_protein)
        self.assertEqual(log.carbs, expected_carbs)
        self.assertEqual(log.fat, expected_fat)
    
    def test_daily_totals_aggregation(self):
        """Test de l'agrégation des totaux journaliers"""
        FoodLog.objects.create(
            owner=self.user, date=self.date_today,
            food=self.chicken, quantity=Decimal('150.00'),
            meal_type='lunch'
        )
        
        FoodLog.objects.create(
            owner=self.user, date=self.date_today,
            food=self.rice, quantity=Decimal('100.00'),
            meal_type='lunch'
        )
        
        logs = FoodLog.objects.filter(owner=self.user, date=self.date_today)
        total_kcal = sum(log.kcal for log in logs)
        total_protein = sum(log.protein for log in logs)
        
        self.assertEqual(round(total_kcal, 2), Decimal('377.50'))
        self.assertEqual(round(total_protein, 2), Decimal('49.20'))
    
    def test_food_log_str_representation(self):
        """Test de la représentation string"""
        log = FoodLog.objects.create(
            owner=self.user,
            date=self.date_today,
            food=self.rice,
            quantity=Decimal('100.00'),
            meal_type='breakfast'
        )
        
        expected = f"Riz Blanc - 100.00Grammes (g) le {self.date_today}"
        self.assertEqual(str(log), expected)


class RecipeModelTests(TestCase):
    """Tests pour le modèle Recipe"""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        
        self.egg = Food.objects.create(
            name="Œuf", slug="oeuf",
            kcal_per_100g=Decimal('155.00'),
            protein_per_100g=Decimal('13.00'),
            carbs_per_100g=Decimal('1.10'),
            fat_per_100g=Decimal('11.00')
        )
        
        self.cheese = Food.objects.create(
            name="Fromage", slug="fromage",
            kcal_per_100g=Decimal('366.00'),
            protein_per_100g=Decimal('29.00'),
            carbs_per_100g=Decimal('0.10'),
            fat_per_100g=Decimal('28.00')
        )
        
        self.recipe = Recipe.objects.create(
            name="Omelette au fromage",
            slug="omelette-fromage",
            description="Une délicieuse omelette",
            instructions="Battre les œufs, ajouter le fromage, cuire",
            prep_time_minutes=5,
            cook_time_minutes=5,
            servings=2,
            difficulty='easy',
            meal_type='breakfast',
            is_public=True
        )
        
        RecipeIngredient.objects.create(
            recipe=self.recipe,
            food=self.egg,
            quantity=Decimal('150.00'),  # 3 œufs
            notes="Œufs entiers"
        )
        
        RecipeIngredient.objects.create(
            recipe=self.recipe,
            food=self.cheese,
            quantity=Decimal('30.00'),
            notes="Râpé"
        )
    
    def test_recipe_creation(self):
        """Test de création d'une recette"""
        self.assertEqual(self.recipe.name, "Omelette au fromage")
        self.assertEqual(self.recipe.servings, 2)
        self.assertTrue(self.recipe.is_public)
    
    def test_total_time_calculation(self):
        """Test du calcul du temps total"""
        self.assertEqual(self.recipe.total_time_minutes, 10)
    
    def test_recipe_nutritional_values(self):
        """Test des valeurs nutritionnelles totales"""
        # Œufs: (155 * 150) / 100 = 232.5 kcal
        # Fromage: (366 * 30) / 100 = 109.8 kcal
        # Total: 342.3 kcal
        
        expected_kcal = Decimal('342.30')
        self.assertEqual(self.recipe.total_kcal, expected_kcal)
        
        # Protéines: (13 * 1.5) + (29 * 0.3) = 28.2g
        expected_protein = Decimal('28.20')
        self.assertEqual(self.recipe.total_protein, expected_protein)
    
    def test_per_serving_calculation(self):
        """Test du calcul par portion"""
        # 342.3 kcal / 2 portions = 171.15 kcal
        expected_kcal_per_serving = Decimal('171.15')
        self.assertEqual(self.recipe.kcal_per_serving, expected_kcal_per_serving)
    
    def test_recipe_str_representation(self):
        """Test de la représentation string"""
        self.assertEqual(str(self.recipe), "Omelette au fromage")


class NutritionTodayViewTests(TestCase):
    """Tests pour la vue nutrition_today"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.client.login(username='testuser', password='password123')
        
        self.food = Food.objects.create(
            name="Test Food", slug="test-food",
            kcal_per_100g=Decimal('100.00'),
            protein_per_100g=Decimal('10.00'),
            carbs_per_100g=Decimal('10.00'),
            fat_per_100g=Decimal('10.00')
        )
        
        self.url = reverse('nutrition_today')
    
    def test_view_requires_login(self):
        """Test que la vue nécessite une authentification"""
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)
    
    def test_view_get_success(self):
        """Test d'accès GET à la vue"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'nutrition/nutrition_today.html')
        self.assertIn('form', response.context)
        self.assertIn('logs', response.context)
        self.assertIn('totals', response.context)
    
    def test_add_food_log_success(self):
        """Test d'ajout d'un log alimentaire"""
        initial_count = FoodLog.objects.count()
        
        response = self.client.post(self.url, {
            'food': self.food.pk,
            'quantity': 100,
            'meal_type': 'lunch'
        }, follow=True)
        
        self.assertEqual(FoodLog.objects.count(), initial_count + 1)
        self.assertRedirects(response, self.url)
        self.assertContains(response, "Aliment ajouté avec succès")
    
    def test_add_food_log_missing_data(self):
        """Test d'ajout avec données manquantes"""
        initial_count = FoodLog.objects.count()
        
        response = self.client.post(self.url, {
            'quantity': 100,  # Pas de food
            'meal_type': 'lunch'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(FoodLog.objects.count(), initial_count)
    
    def test_totals_calculation(self):
        """Test du calcul des totaux"""
        FoodLog.objects.create(
            owner=self.user,
            date=timezone.now().date(),
            food=self.food,
            quantity=Decimal('100.00'),
            meal_type='breakfast'
        )
        
        FoodLog.objects.create(
            owner=self.user,
            date=timezone.now().date(),
            food=self.food,
            quantity=Decimal('150.00'),
            meal_type='lunch'
        )
        
        response = self.client.get(self.url)
        totals = response.context['totals']
        
        # 100 kcal/100g * (100g + 150g) = 250 kcal
        self.assertEqual(totals['kcal'], 250.0)
        self.assertEqual(totals['protein'], 25.0)


class DeleteFoodLogViewTests(TestCase):
    """Tests pour la vue delete_food_log"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.other_user = User.objects.create_user(username='otheruser', password='password123')
        self.client.login(username='testuser', password='password123')
        
        self.food = Food.objects.create(
            name="Test Food", slug="test-food",
            kcal_per_100g=Decimal('100.00'),
            protein_per_100g=Decimal('10.00'),
            carbs_per_100g=Decimal('10.00'),
            fat_per_100g=Decimal('10.00')
        )
        
        self.log = FoodLog.objects.create(
            owner=self.user,
            date=timezone.now().date(),
            food=self.food,
            quantity=Decimal('100.00'),
            meal_type='lunch'
        )
    
    def test_delete_own_log_success(self):
        """Test de suppression de son propre log"""
        url = reverse('delete_food_log', args=[self.log.pk])
        initial_count = FoodLog.objects.count()
        
        response = self.client.post(url, follow=True)
        
        self.assertEqual(FoodLog.objects.count(), initial_count - 1)
        self.assertRedirects(response, reverse('nutrition_today'))
        self.assertContains(response, "supprimée")
    
    def test_cannot_delete_others_log(self):
        """Test qu'on ne peut pas supprimer le log d'un autre utilisateur"""
        other_log = FoodLog.objects.create(
            owner=self.other_user,
            date=timezone.now().date(),
            food=self.food,
            quantity=Decimal('100.00'),
            meal_type='lunch'
        )
        
        url = reverse('delete_food_log', args=[other_log.pk])
        response = self.client.post(url)
        
        # Devrait retourner 404 car le log n'appartient pas à l'utilisateur
        self.assertEqual(response.status_code, 404)


class RecipeViewTests(TestCase):
    """Tests pour les vues de recettes"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password123')
        Profile.objects.get_or_create(user=self.user, defaults={
            'weight_kg': Decimal('70.00'),
            'goal': 'maintain'
        })
        self.client.login(username='testuser', password='password123')
        
        self.food = Food.objects.create(
            name="Test Food", slug="test-food",
            kcal_per_100g=Decimal('100.00'),
            protein_per_100g=Decimal('10.00'),
            carbs_per_100g=Decimal('10.00'),
            fat_per_100g=Decimal('10.00')
        )
        
        self.recipe = Recipe.objects.create(
            name="Test Recipe",
            slug="test-recipe",
            description="Test description",
            instructions="Test instructions",
            prep_time_minutes=10,
            cook_time_minutes=20,
            servings=4,
            difficulty='easy',
            meal_type='lunch',
            is_public=True
        )
        
        RecipeIngredient.objects.create(
            recipe=self.recipe,
            food=self.food,
            quantity=Decimal('200.00')
        )
    
    def test_recipe_list_view(self):
        """Test de la liste des recettes"""
        url = reverse('recipe_list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'nutrition/recipe_list.html')
        self.assertIn('recipes', response.context)
        self.assertIn('daily_goal', response.context)
    
    def test_recipe_list_filter_by_meal_type(self):
        """Test du filtrage par type de repas"""
        Recipe.objects.create(
            name="Breakfast Recipe",
            slug="breakfast-recipe",
            description="Test",
            instructions="Test",
            prep_time_minutes=5,
            servings=1,
            difficulty='easy',
            meal_type='breakfast',
            is_public=True
        )
        
        url = reverse('recipe_list')
        response = self.client.get(url, {'meal_type': 'breakfast'})
        
        self.assertEqual(response.status_code, 200)
        recipes = response.context['recipes']
        for recipe in recipes:
            self.assertEqual(recipe.meal_type, 'breakfast')
    
    def test_recipe_detail_view(self):
        """Test de la vue détail d'une recette"""
        url = reverse('recipe_detail', args=[self.recipe.slug])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'nutrition/recipe_detail.html')
        self.assertEqual(response.context['recipe'], self.recipe)
        self.assertIn('ingredients', response.context)
        self.assertIn('nutrition_info', response.context)


class UtilityFunctionsTests(TestCase):
    """Tests pour les fonctions utilitaires"""
    
    def test_normalize_string(self):
        """Test de la normalisation de chaînes"""
        self.assertEqual(normalize_string("Café"), "cafe")
        self.assertEqual(normalize_string("Crème fraîche"), "creme fraiche")
        self.assertEqual(normalize_string("POULET"), "poulet")
    
    def test_calculate_daily_goal_bulk(self):
        """Test du calcul des objectifs pour prise de masse"""
        user = User.objects.create_user(username='testuser_bulk', password='password123')
        profile, _ = Profile.objects.get_or_create(
            user=user,
            defaults={'weight_kg': Decimal('80.00'), 'goal': 'bulk'}
        )
        profile.weight_kg = Decimal('80.00')
        profile.goal = 'bulk'
        profile.save()
        
        goals = calculate_daily_goal(profile)
        
        # 80kg * 35 = 2800 kcal
        self.assertEqual(goals['kcal'], 2800)
        # 80kg * 2.2 = 176g protein
        self.assertEqual(goals['protein'], 176)
    
    def test_calculate_daily_goal_cut(self):
        """Test du calcul des objectifs pour perte de poids"""
        user = User.objects.create_user(username='testuser_cut', password='password123')
        profile, _ = Profile.objects.get_or_create(
            user=user,
            defaults={'weight_kg': Decimal('80.00'), 'goal': 'cut'}
        )
        profile.weight_kg = Decimal('80.00')
        profile.goal = 'cut'
        profile.save()
        
        goals = calculate_daily_goal(profile)
        
        # 80kg * 25 = 2000 kcal
        self.assertEqual(goals['kcal'], 2000)
        # 80kg * 2.5 = 200g protein
        self.assertEqual(goals['protein'], 200)
    
    def test_calculate_daily_goal_maintain(self):
        """Test du calcul des objectifs pour maintien"""
        user = User.objects.create_user(username='testuser_maintain', password='password123')
        profile, _ = Profile.objects.get_or_create(
            user=user,
            defaults={'weight_kg': Decimal('70.00'), 'goal': 'maintain'}
        )
        profile.weight_kg = Decimal('70.00')
        profile.goal = 'maintain'
        profile.save()
        
        goals = calculate_daily_goal(profile)
        
        # 70kg * 30 = 2100 kcal
        self.assertEqual(goals['kcal'], 2100)
        # 70kg * 2 = 140g protein
        self.assertEqual(goals['protein'], 140)
    
    def test_calculate_daily_goal_no_weight(self):
        """Test du calcul avec poids non renseigné"""
        user = User.objects.create_user(username='testuser_noweight', password='password123')
        profile, _ = Profile.objects.get_or_create(
            user=user,
            defaults={'weight_kg': None, 'goal': 'maintain'}
        )
        profile.weight_kg = None
        profile.goal = 'maintain'
        profile.save()
        
        goals = calculate_daily_goal(profile)
        
        # Valeurs par défaut
        self.assertEqual(goals['kcal'], 2000)
        self.assertEqual(goals['protein'], 150)
