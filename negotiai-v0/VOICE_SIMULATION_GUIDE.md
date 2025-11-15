# 🎤 Guide: Simulation Vocale avec ElevenLabs

## Vue d'ensemble

La simulation vocale utilise **ElevenLabs Conversational AI** pour créer une expérience de négociation vocale en temps réel. Vous parlez directement avec un agent IA qui joue le rôle d'un client difficile.

## Architecture

```
┌─────────────┐
│   Mistral   │ ──► Recherche pré-négociation (produit + client)
└─────────────┘

┌─────────────┐
│   Mistral   │ ──► Création du prompt de l'agent IA
└─────────────┘

┌─────────────────────────────────────────────────────┐
│          ElevenLabs Conversational AI               │
│  ┌─────────┐    ┌──────────┐    ┌────────────┐    │
│  │   STT   │───►│ AI Logic │───►│    TTS     │    │
│  │(Whisper)│    │(LLM+RAG) │    │ (Rachel)   │    │
│  └─────────┘    └──────────┘    └────────────┘    │
└─────────────────────────────────────────────────────┘
         ▲                                    │
         │                                    ▼
    Voix Utilisateur              Audio Réponse Agent
```

## Flux de Fonctionnement

### 1. **Recherche Pré-Négociation** (Optionnel mais recommandé)

L'utilisateur entre:
- **Nom du produit** (requis): ex. "Plateforme SaaS Analytics"
- **Nom de l'entreprise cliente** (optionnel): ex. "Acme Corp"
- **Secteur d'activité** (optionnel): ex. "E-commerce"

**Backend** (`POST /api/simulation/research`):
```python
# web_research_service.py utilise Mistral pour rechercher:
- Caractéristiques du produit
- Prix marché typique
- Concurrents principaux
- Position marché
- Taille de l'entreprise cliente
- Budget estimé
- Points de douleur
- Facteurs de décision
```

**Frontend** affiche les résultats de recherche avant de démarrer.

### 2. **Création de l'Agent IA**

L'utilisateur choisit le mode:
- **🎤 Voice-to-Voice**: Conversation vocale en temps réel
- **⌨️ Texte (Demo)**: Simulation textuelle classique

**Backend** (`POST /api/simulation/setup`):
```python
# elevenlabs_agent_service.py crée un agent avec:
- Système prompt enrichi avec données de recherche
- Voix française professionnelle (Rachel)
- Tactiques de négociation (lowball, urgence, objections...)
- Progression adaptative (ferme → évalue → intéressé)

# Retourne:
{
  "agent_id": "agent_123",
  "conversation_id": "conv_456",
  "websocket_url": "wss://api.elevenlabs.io/v1/convai/conversation?agent_id=agent_123"
}
```

### 3. **Connexion WebSocket et Conversation**

**Frontend** (`ElevenLabsVoiceChat.jsx`):

#### 3.1 Initialisation
```javascript
// Demande permission microphone
const stream = await navigator.mediaDevices.getUserMedia({
  audio: {
    channelCount: 1,
    sampleRate: 16000,
    echoCancellation: true,
    noiseSuppression: true
  }
});

// Connexion WebSocket ElevenLabs
const ws = new WebSocket(
  `wss://api.elevenlabs.io/v1/convai/conversation?agent_id=${agentId}`
);
```

#### 3.2 Streaming Audio Sortant (Utilisateur → ElevenLabs)
```javascript
// Capture audio micro en temps réel
const processor = audioContext.createScriptProcessor(4096, 1, 1);

