from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse


def feature_required(feature_name):
    """
    Décorateur pour vérifier qu'un utilisateur a activé une fonctionnalité spécifique.
    
    Usage:
        @feature_required('workouts')
        def my_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                # Si l'utilisateur n'est pas connecté, rediriger vers login
                return redirect('accounts:login')
            
            # Vérifier si l'utilisateur a un profil
            if not hasattr(request.user, 'profile'):
                messages.error(request, "Votre profil n'est pas configuré correctement.")
                return redirect('accounts:profile')
            
            # Mapper le nom de la fonctionnalité au champ du profil
            feature_field = f'feature_{feature_name}'
            
            # Vérifier si la fonctionnalité est activée
            if not getattr(request.user.profile, feature_field, False):
                feature_labels = {
                    'workouts': 'Exercices & Workouts',
                    'nutrition': 'Nutrition',
                    'running': 'Running',
                    'leaderboard': 'Classement',
                }
                feature_label = feature_labels.get(feature_name, feature_name)
                
                messages.warning(
                    request,
                    f"La fonctionnalité '{feature_label}' n'est pas activée sur votre profil. "
                    f"Vous pouvez l'activer en modifiant vos préférences."
                )
                return redirect('accounts:profile_edit')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator