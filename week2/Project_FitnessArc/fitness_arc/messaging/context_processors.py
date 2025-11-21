from .models import Message

def unread_messages(request):
    """
    Add the number of unread messages for the logged-in user
    to every template as 'unread_messages_count'.
    """
    user = getattr(request, "user", None)
    if not user or not user.is_authenticated:
        return {}

    count = (
        Message.objects
        .filter(conversation__participants=user, is_read=False)
        .exclude(sender=user)          # only messages sent BY others
        .count()
    )

    return {"unread_messages_count": count}
