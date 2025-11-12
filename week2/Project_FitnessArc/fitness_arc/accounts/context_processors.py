from .models import Friendship

def friends_requests_count(request):
    """Compteur de demandes d'amis en attente"""
    if request.user.is_authenticated:
        count = Friendship.objects.filter(to_user=request.user, status='pending').count()
        return {'pending_requests_count': count}
    return {'pending_requests_count': 0}
