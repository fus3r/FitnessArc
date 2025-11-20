from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from workouts.models import WorkoutTemplate, TemplateItem, Exercise


class Command(BaseCommand):
    help = 'Crée les templates publics par défaut (Push/Pull/Legs) pour tous les utilisateurs qui n\'en ont pas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user',
            type=str,
            help='Créer uniquement pour cet utilisateur (username)',
        )

    def handle(self, *args, **options):
        username = options.get('user')
        
        if username:
            try:
                users = [User.objects.get(username=username)]
                self.stdout.write(f"Création des templates pour l'utilisateur: {username}")
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Utilisateur "{username}" introuvable'))
                return
        else:
            users = User.objects.all()
            self.stdout.write(f"Création des templates pour {users.count()} utilisateur(s)")

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

        for user in users:
            # Vérifier si l'utilisateur a déjà ces templates
            existing = WorkoutTemplate.objects.filter(
                owner=user,
                name__in=[t['name'] for t in templates_data]
            ).count()
            
            if existing > 0:
                self.stdout.write(
                    self.style.WARNING(f"  → {user.username} a déjà des templates par défaut, skip")
                )
                continue

            created_count = 0
            for template_data in templates_data:
                # Créer le template
                template = WorkoutTemplate.objects.create(
                    owner=user,
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
                        self.stdout.write(
                            self.style.WARNING(
                                f"    Exercice {exercise_data['exercise_id']} introuvable, skip"
                            )
                        )
                
                created_count += 1
            
            self.stdout.write(
                self.style.SUCCESS(f"  ✓ {created_count} template(s) créé(s) pour {user.username}")
            )

        self.stdout.write(self.style.SUCCESS('\n✅ Terminé !'))
