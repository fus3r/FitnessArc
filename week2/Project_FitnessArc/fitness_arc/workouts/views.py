from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Exercise, WorkoutTemplate, TemplateItem, WorkoutSession, SetLog

def exercise_list(request):
    qs = Exercise.objects.all()
    m = request.GET.get("muscle"); e = request.GET.get("equip")
    if m: qs = qs.filter(muscle_group=m)
    if e: qs = qs.filter(equipment=e)
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
        return redirect("template_list")
    return render(request, "workouts/template_form.html")

@login_required
def start_session(request, pk):
    tpl = get_object_or_404(WorkoutTemplate, pk=pk, owner=request.user)
    sess = WorkoutSession.objects.create(owner=request.user, from_template=tpl)
    return redirect("session_detail", pk=sess.pk)

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
        return redirect("session_detail", pk=pk)
    return render(request, "workouts/session_detail.html", {"session": sess})
