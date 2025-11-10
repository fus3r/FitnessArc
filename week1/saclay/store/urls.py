from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    # URL pour la page d'accueil de la boutique qui affiche la liste des produits
    path('', views.index, name='index'),
    
    # Vous pouvez ajouter d'autres URLs ici comme :
    # path('product/<int:id>/', views.product_detail, name='product_detail'),
    # path('category/<str:category_name>/', views.category, name='category'),
]