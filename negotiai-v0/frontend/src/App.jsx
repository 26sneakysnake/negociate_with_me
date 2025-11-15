// frontend/src/App.jsx
import React, { useState } from 'react';
import PrepPage from './pages/PrepPage';
import StrategyPage from './pages/StrategyPage';
import AnalysisPage from './pages/AnalysisPage';
import HistoryPage from './pages/HistoryPage';
import SimulationPage from './pages/SimulationPage';
import PhoneCallPage from './pages/PhoneCallPage';
import './App.css';

function App() {
  const [currentPage, setCurrentPage] = useState('prep'); // prep, strategy, analysis, history, simulation, phone
  const [sessionData, setSessionData] = useState({
    context: null,
    strategy: null,
    analysis: null
  });

  const handleContextReady = (context) => {
    setSessionData({ ...sessionData, context });
    setCurrentPage('strategy');
  };

  const handleStrategyGenerated = (strategy) => {
    setSessionData({ ...sessionData, strategy });
  };

  const handleAnalysisComplete = (analysis) => {
    setSessionData({ ...sessionData, analysis });
    setCurrentPage('analysis');
  };

  const handleNewNegotiation = () => {
    setSessionData({
      context: null,
      strategy: null,
      analysis: null
    });
    setCurrentPage('prep');
  };

  return (
    <div className="App">
      <header className="app-header">
        <h1>🤝 NegotiAI</h1>
        <p className="tagline">Prepare. Negotiate. Learn.</p>
      </header>

      <nav className="progress-bar">
        <div className={`step ${currentPage === 'prep' ? 'active' : ''}`}>
          1. Prepare
        </div>
        <div className={`step ${currentPage === 'strategy' ? 'active' : ''}`}>
          2. Strategy
        </div>
        <div className={`step ${currentPage === 'analysis' ? 'active' : ''}`}>
          3. Analysis
        </div>
        <div
          className={`step ${currentPage === 'history' ? 'active' : ''}`}
          onClick={() => setCurrentPage('history')}
          style={{ cursor: 'pointer' }}
        >
          📊 History
        </div>
        <div
          className={`step ${currentPage === 'simulation' ? 'active' : ''}`}
          onClick={() => setCurrentPage('simulation')}
          style={{ cursor: 'pointer', background: currentPage === 'simulation' ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' : '' }}
        >
          🎤 Simulation Live
        </div>
        <div
          className={`step ${currentPage === 'phone' ? 'active' : ''}`}
          onClick={() => setCurrentPage('phone')}
          style={{ cursor: 'pointer', background: currentPage === 'phone' ? 'linear-gradient(135deg, #f44336 0%, #e91e63 100%)' : '' }}
        >
          📞 Appel Téléphone
        </div>
      </nav>

      <main className="app-main">
        {currentPage === 'prep' && (
          <PrepPage onReady={handleContextReady} />
        )}

        {currentPage === 'strategy' && (
          <StrategyPage
            context={sessionData.context}
            onStrategyGenerated={handleStrategyGenerated}
            onAnalyze={() => setCurrentPage('analysis')}
            strategy={sessionData.strategy}
          />
        )}

        {currentPage === 'analysis' && (
          <AnalysisPage
            strategy={sessionData.strategy}
            onAnalysisComplete={handleAnalysisComplete}
            analysis={sessionData.analysis}
          />
        )}

        {currentPage === 'history' && (
          <HistoryPage onNewNegotiation={handleNewNegotiation} />
        )}

        {currentPage === 'simulation' && (
          <SimulationPage onBack={() => setCurrentPage('prep')} />
        )}

        {currentPage === 'phone' && (
          <PhoneCallPage />
        )}
      </main>
    </div>
  );
}

export default App;
