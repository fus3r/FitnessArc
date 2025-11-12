from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views

from .views import SignupView, ProfileDetailView, ProfileEditView

app_name = "accounts"

urlpatterns = [
    # Auth
    path("signup/", SignupView.as_view(), name="signup"),
    path("login/", auth_views.LoginView.as_view(
        template_name="accounts/login.html"
    ), name="login"),
    path("logout/", auth_views.LogoutView.as_view(
        next_page="/accounts/login/"
    ), name="logout"),
    # (optionnel) changement de mot de passe
    path("password-change/", auth_views.PasswordChangeView.as_view(
        template_name="accounts/password_change.html",
        success_url=reverse_lazy("accounts:profile"),
    ), name="password_change"),

    # Profil
    path("profile/", ProfileDetailView.as_view(), name="profile"),
    path("profile/edit/", ProfileEditView.as_view(), name="profile_edit"),
]
