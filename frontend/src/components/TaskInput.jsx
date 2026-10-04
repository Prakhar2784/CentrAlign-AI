import React from 'react';

export default function TaskInput({
  goal,
  setGoal,
  onRunTask,
  isRunning,
  failFirstUpdate,
  setFailFirstUpdate,
  failVerification,
  setFailVerification
}) {
  const quickCompanies = [
    { name: "Acme Corp", text: "Find the latest invoice from Acme Corp, extract the amount and due date, update the invoice record in the finance system, and tell me when it is done." },
    { name: "Globex", text: "Find the latest invoice from Globex, extract the amount and due date, update the invoice record in the finance system, and tell me when it is done." },
    { name: "Initech", text: "Find the latest invoice from Initech, extract the amount and due date, update the invoice record in the finance system, and tell me when it is done." },
    { name: "Umbrella", text: "Find the latest invoice from Umbrella, extract the amount and due date, update the invoice record in the finance system, and tell me when it is done." }
  ];

  return (
    <div className="task-input-card">
      <div className="task-input-header">
        <label className="input-label">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="4 17 10 11 4 5"></polyline>
            <line x1="12" y1="19" x2="20" y2="19"></line>
          </svg>
          Natural Language Task Goal
        </label>
        <div className="quick-tags">
          <span className="quick-label">Vendors:</span>
          {quickCompanies.map((c) => (
            <button
              key={c.name}
              type="button"
              className="tag-btn"
              onClick={() => setGoal(c.text)}
              disabled={isRunning}
            >
              {c.name}
            </button>
          ))}
        </div>
      </div>

      <div className="textarea-wrap">
        <textarea
          value={goal}
          onChange={(e) => setGoal(e.target.value)}
          placeholder="Enter natural language instructions for the autonomous worker..."
          rows={3}
          disabled={isRunning}
          className="task-textarea"
        />
      </div>

      <div className="task-input-footer">
        <div className="simulation-toggles">
          <label className="toggle-label">
            <input
              type="checkbox"
              checked={failFirstUpdate}
              onChange={(e) => setFailFirstUpdate(e.target.checked)}
              disabled={isRunning}
            />
            <span>Simulate DB Lock on 1st Update</span>
          </label>
          <label className="toggle-label">
            <input
              type="checkbox"
              checked={failVerification}
              onChange={(e) => setFailVerification(e.target.checked)}
              disabled={isRunning}
            />
            <span>Simulate Verification Mismatch</span>
          </label>
        </div>

        <button
          onClick={onRunTask}
          disabled={isRunning || !goal.trim()}
          className={`btn-run ${isRunning ? 'loading' : ''}`}
        >
          {isRunning ? (
            <>
              <span className="spinner"></span>
              <span>Worker Executing...</span>
            </>
          ) : (
            <>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
                <polygon points="5 3 19 12 5 21 5 3"></polygon>
              </svg>
              <span>Run Task Autonomously</span>
            </>
          )}
        </button>
      </div>
    </div>
  );
}
