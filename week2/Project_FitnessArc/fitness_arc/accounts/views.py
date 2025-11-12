from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView, UpdateView

from .forms import SignupForm, ProfileForm
from .models import Profile


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
