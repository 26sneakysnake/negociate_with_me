# 🚀 NegotiAI v0 - Guide de Configuration

## Étape 1 : Obtenir les Clés API

### 1. Mistral AI (Obligatoire)
- Créez un compte sur https://console.mistral.ai/
- Allez dans "API Keys"
- Créez une nouvelle clé
- **Coût** : Pay-as-you-go, quelques centimes par requête

### 2. Qdrant (Recommandé pour les tactiques)
- Créez un compte sur https://cloud.qdrant.io/
- Créez un cluster **gratuit** (1GB)
- Copiez l'URL du cluster (ex: `https://xyz-abc-123.qdrant.io`)
- Copiez la clé API dans "Cluster Details"

### 3. ElevenLabs (Optionnel pour l'audio)
- Créez un compte sur https://elevenlabs.io/
- Allez dans votre profil → "API Keys"
- Créez une clé
- **Gratuit** : 10,000 caractères/mois

---

## Étape 2 : Configurer le fichier .env

Dans le dossier `negotiai-v0/`, éditez le fichier `.env` :

```bash
# Mistral AI - OBLIGATOIRE
MISTRAL_API_KEY=votre_vraie_clé_mistral_ici

# Qdrant Vector DB - RECOMMANDÉ (améliore la qualité des tactiques)
QDRANT_URL=https://votre-cluster-id.qdrant.io
QDRANT_API_KEY=votre_clé_qdrant_ici

# ElevenLabs - OPTIONNEL (pour feedback audio)
ELEVENLABS_API_KEY=votre_clé_elevenlabs_ici
```

**⚠️ IMPORTANT** :
- Remplacez les valeurs par vos **vraies clés API**
- Au minimum, vous devez configurer **MISTRAL_API_KEY**
- Sans Qdrant, l'app fonctionnera mais les tactiques seront moins pertinentes
- Sans ElevenLabs, il n'y aura pas de feedback audio (mais le reste fonctionne)

---

## Étape 3 : Démarrer l'Application

### Option A : Avec Docker (Recommandé)

```bash
cd negotiai-v0

# Build et démarrage
docker-compose up --build
```

### Option B : Manuel (sans Docker)

**Backend :**
```bash
cd negotiai-v0/backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

**Frontend (autre terminal) :**
```bash
cd negotiai-v0/frontend
npm install
npm start
```

---

## Étape 4 : Vérifier le Démarrage

Vous devriez voir :

```
======================================================================
🚀 Starting NegotiAI v0 Backend
======================================================================
✅ Mistral service initialized
✅ Qdrant service initialized
✅ ElevenLabs service initialized
✅ Loaded 15 negotiation tactics into Qdrant
======================================================================
✅ Backend is ready!
======================================================================

INFO:     Uvicorn running on http://0.0.0.0:8000
```

Frontend :
```
Compiled successfully!

You can now view negotiai-frontend in the browser.
  Local:            http://localhost:3000
```

---

## Étape 5 : Accéder à l'Application

- **Frontend** : http://localhost:3000
- **Backend API** : http://localhost:8000
- **API Docs** : http://localhost:8000/docs

---

## 🔧 Dépannage

### Problème : Services non initialisés

Si vous voyez :
```
⚠️ Mistral service failed to initialize
⚠️ Qdrant service failed to initialize
```

**Solution** :
1. Vérifiez que votre fichier `.env` contient de vraies clés API
2. Redémarrez Docker : `docker-compose down && docker-compose up --build`

### Problème : Qdrant connection error

Si Qdrant ne se connecte pas :
- Vérifiez que `QDRANT_URL` est correct (doit commencer par `https://`)
- Vérifiez que votre cluster Qdrant est bien actif sur cloud.qdrant.io
- L'app peut fonctionner **sans Qdrant** (les tactiques seront juste moins pertinentes)

### Problème : Frontend ne compile pas

```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm start
```

---

## 🎯 Test Rapide

1. Ouvrez http://localhost:3000
2. Copiez le contenu de `demo/sample-context.txt`
3. Collez-le dans l'application
4. Objectif : `Secure 55K€ annual contract`
5. Minimum : `45K€`
6. Cliquez sur "Generate Strategy"
7. Explorez votre stratégie de négociation générée !

---

## 💰 Coûts Estimés

- **Mistral AI** : ~0.002€ par requête de stratégie (très peu cher)
- **Qdrant** : **Gratuit** jusqu'à 1GB
- **ElevenLabs** : **Gratuit** jusqu'à 10,000 caractères/mois

**Total pour tester** : < 1€

---

## 📚 Prochaines Étapes

Une fois l'app qui fonctionne :
1. Testez avec vos propres contextes de négociation
2. Explorez l'analyse post-négociation
3. Écoutez le feedback audio (si ElevenLabs configuré)

Pour plus d'infos, consultez le [README.md](./README.md)
