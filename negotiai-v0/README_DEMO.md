# 🎯 NegotiAI v0 - Documentation Démo

> Plateforme d'entraînement à la négociation avec IA vocale

## 📚 Index des Documents

### Pour démarrer rapidement
- **[QUICK_START.md](./QUICK_START.md)** - Installation et premier test en 5 minutes

### Pour préparer une démo
- **[DEMO_EXAMPLE.md](./DEMO_EXAMPLE.md)** - Guide complet avec script de présentation
- **[DEMO_SCENARIOS.json](./DEMO_SCENARIOS.json)** - 5 scénarios pré-configurés

### Configuration technique
- **[.env.example](./.env.example)** - Template de configuration avec documentation
- **[API_KEYS_SETUP.md](./API_KEYS_SETUP.md)** - Guide d'obtention des clés API
- **[README.md](./README.md)** - Documentation technique complète

---

## 🚀 Quick Start (TL;DR)

```bash
# 1. Copier et configurer .env
cp .env.example .env
# Éditer .env avec vos clés API

# 2. Lancer ngrok (terminal séparé)
ngrok http 8000
# Copier l'URL HTTPS dans .env → WEBHOOK_BASE_URL

# 3. Démarrer l'application
docker-compose up --build

# 4. Ouvrir http://localhost:3000
# 5. Utiliser le scénario de DEMO_EXAMPLE.md
```

---

## 🎬 Cas d'Usage

### Hackathon / Pitch
→ **[DEMO_EXAMPLE.md](./DEMO_EXAMPLE.md)**
- Script de présentation (7 minutes)
- Scénario SaaS B2B détaillé
- Points clés à mettre en avant

### Formation commerciale
→ **[DEMO_SCENARIOS.json](./DEMO_SCENARIOS.json)**
- 5 scénarios différents (SaaS, Freelance, Salaire, Partenariat, Immobilier)
- Tactiques recommandées par scénario
- Résultats attendus

### Test technique
→ **[QUICK_START.md](./QUICK_START.md)**
- Installation rapide
- Troubleshooting
- Commandes utiles

---

## 🛠 Architecture Technique

```
┌─────────────┐
│   Frontend  │ React 18 + Axios
│ :3000       │
└──────┬──────┘
       │ HTTP
┌──────▼──────┐
│   Backend   │ FastAPI (Python)
│ :8000       │
└──┬────┬─────┘
   │    │
   │    └──────────┐
   │               │
┌──▼────┐   ┌─────▼──────┐   ┌───────────┐
│Mistral│   │ ElevenLabs │   │  Qdrant   │
│  AI   │   │ Conv. AI   │   │  Vector   │
└───────┘   └────────────┘   └───────────┘
Research    Voice Agent       Tactics DB
Analysis    + Twilio          (optional)
```

### Technologies utilisées

**IA & Voice**
- **Mistral AI** : Recherche entreprise + Analyse négociation (mistral-large-latest)
- **ElevenLabs** : Agent vocal conversationnel + Appels Twilio
- **Qdrant** : Base vectorielle pour les tactiques (optionnel)

**Backend**
- **FastAPI** : API REST asynchrone
- **Pydantic v2** : Validation des données
- **httpx** : Client HTTP async
- **Python 3.11**

**Frontend**
- **React 18** : UI interactive
- **Axios** : HTTP client
- **CSS3** : Animations et design moderne

**Infrastructure**
- **Docker Compose** : Orchestration multi-containers
- **PostgreSQL** : Base de données (sessions, templates)
- **Ngrok** : Tunneling pour webhooks locaux

---

## 🔑 API Keys Requises

| Service | Où l'obtenir | Utilisé pour | Coût |
|---------|--------------|--------------|------|
| **Mistral AI** | https://console.mistral.ai/ | Recherche + Analyse | ~0.01€/appel |
| **ElevenLabs** | https://elevenlabs.io/ | Agent vocal + Appels | ~0.20€/appel |
| **Qdrant** | https://cloud.qdrant.io/ | Stockage tactiques | Gratuit (tier free) |

**Total par démo** : ~0.25€

---

## 📊 Métriques du Système

**Performance**
- Temps de réponse API : < 200ms
- Latence appel téléphonique : < 500ms
- Temps d'analyse Mistral : 5-10 secondes

**Coûts (estimation)**
- Setup initial : 0€ (tiers gratuits disponibles)
- Par négociation : ~0.25€
- Par mois (100 users, 5 sessions/user) : ~125€

**Scalabilité**
- Concurrent users : 50+ (avec infrastructure actuelle)
- Appels simultanés : Limité par ElevenLabs (5-10)
- Stockage : PostgreSQL scale linéairement

---

## 🎓 Scénarios Disponibles

1. **SaaS B2B** - Vente de logiciel entreprise
2. **Freelance** - Négociation tarif développeur
3. **Salary** - Négociation salariale (recruteur)
4. **Partnership** - Partenariat commercial B2B
5. **Real Estate** - Achat immobilier

Chaque scénario a :
- Persona IA différente
- Tactiques spécifiques
- Objectifs adaptés
- Prompt personnalisé

---

## 🐛 Troubleshooting Rapide

**L'appel ne se lance pas**
```bash
docker-compose logs backend | grep "agent_phone_number_id"
# Vérifier que la variable est configurée
```

**Le webhook ne fonctionne pas**
```bash
curl https://your-ngrok-url.ngrok-free.app/health
# Doit retourner 200 OK
```

**Mistral est lent**
```bash
# Vérifier les crédits API
# Passer à mistral-small-latest si besoin
```

**Frontend ne compile pas**
```bash
cd frontend && npm install
# Vérifier que axios est installé
```

---

## 📱 Contact & Support

- **Issues** : Créez une issue GitHub
- **Questions** : Consultez les docs ci-dessus
- **Contributions** : Pull requests bienvenues !

---

## 📄 Licence

Ce projet est sous licence MIT - voir le fichier LICENSE pour plus de détails.

---

**Prêt pour la démo ? Suivez [DEMO_EXAMPLE.md](./DEMO_EXAMPLE.md) ! 🚀**
