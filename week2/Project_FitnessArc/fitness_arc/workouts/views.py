from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from accounts.decorators import feature_required
from .models import Exercise, WorkoutTemplate, TemplateItem, WorkoutSession, SetLog, SportCategory
from django.contrib import messages
from django.db.models import Max
from .forms import TemplateItemForm
import json
from django.db.models import Max
from .models import WorkoutSession, SetLog, PR 

@feature_required('workouts')
def exercise_list(request):
    exercises = Exercise.objects.all().select_related('sport_category')
    
    # Only get categories that have exercises
    sport_categories = SportCategory.objects.filter(
        exercises__isnull=False
    ).distinct().order_by('order')
    
    # Filtres
    muscle = request.GET.get('muscle')
    equip = request.GET.get('equip')
    sport_cats = request.GET.getlist('sport_category')
    
    if muscle:
        exercises = exercises.filter(muscle_group=muscle)
    if equip:
        exercises = exercises.filter(equipment=equip)
    if sport_cats:
        exercises = exercises.filter(sport_category__id__in=sport_cats)
    
    # JSON pour Vue.js
    exercises_json = json.dumps([
        {
            'id': ex.id,
            'name': ex.name,
            'muscle_group': ex.muscle_group,
            'equipment': ex.equipment,
            'difficulty': ex.difficulty,
            'description': ex.description,
            'image': ex.image.name if ex.image else '',
            'sport_category': {
                'id': ex.sport_category.id,
                'name': ex.sport_category.name,
                'icon': ex.sport_category.icon
            } if ex.sport_category else None
        }
        for ex in exercises
    ])
    
    return render(request, 'workouts/exercise_list.html', {
        'exercises': exercises,
        'exercises_json': exercises_json,
        'sport_categories': sport_categories,
        'selected_sport_cats': [int(sc) for sc in sport_cats] if sport_cats else []
    })

@login_required
@feature_required('workouts')
def template_list(request):
    my_templates = WorkoutTemplate.objects.filter(owner=request.user, is_public=False)
    # User's default public templates (Push/Pull/Legs)
    public_templates = WorkoutTemplate.objects.filter(owner=request.user, is_public=True)
    
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
    
    # Check if user has permission to use this template
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
        
        # Determine if it's a time-based or reps-based exercise
        exercise_id = int(request.POST["exercise_id"])
        exercise = Exercise.objects.get(id=exercise_id)
        
        set_log_data = {
            "session": sess,
            "exercise_id": exercise_id,
            "set_number": int(request.POST["set_number"]),
            "weight_kg": request.POST["weight_kg"],
        }
        
        if exercise.is_time_based:
            # Time-based exercise
            duration_seconds = request.POST.get("duration_seconds")
            if duration_seconds:
                set_log_data["duration_seconds"] = int(duration_seconds)
        else:
            # Reps-based exercise
            reps = request.POST.get("reps")
            if reps:
                set_log_data["reps"] = int(reps)
        
        SetLog.objects.create(**set_log_data)
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

def update_prs_for_session(session):
    """
    Met à jour les PR (records) de l'utilisateur pour tous les exercices
    présents dans cette séance.
    """
    user = session.owner

    # All exercises used in this session
    exercise_ids = (
        session.set_logs
        .values_list('exercise_id', flat=True)
        .distinct()
    )

    for ex_id in exercise_ids:

        # ----- PR de CHARGE MAX (max_weight) -----
        agg_weight = (
            SetLog.objects
            .filter(session__owner=user, exercise_id=ex_id)
            .aggregate(max_w=Max("weight_kg"))
        )
        max_weight = agg_weight["max_w"]

        if max_weight is not None:
            pr, created = PR.objects.get_or_create(
                owner=user,
                exercise_id=ex_id,
                metric="max_weight",
                defaults={"value": max_weight},
            )
            if not created and max_weight > pr.value:
                pr.value = max_weight
                pr.save()

        # ----- PR de REPS MAX (max_reps) -----
        agg_reps = (
            SetLog.objects
            .filter(session__owner=user, exercise_id=ex_id)
            .aggregate(max_r=Max("reps"))
        )
        max_reps = agg_reps["max_r"]

        if max_reps is not None:
            pr, created = PR.objects.get_or_create(
                owner=user,
                exercise_id=ex_id,
                metric="max_reps",
                defaults={"value": max_reps},
            )
            if not created and max_reps > pr.value:
                pr.value = max_reps
                pr.save()

@login_required
def complete_session(request, pk):
    """Terminer une séance et afficher le récapitulatif"""
    sess = get_object_or_404(WorkoutSession, pk=pk, owner=request.user)
    
    if request.method == "POST":
        duration_minutes = request.POST.get("duration_minutes", 0)
        try:
            duration_minutes = int(duration_minutes)
        except ValueError:
            duration_minutes = 0
        
        # If session lasted less than 1 minute and has no logs, cancel it
        if duration_minutes == 0 and sess.set_logs.count() == 0:
            sess.delete()
            messages.info(request, "Séance annulée (aucune série effectuée).")
            return redirect("workouts:template_list")
        
        # Otherwise, finish the session normally
        sess.duration_minutes = max(1, duration_minutes)  # Minimum 1 minute
        sess.is_completed = True
        sess.save()
        update_prs_for_session(sess)
        messages.success(request, f"Séance terminée ! Durée : {sess.duration_minutes} min | Calories : {sess.estimated_calories_burned} kcal")
        return redirect("workouts:session_summary", pk=sess.pk)
    
    return redirect("workouts:session_detail", pk=pk)

