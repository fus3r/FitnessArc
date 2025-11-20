from decimal import Decimal

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from .models import Profile

User = get_user_model()

FRENCH_PASSWORD_HELP_HTML = mark_safe("""
<ul>
  <li>Doit être différent de vos informations personnelles.</li>
  <li>Minimum 8 caractères.</li>
  <li>Ne doit pas être un mot de passe trop courant.</li>
  <li>Ne doit pas être composé uniquement de chiffres.</li>
</ul>
""")

class SignupForm(UserCreationForm):
    error_messages = {
        "password_mismatch": _("Les deux mots de passe ne correspondent pas."),
    }

    username = forms.CharField(
        label=_("Nom d’utilisateur"),
        help_text=_("Lettres, chiffres et @/./+/-/_ uniquement."),
        error_messages={
            "required": _("Le nom d’utilisateur est obligatoire."),
            "unique": _("Ce nom d’utilisateur est déjà pris."),
            "invalid": _("Saisis un nom d’utilisateur valide."),
            "max_length": _("Le nom d’utilisateur est trop long."),
        },
    )
    email = forms.EmailField(
        required=True,
        label=_("Email"),
        help_text=_("Adresse utilisée pour la connexion et la récupération du mot de passe."),
        error_messages={
            "required": _("L’email est obligatoire."),
            "invalid": _("Saisis une adresse email valide."),
        },
    )
    password1 = forms.CharField(
        label=_("Mot de passe"),
        strip=False,
        widget=forms.PasswordInput,
        help_text=FRENCH_PASSWORD_HELP_HTML,   
        error_messages={"required": _("Le mot de passe est obligatoire.")},
    )
    password2 = forms.CharField(
        label=_("Confirmation du mot de passe"),
        strip=False,
        widget=forms.PasswordInput,
        help_text=_("Saisis le même mot de passe pour vérification."),
        error_messages={"required": _("Merci de confirmer ton mot de passe.")},
    )

    sex = forms.ChoiceField(
        choices=getattr(Profile, "SEX_CHOICES", (("M", "Homme"), ("F", "Femme"), ("O", "Autre"))),
        required=True,
        label=_("Sexe"),
        error_messages={"required": _("Le sexe est obligatoire.")},
    )
    height_cm = forms.IntegerField(
        required=True,
        min_value=50,
        max_value=300,
        label=_("Taille (cm)"),
        help_text=_("Entre 50 et 300 cm."),
        error_messages={
            "required": _("La taille est obligatoire."),
            "invalid": _("Saisis une valeur numérique valide."),
            "min_value": _("La taille doit être au moins de 50 cm."),
            "max_value": _("La taille ne peut pas dépasser 300 cm."),
        },
    )
    weight_kg = forms.DecimalField(
        required=True,
        min_value=Decimal("20.0"),
        max_value=Decimal("400.0"),
        max_digits=6,
        decimal_places=2,
        label=_("Poids (kg)"),
        help_text=_("Entre 20,00 et 400,00 kg."),
        error_messages={
            "required": _("Le poids est obligatoire."),
            "invalid": _("Saisis un nombre valide (ex. 72.5)."),
            "min_value": _("Le poids doit être au moins de 20 kg."),
            "max_value": _("Le poids ne peut pas dépasser 400 kg."),
        },
    )
    goal = forms.ChoiceField(
        choices=Profile.GOAL_CHOICES,
        label=_("Objectif"),
        help_text=_("Choisis ton objectif principal."),
    )
    
    # Feature selection fields
    feature_workouts = forms.BooleanField(
        required=False,
        initial=True,
        label=_("Exercices & Workouts"),
        help_text=_("Gérer et suivre tes séances d'entraînement."),
    )
    feature_nutrition = forms.BooleanField(
        required=False,
        initial=True,
        label=_("Nutrition"),
        help_text=_("Suivre ton alimentation et tes calories."),
    )
    feature_running = forms.BooleanField(
        required=False,
        initial=True,
        label=_("Running"),
        help_text=_("Tracker tes activités de course à pied."),
    )
    feature_leaderboard = forms.BooleanField(
        required=False,
        initial=True,
        label=_("Classement"),
        help_text=_("Voir ton classement et celui de tes amis."),
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(_("Un compte existe déjà avec cet email."))
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"].strip()
        if commit:
            user.save()
            profile = user.profile  
            profile.goal = self.cleaned_data["goal"]
            profile.sex = self.cleaned_data["sex"]
            profile.height_cm = self.cleaned_data["height_cm"]
            profile.weight_kg = self.cleaned_data["weight_kg"]
            profile.feature_workouts = self.cleaned_data.get("feature_workouts", True)
            profile.feature_nutrition = self.cleaned_data.get("feature_nutrition", True)
            profile.feature_running = self.cleaned_data.get("feature_running", True)
            profile.feature_leaderboard = self.cleaned_data.get("feature_leaderboard", True)
            profile.save()
        else:
            self._pending_profile = {
                "goal": self.cleaned_data["goal"],
                "sex": self.cleaned_data["sex"],
                "height_cm": self.cleaned_data["height_cm"],
                "weight_kg": self.cleaned_data["weight_kg"],
                "feature_workouts": self.cleaned_data.get("feature_workouts", True),
                "feature_nutrition": self.cleaned_data.get("feature_nutrition", True),
                "feature_running": self.cleaned_data.get("feature_running", True),
                "feature_leaderboard": self.cleaned_data.get("feature_leaderboard", True),
            }
        return user


class ProfileForm(forms.ModelForm):
    height_cm = forms.IntegerField(
        required=True,
        min_value=50,
        max_value=300,
        label=_("Taille (cm)"),
        help_text=_("Entre 50 et 300 cm."),
        error_messages={
            "required": _("La taille est obligatoire."),
            "invalid": _("Saisis une valeur numérique valide."),
            "min_value": _("La taille doit être au moins de 50 cm."),
            "max_value": _("La taille ne peut pas dépasser 300 cm."),
        },
    )
    weight_kg = forms.DecimalField(
        required=True,
        min_value=Decimal("20.0"),
        max_value=Decimal("400.0"),
        max_digits=6,
        decimal_places=2,
        label=_("Poids (kg)"),
        help_text=_("Entre 20,00 et 400,00 kg."),
        error_messages={
            "required": _("Le poids est obligatoire."),
            "invalid": _("Saisis un nombre valide (ex. 72.5)."),
            "min_value": _("Le poids doit être au moins de 20 kg."),
            "max_value": _("Le poids ne peut pas dépasser 400 kg."),
        },
    )

    running_data_source = forms.ChoiceField(
        choices=Profile.RUNNING_DATA_SOURCE_CHOICES,
        label=_("Source des données de running"),
        help_text=_("Choisis comment tu veux enregistrer tes activités running."),
        required=False,  # Made optional, will be required conditionally based on feature_running
    )

    class Meta:
        model = Profile
        fields = ("sex", "height_cm", "weight_kg", "goal", "running_data_source", 
                  "feature_workouts", "feature_nutrition", "feature_running", "feature_leaderboard")
        labels = {
            "sex": _("Sexe"), 
            "goal": _("Objectif"), 
            "running_data_source": _("Source running"),
            "feature_workouts": _("Exercices & Workouts"),
            "feature_nutrition": _("Nutrition"),
            "feature_running": _("Running"),
            "feature_leaderboard": _("Classement"),
        }
        help_texts = {
            "sex": _("Sélectionne ton sexe."),
            "goal": _("Choisis l'objectif qui te correspond."),
            "running_data_source": _("Choisis comment tu veux enregistrer tes activités running."),
            "feature_workouts": _("Gérer et suivre tes séances d'entraînement."),
            "feature_nutrition": _("Suivre ton alimentation et tes calories."),
            "feature_running": _("Tracker tes activités de course à pied."),
            "feature_leaderboard": _("Voir ton classement et celui de tes amis."),
        }

    def clean_height_cm(self):
        h = self.cleaned_data.get("height_cm")
        if h is None or h <= 0:
            raise forms.ValidationError(_("La taille doit être strictement positive."))
        return h

    def clean_weight_kg(self):
        w = self.cleaned_data.get("weight_kg")
        if w is None or w <= 0:
            raise forms.ValidationError(_("Le poids doit être strictement positif."))
        return w
    
    def clean(self):
        cleaned_data = super().clean()
        feature_running = cleaned_data.get("feature_running")
        running_data_source = cleaned_data.get("running_data_source")
        
        # If running feature is enabled, running_data_source is required
        if feature_running and not running_data_source:
            self.add_error("running_data_source", _("La source de données running est obligatoire si tu actives le running."))
        
        return cleaned_data
    
    def save(self, commit=True):
        profile = super().save(commit=False)
        # Explicitly set boolean fields (unchecked checkboxes don't appear in POST data)
        profile.feature_workouts = self.cleaned_data.get("feature_workouts", False)
        profile.feature_nutrition = self.cleaned_data.get("feature_nutrition", False)
        profile.feature_running = self.cleaned_data.get("feature_running", False)
        profile.feature_leaderboard = self.cleaned_data.get("feature_leaderboard", False)
        if commit:
            profile.save()
        return profile


class PasswordChangeFormFR(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["old_password"].label = _("Ancien mot de passe")
        self.fields["new_password1"].label = _("Nouveau mot de passe")
        self.fields["new_password2"].label = _("Confirmer le nouveau mot de passe")
        self.fields["new_password1"].help_text = FRENCH_PASSWORD_HELP_HTML