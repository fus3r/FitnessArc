# FitnessArc - Plateforme de Suivi Fitness

**Projet CodingWeek 2025 - CentraleSupélec**

Application web complète de suivi fitness permettant la gestion d'entraînements, de nutrition, de courses à pied, avec système social (amis, messagerie, classements).

---

## 👥 Équipe de Développement

| Nom | Prénom | Email |
|-----|--------|-------|
| **DARWISH** | Riad | riad.darwish@student-cs.fr |
| **FLIPO** | Rémi | remi.sithisak@student-cs.fr |
| **KABBARA** | Issam | issam.kabbara@student-cs.fr |
| **FLAMENT** | Thomas | thomas.flament08@student-cs.fr |
| **TAJAN** | Sao | sao.tajan@student-cs.fr |

---

## 📋 Table des Matières

1. [Présentation du Projet](#-présentation-du-projet)
2. [Fonctionnalités](#-fonctionnalités)
3. [Installation et Configuration](#-installation-et-configuration)
4. [Structure du Code](#-structure-du-code)
5. [Modèle de Données](#-modèle-de-données)
6. [Jalons et Méthodologie](#-jalons-et-méthodologie)
7. [Répartition du Travail](#-répartition-du-travail)
8. [Utilisation de Git](#-utilisation-de-git)
9. [Utilisation de l'IA](#-utilisation-de-lia)
10. [Tests](#-tests)
11. [Déploiement](#-déploiement)

---

## 🎯 Présentation du Projet

**FitnessArc** est une application web Django complète permettant aux utilisateurs de suivre leurs activités physiques de manière holistique :

- **Workouts** : Création de programmes d'entraînement personnalisés, suivi de séances avec chronomètre, logging de séries et répétitions, tracking de PR (Personal Records)
- **Nutrition** : Tracking alimentaire quotidien, base de données d'aliments, calcul automatique des macronutriments et calories
- **Running** : Intégration avec Strava et Garmin pour synchroniser automatiquement les courses
- **Social** : Système d'amis, messagerie privée, classements (leaderboards) pour se motiver mutuellement
- **Dashboard** : Vue d'ensemble avec statistiques, graphiques de progression, streaks, analyse de consistance

### Système de Feature Flags

L'application intègre un système innovant de **feature toggles** permettant à chaque utilisateur d'activer/désactiver les modules selon ses besoins :
- Workouts (entraînements)
- Nutrition (alimentation)
- Running (course à pied)
- Leaderboard (classements)

---

## ✨ Fonctionnalités

### Comptes & Authentification
- Inscription et connexion sécurisées
- Profil utilisateur avec objectifs fitness (perte de poids, prise de muscle, maintien)
- Personnalisation des features activées
- Changement de mot de passe

### Workouts (Entraînements)
- **Base de données** : 150+ exercices pré-chargés avec images, classés par groupe musculaire et équipement
- **Templates publics** : Programmes Push/Pull/Legs accessibles à tous
- **Templates personnels** : Création de ses propres workouts avec sélection d'exercices
- **Logging de séances** : Chronomètre intégré avec pause/reprise, ajout de séries en temps réel
- **Exercices temps/reps** : Support des exercices à temps (planche, cardio) et à répétitions (squats, développé couché)
- **Calcul PR** : Détection automatique des records personnels
- **Récapitulatif** : Durée, volume total, calories brûlées après chaque séance

### Nutrition
- **Food logging** : Ajout d'aliments par repas (petit-déjeuner, déjeuner, dîner, collations)
- **Base alimentaire** : Aliments pré-enregistrés avec valeurs nutritionnelles
- **Calcul automatique** : Totaux journaliers de calories, protéines, glucides, lipides
- **Objectifs personnalisés** : Calcul des besoins selon profil et objectif
- **Recettes** : Création et partage de recettes avec calcul nutritionnel automatique

### Running
- **Intégration Strava** : OAuth2, synchronisation automatique des courses
- **Intégration Garmin** : Import des runs depuis Garmin Connect
- **Entrée manuelle** : Ajout de courses sans tracker externe
- **Statistiques** : Calcul automatique de l'allure, calories brûlées, distance totale

### Social
- **Système d'amis** : Recherche utilisateurs, demandes d'amitié, acceptation/rejet
- **Notifications** : Badge avec compteur de demandes en attente
- **Dashboard ami** : Consultation des statistiques de ses amis acceptés
- **Messagerie** : Conversations privées entre utilisateurs
- **Leaderboard** : Classements par période avec filtres (tous/amis uniquement)

### Dashboard
- **Vue d'ensemble** : Cartes statistiques (poids, workouts, calories, streak)
- **Graphiques** : Évolution du poids, répartition des macronutriments, consistance mensuelle
- **Streaks** : Suivi de la régularité (jours consécutifs avec activité)
- **Analyse** : Calcul de la consistance (% jours actifs dans le mois)

---

## 🚀 Installation et Configuration

### Prérequis
- Python 3.13+
- pip (gestionnaire de paquets Python)
- Virtualenv (recommandé)
- PostgreSQL (pour production) ou SQLite (développement)

### Installation Locale

1. **Cloner le dépôt**
   ```bash
   git clone https://gitlab-cw4.centralesupelec.fr/riad.darwish/webapp_by_team_5.git
   cd webapp_by_team_5
   ```

2. **Créer et activer l'environnement virtuel**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # Sur macOS/Linux
   # Ou sur Windows : .venv\Scripts\activate
   ```

3. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configuration de la base de données**
   
   Le projet utilise SQLite par défaut pour le développement. Pour production avec PostgreSQL :
   
   Créer un fichier `.env` dans `week2/Project_FitnessArc/fitness_arc/` :
   ```env
   DATABASE_URL=postgresql://user:password@localhost:5432/fitnessarc
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   ```

5. **Naviguer vers le projet principal**
   ```bash
   cd week2/Project_FitnessArc/fitness_arc
   ```

6. **Appliquer les migrations**
   ```bash
   python manage.py migrate
   ```

7. **Charger les données initiales**
   ```bash
   python manage.py loaddata fixtures/exercices.json
   python manage.py loaddata fixtures/foods.json
   python manage.py loaddata fixtures/demo_users.json  # Utilisateurs de démo (optionnel)
   ```

8. **Créer un superutilisateur**
   ```bash
   python manage.py createsuperuser
   ```

9. **Lancer le serveur de développement**
   ```bash
   python manage.py runserver
   ```

10. **Accéder à l'application**
    - Application : http://127.0.0.1:8000
    - Admin : http://127.0.0.1:8000/admin

---

## 📁 Structure du Code

### Architecture Générale

Le projet suit l'architecture **Django MVT** (Model-View-Template) avec une séparation claire par applications fonctionnelles :

```
webapp_by_team_5/
├── week1/                          # Projet Semaine 1 (Comptoir Local Saclay - archive)
│   └── saclay/
├── week2/                          # Projet Semaine 2 (FitnessArc - projet principal)
│   └── Project_FitnessArc/
│       ├── fitness_arc/            # Racine du projet Django
│       │   ├── manage.py
│       │   ├── db.sqlite3
│       │   ├── fitness_arc/        # Configuration projet
│       │   │   ├── settings.py     # Configuration Django
│       │   │   ├── urls.py         # URLs principales
│       │   │   └── wsgi.py
│       │   ├── accounts/           # Gestion utilisateurs et profils
│       │   │   ├── models.py       # Profile, Friendship
│       │   │   ├── views.py        # Signup, login, profile, friends
│       │   │   ├── forms.py        # ProfileForm, UserRegistrationForm
│       │   │   ├── decorators.py   # feature_required
│       │   │   ├── context_processors.py  # user_features
│       │   │   └── tests/
│       │   ├── workouts/           # Entraînements
│       │   │   ├── models.py       # Exercise, WorkoutTemplate, WorkoutSession, SetLog, PR
│       │   │   ├── views.py        # CRUD templates, session logging
│       │   │   ├── forms.py        # TemplateItemForm
│       │   │   └── tests/
│       │   ├── nutrition/          # Alimentation
│       │   │   ├── models.py       # Food, FoodLog, Recipe, RecipeIngredient
│       │   │   ├── views.py        # Food logging, recipe management
│       │   │   └── tests/
│       │   ├── running/            # Course à pied
│       │   │   ├── models.py       # Run, StravaAuth, GarminAuth
│       │   │   ├── views.py        # Strava/Garmin OAuth, sync, manual entry
│       │   │   └── tests/
│       │   ├── dashboard/          # Tableau de bord
│       │   │   ├── views.py        # Vue dashboard
│       │   │   ├── services.py     # Calculs statistiques
│       │   │   └── tests/
│       │   ├── leaderboard/        # Classements
│       │   │   ├── views.py        # Leaderboards hebdo/mensuel/annuel
│       │   │   ├── services.py     # Calculs scores
│       │   │   └── tests/
│       │   ├── messaging/          # Messagerie
│       │   │   ├── models.py       # Conversation, Message
│       │   │   └── views.py        # CRUD conversations/messages
│       │   ├── common/             # Utilitaires partagés
│       │   │   └── templatetags/
│       │   ├── fixtures/           # Données initiales
│       │   │   ├── exercices.json  # 150+ exercices
│       │   │   ├── foods.json      # Base alimentaire
│       │   │   └── demo_users.json # Utilisateurs de test
│       │   ├── media/              # Fichiers uploadés
│       │   │   └── exercises/      # Images exercices
│       │   └── templates/          # Templates HTML
│       │       └── base.html       # Template de base
│       └── WorkingDocs/
│           └── TODO.md             # Suivi du développement
├── requirements.txt                # Dépendances Python
├── .gitignore                      # Fichiers exclus du versioning
└── README.md                       # Ce fichier
```

### Séparation des Responsabilités

**Modèles (models.py)**
- Définition de la structure de données
- Relations entre entités
- Validation métier
- Méthodes de calcul (PR, calories, etc.)

**Vues (views.py)**
- Logique de contrôle
- Interactions avec la base de données
- Gestion des formulaires
- Authentification et autorisations

**Services (services.py)**
- Logique métier complexe réutilisable
- Calculs statistiques (dashboard, leaderboard)
- Séparation de la logique des vues

**Templates (HTML)**
- Présentation des données
- Interface utilisateur
- Héritage de `base.html`

**Forms (forms.py)**
- Validation des entrées utilisateur
- Génération de formulaires HTML

---

## 🗄️ Modèle de Données

### Schéma de la Base de Données

```
┌─────────────────────┐
│       User          │ (Django auth.User)
│  - username         │
│  - email            │
│  - password         │
└──────────┬──────────┘
           │ 1:1
           │
┌──────────▼──────────────────────────────┐
│             Profile                     │
│  - user (FK User)                       │
│  - height_cm                            │
│  - weight_kg                            │
│  - goal (CHOICES)                       │
│  - feature_workouts (bool)              │
│  - feature_nutrition (bool)             │
│  - feature_running (bool)               │
│  - feature_leaderboard (bool)           │
└──────────┬──────────────────────────────┘
           │
           ├─────────────────────┐
           │ M:M (self)          │
┌──────────▼──────────┐          │
│    Friendship       │          │
│  - from_user (FK)   │◄─────────┘
│  - to_user (FK)     │
│  - status (CHOICES) │
│  - created_at       │
└─────────────────────┘

┌─────────────────────────────────────┐
│          WorkoutSession             │
│  - user (FK User)                   │
│  - template (FK WorkoutTemplate)    │
│  - date                             │
│  - duration_minutes                 │
│  - total_volume_kg                  │
│  - estimated_calories               │
│  - completed (bool)                 │
└──────────┬──────────────────────────┘
           │ 1:N
           │
┌──────────▼──────────────────────────┐
│             SetLog                  │
│  - session (FK WorkoutSession)      │
│  - exercise (FK Exercise)           │
│  - set_number                       │
│  - weight_kg                        │
│  - reps / duration_seconds          │
│  - exercise_type (CHOICES)          │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│          Exercise                   │
│  - name                             │
│  - muscle_group (CHOICES)           │
│  - equipment (CHOICES)              │
│  - image (ImageField)               │
└──────────┬──────────────────────────┘
           │
           │ M:N via TemplateItem
           │
┌──────────▼──────────────────────────┐
│       WorkoutTemplate               │
│  - user (FK User)                   │
│  - name                             │
│  - is_public (bool)                 │
└──────────┬──────────────────────────┘
           │ 1:N
           │
┌──────────▼──────────────────────────┐
│        TemplateItem                 │
│  - template (FK WorkoutTemplate)    │
│  - exercise (FK Exercise)           │
│  - order                            │
│  - target_sets                      │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│             FoodLog                 │
│  - user (FK User)                   │
│  - food (FK Food)                   │
│  - date                             │
│  - meal_type (CHOICES)              │
│  - quantity                         │
│  - unit (CHOICES)                   │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│              Food                   │
│  - name                             │
│  - calories_per_100g                │
│  - proteins_per_100g                │
│  - carbs_per_100g                   │
│  - fats_per_100g                    │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│              Recipe                 │
│  - user (FK User)                   │
│  - name                             │
│  - instructions                     │
│  - servings                         │
│  - is_public (bool)                 │
└──────────┬──────────────────────────┘
           │ M:N via RecipeIngredient
           │
┌──────────▼──────────────────────────┐
│       RecipeIngredient              │
│  - recipe (FK Recipe)               │
│  - food (FK Food)                   │
│  - quantity                         │
│  - unit (CHOICES)                   │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│               Run                   │
│  - user (FK User)                   │
│  - date                             │
│  - distance_km                      │
│  - duration_minutes                 │
│  - calories                         │
│  - source (strava/garmin/manual)    │
│  - strava_id / garmin_id            │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│          Conversation               │
│  - participants (M2M User)          │
│  - created_at                       │
│  - updated_at                       │
└──────────┬──────────────────────────┘
           │ 1:N
           │
┌──────────▼──────────────────────────┐
│            Message                  │
│  - conversation (FK Conversation)   │
│  - sender (FK User)                 │
│  - content                          │
│  - timestamp                        │
│  - is_read (bool)                   │
└─────────────────────────────────────┘
```

### Relations Clés

- **User → Profile** : Relation 1:1 créée automatiquement via signal Django
- **User → Friendship** : Relation M:M réflexive avec status (pending/accepted/rejected)
- **User → WorkoutSession → SetLog** : Hierarchie pour tracking détaillé des entraînements
- **Exercise ↔ WorkoutTemplate** : Relation M:N via `TemplateItem` pour créer des programmes
- **User → FoodLog → Food** : Tracking alimentaire avec quantities et meal types
- **Recipe → Food** : Relation M:N via `RecipeIngredient` pour recettes composées
- **Conversation ↔ User** : M2M pour messagerie entre plusieurs participants


---

## 🔀 Utilisation de Git

### Stratégie de Branches

Le projet a adopté une stratégie **Git Flow simplifiée** adaptée au contexte d'une semaine de développement intensif.

#### Branches Principales

- **`main`** : Branche protégée, code stable et déployable
  - Pas de commits directs
  - Merge uniquement via Merge Requests approuvées
  - Tests passants requis avant merge

#### Branches de Features

Nomenclature : `feature/<app-name>` ou `feature/<app-name>.<description>`

**Branches créées** :
- `feature/accounts` : Système utilisateurs et profils
- `feature/workouts` : Entraînements et exercices
- `feature/nutrition` : Alimentation et recettes
- `feature/running` : Course à pied et intégrations externes
- `feature/dashboard` : Tableau de bord et statistiques
- `feature/leaderboard` : Classements
- `feature/message` : Messagerie
- `form` : Feature toggles (nom court pour facilité)

**Branches de bugfix** :
- `feature/accounts.bugs`
- `feature/nutrition.bugs`
- `feature/running.bugs`
- `feature/workouts.bugs`

#### Workflow de Développement

1. **Création de branche depuis `main`**
   ```bash
   git checkout main
   git pull origin main
   git checkout -b feature/my-feature
   ```

2. **Développement avec commits réguliers**
   ```bash
   git add .
   git commit -m "[app] Description claire de la modification"
   git push origin feature/my-feature
   ```

3. **Merge Request sur GitLab**


### Convention de Commits

Format : `[app] - Description`

**Exemples** :
- `[accounts] - User registration and profile creation`
- `[workouts] - Add time-based exercise support`
- `[nutrition] - Fix calorie calculation for recipes`
- `[running] - Strava OAuth implementation`
- `[dashboard] - Add weekly consistency chart`
- `[form] - Apply feature_required decorator`

**Prefixes utilisés** :
- `[app]` : Feature ou modification
- `fix:` : Correction de bug
- `test:` : Ajout de tests
- `doc:` : Documentation
- `refactor:` : Refactorisation sans changement fonctionnel

---

## 🧪 Tests

Le projet intègre une suite de tests unitaires couvrant les fonctionnalités critiques.

### Structure des Tests

```
fitness_arc/
├── accounts/tests/
│   ├── test_models.py      # Tests Profile, Friendship
│   ├── test_views.py       # Tests signup, login, friends
│   └── test_forms.py       # Tests ProfileForm
├── workouts/tests.py       # Tests Exercise, WorkoutSession, PR
├── nutrition/tests.py      # Tests Food, FoodLog, Recipe
├── running/tests.py        # Tests Run, Strava/Garmin sync
├── dashboard/tests.py      # Tests stats calculation
└── leaderboard/tests.py    # Tests leaderboard scoring
```

### Exécution des Tests

```bash
# Tous les tests
python manage.py test

# Tests d'une app spécifique
python manage.py test accounts
python manage.py test workouts

# Tests avec couverture
coverage run --source='.' manage.py test
coverage report
coverage html  # Rapport HTML dans htmlcov/
```

### Couverture de Tests

**Cible** : 80%+ de couverture

---

## 🚀 Déploiement

### Configuration Production

Le projet est configuré pour être déployé sur **Railway** ou **Heroku**.

#### Variables d'Environnement

Créer un fichier `.env` avec :

```env
# Django
SECRET_KEY=your-production-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# Database (Railway PostgreSQL)
DATABASE_URL=postgresql://user:password@host:5432/dbname

# Strava API
STRAVA_CLIENT_ID=your-client-id
STRAVA_CLIENT_SECRET=your-client-secret
STRAVA_REDIRECT_URI=https://your-domain.com/running/strava/callback/

# Garmin (optional)
GARMIN_EMAIL=your-garmin-email
GARMIN_PASSWORD=your-garmin-password
```

#### Fichiers de Configuration Production

**Procfile** (pour Railway/Heroku) :
```
web: gunicorn fitness_arc.wsgi --log-file -
release: python manage.py migrate
```

**runtime.txt** :
```
python-3.13.1
```

#### Commandes de Déploiement

1. **Collecte des fichiers statiques**
   ```bash
   python manage.py collectstatic --noinput
   ```

2. **Migrations**
   ```bash
   python manage.py migrate
   ```

3. **Création du superuser**
   ```bash
   python manage.py createsuperuser
   ```

4. **Chargement des fixtures**
   ```bash
   python manage.py loaddata fixtures/exercices.json
   python manage.py loaddata fixtures/foods.json
   ```

### Checklist Pré-Déploiement

- [ ] `DEBUG=False` dans `.env`
- [ ] `SECRET_KEY` unique et sécurisée
- [ ] `ALLOWED_HOSTS` configuré
- [ ] Base PostgreSQL configurée
- [ ] Fichiers statiques collectés
- [ ] Migrations appliquées
- [ ] Tests passants
- [ ] Variables d'environnement Strava/Garmin configurées

---

## 📄 Licence

Projet académique - CentraleSupélec - CodingWeek 2025

---

**Développé avec ❤️ par Team 5 - CentraleSupélec**