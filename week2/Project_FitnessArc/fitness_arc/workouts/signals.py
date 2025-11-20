from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import WorkoutTemplate, TemplateItem, Exercise


@receiver(post_save, sender=User)
def create_default_templates_for_new_user(sender, instance, created, **kwargs):
    """
    Signal qui crée automatiquement les templates publics par défaut
    (Push/Pull/Legs) pour chaque nouvel utilisateur.
    Ignore les superusers et staff (comptes admin).
    """
    if not created:
        # User already exists, do nothing
        return
    
    # Ignorer les superusers et staff
    if instance.is_superuser or instance.is_staff:
        return
    
    # Vérifier si l'utilisateur a déjà des templates
    if WorkoutTemplate.objects.filter(owner=instance).exists():
        return
    
    templates_data = [
        {
            'name': '💪 Push (Pecs/Épaules/Triceps)',
            'exercises': [
                {'exercise_id': 1, 'order': 1, 'sets': 4, 'reps': 8, 'rest': 120, 'notes': 'Développé couché'},
                {'exercise_id': 4, 'order': 2, 'sets': 3, 'reps': 10, 'rest': 90, 'notes': 'Développé épaules'},
                {'exercise_id': 7, 'order': 3, 'sets': 3, 'reps': 12, 'rest': 60, 'notes': 'Extensions triceps'},
            ]
        },
        {
            'name': '🔙 Pull (Dos/Biceps)',
            'exercises': [
                {'exercise_id': 60, 'order': 1, 'sets': 4, 'reps': 8, 'rest': 120, 'notes': 'Tractions'},
                {'exercise_id': 54, 'order': 2, 'sets': 4, 'reps': 10, 'rest': 90, 'notes': 'Rowing barre'},
                {'exercise_id': 80, 'order': 3, 'sets': 3, 'reps': 12, 'rest': 60, 'notes': 'Curl biceps'},
            ]
        },
        {
            'name': '🦵 Legs (Jambes/Abdos)',
            'exercises': [
                {'exercise_id': 150, 'order': 1, 'sets': 4, 'reps': 8, 'rest': 180, 'notes': 'Squat'},
                {'exercise_id': 151, 'order': 2, 'sets': 3, 'reps': 12, 'rest': 90, 'notes': 'Presse à cuisses'},
                {'exercise_id': 100, 'order': 3, 'sets': 3, 'reps': 15, 'rest': 45, 'notes': 'Crunchs'},
            ]
        },
    ]
    
    for template_data in templates_data:
        # Créer le template
        template = WorkoutTemplate.objects.create(
            owner=instance,
            name=template_data['name'],
            is_public=True
        )
        
        # Ajouter les exercices
        for exercise_data in template_data['exercises']:
            try:
                exercise = Exercise.objects.get(id=exercise_data['exercise_id'])
                TemplateItem.objects.create(
                    template=template,
                    exercise=exercise,
                    order=exercise_data['order'],
                    sets=exercise_data['sets'],
                    reps=exercise_data['reps'],
                    rest_seconds=exercise_data['rest'],
                    notes=exercise_data['notes']
                )
            except Exercise.DoesNotExist:
                # Si l'exercice n'existe pas, on continue
                pass
