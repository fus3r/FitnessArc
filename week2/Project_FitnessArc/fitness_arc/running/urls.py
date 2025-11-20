from django.urls import path
from . import views

app_name = "running"

urlpatterns = [
    path("", views.my_runs, name="my_runs"),
    path("strava/connect/", views.strava_connect, name="strava_connect"),
    path("strava/callback/", views.strava_callback, name="strava_callback"),
]
