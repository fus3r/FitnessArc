from django.shortcuts import render

# Create your views here.
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Max
from django.shortcuts import get_object_or_404, redirect

from .models import Conversation, Message


def _get_or_create_private_conversation(user1, user2):
    conv = (
        Conversation.objects
        .filter(participants=user1)
        .filter(participants=user2)
        .first()
    )
    if not conv:
        conv = Conversation.objects.create()
        conv.participants.add(user1, user2)
    return conv


@login_required
def inbox(request):
    conversations = (
        Conversation.objects
        .filter(participants=request.user)
        .annotate(last_message_at=Max('messages__created_at'))
        .order_by('-last_message_at')
    )
    return render(request, 'messaging/inbox.html', {
        'conversations': conversations,
    })


@login_required
def conversation_with(request, username):
    other = get_object_or_404(User, username=username)
    if other == request.user:
        return redirect('messaging:inbox')
    


    conv = _get_or_create_private_conversation(request.user, other)

    if request.method == 'POST':
        text = request.POST.get('text', '').strip()
        if text:
            Message.objects.create(
                conversation=conv,
                sender=request.user,
                text=text
            )
            return redirect('messaging:conversation_with', username=other.username)

    messages = conv.messages.select_related('sender')

    # Mark messages from the other user as read
    conv.messages.filter(sender=other, is_read=False).update(is_read=True)

    return render(request, 'messaging/conversation_detail.html', {
        'conversation': conv,
        'other_user': other,
        'messages': messages,
    })