from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Exercise, WorkoutTemplate, TemplateItem, WorkoutSession, SetLog
from django.contrib import messages
from django.db.models import Max
from .forms import TemplateItemForm
import json

def exercise_list(request):
    exercises = Exercise.objects.all()
    
    # Filtres
    muscle = request.GET.get('muscle')
    equip = request.GET.get('equip')
    if muscle:
        exercises = exercises.filter(muscle_group=muscle)
    if equip:
        exercises = exercises.filter(equipment=equip)
    
    # JSON pour Vue.js
    exercises_json = json.dumps([
        {
            'id': ex.id,
            'name': ex.name,
            'muscle_group': ex.muscle_group,
            'equipment': ex.equipment,
            'difficulty': ex.difficulty,
            'description': ex.description,
            'image': ex.image.name if ex.image else ''
        }
        for ex in exercises
    ])
    
    return render(request, 'workouts/exercise_list.html', {
        'exercises': exercises,
        'exercises_json': exercises_json  # ← Assurez-vous que c'est bien passé
    })

@login_required
def template_list(request):
    my_templates = WorkoutTemplate.objects.filter(owner=request.user, is_public=False)
    public_templates = WorkoutTemplate.objects.filter(is_public=True)
    
    return render(request, "workouts/template_list.html", {
        "my_templates": my_templates,
        "public_templates": public_templates
    })

@login_required
def template_create(request):
    if request.method == "POST":
        name = request.POST.get("name") or "Mon template"
        tpl = WorkoutTemplate.objects.create(owner=request.user, name=name)
        return redirect("workouts:template_list")  # ← Ajout namespace
    return render(request, "workouts/template_form.html")

@login_required
def start_session(request, pk):
    tpl = get_object_or_404(WorkoutTemplate, pk=pk)
    
    # Vérifier que l'utilisateur a le droit d'utiliser ce template
    if not (tpl.owner == request.user or tpl.is_public):
        messages.error(request, "Vous n'avez pas accès à ce template.")
        return redirect("workouts:template_list")
    
    sess = WorkoutSession.objects.create(owner=request.user, from_template=tpl)
    return redirect("workouts:session_detail", pk=sess.pk)  # ← Ajout namespace

@login_required
def session_detail(request, pk):
    sess = get_object_or_404(WorkoutSession, pk=pk, owner=request.user)
    if request.method == "POST":
        duration_minutes = request.POST.get("duration_minutes", 0)
        try:
            sess.duration_minutes = int(duration_minutes)
            sess.save()
        except ValueError:
            pass
        
        SetLog.objects.create(
            session=sess,
            exercise_id=int(request.POST["exercise_id"]),
            set_number=int(request.POST["set_number"]),
            reps=int(request.POST["reps"]),
            weight_kg=request.POST["weight_kg"],
        )
        return redirect("workouts:session_detail", pk=pk)
    return render(request, "workouts/session_detail.html", {"session": sess})

#Ajouts exercices template
@login_required
def template_detail(request, pk):
    tpl = get_object_or_404(WorkoutTemplate, pk=pk)
    is_owner = tpl.owner == request.user
    
    if request.method == "POST":
        if not is_owner:
            messages.error(request, "Vous ne pouvez pas modifier un template public.")
            return redirect("workouts:template_detail", pk=tpl.pk)
        
        form = TemplateItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.template = tpl
            last = tpl.items.aggregate(m=Max("order"))["m"] or 0
            item.order = last + 1
            item.save()
            messages.success(request, "Exercice ajouté au template.")
            return redirect("workouts:template_detail", pk=tpl.pk)
    else:
        form = TemplateItemForm()

    ctx = {
        "template": tpl,
        "form": form,
        "items": tpl.items.select_related("exercise"),
        "is_owner": is_owner
    }
    return render(request, "workouts/template_detail.html", ctx)

@login_required
def template_item_delete(request, pk, item_id):
    tpl = get_object_or_404(WorkoutTemplate, pk=pk, owner=request.user)
    item = get_object_or_404(TemplateItem, pk=item_id, template=tpl)
    if request.method == "POST":
        item.delete()
        messages.success(request, "Item supprimé.")
    return redirect("workouts:template_detail", pk=tpl.pk)

@login_required
def template_delete(request, pk):
    """Supprimer un template complet"""
    tpl = get_object_or_404(WorkoutTemplate, pk=pk, owner=request.user)
    if request.method == "POST":
        template_name = tpl.name
        tpl.delete()
        messages.success(request, f"Template '{template_name}' supprimé avec succès.")
        return redirect("workouts:template_list")
    return render(request, "workouts/template_confirm_delete.html", {"template": tpl})

@login_required
def complete_session(request, pk):
    """Terminer une séance et afficher le récapitulatif"""
    sess = get_object_or_404(WorkoutSession, pk=pk, owner=request.user)
    
    if request.method == "POST":
        duration_minutes = request.POST.get("duration_minutes", 0)
        try:
            sess.duration_minutes = int(duration_minutes)
        except ValueError:
            pass
        
        # Si la séance dure moins de 30 secondes (0 minutes), on l'annule (supprime)
        if sess.duration_minutes == 0 and sess.set_logs.count() == 0:
            sess.delete()
            messages.info(request, "Séance annulée.")
            return redirect("workouts:template_list")
        
        sess.is_completed = True
        sess.save()
        messages.success(request, f"Séance terminée ! Durée : {sess.duration_minutes} min | Calories : {sess.estimated_calories_burned} kcal")
        return redirect("workouts:session_summary", pk=sess.pk)
    
    return redirect("workouts:session_detail", pk=pk)

@login_required
def session_summary(request, pk):
    """Afficher le récapitulatif d'une séance terminée"""
    sess = get_object_or_404(WorkoutSession, pk=pk, owner=request.user)
    
    # Calculer les statistiques
    total_sets = sess.set_logs.count()
    total_reps = sum(log.reps for log in sess.set_logs.all())
    
    # Grouper les logs par exercice
    exercises_data = {}
    for log in sess.set_logs.select_related('exercise'):
        ex_name = log.exercise.name
        if ex_name not in exercises_data:
            exercises_data[ex_name] = {'sets': 0, 'total_reps': 0, 'total_volume': 0}
        exercises_data[ex_name]['sets'] += 1
        exercises_data[ex_name]['total_reps'] += log.reps
        exercises_data[ex_name]['total_volume'] += log.volume
    
    context = {
        'session': sess,
        'total_sets': total_sets,
        'total_reps': total_reps,
        'exercises_data': exercises_data,
    }
    return render(request, "workouts/session_summary.html", context)