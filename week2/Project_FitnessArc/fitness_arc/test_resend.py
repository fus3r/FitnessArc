#!/usr/bin/env python
"""
Script de test pour vérifier l'envoi d'email via Resend
Usage: python test_resend.py
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

def test_resend():
    print("🔍 Configuration Email:")
    print(f"  EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    print(f"  RESEND_API_KEY: {'***' + settings.RESEND_API_KEY[-4:] if settings.RESEND_API_KEY else 'NON DÉFINI ❌'}")
    print(f"  DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
    print()

    if not settings.RESEND_API_KEY:
        print("❌ ERREUR: RESEND_API_KEY non défini dans les variables d'environnement")
        return False

    # Email de test
    test_email = "fitnessarc.contact@gmail.com"  # Changez par votre email
    
    print(f"📧 Envoi d'un email de test à {test_email}...")
    try:
        send_mail(
            subject="Test FitnessArc - Resend Configuration",
            message="Ceci est un email de test depuis FitnessArc via Resend.\n\nSi tu reçois ce message, la configuration Resend fonctionne correctement ! ✅",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[test_email],
            fail_silently=False,
        )
        print("✅ Email envoyé avec succès via Resend !")
        print(f"   Vérifie la boîte mail: {test_email}")
        return True
    except Exception as e:
        print(f"❌ ERREUR lors de l'envoi: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_resend()
    sys.exit(0 if success else 1)