processor.onaudioprocess = (e) => {
  const inputData = e.inputBuffer.getChannelData(0);

  // Conversion Float32 → Int16 PCM
  const pcmData = new Int16Array(inputData.length);
  for (let i = 0; i < inputData.length; i++) {
    const s = Math.max(-1, Math.min(1, inputData[i]));
    pcmData[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
  }

  // Envoi à ElevenLabs
  ws.send(pcmData.buffer);
};
```

#### 3.3 Réception Messages ElevenLabs
```javascript
ws.onmessage = (event) => {
  const message = JSON.parse(event.data);

  switch (message.type) {
    case 'user_transcript':
      // Transcription de ce que l'utilisateur a dit
      addTranscript('user', message.transcript);
      break;

    case 'agent_response':
      // L'agent commence à parler
      addTranscript('agent', message.transcript);
      break;

    case 'audio':
      // Chunk audio de la réponse de l'agent
      playAudioChunk(message.audio);
      break;

    case 'interruption':
      // L'utilisateur a interrompu l'agent
      stopCurrentAudio();
      break;
  }
};
```

#### 3.4 Lecture Audio Entrant (ElevenLabs → Haut-parleurs)
```javascript
const playAudioChunk = async (audioBlob) => {
  const arrayBuffer = await audioBlob.arrayBuffer();
  const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);

  const source = audioContext.createBufferSource();
  source.buffer = audioBuffer;
  source.connect(audioContext.destination);
  source.start(0);
};
```

## Fichiers Impliqués

### Backend

| Fichier | Rôle |
|---------|------|
| `services/web_research_service.py` | Recherche Mistral sur produit/client |
| `services/elevenlabs_agent_service.py` | Création agent ElevenLabs |
| `main.py` | Endpoints `/api/simulation/research` et `/api/simulation/setup` |

### Frontend

| Fichier | Rôle |
|---------|------|
| `pages/SimulationPage.jsx` | Formulaire recherche + sélection mode |
| `components/ElevenLabsVoiceChat.jsx` | Connexion WebSocket + streaming audio |
| `components/VoiceSimulator.jsx` | Mode texte (fallback) |

## Utilisation

### Démarrage

```bash
cd negotiai-v0
docker compose up --build
```

### Test Complet

1. **Ouvrir** http://localhost:3000
2. **Cliquer** sur "🎤 Simulation Live"
3. **Remplir** le formulaire de recherche:
   ```
   Produit: Plateforme SaaS Analytics
   Entreprise: TechCorp (optionnel)
   Secteur: Finance (optionnel)
   ```
4. **Cliquer** "🚀 Lancer la recherche"
5. **Vérifier** les résultats de recherche
6. **Sélectionner** "🎤 Voice-to-Voice"
7. **Cliquer** "🎤 Démarrer la Conversation Vocale"
8. **Autoriser** l'accès au microphone
9. **Parler** naturellement avec l'agent IA

### États de la Conversation

| État | Emoji | Description |
|------|-------|-------------|
| `initializing` | ⏳ | Création de l'agent IA en cours |
| `ready` | ▶️ | Prêt à démarrer |
| `connecting` | 🔌 | Connexion WebSocket en cours |
| `connected` | ✅ | Connecté - vous pouvez parler |
| `listening` | 👂 | L'agent vous écoute |
| `speaking` | 🗣️ | L'agent parle |
| `error` | ❌ | Erreur de connexion |

### Contrôles Disponibles

- **🎤 Couper micro**: Désactive temporairement le microphone (vous n'êtes plus entendu)
- **⏹️ Terminer**: Arrête la conversation et retourne au setup

## Exemple de Conversation

```
🗣️ Agent IA:
"Bonjour, merci de me recevoir. J'ai regardé votre plateforme SaaS Analytics
et ça m'intéresse, mais franchement 50 000€ par an, c'est vraiment trop cher
pour nous."

👂 Vous (parlez au micro):
"Je comprends votre préoccupation sur le prix. Mais regardons le ROI : avec
nos clients, on observe un gain de productivité de 35% en 3 mois..."

🗣️ Agent IA:
"Oui mais vos concurrents comme Tableau ou Power BI proposent des solutions
similaires à 35 000€. Comment vous justifiez cette différence ?"

👂 Vous:
"Excellente question. La différence c'est notre support 24/7 dédié et
l'intégration custom incluse. Nos concurrents facturent ça en supplément..."
```

## Prompt de l'Agent IA

Le prompt est construit dynamiquement avec les données de recherche:

```python
# elevenlabs_agent_service.py - _build_agent_prompt()

