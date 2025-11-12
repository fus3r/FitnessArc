# TODO - Fitness Arc (Semaine 2)

## 🚨 Priorité Immédiate (Jour 1 - Matin)

### Stratégie Git & Setup
- [x] **RÉUNION ÉQUIPE (30 min)** : valider stratégie branches feature/app
- [x] **Setup Django de base sur `main`**
  - [x] `django-admin startproject fitness_arc`
  - [x] Créer 5 apps vides : `accounts`, `workouts`, `nutrition`, `dashboard`, `common`
  - [x] Configurer `INSTALLED_APPS` dans `settings.py`
  - [x] Commit initial : `"Setup: Django project + apps structure"`
  - [x] Push sur `main`

- [ ] **Chaque membre crée SA branche**
  - [x] Personne A : `git checkout -b feature/accounts`
  - [x] Personne B : `git checkout -b feature/workouts`
  - [x] Personne C : rejoint `feature/workouts` (ou `feature/workouts-sessions`)
  - [ ] Personne D : `git checkout -b feature/nutrition`
  - [ ] Personne E : `git checkout -b feature/dashboard`

### Documentation
- [ ] Dessiner wireframes (main, 5 pages clés) → commit images dans `WorkingDocs/wireframes/`
- [x] Page d'accueil (/) avec navigation vers toutes les apps ✅
- [ ] Créer `requirements.txt` (Django 5.x, pytest-django, flake8, black)
- [ ] Rédiger conventions de code (fichier `CONVENTIONS.md`)

---

## 📋 Backlog par Jour

### Jour 1 (Lundi) - Fondations

#### Modèles & Migrations
- [x] **App `accounts`** (Personne A)
  - [x] Modèle `Profile` (height_cm, weight_kg, goal)
  - [x] Migration
  - [x] Admin : enregistrer Profile
  - [x] Test : créer profile via signal User.post_save
  - [x] **MERGÉ DANS MAIN** ✅

- [x] **App `workouts`** (Personne B)
  - [x] Modèles : `Exercise`, `WorkoutTemplate`, `TemplateItem`, `WorkoutSession`, `SetLog`, `PR`
  - [x] Migrations appliquées (+ ImageField pour images locales)
  - [x] Admin : inline TemplateItems + SetLogs, filtres Exercise
  - [x] Fixtures : `exercices.json` (10 exercices avec images) ✅
  - [x] Fixtures : `templates_public.json` (3 templates Push/Pull/Legs publics) ✅
  - [x] Images : 2 locales (barbell_bench_press.webp, squat.webp) + 8 URLs ExRx.net ✅
  - [x] Tests : créer template avec 3 items ✅
  - [x] Views : exercise_list (filtres muscle/equip auto), template CRUD (list avec publics, create, detail, delete), session logging ✅
  - [x] Templates : exercise_list.html, template_list.html (avec section publics), template_detail.html (lecture seule pour publics), template_form.html, template_confirm_delete.html, session_detail.html ✅
  - [x] URLs : /workouts/exercises/, /workouts/templates/, /workouts/templates/<id>/delete/, /workouts/sessions/ (avec namespace workouts:) ✅
  - [x] Base template créé dans templates/base.html avec navigation ✅
  - [x] Configuration MEDIA : settings.py + urls.py + context_processors.media ✅
  - [x] Forms : TemplateItemForm pour ajouter exercices aux templates ✅
  - [x] Fonctionnalité : Suppression de templates avec confirmation ✅
  - [x] Fonctionnalité : Chronomètre auto-start avec Pause/Reprendre + persistance localStorage ✅
  - [x] Fonctionnalité : Templates publics préfaits (Push/Pull/Legs) accessibles à tous ✅
  - [ ] **PRÊT POUR MR sur GitLab** (après dernier push)

- [x] **App `nutrition`** (Personne D)
  - [x] Modèles : `Food`, `FoodLog` ✅
  - [x] Migrations créées et appliquées ✅
  - [x] Admin : Food + FoodLog avec filtres date/meal_type ✅
  - [x] Views : nutrition_today (affiche logs + totaux) ✅
  - [x] Forms : FoodLogForm ✅
  - [x] Template : nutrition/templates/nutrition/nutrition_today.html ✅
  - [x] URLs : /nutrition/today/ ✅
  - [x] Fixtures : `foods.json` (5 aliments de base) ✅
  - [x] Page fonctionnelle : ajout de logs + calcul totaux ✅
  - [ ] Tests : ajouter food log, calculer totaux jour
  - [ ] **PRÊT POUR MR** (après tests)

---

### Jour 2 (Mardi) - Vues CRUD

