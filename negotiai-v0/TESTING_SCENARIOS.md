# 🧪 NegotiAI v1 - Scénarios de Test

Ce document contient des exemples concrets pour tester toutes les fonctionnalités de NegotiAI v1.

---

## 📝 Scénario 1 : Négociation SaaS Enterprise (Complet)

### **Étape 1 : Préparation**
1. Allez sur http://localhost:3000
2. Dans le dropdown **"Quick Start - Use a Template"**, sélectionnez **"💼 SaaS Enterprise License"**
3. Le formulaire se remplit automatiquement
4. Cliquez sur **"Generate Strategy →"**

### **Étape 2 : Révision de la Stratégie**
- Lisez la stratégie générée
- Notez les **Red Lines** (lignes rouges à ne pas franchir)
- Téléchargez le **PDF de stratégie** avec le bouton "📄 Download PDF"

### **Étape 3 : Simulation de Négociation**

Collez ce transcript dans l'AnalysisPage :

```
TRANSCRIPT DE LA NÉGOCIATION:

Me: Bonjour, merci de me recevoir. J'ai bien étudié votre plateforme DataViz Pro et je dois dire qu'elle répond parfaitement à nos besoins d'analyse.

Vendeur: Ravi de l'entendre ! Nous avons préparé une offre pour TechCorp Solutions. Pour 200 utilisateurs, notre tarif standard est de 35 000€ par an.

Me: Je vois. J'apprécie votre offre, mais permettez-moi d'être transparent avec vous. Nous avons un budget alloué de 40 000€ maximum pour cette solution, mais nous espérions rester autour de 30 000€ pour avoir une marge sur notre budget tech global.

Vendeur: Je comprends vos contraintes budgétaires. Cependant, à 35K, nous offrons déjà une remise de 15% par rapport au tarif catalogue. Descendre à 30K serait compliqué...

Me: Je comprends votre position. Laissez-moi vous expliquer notre contexte : nous sommes une startup en forte croissance. Actuellement 200 employés, mais nous prévoyons 350 employés d'ici 18 mois. Si votre solution nous convient, cela représenterait un renouvellement automatique et une expansion significative.

Vendeur: C'est un excellent point. La croissance future est effectivement quelque chose que nous valorisons.

Me: De plus, nous pouvons vous offrir une visibilité exceptionnelle. Nous sommes bien connectés dans l'écosystème tech français et serions ravis de partager notre expérience lors d'événements et sur nos réseaux. Un case study serait-il intéressant pour vous ?

Vendeur: Absolument ! Les success stories dans le secteur tech sont très précieuses pour nous. Voici ce que je peux faire : je descends à 32 000€ pour la première année, en incluant le case study et avec une clause d'expansion automatique si vous dépassez 250 utilisateurs.

Me: C'est déjà mieux. Mais pour vraiment sceller cet accord, j'aurais besoin de 30 000€. En contrepartie, je vous garantis :
- Case study détaillé avec interview vidéo
- Témoignage client sur votre site
- 3 références actives aux prospects que vous nous enverrez
- Engagement ferme sur 24 mois (au lieu de 12)

Vendeur: (Pause) Laissez-moi consulter mon manager... (5 minutes plus tard) OK, j'ai l'accord. 30 000€ pour la première année, puis 33 000€ pour l'année 2, avec tout ce que vous avez mentionné. Plus un bonus : 3 mois de support premium offerts.

Me: Parfait ! J'apprécie vraiment votre flexibilité. Je rajoute une dernière chose : pouvons-nous avoir une formation avancée pour nos 5 power users ?

Vendeur: Oui, 2 jours de formation on-site inclus dans le package.

Me: Excellent. Envoyez-moi le contrat, nous le signons cette semaine.

RÉSULTAT: Deal conclu à 30 000€ première année, 33 000€ deuxième année, avec formation et support premium offerts.
```

**Outcome à entrer :**
```
Deal signé à 30K€ (année 1) + 33K€ (année 2) avec formation premium et support inclus
```

### **Étape 4 : Analyse**
1. Cliquez sur **"Analyze Performance"**
2. Attendez l'analyse (peut prendre 10-20 secondes)
3. Consultez vos **scores** (Preparation, Tactics, Outcome)
4. Lisez les **tactiques détectées**
5. Téléchargez le **PDF d'analyse**

### **Étape 5 : Historique**
1. Cliquez sur **"📊 History"**
2. Voyez votre négociation apparaître
3. Consultez vos statistiques

---

## 🏠 Scénario 2 : Négociation Immobilière

### **Contexte**
Template : **"🏡 Real Estate Purchase"**

### **Transcript simplifié**
```
NÉGOCIATION IMMOBILIER:

Agent: Le propriétaire demande 380 000€ pour cet appartement de 85m² dans le 11ème.

Moi: J'ai visité et l'appartement me plaît, mais j'ai remarqué que les travaux de rafraîchissement sont nécessaires. Les peintures, la cuisine... Je dirais au moins 30 000€ de travaux. Je peux faire une offre à 340 000€.

Agent: C'est très en dessous du prix demandé. Le marché est tendu en ce moment...

Moi: Je comprends, mais je suis acheteur cash, sans condition de prêt. Je peux signer sous 3 semaines. Cela a de la valeur pour le vendeur, non ?

Agent: En effet, c'est un bon argument. Je vais transmettre votre offre à 340K avec mention de l'achat comptant.

(Après 2 jours)

Agent: Le vendeur accepte de descendre à 365 000€, c'est son dernier prix.

Moi: J'apprécie le geste. Voici ma proposition finale : 355 000€, achat comptant, signature sous 15 jours, et je prends en charge les frais de diagnostics. C'est mon budget maximum.

Agent: (Après consultation) Le vendeur accepte à 355 000€. Félicitations !

RÉSULTAT: Appartement acheté à 355 000€ au lieu de 380 000€
```