@login_required
def session_summary(request, pk):
    """Afficher le récapitulatif d'une séance terminée"""
    sess = get_object_or_404(WorkoutSession, pk=pk, owner=request.user)
    
    # Calculer les statistiques
    total_sets = sess.set_logs.count()
    total_reps = sum(log.reps if log.reps else 0 for log in sess.set_logs.all())
    
    # Grouper les logs par exercice
    exercises_data = {}
    for log in sess.set_logs.select_related('exercise'):
        ex_name = log.exercise.name
        if ex_name not in exercises_data:
            exercises_data[ex_name] = {
                'sets': 0,
                'total_reps': 0,
                'total_duration': 0,
                'total_volume': 0,
                'is_time_based': log.exercise.is_time_based,
                'display_duration': ''
            }
        exercises_data[ex_name]['sets'] += 1
        if log.reps:
            exercises_data[ex_name]['total_reps'] += log.reps
        if log.duration_seconds:
            exercises_data[ex_name]['total_duration'] += log.duration_seconds
        exercises_data[ex_name]['total_volume'] += log.volume
    
    # Format total duration for display
    for ex_name, data in exercises_data.items():
        if data['is_time_based'] and data['total_duration'] > 0:
            mins, secs = divmod(data['total_duration'], 60)
            if mins > 0:
                data['display_duration'] = f"{mins}:{secs:02d}"
            else:
                data['display_duration'] = f"{secs}s"
    
    context = {
        'session': sess,
        'total_sets': total_sets,
        'total_reps': total_reps,
        'exercises_data': exercises_data,
    }
    return render(request, "workouts/session_summary.html", context)

@login_required
def session_delete(request, pk):
    """Supprimer une séance terminée"""
    sess = get_object_or_404(WorkoutSession, pk=pk, owner=request.user)
    
    if request.method == "POST":
        # Get all affected exercises before deletion
        exercise_ids = set(sess.set_logs.values_list('exercise_id', flat=True))
        
        # Delete session (SetLogs will be deleted by cascade)
        sess.delete()
        
        # Recalculate PRs for all affected exercises
        for ex_id in exercise_ids:
            # Recalculer max_weight
            agg_weight = SetLog.objects.filter(
                session__owner=request.user,
                exercise_id=ex_id
            ).aggregate(max_w=Max("weight_kg"))
            max_weight = agg_weight["max_w"]
            
            if max_weight is not None:
                pr, _ = PR.objects.get_or_create(
                    owner=request.user,
                    exercise_id=ex_id,
                    metric="max_weight",
                    defaults={"value": max_weight}
                )
                pr.value = max_weight
                pr.save()
            else:
                # Plus aucun log pour cet exercice, supprimer le PR
                PR.objects.filter(
                    owner=request.user,
                    exercise_id=ex_id,
                    metric="max_weight"
                ).delete()
            
            # Recalculer max_reps
            agg_reps = SetLog.objects.filter(
                session__owner=request.user,
                exercise_id=ex_id
            ).aggregate(max_r=Max("reps"))
            max_reps = agg_reps["max_r"]
            
            if max_reps is not None:
                pr, _ = PR.objects.get_or_create(
                    owner=request.user,
                    exercise_id=ex_id,
                    metric="max_reps",
                    defaults={"value": max_reps}
                )
                pr.value = max_reps
                pr.save()
            else:
                PR.objects.filter(
                    owner=request.user,
                    exercise_id=ex_id,
                    metric="max_reps"
                ).delete()
        
        messages.success(request, "Séance supprimée. Les statistiques ont été mises à jour.")
        return redirect("dashboard:index")
    
    return redirect("workouts:session_summary", pk=pk)

@login_required
def set_log_delete(request, session_pk, log_pk):
    """Supprimer un log de série individuel"""
    sess = get_object_or_404(WorkoutSession, pk=session_pk, owner=request.user)
    log = get_object_or_404(SetLog, pk=log_pk, session=sess)
    
    if request.method == "POST":
        exercise_id = log.exercise_id
        log.delete()
        
        # Recalculer les PRs pour cet exercice
        agg_weight = SetLog.objects.filter(
            session__owner=request.user,
            exercise_id=exercise_id
        ).aggregate(max_w=Max("weight_kg"))
        max_weight = agg_weight["max_w"]
        
        if max_weight is not None:
            pr, _ = PR.objects.get_or_create(
                owner=request.user,
                exercise_id=exercise_id,
                metric="max_weight",
                defaults={"value": max_weight}
            )
            pr.value = max_weight
            pr.save()
        else:
            PR.objects.filter(
                owner=request.user,
                exercise_id=exercise_id,
                metric="max_weight"
            ).delete()
        
        agg_reps = SetLog.objects.filter(
            session__owner=request.user,
            exercise_id=exercise_id
        ).aggregate(max_r=Max("reps"))
        max_reps = agg_reps["max_r"]
        
        if max_reps is not None:
            pr, _ = PR.objects.get_or_create(
                owner=request.user,
                exercise_id=exercise_id,
                metric="max_reps",
                defaults={"value": max_reps}
            )
            pr.value = max_reps
            pr.save()
        else:
            PR.objects.filter(
                owner=request.user,
                exercise_id=exercise_id,
                metric="max_reps"
            ).delete()
        
        messages.success(request, "Série supprimée.")
    
    return redirect("workouts:session_detail", pk=session_pk)