- [x] **App `accounts`** (Personne A)
  - [x] Views : signup, login (django.contrib.auth), profile_edit, password_change ✅
  - [x] Templates : `signup.html`, `login.html`, `profile.html`, `profile_edit.html`, `password_change.html` ✅
  - [x] URLs : `/accounts/signup/`, `/accounts/login/`, `/accounts/profile/`, `/accounts/password-change/` ✅
  - [x] Test : signup crée profile, edit profile sauvegarde ✅
  - [x] Fonctionnalité : Changement de mot de passe depuis le profil ✅
  - [ ] **PRÊT POUR MR** (après dernier push)

- [ ] **App `workouts`** (Personne B)
  - [ ] View : `exercise_list` (filtres muscle_group, equipment)
  - [ ] Template : `exercise_list.html` (table + filtres)
  - [ ] URL : `/workouts/exercises/`
  - [ ] Test : filtrer par muscle_group

- [ ] **App `workouts`** (Personne C - démarre après merge modèles B)
  - [ ] Modèles : `WorkoutSession`, `SetLog`, `PR`
  - [ ] Migrations
  - [ ] Admin : inline SetLogs dans Session

---

### Jour 3 (Mercredi) - Features Métier

- [ ] **App `workouts`** (Personne B)
  - [ ] Views : templates CRUD (list, create, detail, update, delete)
  - [ ] View : `start_session` (depuis template) → crée WorkoutSession
  - [ ] Templates : `template_list.html`, `template_detail.html`, `template_form.html`
  - [ ] URLs : `/workouts/templates/`, `/workouts/templates/<id>/`, `/workouts/templates/<id>/start/`
  - [ ] Test : créer template, démarrer session depuis template

- [ ] **App `workouts`** (Personne C)
  - [ ] View : `session_detail` (log séries en AJAX ou form simple)
  - [ ] Template : `session_detail.html` (stack séries, inputs reps/poids/RPE)
  - [ ] URL : `/workouts/sessions/<id>/`
  - [ ] JS : raccourcis clavier (Enter=valider série, Tab=passer champ)
  - [ ] Test : ajouter 3 SetLogs, vérifier volume session

- [ ] **App `nutrition`** (Personne D)
  - [ ] View : `nutrition_today` (affiche FoodLogs du jour + totaux)
  - [ ] View : `add_food_log` (autocomplete Food, input grammes)
  - [ ] Template : `nutrition_today.html` (liste logs + form ajout + totaux)
  - [ ] URL : `/nutrition/today/`
  - [ ] Test : ajouter 3 aliments, vérifier totaux kcal/P/C/F

---

### Jour 4 (Jeudi) - Dashboard & Agrégations

- [ ] **App `dashboard`** (Personne E - démarre après merges workouts/nutrition)
  - [ ] Service : `calculate_weekly_volume(user)` (somme weight*reps 7 derniers jours)
  - [ ] Service : `get_recent_prs(user, limit=5)`
  - [ ] Service : `get_today_nutrition_summary(user)`
  - [ ] View : `dashboard_index` (3 cards : volume, PRs, kcal)
  - [ ] Template : `dashboard/index.html`
  - [ ] URL : `/` (racine)
  - [ ] Test : dashboard affiche volume correct

- [ ] **App `workouts`** (Personne C)
  - [ ] Signal : `post_save` sur `SetLog` → détecter PR (charge max) → créer `PR`
  - [ ] Test : série avec poids > ancien max crée PR

- [ ] **Polish général**
  - [ ] Base template : `templates/base.html` (navbar, messages, footer)
  - [ ] CSS : Bootstrap 5 ou Tailwind (décision équipe)
  - [ ] Messages flash : success/error toasts

---

### Jour 5 (Vendredi) - Tests & Démo

- [ ] **Tests finaux (TOUS)**
  - [ ] Couverture ≥70% par app
  - [ ] Tests d'intégration : scénario complet (signup → template → session → dashboard)

- [ ] **Documentation**
  - [ ] `README.md` : commandes setup, fixtures, tests, démo
  - [ ] `DEMO.md` : script de démo (étapes + captures d'écran)

- [ ] **Bonus (si temps)**
  - [ ] Export .ics d'une séance prévue
  - [ ] Favoris exercices (M2M User ↔ Exercise)
  - [ ] Import CSV aliments
  - [ ] Graphique Chart.js volume 4 semaines

---

## 🔄 Rituels Quotidiens

### Matin (9h)
- [ ] Standup 15 min : hier/aujourd'hui/blocages
- [ ] Pull `main` + rebase branch feature

### Soir (17h)
- [ ] Commit + push branche feature
- [ ] Update TOTO.md (cocher fait, ajouter imprévu)
- [ ] MR si feature complète (review demain matin)

---

## 📝 Conventions de Commits

### 2. Tester l'Ajout d'un Log

1. Visite **http://127.0.0.1:8000/nutrition/today/**
2. Sélectionne un aliment (ex: Poulet)
3. Entre 150g
4. Choisis "Déjeuner"
5. Clique "Ajouter"
6. Les totaux devraient se mettre à jour automatiquement !

---

## 📝 Mise à Jour du TODO

## ✅ Mise à Jour du TODO