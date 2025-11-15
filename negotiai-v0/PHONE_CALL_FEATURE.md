# 📞 Phone Call Feature - Real Negotiation Training

## Overview

The **Phone Call Feature** allows users to receive **real phone calls** on their mobile/landline for negotiation practice with an AI-powered opponent. This provides the most immersive and realistic training experience possible.

## How It Works

### User Flow

1. **Choose Scenario**
   - Select from 5 pre-configured negotiation scenarios
   - Each scenario has specific tactics and objectives

2. **Configure Context**
   - Product/service to negotiate
   - Target price
   - Minimum acceptable price
   - Red lines (non-negotiable points)

3. **Enter Phone Number**
   - Provide phone number in international format
   - Example: +33612345678

4. **Receive Call**
   - Call arrives within ~10 seconds
   - AI opponent initiates negotiation
   - Real-time conversation

5. **Negotiate**
   - Practice negotiation tactics
   - Handle objections
   - Close the deal (or walk away)

6. **Get Analysis**
   - Complete performance report
   - Score breakdown (0-10)
   - Detected tactics
   - Good/bad responses with quotes
   - Actionable recommendations
   - Full transcript

## Available Scenarios

### 1. SaaS B2B (saas)
**Context:** Negotiating SaaS solution pricing
**Opponent tactics:**
- Lowball initial offer (50% reduction)
- Fake urgency ("need decision this week")
- Competitor comparison
- Budget constraints

**Goal:** Get minimum 40% discount

### 2. Freelance Rate (freelance)
**Context:** Client negotiating freelancer rates
**Opponent tactics:**
- Limited budget
- Market comparison
- Volume promises
- Free revisions requests
- Deferred payment

**Goal:** Reduce hourly rate by 30%

### 3. Salary Negotiation (salary)
**Context:** Recruiter negotiating candidate salary
**Opponent tactics:**
- Low anchoring
- Budget constraints
- Future evolution promises
- Non-salary benefits emphasis
- Internal grid comparison

**Goal:** Hire 15% below candidate expectation

### 4. Commercial Partnership (partnership)
**Context:** B2B partnership negotiations
**Opponent tactics:**
- Conditional volume
- Exclusivity demands
- Payment terms
- Included support
- Contract duration

**Goal:** Maximize value, minimize commitment

### 5. Real Estate (real_estate)
**Context:** Property buyer negotiations
**Opponent tactics:**
- Property defects
- Market comparison
- Financing limitations
- Seller urgency probing
- Required renovations

**Goal:** Get 10-15% price reduction

## Technical Architecture

### Backend Components

#### `backend/calls/phone_handler.py`
- Manages phone call lifecycle
- Creates AI agent configurations
- Analyzes call performance with Mistral AI
- 5 pre-configured scenarios with personas

#### Endpoints

**GET `/api/call/scenarios`**
- Returns available scenarios

**POST `/api/call/setup`**
- Creates call session
- Generates agent configuration
- Returns session_id

**POST `/api/call/start/{session_id}`**
- Initiates phone call
- Returns call status
- Or alternatives if API unavailable

**POST `/webhook/elevenlabs/call-ended`**
- ElevenLabs webhook
- Receives transcript when call ends
- Triggers Mistral analysis
- Stores results

**GET `/api/call/results/{session_id}`**
- Retrieves analysis results
- Returns transcript, scores, recommendations

### Frontend Components

#### `PhoneCallPage.jsx`
- Main orchestrator
- Scenario selection
- Context configuration
- Flow management

#### `PhoneCallSetup.jsx`
- Phone number input
- Call initiation
- Status display
- Result polling

#### `CallResults.jsx`
- Performance dashboard
- Score visualization
- Transcript display
- Recommendations

## API Integration

### ElevenLabs Phone API (if available)

The feature is designed to work with **ElevenLabs Phone API** which provides:
- Real phone call initiation
- AI conversation handling
- Automatic transcription
- Webhook notifications

**Status:** As of implementation, ElevenLabs Phone API may not be publicly available yet.

### Fallback Strategy

If ElevenLabs Phone API is unavailable:

1. **Text Mode** (fully functional)
   - Use `SimulationPage` with text-based conversation
   - Same intelligent opponent logic
   - Same Mistral analysis

2. **WebRTC Alternative**
   - Browser-based voice call
   - No real phone involved
   - Still provides voice practice

3. **Twilio + ElevenLabs TTS**
   - Integrate Twilio for phone calls
   - Use ElevenLabs TTS for opponent voice
   - Custom conversation logic

## Configuration

### Environment Variables

```env
ELEVENLABS_API_KEY=your_actual_api_key_here
MISTRAL_API_KEY=your_actual_api_key_here
```

### Webhook Setup (if using ElevenLabs Phone API)

1. **Development (local)**
   ```bash
   # Start ngrok
   ngrok http 8000

   # Copy HTTPS URL
   # Configure in ElevenLabs dashboard
   ```

2. **Production**
   - Set public domain webhook URL
   - Configure in ElevenLabs dashboard
   - URL: `https://yourdomain.com/webhook/elevenlabs/call-ended`
   - Event: `call.ended`

## Analysis Features

### Performance Scores (0-10)

- **Preparation** - How well prepared for the scenario
- **Argumentation** - Quality of arguments
- **Objection Handling** - Response to opponent tactics
- **Outcome** - Final negotiation result
- **Global** - Overall performance

### Detected Patterns

AI identifies opponent tactics used:
- Lowball pricing
- Fake urgency
- Budget constraints
- Competitor comparisons
- Volume promises
- etc.

