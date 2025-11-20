from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User  
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView, UpdateView
from django.db.models import Q
from django.conf import settings
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import PasswordChangeFormFR
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.views import PasswordChangeView  
from django.urls import reverse
from .tokens import activation_token
from .forms import SignupForm, ProfileForm
from .models import Profile, Friendship

import logging
logger = logging.getLogger(__name__)



class SignupView(View):
    template_name = "accounts/signup.html"

    def get(self, request):
        return render(request, self.template_name, {"form": SignupForm()})

    def post(self, request):
        form = SignupForm(request.POST)

        if not form.is_valid():
            logger.error("Signup errors: %s", form.errors.as_json())
            messages.error(request, "Le formulaire contient des erreurs. Merci de corriger et réessayer.")
            return render(request, self.template_name, {"form": form})

        user = form.save()

        if user.is_active: 
            user.is_active = False
            user.save(update_fields=["is_active"])

        try:
            send_activation_email(request, user)
        except Exception:
            logger.exception("Erreur d'envoi de l'email d'activation")

            if getattr(settings, "DEBUG", False):
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = activation_token.make_token(user)
                activate_url = f"{request.scheme}://{request.get_host()}{reverse('accounts:activate', args=[uid, token])}"
                messages.warning(request, f"Email non envoyé. Active ton compte via ce lien DEV : {activate_url}")
                return redirect("accounts:activation_sent")

            messages.error(request, "Impossible d'envoyer l'email d'activation. Réessaie plus tard.")
            return render(request, self.template_name, {"form": form})

        messages.success(request, "Compte créé ! Vérifie ta boîte mail pour activer ton compte.")
        return redirect("accounts:activation_sent")

class ProfileDetailView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/profile.html"
    login_url = "accounts:login"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["profile"] = self.request.user.profile
        return ctx


class ProfileEditView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileForm
    template_name = "accounts/profile_edit.html"
    success_url = reverse_lazy("accounts:profile")
    login_url = "accounts:login"

    def get_object(self, queryset=None):
        return self.request.user.profile

    def form_valid(self, form):
        messages.success(self.request, "Profil mis à jour.")
        return super().form_valid(form)


@login_required
def friends_list(request):
    """List of friends and pending requests."""
    friends = User.objects.filter(
        Q(friendships_received__from_user=request.user, friendships_received__status='accepted') |
        Q(friendships_sent__to_user=request.user, friendships_sent__status='accepted')
    ).distinct()
    
    pending_requests = Friendship.objects.filter(to_user=request.user, status='pending')
    
    sent_requests = Friendship.objects.filter(from_user=request.user, status='pending')
    
    # Exclude current user and admin/staff accounts
    all_users = User.objects.exclude(pk=request.user.pk).exclude(is_superuser=True).exclude(is_staff=True).order_by('username')
    
    context = {
        'friends': friends,
        'pending_requests': pending_requests,
        'sent_requests': sent_requests,
        'all_users': all_users,
    }
    return render(request, 'accounts/friends_list.html', context)

@login_required
def send_friend_request(request, user_id):
    """Send friend request to another user"""
    to_user = get_object_or_404(User, pk=user_id)
    
    if to_user == request.user:
        messages.error(request, "Vous ne pouvez pas vous ajouter vous-même !")
        return redirect('accounts:friends_list')
    
    # Check if a relationship already exists (in both directions)
    existing = Friendship.objects.filter(
        Q(from_user=request.user, to_user=to_user) |
        Q(from_user=to_user, to_user=request.user)
    ).first()
    
    if existing:
        if existing.status == 'accepted':
            messages.info(request, f"Vous êtes déjà ami avec {to_user.username}")
        elif existing.status == 'pending':
            messages.info(request, f"Demande déjà envoyée à {to_user.username}")
        return redirect('accounts:friends_list')
    
    # Use get_or_create to avoid duplicates on double-click
    friendship, created = Friendship.objects.get_or_create(
        from_user=request.user,
        to_user=to_user,
        defaults={'status': 'pending'}
    )
    
    if created:
        messages.success(request, f"Demande d'ami envoyée à {to_user.username} !")
    else:
        messages.info(request, f"Demande déjà envoyée à {to_user.username}")
    
    return redirect('accounts:friends_list')

