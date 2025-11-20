from django.db import models
from django.conf import settings


class StravaAuth(models.Model):
    """
    Stocke l'autorisation Strava d'un utilisateur :
    - access_token / refresh_token
    - date d'expiration du token
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="strava_auth",
    )
    athlete_id = models.BigIntegerField(null=True, blank=True)
    access_token = models.CharField(max_length=255)
    refresh_token = models.CharField(max_length=255)
    token_expires_at = models.DateTimeField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Strava auth de {self.user.username}"


class Run(models.Model):
    """
    Une sortie running (activité Strava type 'Run').
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="runs",
    )
    strava_id = models.BigIntegerField(unique=True)  

    name = models.CharField(max_length=255)
    distance_m = models.FloatField()          
    moving_time_s = models.IntegerField()     
    elapsed_time_s = models.IntegerField()    
    start_date = models.DateTimeField()

    average_speed = models.FloatField(
        null=True,
        blank=True,
        help_text="Vitesse moyenne en m/s",
    )
    average_pace_s_per_km = models.FloatField(
        null=True,
        blank=True,
        help_text="Allure moyenne en secondes / km",
    )
    elevation_gain_m = models.FloatField(
        null=True,
        blank=True,
        help_text="D+ en mètres",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.name} ({self.distance_km:.1f} km)"

    @property
    def distance_km(self):
        return self.distance_m / 1000 if self.distance_m else 0

    @property
    def moving_time_hms(self):
        """
        Retourne une durée lisible, ex: '42m13s' ou '1h03m20s'
        """
        s = self.moving_time_s or 0
        h = s // 3600
        m = (s % 3600) // 60
        sec = s % 60
        if h:
            return f"{h}h{m:02d}m{sec:02d}s"
        return f"{m}m{sec:02d}s"

    @property
    def pace_min_per_km(self):
        """
        Retourne une allure style '4:35 /km'
        """
        if not self.average_pace_s_per_km:
            return None
        total_sec = int(self.average_pace_s_per_km)
        minutes = total_sec // 60
        seconds = total_sec % 60
        return f"{minutes}:{seconds:02d} /km"
