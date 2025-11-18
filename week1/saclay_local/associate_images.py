#!/usr/bin/env python3
"""
Script pour associer automatiquement des images aux produits.
Lance ce script après avoir ajouté les vraies images dans media/products/

Usage:
    python3 associate_images.py
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saclay_local.settings')
django.setup()

from store.models import Product

# Mapping des noms de produits vers les noms de fichiers images
PRODUCT_IMAGE_MAPPING = {
    'Yaourth Vanille': 'products/yaourt_vanille.webp',
    'Yaourt Marron': 'products/yaourt_marron.webp',
    'Jus de Pomme': 'products/jus_pomme.avif',
    'Banane': 'products/banane.jpg'
}

def associate_images():
    """Associe les images aux produits existants."""
    updated = 0
    not_found = []
    
    for product_name, image_path in PRODUCT_IMAGE_MAPPING.items():
        try:
            products = Product.objects.filter(name__icontains=product_name.split()[0])
            if products.exists():
                for product in products:
                    product.image = image_path
                    product.save()
                    print(f"✓ Image associée: {product.name} -> {image_path}")
                    updated += 1
            else:
                not_found.append(product_name)
                print(f"✗ Produit non trouvé: {product_name}")
        except Exception as e:
            print(f"✗ Erreur pour {product_name}: {e}")
    
    print(f"\n{'='*60}")
    print(f"Résumé:")
    print(f"  - {updated} image(s) associée(s)")
    print(f"  - {len(not_found)} produit(s) non trouvé(s)")
    
    if not_found:
        print(f"\nProduits non trouvés dans la base de données:")
        for name in not_found:
            print(f"  - {name}")
    
    print(f"{'='*60}")

if __name__ == '__main__':
    print("Association des images aux produits...")
    print(f"{'='*60}\n")
    associate_images()
    print("\nTerminé !")
