from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from .models import Profile


User = get_user_model()


class SignupForm(UserCreationForm):
    """
    Formulaire d'inscription : username + (email optionnel) + choix d'objectif (goal).
    Crée l'utilisateur, s'assure que le Profile existe (via signal ou get_or_create),
    puis applique l'objectif sélectionné.
    """
    email = forms.EmailField(required=False, label="Email (optionnel)")
    goal = forms.ChoiceField(choices=Profile.GOAL_CHOICES, label="Objectif")

    class Meta(UserCreationForm.Meta):
        model = User
        # password1/password2 sont inclus par UserCreationForm
        fields = ("username", "email")
        labels = {
            "username": "Nom d'utilisateur",
        }
        help_texts = {
            "username": "",  # on retire le helptext verbeux par défaut si souhaité
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data.get("email", "")
        if commit:
            user.save()
            # Grâce au signal, un Profile est créé à la création d'un User,
            # mais on sécurise quand même avec get_or_create (fixtures, etc.)
            profile, _ = Profile.objects.get_or_create(user=user)
            profile.goal = self.cleaned_data["goal"]
            profile.save()
        else:
            # si commit=False, le caller devra sauver user puis appliquer le goal
            self._pending_goal = self.cleaned_data["goal"]
        return user


class ProfileForm(forms.ModelForm):
    """
    Edition des champs du profil.
    Validation serveurside : height_cm > 0 si renseigné, weight_kg > 0 si renseigné.
    """
    height_cm = forms.IntegerField(
        required=False,
        min_value=1,  # validation immédiate côté formulaire
        label="Taille (cm)",
    )
    weight_kg = forms.DecimalField(
        required=False,
        min_value=0.1,  # validation immédiate
        max_digits=5,
        decimal_places=2,
        label="Poids (kg)",
    )

    class Meta:
        model = Profile
        fields = ("sex", "height_cm", "weight_kg", "goal")
        labels = {
            "sex": "Sexe",
            "goal": "Objectif",
        }

    # Redondance volontaire avec min_value pour être béton (et messages clairs)
    def clean_height_cm(self):
        h = self.cleaned_data.get("height_cm")
        if h is not None and h <= 0:
            raise forms.ValidationError("La taille doit être strictement positive.")
        return h

    def clean_weight_kg(self):
        w = self.cleaned_data.get("weight_kg")
        if w is not None and w <= 0:
            raise forms.ValidationError("Le poids doit être strictement positif.")
        return w
