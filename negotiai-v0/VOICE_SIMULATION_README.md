# 🎤 NegotiAI - Simulation Vocale Temps Réel

## 🚀 Nouvelle Fonctionnalité Hackathon

Cette version ajoute la **simulation vocale en temps réel** à NegotiAI, permettant aux utilisateurs de s'entraîner à négocier contre une IA qui joue un client difficile, avec des suggestions tactiques instantanées et un mode auto-pilot révolutionnaire.

---

## ✨ Fonctionnalités Principales

### 1️⃣ Simulation Conversationnelle
- **IA Opponent** qui joue un client difficile avec des tactiques réalistes
- Scripts de négociation pré-programmés (7 tours de conversation)
- Audio généré par ElevenLabs pour réponses du client
- Transcription temps réel de la conversation

### 2️⃣ Suggestions Tactiques Instantanées
- **Détection de patterns** en temps réel :
  - 💰 Lowball (prix trop bas)
  - ⚠️ False Urgency (fausse urgence)
  - 🛡️ Aggressive tactics (tactiques agressives)
  - 📊 Comparaison avec concurrents
  - 🔧 Objections features
  - ✅ Signaux positifs
- **Analyse IA** avec Mistral pour suggestions contextuelles
- **Priorités** : Critical, High, Medium
- **Explications** du raisonnement tactique

### 3️⃣ Mode Auto-Pilot 🤖
- L'IA peut **répondre à votre place** avec la tactique recommandée
- Utilise ElevenLabs Voice Cloning (optionnel)
- Génère des réponses tactiques personnalisées
- 6 tactiques disponibles :
  - `counter_lowball` : Contre-argument sur le ROI
  - `expose_urgency` : Questionner la vraie deadline
  - `firm_boundary` : Annoncer le prix minimum
  - `value_justification` : Justifier la valeur
  - `confident_close` : Closer avec confiance
  - `deflect_objection` : Répondre aux objections

### 4️⃣ Trois Scénarios Pré-Configurés
1. **💼 SaaS B2B** : Vendre une plateforme analytics à 50K€/an
2. **💻 Freelance Dev** : Négocier un TJM de 800€/jour
3. **🏠 Immobilier** : Acheter un appartement à Paris

---

## 🏗️ Architecture Technique

```
Frontend (React)          WebSocket           Backend (FastAPI)
     │                       ↕️                       │
     ├── VoiceSimulator ─────────────→  WebSocket Handler
     ├── SuggestionPanel                      │
     ├── AutoPilotButton                      ├── RealtimeAnalyzer
     │                                        │   ├── Mistral AI
     │                                        │   └── Qdrant
     │                                        │
     └── SimulationPage                       ├── ElevenLabsVoiceAgent
                                              │   ├── Text-to-Speech
                                              │   └── Voice Cloning
                                              │
                                              └── PatternDetector
```

### Nouveaux Modules Backend

#### `audio/elevenlabs_client.py`
- Client ElevenLabs pour génération audio
- Création d'agents conversationnels
- Clonage de voix pour auto-pilot
- Génération de réponses tactiques

#### `audio/pattern_detector.py`
- Détection de 9 patterns critiques
- Analyse combo patterns
- Scoring de confiance
- Historique conversationnel

#### `ai/realtime_analyzer.py`
- Analyse temps réel avec Mistral
- Recherche de tactiques similaires (Qdrant)
- Génération de suggestions contextuelles
- Résumé de conversation

#### `websocket_handler.py`
- Gestion sessions WebSocket
- Streaming bidirectionnel audio/texte
- Coordination opponent/user/autopilot
- Gestion état conversation

#### `demo_scenario.py`
- 3 scénarios pré-configurés
- Scripts opponents réalistes
- Métriques de succès

### Nouveaux Composants Frontend

#### `components/VoiceSimulator.jsx`
- Interface principale simulation
- Connexion WebSocket
- Affichage transcript temps réel
- Contrôle audio playback
- Input utilisateur

