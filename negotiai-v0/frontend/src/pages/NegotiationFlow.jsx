import React, { useState } from 'react';
import Step1Context from '../components/flow/Step1Context';
import Step2Strategy from '../components/flow/Step2Strategy';
import Step3Call from '../components/flow/Step3Call';
import Step4Briefing from '../components/flow/Step4Briefing';
import Step5Score from '../components/flow/Step5Score';
import './NegotiationFlow.css';

/**
 * Flow principal de négociation en 5 étapes
 *
 * 1. Contexte : Formulaire + recherche Mistral
 * 2. Stratégie : Objectifs + tactiques
 * 3. Appel : Lancement + conversation
 * 4. Briefing : Transcription
 * 5. Score : Performance + recommandations
 */
function NegotiationFlow() {
  const [currentStep, setCurrentStep] = useState(1);
  const [sessionData, setSessionData] = useState({
    // Step 1: Context
    scenario: 'saas',
    context: {
      product: '',
      company_name: '',
      target_price: '',
      minimum_price: '',
      red_lines: []
    },

    // Step 2: Strategy (filled by backend)
    research_data: null,
    session_id: null,

    // Step 3: Call
    phone_number: '',
    call_status: 'idle',

    // Step 4: Briefing
    transcript: null,
    duration: null,

    // Step 5: Score
    analysis: null
  });

  const goToStep = (step) => {
    setCurrentStep(step);
  };

  const updateSessionData = (newData) => {
    setSessionData(prev => ({
      ...prev,
      ...newData
    }));
  };

  const steps = [
    { number: 1, label: '📋 Contexte', component: Step1Context },
    { number: 2, label: '🎯 Stratégie', component: Step2Strategy },
    { number: 3, label: '📞 Appel', component: Step3Call },
    { number: 4, label: '📝 Briefing', component: Step4Briefing },
    { number: 5, label: '⭐ Score', component: Step5Score }
  ];

  const CurrentStepComponent = steps[currentStep - 1].component;

  return (
    <div className="negotiation-flow">
      {/* Progress Bar */}
      <div className="flow-progress">
        <div className="progress-bar">
          {steps.map((step) => (
            <div
              key={step.number}
              className={`progress-step ${
                currentStep === step.number ? 'active' :
                currentStep > step.number ? 'completed' : ''
              }`}
              onClick={() => currentStep > step.number && goToStep(step.number)}
              style={{ cursor: currentStep > step.number ? 'pointer' : 'default' }}
            >
              <div className="step-number">{step.number}</div>
              <div className="step-label">{step.label}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Current Step Content */}
      <div className="flow-content">
        <CurrentStepComponent
          sessionData={sessionData}
          updateSessionData={updateSessionData}
          goToStep={goToStep}
        />
      </div>
    </div>
  );
}

export default NegotiationFlow;
