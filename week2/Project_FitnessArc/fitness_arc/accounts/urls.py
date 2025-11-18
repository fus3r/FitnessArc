from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from django.urls import path, reverse_lazy
from .views import PasswordChangeProfileView
from .views import ActivateAccountView
from django.views.generic import TemplateView


app_name = "accounts"

urlpatterns = [
    path("login/", auth_views.LoginView.as_view(template_name="accounts/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("signup/", views.SignupView.as_view(), name="signup"),
    path("profile/", views.ProfileDetailView.as_view(), name="profile"),
    path("profile/edit/", views.ProfileEditView.as_view(), name="profile_edit"),
    path("password-reset/", auth_views.PasswordResetView.as_view(
        template_name="accounts/password_reset_form.html",
        email_template_name="accounts/password_reset_email.txt",
        subject_template_name="accounts/password_reset_subject.txt",
        success_url=reverse_lazy("accounts:password_reset_done"),
    ), name="password_reset"),
    path("password-reset/done/", auth_views.PasswordResetDoneView.as_view(
        template_name="accounts/password_reset_done.html",
    ), name="password_reset_done"),
    path("reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(
        template_name="accounts/password_reset_confirm.html",
        success_url=reverse_lazy("accounts:password_reset_complete"),
    ), name="password_reset_confirm"),
    path("reset/done/", auth_views.PasswordResetCompleteView.as_view(
        template_name="accounts/password_reset_complete.html",
    ), name="password_reset_complete"),
    path("password-change/", PasswordChangeProfileView.as_view(), name="password_change"),
    path("signup/done/", TemplateView.as_view(
        template_name="accounts/activation_sent.html"
    ), name="activation_sent"),

    path("activate/<uidb64>/<token>/", ActivateAccountView.as_view(), name="activate"),
    
    # Friends URLs
    path("friends/", views.friends_list, name="friends_list"),
    path("friends/send/<int:user_id>/", views.send_friend_request, name="send_friend_request"),
    path("friends/accept/<int:friendship_id>/", views.accept_friend_request, name="accept_friend_request"),
    path("friends/reject/<int:friendship_id>/", views.reject_friend_request, name="reject_friend_request"),
    path("friends/remove/<int:user_id>/", views.remove_friend, name="remove_friend"),
    path("friends/<int:user_id>/dashboard/", views.friend_dashboard, name="friend_dashboard"),
]

