from django import forms
from .models import TemplateItem, Exercise

class TemplateItemForm(forms.ModelForm):
    class Meta:
        model = TemplateItem
        fields = ["exercise", "sets", "reps", "rest_seconds"]
        widgets = {
            "sets": forms.NumberInput(attrs={"min": 1}),
            "reps": forms.NumberInput(attrs={"min": 1}),
            "rest_seconds": forms.NumberInput(attrs={"min": 0}),
        }

    def __init__(self, *args, **kwargs):
        # on pourrait filtrer les exercices plus tard (tags, niveau, etc.)
        super().__init__(*args, **kwargs)
        self.fields["exercise"].queryset = Exercise.objects.all().order_by("name")