#### `components/SuggestionPanel.jsx`
- Affichage suggestion tactique
- Badge priorité (critical/high/medium)
- Bouton activation auto-pilot
- Historique suggestions

#### `components/AutoPilotButton.jsx`
- Toggle mode auto-pilot
- Indicateur disponibilité
- États actif/inactif

#### `pages/SimulationPage.jsx`
- Page d'accueil simulation
- Sélection scénario
- Instructions utilisation
- Lancement simulation

---

## 🚦 Démarrage Rapide

### 1. Installation

```bash
cd negotiai-v0

# Backend
cd backend
pip install -r requirements.txt  # Installe websockets, httpx, elevenlabs

# Frontend (pas de nouveaux packages nécessaires)
cd ../frontend
npm install
```

### 2. Configuration

Assurez-vous que votre `.env` contient :

```bash
# Obligatoire pour simulation
MISTRAL_API_KEY=your_key_here
ELEVENLABS_API_KEY=your_key_here

# Optionnel (améliore suggestions)
QDRANT_URL=your_qdrant_url
QDRANT_API_KEY=your_qdrant_key
```

### 3. Lancement

```bash
# Terminal 1 : Backend
cd backend
python main.py
# ou
uvicorn main:app --reload

# Terminal 2 : Frontend
cd frontend
npm start
```

### 4. Accès

- Frontend : http://localhost:3000
- Cliquez sur **"🎤 Simulation Live"** dans la navigation
- Choisissez un scénario (SaaS, Freelance, Immobilier)
- Cliquez **"Démarrer la Simulation"**

---

## 🎮 Guide d'Utilisation

### Étape 1 : Sélection du Scénario

1. Accédez à la page Simulation via le menu
2. Choisissez parmi 3 scénarios :
   - **💼 SaaS B2B** : Négociation complexe (7 tours)
   - **💻 Freelance** : Négociation rapide (4 tours)
   - **🏠 Immobilier** : Négociation modérée (4 tours)
3. Lisez les détails (prix cible, minimum, value props)

### Étape 2 : Déroulement de la Simulation

1. **Le client IA parle en premier**
   - Audio généré automatiquement
   - Transcript affiché en temps réel
   - Pattern détecté (si applicable)

2. **Vous recevez une suggestion tactique**
   - Apparaît dans le panneau de droite
   - Indique la priorité (⚠️ Critical, 🔸 High, 🔹 Medium)
   - Explique le raisonnement
   - Propose une action concrète

3. **Vous répondez (2 options)**

   **Option A : Réponse manuelle**
   - Tapez votre réponse dans le champ texte
   - Appuyez sur Entrée ou cliquez "Envoyer"
   - Votre réponse est ajoutée au transcript

   **Option B : Auto-Pilot 🤖**
   - Cliquez sur "🤖 Activer" dans la suggestion
   - L'IA génère une réponse tactique optimale
   - Audio joué automatiquement (optionnel)
   - Réponse ajoutée au transcript avec badge "Auto-Pilot"

4. **Le cycle continue**
   - Le client IA réagit à votre réponse
   - Nouvelle suggestion générée
   - Patterns détectés s'accumulent

### Étape 3 : Fin de Simulation

- Après 4-7 tours (selon le scénario)
- Message de fin : "🏁 Simulation terminée"
- Résumé des patterns détectés
- Stats de la conversation

---

## 🔥 Exemples de Patterns Détectés

### Pattern : Lowball (Prix Bas)

**Client dit :**
> "50 000 euros, c'est vraiment trop cher. Vos concurrents font 30K."

**Suggestion :**
> 💡 Comparaison de prix détectée → Parlez ROI, pas prix

**Auto-Pilot répond :**
> "Je comprends votre comparaison, mais regardons le ROI réel. Avec notre solution, vous économisez 150K€ en 6 mois. Si on compare la valeur totale plutôt que juste le prix, on est largement compétitifs."

---

### Pattern : False Urgency (Fausse Urgence)

**Client dit :**
> "Je dois prendre une décision aujourd'hui, c'est urgent."

