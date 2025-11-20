from django import forms
from .models import Run
import re

class ManualRunForm(forms.ModelForm):
    start_date = forms.DateTimeField(
        label='Date et heure de début',
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-control'
        }),
        help_text='Quand as-tu commencé cette sortie ? Ex: 2025-11-20 08:30',
        input_formats=['%Y-%m-%dT%H:%M']
    )
    
    moving_time = forms.CharField(
        label='Temps en mouvement',
        help_text='Ex: "45:30" (45min 30s), "1:30:00" (1h 30min), "30" (30 secondes)',
        required=True
    )
    
    elapsed_time = forms.CharField(
        label='Temps total',
        help_text='Ex: "47:15" (47min 15s), "1:32:00" (1h 32min), "35" (35 secondes)',
        required=True
    )
    
    elevation_gain_m = forms.FloatField(
        label='Dénivelé positif (mètres)',
        required=False,
        initial=0,
        help_text='Laisser à 0 si terrain plat'
    )
    
    class Meta:
        model = Run
        fields = [
            'name', 'start_date', 'distance_m', 'calories_burned'
        ]
        labels = {
            'name': 'Nom de la sortie',
            'distance_m': 'Distance (mètres)',
            'calories_burned': 'Calories brûlées (kcal)',
        }
        help_texts = {
            'distance_m': 'Ex: 5000 pour 5 km',
            'calories_burned': 'Optionnel - sera calculé automatiquement si non renseigné',
        }
    
    def parse_time(self, time_str):
        """
        Parse un temps au format flexible:
        - "30" -> 30 secondes
        - "5:30" -> 5 minutes 30 secondes
        - "1:30:00" -> 1 heure 30 minutes
        - "1h30m" -> 1 heure 30 minutes
        - "45m30s" -> 45 minutes 30 secondes
        """
        time_str = time_str.strip()
        
        # Format: 1h30m45s ou 1h30m ou 30m ou 45s
        if 'h' in time_str or 'm' in time_str or 's' in time_str:
            hours = minutes = seconds = 0
            
            h_match = re.search(r'(\d+)h', time_str, re.IGNORECASE)
            m_match = re.search(r'(\d+)m', time_str, re.IGNORECASE)
            s_match = re.search(r'(\d+)s', time_str, re.IGNORECASE)
            
            if h_match:
                hours = int(h_match.group(1))
            if m_match:
                minutes = int(m_match.group(1))
            if s_match:
                seconds = int(s_match.group(1))
            
            return hours * 3600 + minutes * 60 + seconds
        
        # Format: HH:MM:SS ou MM:SS ou juste secondes
        parts = time_str.split(':')
        
        if len(parts) == 1:
            # Juste des secondes
            return int(parts[0])
        elif len(parts) == 2:
            # MM:SS
            return int(parts[0]) * 60 + int(parts[1])
        elif len(parts) == 3:
            # HH:MM:SS
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
        
        raise forms.ValidationError("Format de temps non reconnu")
    
    def clean_moving_time(self):
        time_str = self.cleaned_data.get('moving_time')
        try:
            return self.parse_time(time_str)
        except (ValueError, AttributeError):
            raise forms.ValidationError(
                'Format invalide. Ex: "45:30", "1:30:00", "30m", "1h30m45s"'
            )
    
    def clean_elapsed_time(self):
        time_str = self.cleaned_data.get('elapsed_time')
        try:
            return self.parse_time(time_str)
        except (ValueError, AttributeError):
            raise forms.ValidationError(
                'Format invalide. Ex: "47:15", "1:32:00", "35m", "1h32m15s"'
            )
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.moving_time_s = self.cleaned_data['moving_time']
        instance.elapsed_time_s = self.cleaned_data['elapsed_time']
        
        if self.cleaned_data.get('elevation_gain_m') is not None:
            instance.elevation_gain_m = self.cleaned_data['elevation_gain_m']
        else:
            instance.elevation_gain_m = 0
        
        if commit:
            instance.save()
        return instance
