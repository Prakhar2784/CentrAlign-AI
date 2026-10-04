import React from 'react';

export default function PlanSteps({ plan, currentStatus }) {
  if (!plan || plan.length === 0) {
    return (
      <div className="plan-container empty-plan">
        <p className="text-muted">Agent execution plan will populate when a task begins.</p>
      </div>
    );
  }

  const getStatusBadge = (status) => {
    switch (status) {
      case 'COMPLETED':
        return <span className="status-badge badge-completed">✓ Done</span>;
      case 'IN_PROGRESS':
        return <span className="status-badge badge-progress"><span className="mini-spin"></span> Active</span>;
      case 'FAILED':
        return <span className="status-badge badge-failed">✗ Failed</span>;
      default:
        return <span className="status-badge badge-pending">○ Pending</span>;
    }
  };

  return (
    <div className="plan-container">
      <div className="section-header-compact">
        <h4 className="section-subtitle">Execution Plan & Dynamic Progress</h4>
        <span className="step-count-badge">{plan.filter(p => p.status === 'COMPLETED').length} / {plan.length} Completed</span>
      </div>

      <div className="plan-steps-list">
        {plan.map((step) => (
          <div key={step.step_number} className={`plan-step-item status-${step.status.toLowerCase()}`}>
            <div className="step-left">
              <span className="step-num">{step.step_number}</span>
              <span className="step-desc">{step.description}</span>
            </div>
            <div className="step-right">
              {getStatusBadge(step.status)}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
