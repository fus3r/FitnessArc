from django.urls import path
from .models import PRODUCTS
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('search/', views.search, name="search"),
    path('products/', views.products_list, name="products_list"),
    path('product/<int:product_id>/', views.product_detail, name="product_detail"),
    path('producers/', views.producers_list, name="producers_list"),
    path('producer/<int:producer_id>/', views.producer_detail, name="producer_detail"),
    path('about/', views.about, name="about"),
    path('cart/', views.view_cart, name="cart"),
    path('cart/add/<int:product_id>/', views.add_to_cart, name="add_to_cart"),
    path('cart/update/<int:product_id>/', views.update_cart, name="update_cart"),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name="remove_from_cart"),
    path('cart/clear/', views.clear_cart, name="clear_cart"),
]

for i in range(len(PRODUCTS)):
    urlpatterns.append(
        path(f'{i}', views.info_product, kwargs={'product_id': i}, name=f"store_{i}")
    )

