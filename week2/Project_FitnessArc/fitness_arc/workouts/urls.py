from django.urls import path
from . import views

app_name = 'workouts'

urlpatterns = [
    # Liste des exercices
    path('exercises/', views.exercise_list, name='exercise_list'),
    
    # Templates de workout
    path('templates/', views.template_list, name='template_list'),
    path('templates/create/', views.template_create, name='template_create'),
    # path('templates/<int:pk>/', views.template_detail, name='template_detail'),  # TODO: À implémenter
    # path('templates/<int:pk>/edit/', views.template_update, name='template_update'),  # TODO: À implémenter
    # path('templates/<int:pk>/delete/', views.template_delete, name='template_delete'),  # TODO: À implémenter
    
    # Démarrer une session depuis un template
    path('templates/<int:pk>/start/', views.start_session, name='start_session'),
    
    # Détail d'une session
    path('sessions/<int:pk>/', views.session_detail, name='session_detail'),
]
