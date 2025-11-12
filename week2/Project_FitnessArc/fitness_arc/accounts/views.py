from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User  # ← AJOUTER
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView, UpdateView
from django.db.models import Q

from .forms import SignupForm, ProfileForm
from .models import Profile, Friendship


class SignupView(View):
    template_name = "accounts/signup.html"

    def get(self, request):
        return render(request, self.template_name, {"form": SignupForm()})

    def post(self, request):
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()  # crée l'user (+ profile via signal) et applique le goal
            # Authentifie et connecte
            user_auth = authenticate(
                request,
                username=user.username,
                password=form.cleaned_data["password1"],
            )
            if user_auth is not None:
                login(request, user_auth)
            messages.success(request, "Compte créé avec succès. Bienvenue !")
            return redirect("accounts:profile")  # → /accounts/profile/
        return render(request, self.template_name, {"form": form})


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
    """Liste des amis + demandes en attente"""
    # Amis acceptés (bidirectionnel)
    friends = User.objects.filter(
        Q(friendships_received__from_user=request.user, friendships_received__status='accepted') |
        Q(friendships_sent__to_user=request.user, friendships_sent__status='accepted')
    ).distinct()
    
    # Demandes reçues en attente
    pending_requests = Friendship.objects.filter(to_user=request.user, status='pending')
    
    # Demandes envoyées en attente
    sent_requests = Friendship.objects.filter(from_user=request.user, status='pending')
    
    # Tous les utilisateurs (pour recherche)
    all_users = User.objects.exclude(pk=request.user.pk).order_by('username')
    
    context = {
        'friends': friends,
        'pending_requests': pending_requests,
        'sent_requests': sent_requests,
        'all_users': all_users,
    }
    return render(request, 'accounts/friends_list.html', context)

@login_required
def send_friend_request(request, user_id):
    """Envoyer une demande d'ami"""
    to_user = get_object_or_404(User, pk=user_id)
    
    if to_user == request.user:
        messages.error(request, "Vous ne pouvez pas vous ajouter vous-même !")
        return redirect('accounts:friends_list')
    
    # Vérifier si une demande existe déjà
    existing = Friendship.objects.filter(
        Q(from_user=request.user, to_user=to_user) |
        Q(from_user=to_user, to_user=request.user)
    ).first()
    
    if existing:
        if existing.status == 'accepted':
            messages.info(request, f"Vous êtes déjà ami avec {to_user.username}")
        elif existing.status == 'pending':
            messages.info(request, f"Demande déjà envoyée à {to_user.username}")
    else:
        Friendship.objects.create(from_user=request.user, to_user=to_user)
        messages.success(request, f"Demande d'ami envoyée à {to_user.username} !")
    
    return redirect('accounts:friends_list')

@login_required
def accept_friend_request(request, friendship_id):
    """Accepter une demande d'ami"""
    friendship = get_object_or_404(Friendship, pk=friendship_id, to_user=request.user, status='pending')
    friendship.status = 'accepted'
    friendship.save()
    messages.success(request, f"Vous êtes maintenant ami avec {friendship.from_user.username} !")
    return redirect('accounts:friends_list')

@login_required
def reject_friend_request(request, friendship_id):
    """Refuser une demande d'ami"""
    friendship = get_object_or_404(Friendship, pk=friendship_id, to_user=request.user, status='pending')
    friendship.status = 'rejected'
    friendship.save()
    messages.info(request, f"Demande de {friendship.from_user.username} refusée")
    return redirect('accounts:friends_list')

@login_required
def remove_friend(request, user_id):
    """Retirer un ami"""
    friend = get_object_or_404(User, pk=user_id)
    Friendship.objects.filter(
        Q(from_user=request.user, to_user=friend) |
        Q(from_user=friend, to_user=request.user)
    ).delete()
    messages.success(request, f"{friend.username} retiré de vos amis")
    return redirect('accounts:friends_list')

@login_required
def friend_dashboard(request, user_id):
    """Voir le dashboard d'un ami"""
    friend = get_object_or_404(User, pk=user_id)
    
    # Vérifier qu'ils sont amis
    is_friend = Friendship.objects.filter(
        Q(from_user=request.user, to_user=friend, status='accepted') |
        Q(from_user=friend, to_user=request.user, status='accepted')
    ).exists()
    
    if not is_friend:
        messages.error(request, "Vous devez être ami avec cet utilisateur pour voir son dashboard")
        return redirect('accounts:friends_list')
    
    # Importer les données dashboard
    from dashboard.services import get_dashboard_data
    dashboard_data = get_dashboard_data(friend)
    dashboard_data['friend'] = friend
    
    return render(request, 'accounts/friend_dashboard.html', dashboard_data)
