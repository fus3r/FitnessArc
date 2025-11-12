from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    message = "Bienvenue sur le comptoir local de Paris Saclay!"
    return HttpResponse(message)

def product_list(request):
    from .models import PRODUCTS
    return render(request, '/store.html', {'products': PRODUCTS})

 