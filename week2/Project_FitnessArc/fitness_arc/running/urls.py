from django.urls import path
from . import views

app_name = "running"

urlpatterns = [
    path("", views.my_runs, name="my_runs"),
    path("strava/connect/", views.strava_connect, name="strava_connect"),
    path("strava/callback/", views.strava_callback, name="strava_callback"),
    path("garmin/connect/", views.garmin_connect, name="garmin_connect"),
    path("garmin/sync/", views.garmin_sync, name="garmin_sync"),
    path("manual/add/", views.manual_run_add, name="manual_run_add"),
]
