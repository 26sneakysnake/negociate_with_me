# 🚀 NegotiAI - Lancement avec Docker

## Démarrage Rapide (1 commande)

### 1️⃣ Prérequis
- Docker Desktop installé et démarré
- Les ports 3000, 8000, 5433 disponibles

### 2️⃣ Configuration API Keys

Créez/éditez le fichier `.env` à la racine de `negotiai-v0/` :

```bash
# Obligatoire pour simulation vocale
MISTRAL_API_KEY=votre_clé_mistral
ELEVENLABS_API_KEY=votre_clé_elevenlabs

# Optionnel (améliore les suggestions tactiques)
QDRANT_URL=votre_url_qdrant
QDRANT_API_KEY=votre_clé_qdrant
```

### 3️⃣ Lancement (1 seule commande)

```bash
cd negotiai-v0

# Première fois : build + start
docker compose up --build

# Les fois suivantes : start seulement
docker compose up
```

**Attendez ces messages** :
```
backend-1   | ✅ Backend is ready!
frontend-1  | webpack compiled successfully
postgres-1  | database system is ready to accept connections
```

### 4️⃣ Accès

- **Frontend** : http://localhost:3000
- **Backend API** : http://localhost:8000
- **API Docs** : http://localhost:8000/docs

---

## 🎤 Tester la Simulation Vocale

1. Ouvrez http://localhost:3000
2. Cliquez sur **"🎤 Simulation Live"** dans le menu
3. Choisissez un scénario (💼 SaaS, 💻 Freelance, ou 🏠 Immobilier)
4. Cliquez **"Démarrer la Simulation"**

**Le client IA parle** → **Suggestion apparaît** → **Vous répondez ou activez Auto-Pilot** 🤖

---

## 🔄 Commandes Docker Utiles

### Arrêter l'application
```bash
docker compose down
```

### Redémarrer un service spécifique
```bash
# Redémarrer seulement le backend
docker compose restart backend

# Redémarrer seulement le frontend
docker compose restart frontend
```

### Voir les logs
```bash
# Tous les logs
docker compose logs -f

# Backend seulement
docker compose logs -f backend

# Frontend seulement
docker compose logs -f frontend
```

### Reconstruire après modifications
```bash
# Rebuild complet
docker compose down
docker compose up --build

# Rebuild un service spécifique
docker compose up --build backend
```

### Réinitialiser la base de données
```bash
# Supprimer les volumes (efface toutes les données)
docker compose down -v

# Redémarrer avec base fraîche
docker compose up --build
```

---

## 🐛 Dépannage

### Problème : Port déjà utilisé

**Symptôme** :
```
Error starting userland proxy: listen tcp4 0.0.0.0:3000: bind: address already in use
```

**Solution** :
```bash
# Arrêter le processus qui utilise le port
# Sur Windows
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Sur Mac/Linux
lsof -ti:3000 | xargs kill -9
```

### Problème : WebSocket ne se connecte pas

**Symptôme** : Status "error" ou "disconnected" dans la simulation

**Solution** :
```bash
# Vérifier que le backend est bien lancé
docker compose logs backend | grep "Backend is ready"

# Redémarrer le backend
docker compose restart backend
```

### Problème : Modifications code non prises en compte

**Solution** :
```bash
# Pour le backend (Python)
docker compose restart backend

# Pour le frontend (React)
# Normalement hot-reload automatique
# Si besoin :
docker compose restart frontend
```

### Problème : Base de données corrompue

**Solution** :
```bash
# Reset complet
docker compose down -v
docker compose up --build
```

---

## 📦 Ce qui tourne dans Docker

### 3 Conteneurs lancés :

1. **postgres** (Port 5433)
   - PostgreSQL 15
   - Stockage sessions, stratégies, analyses

2. **backend** (Port 8000)
   - FastAPI + WebSocket
   - Mistral AI + ElevenLabs
   - Analyse temps réel

3. **frontend** (Port 3000)
   - React application
   - Hot-reload activé pour développement

---

## ✅ Vérification que tout fonctionne

### Test Complet (2 minutes)

```bash
# 1. Lancer l'app
docker compose up

# 2. Vérifier les 3 services
# Dans un autre terminal :
curl http://localhost:8000/
# Devrait retourner : {"message":"NegotiAI v0 API","status":"running"}

curl http://localhost:3000/
# Devrait retourner du HTML

# 3. Ouvrir dans le navigateur
open http://localhost:3000

# 4. Tester la simulation
# Cliquer sur "🎤 Simulation Live"
# Choisir "💻 Freelance Dev" (scénario court)
# Démarrer et vérifier :
#   ✅ Client IA parle (audio + transcript)
#   ✅ Suggestion apparaît
#   ✅ Vous pouvez répondre
#   ✅ Auto-pilot fonctionne
```

---

## 🔥 Mode Production (Hackathon)

Pour une démo stable pendant le hackathon :

```bash
# 1. Arrêter tout
docker compose down

# 2. Rebuild complet
docker compose build --no-cache

# 3. Lancer en mode détaché (background)
docker compose up -d

# 4. Vérifier que tout tourne
docker compose ps
# Les 3 services doivent être "Up"

# 5. Voir les logs en live
docker compose logs -f
```

Pour arrêter :
```bash
docker compose down
```

---

## 🎯 Résumé : 1 Commande Suffit

```bash
# Depuis negotiai-v0/
docker compose up --build
```

Attendez 30 secondes → Allez sur http://localhost:3000 → **C'est parti ! 🚀**

---

## 📝 Notes Importantes

- **Volumes** : Le code est monté en volume, donc vos modifications sont prises en compte sans rebuild
  - Backend : Auto-reload activé (uvicorn --reload)
  - Frontend : Hot-reload React activé

- **Persistence** : La base PostgreSQL persiste dans un volume Docker
  - Les données survivent aux redémarrages
  - Pour reset : `docker compose down -v`

- **Isolation** : Tout tourne dans Docker
  - Pas besoin de Python/Node installés sur votre machine
  - Pas de conflits de versions
  - Fonctionne pareil sur Windows/Mac/Linux

---

**Tout est prêt pour le hackathon ! Lancez `docker compose up` et vous êtes bon ! 💪**
