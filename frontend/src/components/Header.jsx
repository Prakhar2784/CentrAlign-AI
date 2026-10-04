import React from 'react';

export default function Header({ systemHealth, isResetting, onReset }) {
  return (
    <header className="header-container">
      <div className="header-left">
        <div className="logo-badge">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
          </svg>
        </div>
        <div>
          <h1 className="header-title">CentrAlign AI <span className="title-accent">Task Worker</span></h1>
          <p className="header-subtitle">Autonomous Enterprise Invoice Extraction & Finance Ledger Sync</p>
        </div>
      </div>

      <div className="header-right">
        <div className="status-pill active">
          <span className="pulsing-dot"></span>
          <span>Engine: {systemHealth?.llm_provider?.toUpperCase() || 'REACT REASONER'}</span>
        </div>
        <button 
          onClick={onReset} 
          disabled={isResetting} 
          className="btn-reset"
          title="Reset simulated invoice documents and finance database to clean initial state"
        >
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="23 4 23 10 17 10"></polyline>
            <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path>
          </svg>
          {isResetting ? "Resetting..." : "Reset Data"}
        </button>
      </div>
    </header>
  );
}
