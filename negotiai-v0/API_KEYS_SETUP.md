# 🔑 API Keys Setup Guide

## Current Issue

Your NegotiAI v0 application is using **placeholder API keys** which causes:
- ❌ Mistral research returning fallback data ("Feature 1, Feature 2, Feature 3")
- ❌ ElevenLabs Conversational AI returning 405 errors

## Required API Keys

You need to obtain and configure **3 API keys** in your `.env` file:

### 1. Mistral AI API Key 🤖

**What it's used for:**
- Web research on products and clients before negotiation
- Intelligent opponent conversation responses
- Tactical suggestions during negotiation
- Negotiation strategy generation and analysis

**How to get it:**
1. Go to https://console.mistral.ai/
2. Create an account (free tier available)
3. Navigate to "API Keys" section
4. Click "Create new key"
5. Copy the key (starts with something like `sk-...` or similar)

**Free tier limits:**
- Mistral offers free credits for new accounts
- Sufficient for testing and development

### 2. ElevenLabs API Key 🎤

**What it's used for:**
- Voice-to-voice conversation with AI opponent (Conversational AI)
- Text-to-Speech for opponent responses
- Voice cloning for auto-pilot mode

**How to get it:**
1. Go to https://elevenlabs.io/
2. Sign up for an account
3. Navigate to your profile → "API Keys"
4. Copy your API key

**Important notes:**
- Free tier: 10,000 characters/month
- Conversational AI may require paid plan or special access
- For testing, text mode works without Conversational AI

### 3. Qdrant API Key (Optional) 🔍

**What it's used for:**
- Vector database for negotiation tactics retrieval
- Optional - app will work without it

**How to get it:**
1. Go to https://cloud.qdrant.io/
2. Create a free account
3. Create a new cluster
4. Copy your cluster URL and API key

**Note:** Qdrant is optional. The app will work without it.

## Configuration Steps

### Step 1: Open your `.env` file

```bash
cd negotiai-v0
nano .env  # or use your preferred text editor
```

### Step 2: Replace placeholder values

**BEFORE (current):**
```env
MISTRAL_API_KEY=your_mistral_key_here
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your_qdrant_key_here
ELEVENLABS_API_KEY=your_elevenlabs_key_here
```

**AFTER (example with real keys):**
```env
MISTRAL_API_KEY=sk-abc123def456...  # Your actual Mistral key
QDRANT_URL=https://xyz-cluster.qdrant.io  # Your actual Qdrant URL (optional)
QDRANT_API_KEY=abc123...  # Your actual Qdrant key (optional)
ELEVENLABS_API_KEY=a1b2c3d4...  # Your actual ElevenLabs key
```

### Step 3: Rebuild and restart Docker containers

```bash
docker compose down
docker compose up --build
```

### Step 4: Verify setup

Check the backend logs for successful initialization:

```bash
docker compose logs backend | grep "initialized"
```

You should see:
```
✅ Mistral service initialized
✅ Web Research Service initialized
✅ ElevenLabs Conversational AI initialized
```

## Troubleshooting

### Issue: "Services not available" errors

**Solution:** Make sure your `.env` file:
- Has real API keys (not placeholders)
- Is in the correct location (`negotiai-v0/.env`)
- Has been reloaded (restart Docker containers)

### Issue: Mistral API still returning fallback data

**Solution:**
1. Verify your Mistral API key is valid:
   ```bash
   curl https://api.mistral.ai/v1/models \
     -H "Authorization: Bearer YOUR_MISTRAL_API_KEY"
   ```
2. Check you have remaining credits
3. Look at backend logs for detailed error messages

### Issue: ElevenLabs 405 errors

**Potential causes:**
1. Invalid API key → Get a valid key from ElevenLabs
2. Conversational AI not available on your plan → Upgrade or use text mode
3. API endpoint changed → Check ElevenLabs docs

**Workaround:** Use text mode instead of voice mode for testing

## Cost Estimates

**Free tier testing (recommended for development):**
- Mistral AI: Free credits for new accounts
- ElevenLabs: 10,000 characters/month free
- Qdrant: 1GB free cluster

**Total: $0/month** for basic testing

**Production usage (estimated):**
- Mistral AI: ~$2-10/month depending on usage
- ElevenLabs: ~$5-30/month for voice features
- Qdrant: Free tier sufficient for MVP

## Next Steps

After configuring API keys:

1. ✅ Test Mistral research: Should return real product/client data
2. ✅ Test text mode simulation: Should have intelligent opponent responses
3. ✅ Test voice mode (if ElevenLabs Conversational AI available)
4. ✅ Review backend logs to ensure no errors

## Need Help?

- Mistral AI docs: https://docs.mistral.ai/
- ElevenLabs docs: https://elevenlabs.io/docs
- Qdrant docs: https://qdrant.tech/documentation/

---

**Remember:** Never commit your `.env` file with real API keys to version control!
