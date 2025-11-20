"""
Commande de management pour mettre à jour le fixture exercices.json avec le champ is_time_based
"""
from django.core.management.base import BaseCommand
import json
import os


class Command(BaseCommand):
    help = 'Mettre à jour le fixture exercices.json avec le champ is_time_based'

    def handle(self, *args, **options):
        # Liste des exercices basés sur le temps
        time_based_exercises = [
            "Plank", "Side Plank", "Wall Sit", "Dead Hang", 
            "L-Sit", "Hollow Hold", "Superman Hold"
        ]
        
        # Chemin du fichier fixture
        fixture_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
            'fixtures',
            'exercices.json'
        )
        
        # Lire le fixture
        with open(fixture_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Mettre à jour les exercices
        updated_count = 0
        for item in data:
            if item['model'] == 'workouts.exercise':
                exercise_name = item['fields']['name']
                
                # Vérifier si c'est un exercice basé sur le temps
                is_time_based = any(
                    time_name.lower() in exercise_name.lower() 
                    for time_name in time_based_exercises
                )
                
                # Ajouter le champ is_time_based
                item['fields']['is_time_based'] = is_time_based
                
                if is_time_based:
                    updated_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f"✓ {exercise_name} marqué comme basé sur le temps")
                    )
        
        # Sauvegarder le fixture mis à jour
        with open(fixture_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Fixture mis à jour avec succès ! '
                f'{updated_count} exercices marqués comme basés sur le temps.'
            )
        )
