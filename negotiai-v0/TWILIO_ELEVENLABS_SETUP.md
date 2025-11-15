# ⚠️ GUIDE OBSOLÈTE - Voir PHONE_CALL_SETUP.md

**Ce guide est obsolète** depuis la refonte de l'architecture des appels téléphoniques.

## 📖 Nouveau Guide

**Utilisez le nouveau guide** : [PHONE_CALL_SETUP.md](./PHONE_CALL_SETUP.md)

## Pourquoi ce changement ?

L'implémentation précédente était complexe :
- Nécessitait des credentials Twilio séparés
- Nécessitait une URL publique (ngrok)
- Nécessitait la configuration de webhooks
- Nécessitait la génération de TwiML

**Nouvelle approche simplifiée** :
- Utilise l'API native d'ElevenLabs
- ElevenLabs gère Twilio automatiquement
- Plus besoin de ngrok ou URL publique
- Plus besoin de webhooks ou TwiML
- Configuration en 2 variables d'environnement seulement

## Configuration Rapide

```env
ELEVENLABS_API_KEY=sk_your_key
ELEVENLABS_AGENT_PHONE_NUMBER_ID=phnum_your_id
```

Voir [PHONE_CALL_SETUP.md](./PHONE_CALL_SETUP.md) pour les instructions complètes.

---

# 🔧 Configuration Twilio + ElevenLabs pour Appels Téléphoniques (OBSOLÈTE)

**⚠️ Ce guide est conservé pour référence historique uniquement.**

Ce guide explique comment configurer les appels téléphoniques réels avec Twilio + ElevenLabs Conversational AI.

## 📋 Prérequis

### 1. Compte Twilio
- Créer un compte sur https://www.twilio.com/
- Vérifier votre numéro de téléphone
- Acheter un numéro Twilio (≈$1/mois)

### 2. Compte ElevenLabs
- Créer un compte sur https://elevenlabs.io/
- S'assurer d'avoir accès à Conversational AI (peut nécessiter abonnement payant)

