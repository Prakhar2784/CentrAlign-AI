import React from 'react';

export default function DemoControls({ onSelectScenario, isRunning }) {
  const scenarios = [
    {
      id: 1,
      title: "1. Standard Execution",
      company: "Acme Corp",
      tag: "Success Path",
      tagColor: "tag-green",
      desc: "Finds latest Acme invoice (INV-1003, $48k), extracts fields, updates ledger, passes verification.",
      goal: "Find the latest invoice from Acme Corp, extract the amount and due date, update the invoice record in the finance system, and tell me when it is done.",
      failFirstUpdate: false,
      failVerification: false
    },
    {
      id: 2,
      title: "2. Transient Lock & Retry",
      company: "Acme Corp",
      tag: "Self-Healing",
      tagColor: "tag-amber",
      desc: "First finance update fails with transient DB lock (503). Agent detects retryable error, retries update, and completes.",
      goal: "Find the latest invoice from Acme Corp, extract the amount and due date, update the invoice record in the finance system, and tell me when it is done.",
      failFirstUpdate: true,
      failVerification: false
    },
    {
      id: 3,
      title: "3. Verification Failure",
      company: "Acme Corp",
      tag: "Safety Gate",
      tagColor: "tag-red",
      desc: "Simulates auditor discrepancy on verification. Proves agent halts & reports error rather than falsely claiming success.",
      goal: "Find the latest invoice from Acme Corp, extract the amount and due date, update the invoice record in the finance system, and tell me when it is done.",
      failFirstUpdate: false,
      failVerification: true
    },
    {
      id: 4,
      title: "4. Multi-Vendor Generalization",
      company: "Globex Corp",
      tag: "Zero Code Change",
      tagColor: "tag-cyan",
      desc: "Executes seamlessly for Globex (INV-2002, $64k) proving no hardcoded company logic exists.",
      goal: "Find the latest invoice from Globex, extract the amount and due date, update the invoice record in the finance system, and tell me when it is done.",
      failFirstUpdate: false,
      failVerification: false
    }
  ];

  return (
    <div className="demo-controls-card">
      <div className="demo-header">
        <div className="demo-title-wrap">
          <span className="demo-icon">🎯</span>
          <div>
            <h3 className="section-title">Interview Demo Scenarios</h3>
            <p className="section-desc">One-click evaluation presets demonstrating core autonomous behaviors</p>
          </div>
        </div>
      </div>

      <div className="scenarios-grid">
        {scenarios.map((sc) => (
          <button
            key={sc.id}
            onClick={() => onSelectScenario(sc)}
            disabled={isRunning}
            className="scenario-btn"
          >
            <div className="scenario-top">
              <span className="scenario-number">{sc.title}</span>
              <span className={`badge-pill ${sc.tagColor}`}>{sc.tag}</span>
            </div>
            <p className="scenario-text">{sc.desc}</p>
          </button>
        ))}
      </div>
    </div>
  );
}
