from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Exercise, WorkoutTemplate, TemplateItem, WorkoutSession, SetLog
from django.contrib import messages
from django.db.models import Max
from .forms import TemplateItemForm

def exercise_list(request):
    qs = Exercise.objects.all()
    m = request.GET.get("muscle")
    e = request.GET.get("equip")
    
    if m:
        qs = qs.filter(muscle_group=m)
    if e:
        qs = qs.filter(equipment=e)
    
    return render(request, "workouts/exercise_list.html", {"exercises": qs})

@login_required
def template_list(request):
    templates = WorkoutTemplate.objects.filter(owner=request.user)
    return render(request, "workouts/template_list.html", {"templates": templates})

@login_required
def template_create(request):
    if request.method == "POST":
        name = request.POST.get("name") or "Mon template"
        tpl = WorkoutTemplate.objects.create(owner=request.user, name=name)
        return redirect("workouts:template_list")  # ← Ajout namespace
    return render(request, "workouts/template_form.html")

@login_required
def start_session(request, pk):
    tpl = get_object_or_404(WorkoutTemplate, pk=pk, owner=request.user)
    sess = WorkoutSession.objects.create(owner=request.user, from_template=tpl)
    return redirect("workouts:session_detail", pk=sess.pk)  # ← Ajout namespace

@login_required
def session_detail(request, pk):
    sess = get_object_or_404(WorkoutSession, pk=pk, owner=request.user)
    if request.method == "POST":
        SetLog.objects.create(
            session=sess,
            exercise_id=int(request.POST["exercise_id"]),
            set_number=int(request.POST["set_number"]),
            reps=int(request.POST["reps"]),
            weight_kg=request.POST["weight_kg"],
        )
        return redirect("workouts:session_detail", pk=pk)  # ← Ajout namespace
    return render(request, "workouts/session_detail.html", {"session": sess})

#Ajouts exercices template
@login_required
def template_detail(request, pk):
    tpl = get_object_or_404(WorkoutTemplate, pk=pk, owner=request.user)

    if request.method == "POST":
        form = TemplateItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.template = tpl
            last = tpl.items.aggregate(m=Max("order"))["m"] or 0
            item.order = last + 1
            item.save()
            messages.success(request, "Exercice ajouté au template.")
            return redirect("workouts:template_detail", pk=tpl.pk)  # ← Ajouter namespace
    else:
        form = TemplateItemForm()

    ctx = {"template": tpl, "form": form, "items": tpl.items.select_related("exercise")}
    return render(request, "workouts/template_detail.html", ctx)

@login_required
def template_item_delete(request, pk, item_id):
    tpl = get_object_or_404(WorkoutTemplate, pk=pk, owner=request.user)
    item = get_object_or_404(TemplateItem, pk=item_id, template=tpl)
    if request.method == "POST":
        item.delete()
        messages.success(request, "Item supprimé.")
    return redirect("workouts:template_detail", pk=tpl.pk)  # ← Ajouter namespace