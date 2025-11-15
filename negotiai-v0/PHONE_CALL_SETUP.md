# 📞 Configuration des Appels Téléphoniques avec ElevenLabs

Ce guide explique comment configurer les appels téléphoniques réels pour NegotiAI v0.

**Architecture simplifiée** : ElevenLabs Conversational AI gère automatiquement l'intégration Twilio. Vous n'avez besoin que de votre clé API ElevenLabs et d'un Phone Number ID.

## 📋 Prérequis

### 1. Compte ElevenLabs avec Conversational AI
- Créer un compte sur https://elevenlabs.io/
- **Avoir accès à Conversational AI** (peut nécessiter abonnement Pro/Enterprise)
- Configurer un Phone Number dans le dashboard ElevenLabs

### 2. Docker
- Docker et Docker Compose installés

## 🚀 Configuration Rapide (3 étapes)

### Étape 1 : Récupérer l'API Key ElevenLabs

1. Se connecter sur https://elevenlabs.io/

2. Aller dans **Settings** → **API Keys**

3. Copier votre clé API (commence par `sk_...`)

### Étape 2 : Récupérer le Phone Number ID

1. Aller dans **ElevenLabs Dashboard** → **Conversational AI** → **Phone Numbers**

2. Si vous n'avez pas de numéro configuré :
   - Cliquer sur "Add Phone Number"
   - Suivre les instructions d'ElevenLabs
   - ElevenLabs gère automatiquement la connection Twilio

3. Copier le **Phone Number ID** (format: `phnum_01jwgc4x8zfjk9f0632bw7kpz7`)

### Étape 3 : Configurer les Variables d'Environnement

Éditer le fichier `negotiai-v0/.env` :

```env
# Mistral AI (requis pour l'analyse)
MISTRAL_API_KEY=your_actual_mistral_key

# Qdrant (requis pour la recherche de tactiques)
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your_actual_qdrant_key

# ElevenLabs (requis pour les appels vocaux)
ELEVENLABS_API_KEY=sk_your_actual_elevenlabs_key

# ElevenLabs Phone Number ID (REQUIS pour les appels téléphoniques)
# Format: phnum_01jwgc4x8zfjk9f0632bw7kpz7
ELEVENLABS_AGENT_PHONE_NUMBER_ID=phnum_your_phone_number_id
```

**Important** :
- Remplacer toutes les valeurs `your_*` par vos vraies clés
- Le `ELEVENLABS_AGENT_PHONE_NUMBER_ID` est **OBLIGATOIRE** pour que les appels fonctionnent
- Pas besoin de Twilio credentials (ElevenLabs gère tout automatiquement)
- Pas besoin d'URL publique ou ngrok (plus de webhooks à gérer)

### Étape 4 : Redémarrer Docker

```bash
cd negotiai-v0
docker compose down
docker compose up --build
```

### Étape 5 : Vérifier la Configuration

Vérifier les logs au démarrage :

```bash
docker compose logs backend | grep "Phone Call Handler"
```

Vous devriez voir :
```
✅ Phone Call Handler initialized (with phone number)
```

Si vous voyez `phone calls may not work - missing agent_phone_number_id`, vérifiez votre `.env`.

## 🧪 Test de Fonctionnement

### Test 1 : API de Test Simple

```bash
curl -X POST http://localhost:8000/api/call/test \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+33612345678"
  }'
```

**Remplacer** `+33612345678` par votre numéro de téléphone au format international.

**Résultat attendu** :
- Vous recevez un appel dans ~10 secondes
- L'agent dit : "Bonjour ! Ceci est un test de NegotiAI..."

### Test 2 : Scénarios Disponibles

```bash
curl http://localhost:8000/api/call/scenarios
```

Devrait retourner les 5 scénarios :
- `saas` - Négociation SaaS B2B
- `freelance` - Négociation Tarif Freelance
- `salary` - Négociation Salariale
- `partnership` - Négociation Partenariat Commercial
- `real_estate` - Négociation Immobilière

### Test 3 : Flow Complet

1. **Setup** - Créer une session de négociation :

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
```

Vous recevez un `session_id`.

2. **Start** - Lancer l'appel :

```bash
curl -X POST http://localhost:8000/api/call/start/SESSION_ID \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+33612345678"
  }'
```

**Remplacer** :
- `SESSION_ID` par le session_id reçu
- `+33612345678` par votre numéro de téléphone

3. **Receive Call** - Vous recevez l'appel et négociez !

4. **Results** - Après l'appel, récupérer l'analyse :

```bash
curl http://localhost:8000/api/call/results/SESSION_ID
```

## 📱 Utilisation depuis le Frontend

1. Ouvrir http://localhost:3000

2. Cliquer sur **"Entraînement par Téléphone"**

3. Remplir le formulaire :
   - Sélectionner un scénario
   - Entrer les détails de votre négociation
   - Entrer votre numéro de téléphone (format international : +33...)

4. Cliquer sur **"Recevoir l'appel"**

5. Vous recevez l'appel dans ~10 secondes

6. Négociez avec l'agent IA !

7. Après l'appel, consultez votre analyse détaillée

## 🔍 Architecture Technique

### Comment ça fonctionne ?

```
1. Frontend → Backend : Setup négociation
   ↓
