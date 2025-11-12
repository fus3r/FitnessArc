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
        cls.user = User.objects.create_user(username='testuser', password='password123')
        cls.date_today = timezone.now().date()
        
        cls.rice = Food.objects.create(
            name="Riz Blanc", slug="riz-blanc",
            kcal_per_100g=Decimal('130.00'), protein_per_100g=Decimal('2.70'), 
            carbs_per_100g=Decimal('28.00'), fat_per_100g=Decimal('0.30')
        )
        cls.chicken = Food.objects.create(
            name="Poulet", slug="poulet",
            kcal_per_100g=Decimal('165.00'), protein_per_100g=Decimal('31.00'), 
            carbs_per_100g=Decimal('0.00'), fat_per_100g=Decimal('3.60')
        )

    def test_food_log_creation_and_calories_calculation(self):
        quantity_rice = Decimal('200.00')
        log1 = FoodLog.objects.create(
            owner=self.user, date=self.date_today, food=self.rice, quantity=quantity_rice, meal_type='lunch'
        )

        self.assertEqual(log1.kcal, Decimal('260.00'))
        self.assertEqual(log1.protein, Decimal('5.40'))
        self.assertEqual(log1.carbs, Decimal('56.00'))
        self.assertEqual(log1.fat, Decimal('0.60'))
        
    def test_daily_totals_aggregation(self):
        quantity_chicken = Decimal('150.00')
        FoodLog.objects.create(
            owner=self.user, date=self.date_today, food=self.chicken, quantity=quantity_chicken, meal_type='lunch'
        )
        
        quantity_rice = Decimal('100.00')
        FoodLog.objects.create(
            owner=self.user, date=self.date_today, food=self.rice, quantity=quantity_rice, meal_type='lunch'
        )

        logs = FoodLog.objects.filter(owner=self.user, date=self.date_today)
        total_kcal = sum(log.kcal for log in logs)
        total_protein = sum(log.protein for log in logs)
        
        self.assertEqual(round(total_kcal, 2), Decimal('377.50'))
        self.assertEqual(round(total_protein, 2), Decimal('49.20'))

    def test_grams_validation_rule(self):
        from django.core.exceptions import ValidationError
        
        with self.assertRaises(ValidationError):
            log = FoodLog(
                owner=self.user, date=self.date_today, food=self.rice, quantity=Decimal('0.00'), meal_type='lunch'
            )
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
        self.client.login(username='testuser', password='password123')

    def test_nutrition_today_view_success(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'nutrition/nutrition_today.html')
        
    def test_nutrition_today_post_data_addition(self):
        initial_log_count = FoodLog.objects.count()
        
        response = self.client.post(self.url, {
            'food': self.food.pk,
            'quantity': 100,
            'meal_type': 'dinner'
        }, follow=True)
        
        self.assertEqual(FoodLog.objects.count(), initial_log_count + 1)
        self.assertRedirects(response, self.url)
        self.assertContains(response, "Test Food")
        
    def test_nutrition_today_post_invalid_data(self):
        initial_log_count = FoodLog.objects.count()
        
        response = self.client.post(self.url, {
            'food': self.food.pk,
            'quantity': 'invalid_text',
            'meal_type': 'dinner'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(FoodLog.objects.count(), initial_log_count)
        self.assertFormError(response.context['form'], 'quantity', 'Entrez un nombre.')
