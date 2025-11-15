# 🔔 Configuration du Webhook ElevenLabs

## Problème Actuel

Le webhook n'est pas appelé automatiquement par ElevenLabs après les appels. Cela signifie que nous devons le configurer **manuellement dans le dashboard ElevenLabs**.

---

## ✅ Solution : Configuration Manuelle

### Étape 1 : Accéder au Dashboard ElevenLabs

1. Allez sur https://elevenlabs.io/
2. Connectez-vous à votre compte
3. Cliquez sur votre profil (en haut à droite)
4. Allez dans **Settings** ou **Conversational AI**

### Étape 2 : Configurer le Webhook

Cherchez une section appelée :
- **Webhooks** 
- **Callback URL**
- **Integration Settings**
- **Conversational AI Settings**

### Étape 3 : Entrer l'URL du Webhook

**URL à configurer** :
```
https://bengal-quiet-basically.ngrok-free.app/api/elevenlabs-webhook
```

**Secret (si demandé)** :
```
wsec_91c23a20c326b935987c5a2bad1753bc051f9b4655605b2380a5eae3b5be0566
```

### Étape 4 : Sélectionner les Événements

Cochez/sélectionnez :
- ✅ `conversation.ended`
- ✅ `call.ended`
- ✅ `analysis.completed`
- ✅ Ou toute option liée à la fin d'une conversation

### Étape 5 : Sauvegarder

Cliquez sur **Save** ou **Update**

---

## 🧪 Test après Configuration

### 1. Tester le webhook manuellement

```bash
curl -X POST https://bengal-quiet-basically.ngrok-free.app/api/elevenlabs-webhook \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "test",
    "conversation_id": "test123",
    "transcript": "Bonjour, ceci est un test",
    "duration": 60
  }'
```

**Vérifiez les logs** :
```bash
docker-compose logs -f backend
```

Vous devriez voir :
```
📞 ELEVENLABS WEBHOOK RECEIVED
======================================================================
📦 Full payload:
{
  "agent_id": "test",
  ...
}
```

### 2. Faire un vrai appel

1. Lancez un nouvel appel depuis http://localhost:3000
2. Négociez pendant 1-2 minutes
3. Raccrochez
4. **Attendez 10-30 secondes**
5. Vérifiez les logs :

```bash
docker-compose logs backend | grep "WEBHOOK RECEIVED"
```

Si vous voyez le message, le webhook fonctionne ! 🎉

---

## 🔍 Débugger si ça ne marche toujours pas

### Option 1 : Vérifier les logs ElevenLabs

Dans le dashboard ElevenLabs, cherchez :
- **Webhook Logs**
- **Delivery History**
- **Recent Events**

Cela vous montrera si ElevenLabs essaie d'appeler votre webhook et s'il y a des erreurs.

### Option 2 : Vérifier ngrok

```bash
# Vérifier que ngrok est accessible
curl https://bengal-quiet-basically.ngrok-free.app/webhook/test
```

Devrait retourner :
```json
{"status": "ok", "message": "Webhook endpoint is accessible!", ...}
```

### Option 3 : Vérifier les logs backend

```bash
# Voir tous les webhooks reçus
docker-compose logs backend | grep "WEBHOOK"

# Voir la création des agents
docker-compose logs backend | grep "Creating ElevenLabs agent"

# Voir les appels
docker-compose logs backend | grep "Call initiated"
```

---

## 📋 Alternative : Webhook Programmatique (Déjà Implémenté)

Nous avons déjà configuré le webhook programmatiquement dans le code :

```python
# phone_handler.py
webhook_config = {
    "url": f"{webhook_base_url}/api/elevenlabs-webhook",
    "events": ["conversation.ended"]
}
payload["conversation_config"]["webhook"] = webhook_config
```

**MAIS** il semble que cela ne fonctionne pas. ElevenLabs a peut-être besoin que le webhook soit configuré au niveau du compte.

---

## 🎯 Prochaines Étapes

1. **Configurez le webhook manuellement** dans le dashboard ElevenLabs (Étapes 1-5 ci-dessus)
2. **Faites un appel de test**
3. **Vérifiez les logs** avec `docker-compose logs -f backend`
4. Si vous voyez `📞 ELEVENLABS WEBHOOK RECEIVED`, c'est bon ! ✅
5. Sinon, **vérifiez les logs ElevenLabs** dans le dashboard pour voir les erreurs

---

## 📞 Support

Si le webhook ne fonctionne toujours pas après configuration manuelle :

1. Vérifiez que ngrok est bien lancé
2. Vérifiez que l'URL webhook dans ElevenLabs est exactement :
   `https://bengal-quiet-basically.ngrok-free.app/api/elevenlabs-webhook`
3. Essayez de recréer un nouveau compte webhook dans ElevenLabs
4. Contactez le support ElevenLabs pour confirmer la bonne URL/format

---

**Bonne chance ! 🚀**
