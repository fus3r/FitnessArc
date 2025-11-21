#!/usr/bin/env python
"""
Script pour populer automatiquement les image_url des exercices
en utilisant les URLs GitHub Raw pour les images.
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitness_arc.settings')
django.setup()

from workouts.models import Exercise

# Base URL pour les images sur GitHub
GITHUB_RAW_BASE = "https://raw.githubusercontent.com/fus3r/FitnessArc/refs/heads/main/week2/Project_FitnessArc/fitness_arc/media/"

def populate_image_urls():
    """Populate image_url field for all exercises that have an image."""
    updated_count = 0
    skipped_count = 0
    
    exercises = Exercise.objects.all()
    total = exercises.count()
    
    print(f"🔍 Traitement de {total} exercices...")
    print("-" * 60)
    
    for exercise in exercises:
        if exercise.image:
            # Construire l'URL GitHub Raw
            image_path = exercise.image.name  # ex: "exercises/barbell_bench_press.webp"
            github_url = f"{GITHUB_RAW_BASE}{image_path}"
            
            # Mettre à jour seulement si image_url est vide
            if not exercise.image_url:
                exercise.image_url = github_url
                exercise.save(update_fields=['image_url'])
                print(f"✅ {exercise.name}: {github_url}")
                updated_count += 1
            else:
                print(f"⏭️  {exercise.name}: déjà configuré")
                skipped_count += 1
        else:
            print(f"⚠️  {exercise.name}: pas d'image")
            skipped_count += 1
    
    print("-" * 60)
    print(f"\n📊 Résumé:")
    print(f"   ✅ Mis à jour: {updated_count}")
    print(f"   ⏭️  Ignorés: {skipped_count}")
    print(f"   📝 Total: {total}")
    print(f"\n🎉 Terminé ! Les images devraient maintenant s'afficher sur Railway.")

if __name__ == "__main__":
    populate_image_urls()
