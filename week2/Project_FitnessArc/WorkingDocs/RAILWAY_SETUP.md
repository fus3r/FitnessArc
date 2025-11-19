# 🚂 Configuration Railway pour FitnessArc

## 📌 Pourquoi Railway ?

✅ **Avantages :**
- Base de données PostgreSQL partagée entre tous les collaborateurs
- Plus de conflits avec `db.sqlite3` dans Git
- Connexions concurrentes (plusieurs devs en même temps)
- Backups automatiques
- Facile à déployer en production
- Gratuit jusqu'à 500h/mois

---

## 🚀 Mise en place (10 minutes)

### 1️⃣ Créer un compte Railway

1. Aller sur [railway.app](https://railway.app)
2. Se connecter avec GitHub
3. Cliquer sur "New Project"

### 2️⃣ Créer une base PostgreSQL

1. Dans votre projet, cliquer sur "+ New" → "Database" → "PostgreSQL"
2. Railway va créer automatiquement une base de données
3. Cliquer sur la base PostgreSQL créée
4. Aller dans l'onglet "Variables"
5. Copier la valeur de `DATABASE_URL` (format : `postgresql://user:password@host:port/dbname`)

### 3️⃣ Configuration locale

1. Ajouter `DATABASE_URL` dans votre fichier `.env` local :

```env
# Email (déjà configuré)
EMAIL_USER=tototest024@gmail.com
EMAIL_PASSWORD=sjih nkyf tvhc yqjr

# Railway PostgreSQL (ajouter cette ligne)
DATABASE_URL=postgresql://postgres:xxx@xxx.railway.app:5432/railway
```

2. Vérifier que `.env` est dans `.gitignore` ✅ (déjà fait)

### 4️⃣ Appliquer les migrations sur Railway

```bash
cd week2/Project_FitnessArc/fitness_arc

# Vérifier que DATABASE_URL est défini
echo $DATABASE_URL  # Ou vérifier dans .env

# Appliquer les migrations
python3 manage.py migrate

# Créer un superuser (optionnel)
python3 manage.py createsuperuser

# Charger les données initiales
python3 manage.py loaddata fixtures/foods.json
python3 manage.py loaddata fixtures/exercices.json
python3 manage.py loaddata fixtures/templates_public.json
```

---

## 🔄 Workflow collaboratif

### Pour chaque collaborateur :

1. **Récupérer le code** :
   ```bash
   git pull origin main
   ```

2. **Demander `DATABASE_URL`** au chef de projet (via message privé, JAMAIS dans Git)

3. **Ajouter dans son `.env` local** :
   ```env
   DATABASE_URL=postgresql://postgres:xxx@xxx.railway.app:5432/railway
   ```

4. **Appliquer les migrations** (si nouvelles) :
   ```bash
   python3 manage.py migrate
   ```

5. **Travailler normalement** :
   - Tout le monde utilise la même DB
   - Les modifications sont visibles instantanément par tous
   - Plus de conflits `db.sqlite3` dans Git !

### Créer une nouvelle migration :

```bash
# Modifier un model dans models.py
python3 manage.py makemigrations

# Appliquer sur Railway (partagé)
python3 manage.py migrate

# Commit et push la migration
git add */migrations/
git commit -m "Add migration: description"
git push
```

### Les autres collaborateurs :

```bash
git pull
python3 manage.py migrate  # Applique automatiquement les nouvelles migrations
```

---

## 🔐 Sécurité

### ✅ À faire :
- Chaque dev a son propre `.env` (JAMAIS commit dans Git)
- Partager `DATABASE_URL` via un canal privé (Discord, Slack, etc.)
- Utiliser des variables d'environnement pour tous les secrets

### ❌ À NE JAMAIS faire :
- ❌ Commit `.env` dans Git
- ❌ Partager `DATABASE_URL` dans un commit
- ❌ Hardcoder les credentials dans `settings.py`

---

## 🔧 Basculer entre SQLite et PostgreSQL

Le projet est configuré pour supporter les deux :

### PostgreSQL (Railway - recommandé pour équipe) :
```bash
# Dans .env
DATABASE_URL=postgresql://postgres:xxx@xxx.railway.app:5432/railway
```

### SQLite (local uniquement) :
```bash
# Supprimer ou commenter DATABASE_URL dans .env
# DATABASE_URL=...

# Django utilisera automatiquement SQLite local
```

---

## 🆘 Troubleshooting

### "OperationalError: no such table"
```bash
python3 manage.py migrate
```

### "Connection refused" ou timeout
- Vérifier que `DATABASE_URL` est correct dans `.env`
- Vérifier la connexion internet
- Railway pourrait être en maintenance (vérifier [status.railway.app](https://status.railway.app))

### Migrations en conflit
```bash
# Reset des migrations (ATTENTION : perte de données)
python3 manage.py migrate nutrition zero
python3 manage.py migrate nutrition
```

### Accès à la DB Railway en ligne de commande
```bash
# Installer PostgreSQL client
brew install postgresql  # macOS

# Se connecter
psql $DATABASE_URL
```