from django.urls import path
from . import views

app_name = 'workouts'

urlpatterns = [
    path("exercises/", views.exercise_list, name="exercise_list"),
    path("templates/", views.template_list, name="template_list"),
    path("templates/new/", views.template_create, name="template_create"),
    path("templates/<int:pk>/", views.template_detail, name="template_detail"),
    path("templates/<int:pk>/delete/", views.template_delete, name="template_delete"),
    path("templates/<int:pk>/items/<int:item_id>/delete/", views.template_item_delete,name="template_item_delete"),
    path("templates/<int:pk>/start/", views.start_session, name="start_session"),
    path("sessions/<int:pk>/", views.session_detail, name="session_detail"),
]

