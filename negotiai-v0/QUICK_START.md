# 🚀 Quick Start - NegotiAI v0

Guide rapide pour lancer NegotiAI en 5 minutes.

## ⚡ Installation Express

### 1. Cloner le projet
```bash
git clone <votre-repo>
cd negociate_with_me/negotiai-v0
```

### 2. Configurer les API keys
```bash
# Copier le fichier d'exemple
cp .env.example .env

# Éditer avec vos vraies clés
nano .env
# ou
vim .env
# ou ouvrir avec votre éditeur préféré
```

**Clés requises** :
- `MISTRAL_API_KEY` : https://console.mistral.ai/
- `ELEVENLABS_API_KEY` : https://elevenlabs.io/
- `ELEVENLABS_AGENT_PHONE_NUMBER_ID` : Dans ElevenLabs Dashboard → Conversational AI → Phone Numbers
- `QDRANT_URL` et `QDRANT_API_KEY` : https://cloud.qdrant.io/ (optionnel pour démo)

### 3. Lancer ngrok (pour recevoir les webhooks)
```bash
# Dans un terminal séparé
ngrok http 8000
```

**Important** : Copiez l'URL HTTPS affichée (ex: `https://abc123.ngrok-free.app`) et mettez-la dans `.env` :
```bash
WEBHOOK_BASE_URL=https://abc123.ngrok-free.app
```

### 4. Démarrer l'application
```bash
docker-compose up --build
```

**Attendez les messages** :
```
✅ Mistral service initialized
✅ Phone Call Handler initialized (with phone number)
✅ Webhook configured: https://abc123.ngrok-free.app/webhook/elevenlabs/call-ended
```

### 5. Ouvrir l'application
```
Frontend : http://localhost:3000
Backend  : http://localhost:8000
API Docs : http://localhost:8000/docs
```

---

## 🎯 Premier Test (2 minutes)

1. **Remplir le formulaire** :
   - Scénario : `SaaS B2B`
   - Produit : `Plateforme collaborative`
   - Entreprise : `TechCorp`
   - Prix demandé : `15000€`
   - Prix minimum : `10000€`

2. **Voir la stratégie** (Mistral recherche automatiquement)

3. **Lancer l'appel** avec votre numéro : `+33XXXXXXXXX`

4. **Négocier** pendant 2-3 minutes

5. **Voir le score** et les recommandations Mistral

---

## 🔧 Troubleshooting Express

### L'appel ne se lance pas
```bash
# Vérifier les logs
docker-compose logs backend | tail -50

# Vérifier que la variable est bien passée
docker-compose exec backend env | grep ELEVENLABS
```

### Le webhook ne reçoit rien
```bash
# Tester ngrok
curl https://your-ngrok-url.ngrok-free.app/health

# Vérifier que l'URL est dans .env
cat .env | grep WEBHOOK_BASE_URL
```

### Mistral ne répond pas
```bash
# Vérifier la clé API
docker-compose exec backend env | grep MISTRAL_API_KEY

# Redémarrer le backend
docker-compose restart backend
```

---

## 📦 Commandes Utiles

```bash
# Voir les logs en temps réel
docker-compose logs -f backend

# Redémarrer après changement .env
docker-compose restart backend

# Tout nettoyer et recommencer
docker-compose down
docker-compose up --build

# Accéder au backend
docker-compose exec backend bash

# Voir les erreurs uniquement
docker-compose logs backend | grep "❌\|Error"
```

---

## 🎬 Prêt pour la démo !

Voir **DEMO_EXAMPLE.md** pour un scénario complet de démonstration.

---

## 📞 Support

- Documentation complète : `README.md`
- Exemple de démo : `DEMO_EXAMPLE.md`
- Configuration API : `API_KEYS_SETUP.md`
