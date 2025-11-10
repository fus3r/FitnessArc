from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    from .models import PRODUCTS
    return render(request, 'store/product_list.html', {'products': PRODUCTS})

def product_list(request):
    from .models import PRODUCTS
    return render(request, 'store/product_list.html', {'products': PRODUCTS})
