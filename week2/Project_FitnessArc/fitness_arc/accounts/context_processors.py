from .models import Friendship

def friends_requests_count(request):
    """Returns the count of pending friend requests for the current user."""
    if request.user.is_authenticated:
        count = Friendship.objects.filter(to_user=request.user, status='pending').count()
        return {'pending_requests_count': count}
    return {'pending_requests_count': 0}


def user_features(request):
    """Returns which features are enabled for the current user."""
    if request.user.is_authenticated and hasattr(request.user, 'profile'):
        profile = request.user.profile
        return {
            'feature_workouts': profile.feature_workouts,
            'feature_nutrition': profile.feature_nutrition,
            'feature_running': profile.feature_running,
            'feature_leaderboard': profile.feature_leaderboard,
        }
    # Show all features for anonymous users
    return {
        'feature_workouts': True,
        'feature_nutrition': True,
        'feature_running': True,
        'feature_leaderboard': True,
    }