prompt = f"""Tu es un client professionnel qui négocie l'achat de "{product}".

CONTEXTE DE LA NÉGOCIATION:
- Produit proposé: {product}
- Prix demandé par le vendeur: {target_price}
- Concurrents connus: {competitors}  # ← Vient de la recherche Mistral
- Ton objectif: Obtenir le meilleur prix possible

TON PROFIL CLIENT:
- Taille entreprise: {company_size}  # ← Vient de la recherche Mistral
- Budget type: {budget_range}        # ← Vient de la recherche Mistral
- Tes priorités: {pain_points}       # ← Vient de la recherche Mistral

TON RÔLE EN NÉGOCIATION:
- Tu es un acheteur B2B expérimenté et professionnel
- Tu négocies fermement mais respectueusement
- Tu utilises des tactiques de négociation réalistes:
  * Comparaison avec concurrents
  * Questions sur le ROI et la valeur
  * Pression sur les prix et délais
  * Objections sur les fonctionnalités manquantes

TACTIQUES À UTILISER (varie selon le contexte):
1. LOWBALL: "C'est trop cher, {competitor} propose moins"
2. URGENCE: "J'ai besoin d'une décision rapide"
3. BUDGET: "Mon budget maximum est limité à X"
4. OBJECTION: "Il manque telle fonctionnalité importante"
5. CONCESSION: Si l'argument est solide, montre de l'intérêt mais négocie encore

PROGRESSION:
- Début (tours 1-3): Sois ferme sur le prix, questionne la valeur
- Milieu (tours 4-6): Évalue sérieusement les arguments, négocie les détails
- Fin (tours 7+): Si le deal est bon, montre des signes d'accord (mais négocie encore un peu)

IMPORTANT:
- Parle en français naturel
- Garde des réponses courtes (2-3 phrases max)
- Réagis directement à ce que dit le vendeur
"""
```

## Configuration ElevenLabs

```python
# elevenlabs_agent_service.py - create_negotiation_agent()

agent_config = {
    "name": f"Negotiation Opponent - {product}",
    "voice_id": "21m00Tcm4TlvDq8ikWAM",  # Rachel (professionnelle)
    "language": "fr",  # Français
    "conversation_config": {
        "agent": {
            "prompt": {"prompt": system_prompt},
            "first_message": first_message  # Message d'ouverture
        },
        "tts": {
            "model_id": "eleven_turbo_v2_5",  # Modèle rapide
            "voice_settings": {
                "stability": 0.5,          # Naturel
                "similarity_boost": 0.75    # Fidélité voix
            }
        }
    }
}
```

## Dépannage

### Erreur: "Microphone non autorisé"
**Solution**: Autoriser l'accès au microphone dans les paramètres du navigateur
- Chrome: Icône 🔒 dans la barre d'adresse → Autorisations
- Firefox: Icône 🛡️ → Permissions → Microphone

### Erreur: "ElevenLabs Conversational AI not available"
**Solution**: Vérifier la clé API ElevenLabs dans `.env`:
```bash
ELEVENLABS_API_KEY=votre_clé_ici
```

### Erreur: "Web Research Service not available"
**Solution**: Vérifier la clé API Mistral dans `.env`:
```bash
MISTRAL_API_KEY=votre_clé_ici
```

### L'agent ne répond pas
**Solutions**:
1. Vérifier la connexion WebSocket dans la console développeur
2. Vérifier que le microphone fonctionne (indicateur dans le navigateur)
3. Parler plus fort ou se rapprocher du micro
4. Vérifier les logs backend: `docker compose logs -f backend`

### Audio haché ou coupé
**Solutions**:
1. Vérifier la connexion Internet (WebSocket temps réel)
2. Réduire le bruit ambiant
3. Utiliser un casque avec micro intégré

## Limites Actuelles

### ✅ Implémenté
- ✅ Recherche pré-négociation avec Mistral
- ✅ Création d'agent ElevenLabs Conversational AI
- ✅ Connexion WebSocket bidirectionnelle
- ✅ Streaming audio utilisateur → ElevenLabs
- ✅ Réception et lecture audio agent
- ✅ Transcription en temps réel
- ✅ Contrôle micro (mute/unmute)

### 🚧 À Implémenter
- ⏳ **Voice cloning**: Cloner la voix de l'utilisateur pour l'auto-pilot
- ⏳ **Auto-pilot mode**: L'IA répond à votre place avec votre voix clonée
- ⏳ **Suggestions tactiques**: Afficher des suggestions pendant la conversation
- ⏳ **Pattern detection**: Détecter les tactiques utilisées par l'agent
- ⏳ **Analyse post-conversation**: Rapport de performance détaillé

## Prochaines Étapes

### 1. Voice Cloning pour Auto-Pilot

```python
# elevenlabs_agent_service.py - À ajouter

