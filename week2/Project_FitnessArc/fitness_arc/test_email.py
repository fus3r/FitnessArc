#!/usr/bin/env python
"""
Script de test pour vérifier l'envoi d'email
Usage: python test_email.py
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitness_arc.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

def test_email():
    print("🔍 Configuration Email:")
    print(f"  EMAIL_HOST: {settings.EMAIL_HOST}")
    print(f"  EMAIL_PORT: {settings.EMAIL_PORT}")
    print(f"  EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
    print(f"  EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
    print(f"  EMAIL_TIMEOUT: {getattr(settings, 'EMAIL_TIMEOUT', 'Non défini')}")
    print(f"  EMAIL_PASSWORD: {'***' if settings.EMAIL_HOST_PASSWORD else 'NON DÉFINI ❌'}")
    print()

    if not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
        print("❌ ERREUR: EMAIL_USER ou EMAIL_PASSWORD non défini dans les variables d'environnement")
        return False

    print("📧 Envoi d'un email de test...")
    try:
        send_mail(
            subject="Test FitnessArc - Email Configuration",
            message="Ceci est un email de test depuis FitnessArc.\n\nSi tu reçois ce message, la configuration email fonctionne correctement ! ✅",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.EMAIL_HOST_USER],  # Envoyer à soi-même
            fail_silently=False,
        )
        print("✅ Email envoyé avec succès !")
        print(f"   Vérifie la boîte mail: {settings.EMAIL_HOST_USER}")
        return True
    except Exception as e:
        print(f"❌ ERREUR lors de l'envoi: {type(e).__name__}: {e}")
        return False

if __name__ == "__main__":
    success = test_email()
    sys.exit(0 if success else 1)
