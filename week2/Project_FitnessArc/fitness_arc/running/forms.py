from django import forms
from .models import GarminAuth


class GarminConnectForm(forms.ModelForm):
    """
    Formulaire pour connecter un compte Garmin Connect.
    L'utilisateur entre son email et mot de passe Garmin.
    """
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Mot de passe Garmin Connect'
        }),
        help_text="Votre mot de passe Garmin Connect (stocké de manière sécurisée)"
    )
    
    class Meta:
        model = GarminAuth
        fields = ['email', 'password']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email Garmin Connect'
            }),
        }
        help_texts = {
            'email': 'Votre email Garmin Connect',
        }