**Suggestion :**
> ⚠️ FAUSSE URGENCE → Demandez: 'Quelle est la vraie deadline?'

**Auto-Pilot répond :**
> "J'apprécie votre intérêt. Puis-je vous demander : qu'est-ce qui motive cette deadline aujourd'hui précisément ? Souvent, prendre une semaine de plus permet d'éviter des regrets."

---

### Pattern : Positive Signal (Opportunité)

**Client dit :**
> "OK, 40 000 euros avec formation, ça pourrait marcher."

**Suggestion :**
> ✅ SIGNAL POSITIF → C'est le moment de closer!

**Auto-Pilot répond :**
> "Parfait ! Basé sur notre discussion, je propose 42K€ avec formation premium, support 6 mois, et paiement en 3 fois. On signe cette semaine ?"

---

## 📊 API WebSocket

### Endpoint

```
ws://localhost:8000/ws/simulation
```

### Messages Client → Serveur

```javascript
// Démarrer simulation
{
  "type": "start",
  "context": {
    "product": "...",
    "target_price": "...",
    "opponent_script": [...]
  }
}

// Envoyer réponse utilisateur
{
  "type": "transcript",
  "text": "Votre réponse..."
}

// Activer auto-pilot
{
  "type": "autopilot_activate",
  "tactic": "counter_lowball"
}

// Arrêter simulation
{
  "type": "stop"
}
```

### Messages Serveur → Client

```javascript
// Status update
{
  "type": "status",
  "message": "Simulation ready!"
}

// Transcript
{
  "type": "transcript",
  "speaker": "opponent"|"user"|"user_autopilot",
  "text": "...",
  "turn": 3
}

// Audio opponent
{
  "type": "opponent_audio",
  "audio": "base64_mp3_data",
  "format": "mp3"
}

// Suggestion tactique
{
  "type": "suggestion",
  "suggestion": "💡 Action à faire",
  "priority": "critical"|"high"|"medium",
  "tactic": "counter_lowball",
  "autopilot_available": true,
  "reasoning": "Explication..."
}

// Audio auto-pilot
{
  "type": "autopilot_audio",
  "audio": "base64_mp3_data",
  "tactic": "counter_lowball"
}

// Résumé session
{
  "type": "summary",
  "data": {
    "total_turns": 7,
    "pattern_frequency": {...}
  }
}
```

---

## 🧪 Tests et Validation

### Test Rapide (2 minutes)

1. Lancer l'app
2. Aller sur "🎤 Simulation Live"
3. Choisir "💻 Freelance Dev"
4. Démarrer
5. Attendre la première phrase du client
6. Vérifier :
   - ✅ Audio joue
   - ✅ Transcript s'affiche
   - ✅ Suggestion apparaît
7. Taper une réponse et envoyer
8. Vérifier :
   - ✅ Réponse ajoutée au transcript
   - ✅ Client répond (tour 2)
9. Cliquer "🤖 Activer" sur une suggestion
10. Vérifier :
    - ✅ Auto-pilot génère réponse
    - ✅ Audio joue (optionnel)
    - ✅ Badge "Auto-Pilot" visible

### Test Complet (5 minutes)

1. Tester les 3 scénarios
2. Essayer chaque mode (manuel + auto-pilot)
3. Vérifier patterns détectés :
   - Lowball
   - False urgency
   - Positive signal
4. Aller jusqu'à la fin (7 tours pour SaaS)
5. Vérifier résumé final

---

## 🐛 Dépannage

### Problème : WebSocket ne se connecte pas

**Symptôme** : Status "error" ou "disconnected"

**Solution** :
```bash
# Vérifier que le backend tourne
curl http://localhost:8000/

# Vérifier les logs backend
# Doit afficher : "✅ Realtime Analyzer initialized"
```

### Problème : Pas d'audio

**Symptôme** : Transcript s'affiche mais pas de son

**Causes possibles** :
1. ElevenLabs API key manquante
2. Quota ElevenLabs dépassé
3. Browser bloque autoplay