**Outcome :**
```
Achat conclu à 355K€ (au lieu de 380K€), soit 25K€ d'économie - Achat comptant sous 15 jours
```

---

## 💼 Scénario 3 : Négociation de Salaire

### **Contexte**
Template : **"💰 Salary Negotiation"**

### **Transcript**
```
NÉGOCIATION SALAIRE - POSTE SENIOR DEVELOPER:

RH: Nous sommes ravis de vous faire une offre pour le poste de Senior Developer. Notre proposition est de 55 000€ brut annuel, avec tickets restaurant et mutuelle.

Moi: Merci pour cette offre. Je suis vraiment enthousiaste à l'idée de rejoindre votre équipe. Cependant, j'aimerais discuter de la rémunération. Avec mes 6 ans d'expérience et mes compétences en React et Node.js que vous recherchez, je visais plutôt une fourchette de 65-70K€.

RH: Je comprends, mais 55K est notre budget pour ce poste...

Moi: Je vois. Laissez-moi vous présenter ma situation : dans mon poste actuel, je suis à 58K€. Accepter votre offre représenterait une régression financière, même si le projet m'intéresse beaucoup. Seriez-vous flexible sur ce point ?

RH: Hmm, je ne savais pas que vous étiez déjà à 58K. Effectivement, cela change la donne. Je peux monter à 60K€.

Moi: C'est mieux, merci. Pour arriver à un accord, voici ce que je propose : 62K€ de fixe, et si vous ne pouvez vraiment pas aller plus haut tout de suite, je serais d'accord pour un point de révision salariale à 6 mois au lieu de 12 mois. Qu'en pensez-vous ?

RH: Laissez-moi voir avec la direction... (le lendemain) OK pour 62K€, avec effectivement une révision à 6 mois si les objectifs sont atteints. Plus 2 jours de télétravail par semaine. Ça vous va ?

Moi: Parfait ! J'accepte cette offre. Merci pour votre compréhension.

RÉSULTAT: 62K€ brut annuel + révision à 6 mois + 2j télétravail/semaine
```

**Outcome :**
```
Salaire négocié à 62K€ (au lieu de 55K€) + révision à 6 mois + 2j télétravail
```

---

## 🎯 Scénario 4 : Test de Performance Tracking

### **Objectif**
Créer **plusieurs négociations** pour voir le graphique de progression.

### **Instructions**
1. Créez 3-4 négociations avec les templates différents
2. Variez vos performances :
   - Négociation 1 : Suivez bien la stratégie → Score élevé (~80-90)
   - Négociation 2 : Ignorez la stratégie → Score moyen (~60-70)
   - Négociation 3 : Excellente exécution → Score très élevé (~85-95)
3. Allez dans **"📊 History"**
4. Observez le **graphique de progression**
5. Voyez le message : *"Vous vous êtes amélioré de +X points !"*

---

## 📊 Fonctionnalités à Tester

### ✅ **Checklist Complète V1**

**Templates :**
- [ ] SaaS Enterprise License
- [ ] Real Estate Purchase
- [ ] Salary Negotiation
- [ ] Freelance Contract
- [ ] Vendor/Supplier Contract

**PDF Exports :**
- [ ] Télécharger PDF de stratégie
- [ ] Télécharger PDF d'analyse
- [ ] Vérifier le contenu des PDFs

**Persistance :**
- [ ] Créer une négociation
- [ ] Fermer le navigateur
- [ ] Rouvrir → La session est toujours là dans History
- [ ] Cliquer sur une session pour voir les détails

**Performance Tracking :**
- [ ] Créer 3+ négociations
- [ ] Voir le graphique de progression
- [ ] Voir les statistiques (total, moyenne, progrès)
- [ ] Développer une session pour voir tous les détails

**Robustesse :**
- [ ] Tester avec de longs transcripts (1000+ mots)
- [ ] Tester avec plusieurs utilisateurs simultanés
- [ ] Vérifier que les sessions ne se mélangent pas

---

## 💡 Astuces pour de Bons Résultats

### **Pour obtenir un score élevé :**
1. **Préparation** : Mentionnez votre BATNA dans la négociation
2. **Tactiques** : Utilisez les tactiques suggérées (anchoring, mirroring, etc.)
3. **Outcome** : Obtenez un résultat proche de votre objectif initial

### **Exemples de bonnes tactiques dans les transcripts :**
- **Anchoring** : "Je visais plutôt 30K€" (poser votre ancre en premier)
- **Mirroring** : Répéter les derniers mots de l'autre partie
- **Calibrated Questions** : "Comment pouvons-nous arriver à un accord ?"
- **Silence** : "(Pause)" dans le transcript
- **BATNA Reveal** : Mentionner votre alternative
- **Trade-offs** : "Si vous descendez à X, je m'engage sur Y"

---

## 🐛 Tests d'Erreur (Optionnel)

### **Test de robustesse :**
1. Essayer d'exporter un PDF pour une session qui n'existe pas
2. Créer une stratégie sans remplir tous les champs
3. Analyser une négociation sans transcript
4. Fermer le backend pendant une génération

**Tous ces cas devraient être gérés gracieusement !**

---

## 📈 Résultat Attendu

Après ces tests, vous devriez avoir :
- ✅ **3-5 négociations** dans votre historique
- ✅ **6-10 PDFs téléchargés** (stratégies + analyses)
- ✅ Un **graphique de progression** visible
- ✅ Des **statistiques de performance** affichées
- ✅ Une bonne compréhension de comment utiliser l'outil

---

**🎉 Bon test ! Votre application V1 est maintenant 100% fonctionnelle !**