2. Backend → ElevenLabs SDK : create_agent()
   → Crée un agent IA avec prompt personnalisé
   ↓
3. Backend → ElevenLabs SDK : twilio.outbound_call()
   → ElevenLabs gère automatiquement Twilio
   ↓
4. ElevenLabs → Téléphone utilisateur : Appel direct
   ↓
5. Utilisateur ↔ Agent IA : Conversation en temps réel
   ↓
6. Fin d'appel → Backend : Webhook (optionnel)
   → Transcript + Analyse Mistral AI
```

### Code Backend (Simplifié)

```python
from elevenlabs import ElevenLabs

# Initialisation
client = ElevenLabs(api_key="sk_...")

# Créer un agent
agent = client.conversational_ai.create_agent(
    conversation_config={
        "agent": {
            "prompt": {"prompt": "Vous êtes un négociateur..."},
            "first_message": "Bonjour...",
            "language": "fr"
        }
    }
)

# Lancer l'appel
response = client.conversational_ai.twilio.outbound_call(
    agent_id=agent.agent_id,
    agent_phone_number_id="phnum_...",
    to_number="+33695990832"
)
```

**C'est tout !** ElevenLabs gère :
- La connexion Twilio
- Le TwiML
- Les webhooks de statut
- La conversion audio bidirectionnelle

## 🔧 Debugging

### Problème : "agent_phone_number_id not configured"

**Solution** : Vérifier que `ELEVENLABS_AGENT_PHONE_NUMBER_ID` est bien dans `.env`

```bash
# Vérifier dans le container
docker compose exec backend env | grep ELEVENLABS_AGENT_PHONE_NUMBER_ID
```

### Problème : "Failed to create agent: 405"

**Cause** : Votre compte ElevenLabs n'a pas accès à Conversational AI

**Solutions** :
1. Vérifier votre abonnement ElevenLabs (Pro/Enterprise requis)
2. Contacter ElevenLabs pour activer Conversational AI
3. Vérifier que la clé API est correcte

### Problème : Appel ne sonne pas

**Causes possibles** :
1. Numéro de téléphone mal formaté (doit être international : `+33...`)
2. `ELEVENLABS_AGENT_PHONE_NUMBER_ID` incorrect
3. Problème côté ElevenLabs

**Debug** :
```bash
# Vérifier les logs
docker compose logs backend | grep "📞"

# Tester avec l'endpoint de test
curl -X POST http://localhost:8000/api/call/test \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+33612345678"}'
```

### Problème : Docker ne voit pas les nouvelles variables

**Solution** : Toujours rebuild après modification du `.env`

```bash
docker compose down
docker compose up --build
```

## 💰 Coûts

### ElevenLabs Conversational AI
- **Abonnement requis** : Pro (~$22/mois minimum)
- **Appels téléphoniques** : Tarification selon usage
- Vérifier les prix sur https://elevenlabs.io/pricing

### Mistral AI
- **Free tier** : Suffisant pour tests
- **Production** : Pay-as-you-go (~$2-10/mois selon usage)

### Total estimé
- **Développement** : ~$22-30/mois
- **Production** : Variable selon nombre d'appels

## ✅ Checklist de Configuration

- [ ] Compte ElevenLabs créé
- [ ] Accès Conversational AI vérifié
- [ ] Phone Number configuré dans ElevenLabs
- [ ] `ELEVENLABS_API_KEY` copié dans `.env`
- [ ] `ELEVENLABS_AGENT_PHONE_NUMBER_ID` copié dans `.env`
- [ ] `MISTRAL_API_KEY` configuré (pour l'analyse)
- [ ] Docker containers redémarrés
- [ ] Logs vérifiés (✅ Phone Call Handler initialized with phone number)
- [ ] Test d'appel effectué avec succès

## 📚 Documentation Complémentaire

- **ElevenLabs Conversational AI** : https://elevenlabs.io/docs/conversational-ai
- **ElevenLabs Python SDK** : https://github.com/elevenlabs/elevenlabs-python
- **Mistral AI** : https://docs.mistral.ai/

## 🆘 Support

Si vous rencontrez des problèmes :

1. **Vérifier les logs** :
   ```bash
   docker compose logs backend --tail 100 -f
   ```

2. **Tester la configuration** :
   ```bash
   # Test ElevenLabs
   curl -X POST http://localhost:8000/api/call/test \
     -H "Content-Type: application/json" \
     -d '{"phone_number": "+33612345678"}'
   ```

3. **Vérifier les variables d'environnement** :
   ```bash
   docker compose exec backend env | grep -E "ELEVENLABS|MISTRAL"
   ```

## 🎯 Prochaines Étapes

Une fois configuré :

1. **Tester tous les scénarios** (SaaS, Freelance, Salary, etc.)
2. **Affiner les prompts** si besoin
3. **Vérifier la qualité des analyses** Mistral
4. **Préparer votre démo** ! 🚀

Bon courage avec vos négociations !
