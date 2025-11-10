from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    message = "Bienvenue sur le comptoir local de Paris Saclay!"
    return HttpResponse(message)