### 3. URL Publique pour Webhooks
- **Production** : Domaine public (ex: https://your-domain.com)
- **Développement local** : Utiliser ngrok

## 🚀 Configuration Étape par Étape

### Étape 1 : Récupérer les Credentials Twilio

1. Se connecter au [Twilio Console](https://www.twilio.com/console)

2. Trouver vos **credentials** :
   - **Account SID** : Commence par "AC..."
   - **Auth Token** : Cliquer sur "Show" pour révéler

3. Acheter/configurer un **numéro de téléphone** :
   - Aller dans "Phone Numbers" → "Buy a Number"
   - Choisir un numéro avec **Voice capabilities**
   - Acheter (~$1/mois + $0.0085/min d'appel)

### Étape 2 : Récupérer l'API Key ElevenLabs

1. Se connecter sur https://elevenlabs.io/

2. Aller dans **Settings** → **API Keys**

3. Copier votre clé API

4. Vérifier l'accès **Conversational AI** :
   - Si vous n'avez pas accès, vous verrez une erreur 405
   - Peut nécessiter un abonnement Pro/Enterprise

### Étape 3 : Configurer l'URL Publique

#### Option A : Production (domaine public)

Votre backend doit être accessible publiquement :
```
PUBLIC_URL=https://your-domain.com
```

#### Option B : Développement local (ngrok)

1. **Installer ngrok** :
   ```bash
   # macOS
   brew install ngrok

   # Windows
   choco install ngrok

   # Linux
   snap install ngrok
   ```

2. **Démarrer ngrok** :
   ```bash
   ngrok http 8000
   ```

3. **Copier l'URL HTTPS** (ex: `https://abc123.ngrok.io`)

### Étape 4 : Configurer les Variables d'Environnement

Éditer le fichier `.env` :

```env
# Mistral AI (requis)
MISTRAL_API_KEY=your_actual_mistral_key

# ElevenLabs (requis)
ELEVENLABS_API_KEY=your_actual_elevenlabs_key

# Twilio (requis pour appels téléphoniques)
TWILIO_ACCOUNT_SID=AC...your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1234567890

# URL publique pour webhooks
PUBLIC_URL=https://your-domain.com  # ou https://abc123.ngrok.io
```

**Important** : Remplacer toutes les valeurs `your_*` par vos vraies clés !

### Étape 5 : Redémarrer Docker

```bash
docker compose down
docker compose up --build
```

### Étape 6 : Vérifier les Services

Vérifier les logs au démarrage :

```bash
docker compose logs backend | grep "initialized"
```

Vous devriez voir :
```
✅ Mistral service initialized
✅ Phone Call Handler initialized (with Twilio)
```

Si vous voyez `without Twilio`, vérifiez vos variables d'environnement.

### Étape 7 : Configurer les Webhooks ElevenLabs (optionnel)

Si ElevenLabs Conversational AI supporte les webhooks :

1. Aller dans le dashboard ElevenLabs

2. Configurer le webhook :
   - **URL** : `https://your-domain.com/webhook/elevenlabs/call-ended`
   - **Events** : `conversation.ended` ou similaire
   - **Method** : POST

3. Tester avec un appel

## 🧪 Test de Fonctionnement

### Test 1 : Vérifier les Endpoints

```bash
# Scenarios disponibles
curl http://localhost:8000/api/call/scenarios

# Devrait retourner la liste des 5 scénarios
```

### Test 2 : Créer une Session d'Appel

```bash
curl -X POST http://localhost:8000/api/call/setup \
  -H "Content-Type: application/json" \
  -d '{
    "scenario": "saas",
    "context": {
      "product": "Plateforme SaaS Analytics",
      "target_price": "50000€/an",
      "minimum_price": "35000€/an",
      "red_lines": ["Pas de paiement à plus de 30 jours"]
    }
  }'

# Devrait retourner un session_id
```

### Test 3 : Initier un Appel (avec vrai numéro)

```bash
# Remplacer SESSION_ID et +33612345678 par vos valeurs
curl -X POST http://localhost:8000/api/call/start/SESSION_ID \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+33612345678"
  }'

# Si tout est configuré, vous devriez recevoir un appel !
```

## 📊 Flow Technique Complet

```
1. Frontend : Utilisateur clique "Recevoir l'appel"
   ↓
2. Backend : POST /api/call/setup
   → Crée agent ElevenLabs Conversational AI
   → Retourne session_id + agent_id
   ↓
3. Backend : POST /api/call/start/{session_id}
   → Twilio initie l'appel au numéro de l'utilisateur
   → Retourne call_sid
   ↓
4. Twilio : Appelle l'utilisateur
   ↓
5. Utilisateur : Répond au téléphone
   ↓
6. Twilio : GET /api/call/twiml/{agent_id}
   → Backend retourne TwiML XML
   → TwiML connecte l'appel au WebSocket ElevenLabs
   ↓
7. ElevenLabs : Conversation en temps réel
   → Agent IA parle avec l'utilisateur
   → Audio bidirectionnel via WebSocket
   ↓
8. Utilisateur : Raccroche
   ↓
9. Twilio : POST /api/call/status (CallStatus=completed)
   → Backend met à jour le statut de la session
   ↓
10. ElevenLabs : POST /webhook/elevenlabs/call-ended
    → Envoie le transcript complet
    → Backend analyse avec Mistral AI
    → Calcule scores et recommandations
    ↓
11. Frontend : Polling /api/call/results/{session_id}
    → Récupère l'analyse complète
    → Affiche dashboard de résultats
```

## 🔍 Debugging

### Problème : "Twilio not configured"

**Solution** : Vérifier que les variables d'environnement sont bien définies :

```bash
# Vérifier dans le container
docker compose exec backend env | grep TWILIO
```

Devrait afficher :
```
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
TWILIO_PHONE_NUMBER=+1...
```

### Problème : "Failed to create agent: 405"

**Cause** : ElevenLabs Conversational AI n'est pas accessible avec votre clé API

**Solutions** :
1. Vérifier que vous avez un abonnement Pro/Enterprise
2. Contacter ElevenLabs pour accès beta
3. Utiliser mode TEXT en attendant

### Problème : Appel ne sonne pas

**Causes possibles** :
1. Numéro de téléphone mal formaté (doit être international : +33...)
2. Twilio pas configuré
3. URL publique incorrecte

**Debug** :
```bash
# Vérifier les logs Twilio
docker compose logs backend | grep "📞"

# Vérifier sur Twilio Console > Monitor > Logs
```

### Problème : Webhook pas reçu

**Causes** :
1. ngrok arrêté (redémarrer et mettre à jour PUBLIC_URL)
2. URL webhook mal configurée dans ElevenLabs
3. Firewall bloque les webhooks

**Solutions** :
```bash
# Tester webhook manuellement
curl -X POST http://localhost:8000/webhook/elevenlabs/call-ended \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "test",
    "transcript": "Test transcript",
    "duration": 60
  }'
```

### Problème : TwiML Error

**Debug** :
```bash
# Tester l'endpoint TwiML
curl http://localhost:8000/api/call/twiml/test_agent_id

# Devrait retourner du XML
```

## 💰 Coûts Estimés

### Développement / Test (≈$0-5/mois)
- **Twilio** :
  - Numéro de téléphone : $1/mois
  - Appels : $0.0085/min
  - Test 30 min/mois : $0.26
- **ElevenLabs** :
  - Plan gratuit : 10,000 caractères/mois (limité)
  - Conversational AI : Peut nécessiter plan Pro ($22/mois)
- **Mistral AI** :
  - Free tier : Suffisant pour tests
- **Total** : $1-23/mois selon usage

### Production (≈$50-200/mois)
- **Twilio** : $1 + usage
- **ElevenLabs Pro** : $22/mois minimum
- **Mistral AI** : Pay-as-you-go (~$2-10/mois)
- **Hosting** : Variable
- **Total** : Dépend du volume d'appels

## 📝 Notes Importantes

### Sécurité
- **NE JAMAIS** committer le fichier `.env` avec les vraies clés
- Utiliser `.env.example` pour la documentation
- En production, utiliser des secrets managers (AWS Secrets, etc.)

### Limites
- **Twilio** : Vérifier numéros autorisés en mode trial
- **ElevenLabs** : Limites de caractères par mois
- **Mistral** : Rate limits (surtout en free tier)

### Ngrok Gratuit
- URL change à chaque redémarrage
- Timeout après quelques heures
- Pour production, utiliser domaine permanent

## 🎯 Checklist de Configuration

- [ ] Compte Twilio créé
- [ ] Numéro Twilio acheté
- [ ] Credentials Twilio copiés dans `.env`
- [ ] Compte ElevenLabs créé
- [ ] API Key ElevenLabs copiée dans `.env`
- [ ] Accès Conversational AI vérifié
- [ ] URL publique configurée (ngrok ou domaine)
- [ ] PUBLIC_URL mise à jour dans `.env`
- [ ] Docker containers redémarrés
- [ ] Logs vérifiés (✅ Phone Call Handler initialized with Twilio)
- [ ] Test d'appel effectué avec succès

## 🆘 Support

Si vous rencontrez des problèmes :

1. **Vérifier les logs** :
   ```bash
   docker compose logs backend --tail 100 -f
   ```

2. **Tester chaque composant séparément** :
   - Twilio : Appel manuel via Console
   - ElevenLabs : Test API directement
   - Webhooks : Test avec curl

3. **Consulter la documentation** :
   - Twilio : https://www.twilio.com/docs/voice
   - ElevenLabs : https://elevenlabs.io/docs
   - TwiML : https://www.twilio.com/docs/voice/twiml

## ✅ Prochaines Étapes

Une fois configuré :

1. **Tester un scénario complet** (SaaS B2B recommandé)
2. **Vérifier l'analyse Mistral** (qualité des scores)
3. **Optimiser les prompts** si nécessaire
4. **Préparer démo** pour hackathon !

Bon courage ! 🚀