@login_required
def accept_friend_request(request, friendship_id):
    """Accept a friend request"""
    friendship = get_object_or_404(Friendship, pk=friendship_id, to_user=request.user, status='pending')
    friendship.status = 'accepted'
    friendship.save()
    messages.success(request, f"Vous êtes maintenant ami avec {friendship.from_user.username} !")
    return redirect('accounts:friends_list')

@login_required
def reject_friend_request(request, friendship_id):
    """Reject a friend request"""
    friendship = get_object_or_404(Friendship, pk=friendship_id, to_user=request.user, status='pending')
    friendship.status = 'rejected'
    friendship.save()
    messages.info(request, f"Demande de {friendship.from_user.username} refusée")
    return redirect('accounts:friends_list')

@login_required
def remove_friend(request, user_id):
    """Remove a friend"""
    friend = get_object_or_404(User, pk=user_id)
    Friendship.objects.filter(
        Q(from_user=request.user, to_user=friend) |
        Q(from_user=friend, to_user=request.user)
    ).delete()
    messages.success(request, f"{friend.username} retiré de vos amis")
    return redirect('accounts:friends_list')

@login_required
def friend_dashboard(request, user_id):
    """View a friend's dashboard"""
    friend = get_object_or_404(User, pk=user_id)
    
    is_friend = Friendship.objects.filter(
        Q(from_user=request.user, to_user=friend, status='accepted') |
        Q(from_user=friend, to_user=request.user, status='accepted')
    ).exists()
    
    if not is_friend:
        messages.error(request, "Vous devez être ami avec cet utilisateur pour voir son dashboard")
        return redirect('accounts:friends_list')
    
    from dashboard.services import get_dashboard_data
    dashboard_data = get_dashboard_data(friend)
    dashboard_data['friend'] = friend
    
    return render(request, 'accounts/friend_dashboard.html', dashboard_data)



class PasswordChangeProfileView(LoginRequiredMixin, PasswordChangeView):
    template_name = "accounts/password_change.html" 
    success_url = reverse_lazy("accounts:profile")
    form_class = PasswordChangeFormFR
    login_url = "accounts:login"

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Mot de passe mis à jour.")
        return response


from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

def send_activation_email(request, user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = activation_token.make_token(user)
    scheme = "https" if request.is_secure() else "http"
    domain = request.get_host()
    activate_url = f"{scheme}://{domain}{reverse('accounts:activate', args=[uid, token])}"

    context = {
        "user": user,
        "activate_url": activate_url,
        "project_name": "Fitness Arc",
    }

    try:
        subject = render_to_string("accounts/email/activation_subject.txt", context).strip()
    except Exception:
        subject = f"Active ton compte sur Fitness Arc"

    try:
        text_body = render_to_string("accounts/email/activation_body.txt", context)
    except Exception:
        text_body = f"Bonjour {user.username},\n\nActive ton compte : {activate_url}\n"

    try:
        html_body = render_to_string("accounts/email/activation_body.html", context)
    except Exception:
        html_body = f"<p>Bonjour <strong>{user.username}</strong>,</p><p><a href='{activate_url}'>Activer mon compte</a></p>"

    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", settings.EMAIL_HOST_USER)
    email = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=from_email,
        to=[user.email],
    )
    email.attach_alternative(html_body, "text/html")
    email.send(fail_silently=False)  

class ActivateAccountView(View):
    template_invalid = "accounts/activation_invalid.html"

    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except Exception:
            user = None

        if user is not None and activation_token.check_token(user, token):
            if not user.is_active:
                user.is_active = True
                user.save(update_fields=["is_active"])
            messages.success(request, "Ton compte est activé ✅ Bienvenue !")
            login(request, user)
            return redirect("accounts:profile")
        else:
            return render(request, self.template_invalid, {})