async def clone_user_voice(self, audio_sample: bytes, name: str) -> str:
    """
    Clone user voice from 30-60s audio sample

    Args:
        audio_sample: WAV audio (30-60s)
        name: Voice name

    Returns:
        voice_id: Cloned voice ID
    """
    response = await client.post(
        f"{self.base_url}/voices/add",
        headers={"xi-api-key": self.api_key},
        files={"files": ("sample.wav", audio_sample, "audio/wav")},
        data={"name": name}
    )

    return response.json()["voice_id"]
```

### 2. Intégration Suggestions Tactiques

Combiner:
- `realtime_analyzer.py` (suggestions existantes)
- `ElevenLabsVoiceChat.jsx` (affichage pendant conversation)

### 3. Mode Auto-Pilot Vocal

```javascript
// ElevenLabsVoiceChat.jsx - À ajouter

const activateAutoPilot = async (tactic) => {
  // Générer réponse avec tactique recommandée
  const response = await fetch('/api/autopilot/generate', {
    method: 'POST',
    body: JSON.stringify({
      tactic,
      context,
      conversation_history: transcript
    })
  });

  const { text, audio_with_cloned_voice } = await response.json();

  // Jouer audio avec voix clonée
  playAudio(audio_with_cloned_voice);
};
```

## API Reference

### POST `/api/simulation/research`

**Request**:
```json
{
  "product_name": "Plateforme SaaS Analytics",
  "company_name": "Acme Corp",  // optionnel
  "industry": "E-commerce"       // optionnel
}
```

**Response**:
```json
{
  "product": {
    "name": "Plateforme SaaS Analytics",
    "features": ["Dashboard temps réel", "Prédictions ML", "API complète"],
    "typical_pricing": "30 000€ - 60 000€/an selon taille",
    "competitors": ["Tableau", "Power BI", "Looker"],
    "market_position": "Premium avec support dédié",
    "key_benefits": ["ROI rapide", "Support 24/7", "Intégrations custom"]
  },
  "client": {
    "name": "Acme Corp",
    "company_size": "PME (50-200 employés)",
    "industry": "E-commerce",
    "pain_points": ["Données dispersées", "Reporting manuel", "Décisions lentes"],
    "budget_range": "20 000€ - 50 000€/an",
    "decision_factors": ["ROI", "Facilité d'usage", "Support"]
  }
}
```

### POST `/api/simulation/setup`

**Request**:
```json
{
  "product": "Plateforme SaaS Analytics",
  "target_price": "50000€/an",
  "minimum_price": "35000€/an",
  "value_props": ["ROI 3x en 6 mois", "Support 24/7", "Intégration custom"],
  "opponent_goal": "Obtenir le meilleur prix",
  "research_data": { /* Résultat de /api/simulation/research */ }
}
```

**Response**:
```json
{
  "status": "ready",
  "agent_id": "agent_abc123",
  "conversation_id": "conv_xyz789",
  "websocket_url": "wss://api.elevenlabs.io/v1/convai/conversation?agent_id=agent_abc123",
  "message": "ElevenLabs Conversational AI agent ready for voice simulation"
}
```

## Performance

### Latence Typique

| Opération | Temps |
|-----------|-------|
| Recherche Mistral (produit + client) | 3-5s |
| Création agent ElevenLabs | 1-2s |
| STT (parole → texte) | ~500ms |
| AI réponse (LLM) | 1-2s |
| TTS (texte → audio) | ~800ms |
| **Latence totale conversation** | **2-3s** |

### Optimisations Possibles

- Streaming TTS progressif (audio par chunks)
- Cache des réponses communes
- Pré-chargement des tactiques fréquentes

---

**Version**: 1.0
**Dernière mise à jour**: 2025-01-15
**Statut**: ✅ Voice-to-Voice opérationnel | ⏳ Auto-pilot en développement