### User Performance Analysis

**Good Responses:**
- Exact quotes from transcript
- Why it was effective
- What tactic it countered

**Bad Responses:**
- Exact quotes from transcript
- Why it was problematic
- What should have been done

### Recommendations

3-4 actionable improvements for next negotiation:
- Specific to errors made
- Based on scenario tactics
- Practical and implementable

## Testing

### Test Flow (Without Real Phone API)

Since ElevenLabs Phone API may not be available:

1. Click "📞 Appel Téléphone" in navigation
2. Select a scenario (e.g., "SaaS B2B")
3. Fill in context (product, prices, red lines)
4. Click "Continuer"
5. Enter phone number (any format)
6. Click "Recevoir l'appel"

**Expected behavior:**
- Error message: "ElevenLabs Phone API is not available yet"
- Suggestion: "Use TEXT mode for fully functional training"
- Alternative: Link to SimulationPage

### Manual Testing (If API Available)

1. Complete steps 1-6 above with real phone number
2. Wait 10 seconds for call
3. Answer and negotiate with AI
4. Hang up when done
5. Wait for analysis (auto-appears)
6. Review scores and transcript

## Demo Script

For hackathon demo:

**Scenario:** SaaS B2B Negotiation

```
User: [Receives call]
AI: "Bonjour, j'ai regardé votre solution SaaS et elle m'intéresse.
     Par contre, franchement, le prix me semble vraiment élevé
     comparé à ce que je vois sur le marché."

User: "Je comprends votre préoccupation. Puis-je vous demander
       quelles solutions vous avez comparé ?"

AI: "J'ai regardé [Competitor A] qui propose à 30K€/an."

User: "Je vois. La différence principale est que nous incluons
       [feature X] et [feature Y] qui vous feront économiser 20K€
       par an en coûts opérationnels."

[... negotiation continues ...]

User: "Je peux vous proposer 42K€/an avec un contrat de 2 ans,
       ce qui nous permet de garantir ce prix."

AI: "D'accord, c'est intéressant. Quelles sont les conditions
     de paiement ?"

[... final terms ...]

AI: "OK, je pense qu'on peut s'accorder sur ces termes."

[Call ends]
```

**Analysis received:**
- Score: 7.5/10
- Detected tactics: Lowball, competitor comparison
- Good: Justified price with ROI calculation
- Bad: Could have anchored higher initially
- Recommendations:
  1. Start with reference to highest-value client
  2. Ask about budget before proposing price
  3. Offer tiered pricing options

## Future Enhancements

### Voice Cloning (Planned)
- Record user voice (30s)
- Clone for auto-pilot mode
- AI can take over if user stuck

### Multi-language
- Support EN, ES, DE, etc.
- Adapt scenarios to local markets

### Custom Scenarios
- Users create their own scenarios
- Upload specific context
- Train for real negotiations

### Team Training
- Multiple users
- Team-based simulations
- Group analysis

### Analytics Dashboard
- Track progress over time
- Compare to benchmarks
- Identify patterns

## Troubleshooting

### Issue: "Phone API not available"

**Cause:** ElevenLabs Phone API requires special access or different endpoint

**Solutions:**
1. Use TEXT mode (fully functional)
2. Check ElevenLabs docs for Phone API availability
3. Contact ElevenLabs for beta access
4. Implement Twilio alternative

### Issue: Call never arrives

**Possible causes:**
- Wrong phone number format
- Phone API credentials invalid
- Webhook not configured
- Network/firewall blocking

**Debug:**
1. Check backend logs for errors
2. Verify ElevenLabs API key
3. Test webhook with curl
4. Check phone number format

### Issue: Analysis not showing

**Possible causes:**
- Webhook not received
- Mistral API error
- Session not found

**Debug:**
1. Check backend logs for webhook
2. Verify Mistral API key
3. Check session_id in URL
4. Look for analysis errors in logs

## Cost Estimates

**Per call (estimated):**
- ElevenLabs Phone API: ~$0.10-0.30 per minute
- Mistral analysis: ~$0.01 per call
- **Total:** ~$0.20-1.00 per call (5-10 min)

**Free tier testing:**
- Mistral: Free credits for new accounts
- ElevenLabs: 10,000 characters/month
- May be sufficient for initial testing

## Hackathon Demo Tips

1. **Prepare scenario in advance**
   - Have product/pricing ready
   - Know your red lines
   - Practice flow

2. **Use compelling example**
   - Real-world SaaS pricing
   - Relatable numbers
   - Clear value proposition

3. **Highlight analysis**
   - Show score dashboard
   - Point out specific quotes
   - Emphasize actionable recommendations

4. **Backup plan**
   - If phone API fails, use text mode
   - Emphasize "real call" concept
   - Show architecture diagrams

5. **Value proposition**
   - "Practice like it's real"
   - "Immediate expert feedback"
   - "Track your progress"
   - "Safe environment to fail"

## Conclusion

The Phone Call Feature represents the **most immersive negotiation training** possible. By combining:
- Real phone calls (ElevenLabs)
- Intelligent opponents (Mistral AI)
- Expert analysis (Mistral AI)
- Multiple scenarios

Users get **professional-grade training** that prepares them for real negotiations.

Perfect for:
- Sales professionals
- Freelancers
- Job seekers
- Entrepreneurs
- Procurement teams

**Next steps:**
1. Test with real ElevenLabs Phone API when available
2. Add more scenarios based on user feedback
3. Implement voice cloning for auto-pilot
4. Build analytics dashboard
