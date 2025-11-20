from .models import Friendship

def friends_requests_count(request):
    """Compteur de demandes d'amis en attente"""
    if request.user.is_authenticated:
        count = Friendship.objects.filter(to_user=request.user, status='pending').count()
        return {'pending_requests_count': count}
    return {'pending_requests_count': 0}


def user_features(request):
    """Fonctionnalités activées pour l'utilisateur"""
    if request.user.is_authenticated and hasattr(request.user, 'profile'):
        profile = request.user.profile
        return {
            'feature_workouts': profile.feature_workouts,
            'feature_nutrition': profile.feature_nutrition,
            'feature_running': profile.feature_running,
            'feature_leaderboard': profile.feature_leaderboard,
        }
    # Pour les utilisateurs non connectés, afficher toutes les fonctionnalités
    return {
        'feature_workouts': True,
        'feature_nutrition': True,
        'feature_running': True,
        'feature_leaderboard': True,
    }