from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    # URL pour la page d'accueil de la boutique
    path('', views.index, name='index'),
    # URL pour afficher les détails d'un produit spécifique
    path('/store.html', views.product_list, name='product_list'),
]