**Solution** :
- Vérifier `.env` contient `ELEVENLABS_API_KEY`
- Vérifier quota sur https://elevenlabs.io/
- Cliquer sur la page pour autoriser audio

### Problème : Suggestions génériques

**Symptôme** : Suggestions non contextuelles

**Cause** : Qdrant non configuré

**Solution** :
- Configurer Qdrant dans `.env`
- Ou accepter suggestions basiques (fonctionne quand même)

### Problème : Auto-pilot ne répond pas

**Symptôme** : Bouton auto-pilot grisé

**Cause** : Aucune tactique détectée

**Explication** :
- Auto-pilot n'est disponible que si un pattern critique est détecté
- Normal si conversation est normale sans tactique agressive

---

## 🎯 Checklist MVP Hackathon

- [x] Connexion WebSocket fonctionnelle
- [x] Client IA joue le opponent
- [x] Génération audio ElevenLabs
- [x] Détection patterns temps réel
- [x] Suggestions tactiques Mistral
- [x] Mode auto-pilot opérationnel
- [x] 3 scénarios pré-configurés
- [x] UI responsive et claire
- [x] Transcript en temps réel
- [x] Panneau suggestions dynamique

---

## 🚀 Démo Vidéo (2 minutes)

### Scénario Recommandé : SaaS B2B

**0:00-0:30** - Montrer le problème
- "Voici comment on se fait lowballer en négociation..."
- Client dit : "50K c'est trop cher, concurrent fait 30K"
- Sans aide = accepter ou perdre le deal

**0:30-1:30** - Solution avec NegotiAI
- Lancer simulation SaaS
- Client opponent attaque avec lowball
- Suggestion apparaît : "💡 Parlez ROI, pas prix"
- Taper réponse manuelle (montre ROI)
- Client contre avec false urgency
- Nouvelle suggestion : "⚠️ FAUSSE URGENCE"

**1:30-1:50** - Killer Feature : Auto-Pilot
- Cliquer "🤖 Activer"
- IA génère réponse tactique parfaite
- Audio joue
- Client accepte le deal

**1:50-2:00** - Résultat
- Deal conclu à 42K€ (vs 30K initial)
- +40% vs concurrent
- Message : "Avec NegotiAI, vous ne vous faites plus avoir"

---

## 📈 Métriques de Succès

### Pendant Démo
- ⏱️ Temps de setup : < 10 secondes
- 🎯 Patterns détectés : 3-5 par simulation
- 💬 Fluidité conversation : < 2s entre tours
- 🤖 Auto-pilot activation : 1-2 fois
- 🎤 Audio quality : Clair et naturel

### Objectifs Hackathon
- ✅ 5+ technologies utilisées (FastAPI, React, Mistral, ElevenLabs, Qdrant, WebSocket, PostgreSQL)
- ✅ Feature innovante (Auto-pilot avec voice cloning)
- ✅ Temps réel (< 2s latence)
- ✅ Production-ready UI
- ✅ Demo-able en 2 minutes

---

## 🎓 Pour Aller Plus Loin

### Améliorations Possibles

1. **Vraie reconnaissance vocale**
   - Intégrer Whisper API pour transcription
   - Parler au lieu de taper

2. **Multi-langue**
   - Détection langue automatique
   - Suggestions dans langue conversation

3. **Historique et Analytics**
   - Sauvegarder simulations en DB
   - Graphiques progression
   - Replay conversations

4. **Custom Scenarios**
   - Créer ses propres scénarios
   - Uploader scripts opponents
   - Partager avec équipe

5. **Multiplayer**
   - 2 humains négocient
   - IA observe et suggère aux 2
   - Mode training en équipe

---

## 📞 Support

Pour questions ou problèmes :
1. Vérifier ce README
2. Consulter logs backend (patterns détectés, erreurs)
3. Tester avec scénario simple (Freelance = 4 tours seulement)
4. Vérifier API keys valides

---

**Built with ❤️ for the hackathon!**

**Stack**: FastAPI • React • Mistral AI • ElevenLabs • Qdrant • WebSocket
