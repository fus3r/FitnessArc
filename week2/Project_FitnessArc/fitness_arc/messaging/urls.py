from django.urls import path
from . import views

app_name = "messaging"

urlpatterns = [
    path('', views.inbox, name='inbox'),
    path('with/<str:username>/', views.conversation_with, name='conversation_with'),
]