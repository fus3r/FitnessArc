from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.contrib import messages
from datetime import datetime, timezone as dt_timezone
import requests
from django.conf import settings
from django.utils import timezone
from urllib.parse import urlencode

from accounts.decorators import feature_required
from .forms_manual import ManualRunForm
from .models import Run, StravaAuth

@login_required
@feature_required('running')
def manual_run_add(request):
    """
    Permet à l'utilisateur d'ajouter une sortie manuelle si son profil est configuré sur 'manual'.
    """
    if getattr(request.user.profile, "running_data_source", "manual") != "manual":
        messages.error(request, "Tu dois choisir 'Entrer manuellement' dans ton profil pour ajouter une sortie manuelle.")
        return redirect("running:my_runs")

    if request.method == "POST":
        form = ManualRunForm(request.POST)
        if form.is_valid():
            run = form.save(commit=False)
            run.user = request.user
            run.source = "manual"
            run.save()
            messages.success(request, "Sortie ajoutée avec succès !")
            return redirect("running:my_runs")
    else:
        form = ManualRunForm()
    return render(request, "running/manual_run_form.html", {"form": form})

from datetime import datetime, timezone as dt_timezone
import requests
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone
from urllib.parse import urlencode


from .models import Run, StravaAuth


@login_required
@feature_required('running')
def my_runs(request):
    """
    Page principale : liste des runs de l'utilisateur.
    Affiche le bon module selon le choix de l'utilisateur (manuel, Strava, Garmin).
    """
    runs = Run.objects.filter(user=request.user).order_by("-start_date")
    strava_connected = StravaAuth.objects.filter(user=request.user).exists()
    try:
        garmin_connected = hasattr(request.user, "garmin_auth") and request.user.garmin_auth.is_active
    except Exception:
        garmin_connected = False

    running_data_source = getattr(request.user.profile, "running_data_source", "manual")

    context = {
        "runs": runs,
        "strava_connected": strava_connected,
        "garmin_connected": garmin_connected,
        "running_data_source": running_data_source,
    }
    return render(request, "running/run_list.html", context)


# --- Garmin Integration (stubs) ---
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse


from garminconnect import Garmin
from django import forms

class GarminLoginForm(forms.Form):
    email = forms.EmailField(label="Email Garmin Connect")
    password = forms.CharField(widget=forms.PasswordInput, label="Mot de passe")

@login_required
@feature_required('running')
def garmin_connect(request):
    message = None
    if request.method == "POST":
        form = GarminLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            try:
                # Authentification Garmin
                client = Garmin(email, password)
                client.login()
                # Stocker le token dans la session (ou en base pour prod)
                request.session["garmin_email"] = email
                request.session["garmin_password"] = password
                request.session["garmin_authenticated"] = True
                return HttpResponseRedirect(reverse("running:my_runs"))
            except Exception as e:
                message = f"Erreur d'authentification Garmin: {e}"
    else:
        form = GarminLoginForm()
    return render(request, "running/garmin_connect.html", {"form": form, "message": message})

@login_required
@feature_required('running')
def garmin_sync(request):
    """
    Stub: Synchronisation Garmin (à remplacer par logique réelle)
    """
    return HttpResponse("Synchronisation Garmin à implémenter.")


@login_required
@feature_required('running')
def strava_connect(request):
    """
    Redirige l'utilisateur vers la page d'autorisation Strava.
    """
    client_id = settings.STRAVA_CLIENT_ID
    redirect_uri = settings.STRAVA_REDIRECT_URI

    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "activity:read_all",
        "approval_prompt": "auto",
    }
    auth_url = "https://www.strava.com/oauth/authorize?" + urlencode(params)
    return redirect(auth_url)


@login_required
@feature_required('running')
def strava_callback(request):
    """
    Strava redirige ici après l'autorisation.
    On reçoit un "code" qu'on échange contre des tokens,
    puis on importe les dernières activités running.
    """
    error = request.GET.get("error")
    if error:
        
        return redirect("running:my_runs")

    code = request.GET.get("code")
    if not code:
        return redirect("running:my_runs")

    
    token_url = "https://www.strava.com/oauth/token"
    data = {
        "client_id": settings.STRAVA_CLIENT_ID,
        "client_secret": settings.STRAVA_CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
    }
    resp = requests.post(token_url, data=data)
    resp.raise_for_status()
    token_data = resp.json()

    access_token = token_data["access_token"]
    refresh_token = token_data["refresh_token"]
    expires_at_epoch = token_data["expires_at"]
    athlete_id = token_data["athlete"]["id"]

    expires_at = datetime.fromtimestamp(token_data["expires_at"], tz=dt_timezone.utc)


    
    StravaAuth.objects.update_or_create(
        user=request.user,
        defaults={
            "athlete_id": athlete_id,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_expires_at": expires_at,
        },
    )

    
    activities_url = "https://www.strava.com/api/v3/athlete/activities"
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"per_page": 30, "page": 1}
    act_resp = requests.get(activities_url, headers=headers, params=params)
    act_resp.raise_for_status()
    activities = act_resp.json()

    
    for act in activities:
        if act.get("type") != "Run":
            continue

        strava_id = act["id"]
        name = act.get("name", "Sortie Strava")
        distance = act.get("distance", 0.0)  
        moving_time = act.get("moving_time", 0)
        elapsed_time = act.get("elapsed_time", moving_time)
        start_date_str = act.get("start_date")  
        start_date = datetime.fromisoformat(start_date_str.replace("Z", "+00:00"))

        elevation_gain = act.get("total_elevation_gain", 0.0)
        avg_speed = act.get("average_speed")  

        avg_pace_s_per_km = None
        if distance > 0 and moving_time > 0:
            
            avg_pace_s_per_km = moving_time / (distance / 1000)

        Run.objects.update_or_create(
            user=request.user,
            strava_id=strava_id,
            defaults={
                "name": name,
                "distance_m": distance,
                "moving_time_s": moving_time,
                "elapsed_time_s": elapsed_time,
                "start_date": start_date,
                "elevation_gain_m": elevation_gain,
                "average_speed": avg_speed,
                "average_pace_s_per_km": avg_pace_s_per_km,
            },
        )

    return redirect("running:my_runs")