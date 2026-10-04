import React from 'react';

export default function VerificationBadge({ state }) {
  if (!state || state.status === 'INITIALIZING' || state.status === 'PLANNING') {
    return null;
  }

  const isCompleted = state.status === 'COMPLETED';
  const isFailed = state.status === 'FAILED';
  const isBlocked = state.status === 'BLOCKED_SAFETY';
  const isVerified = state.verification_passed;
  const extracted = state.extracted_data || {};

  return (
    <div className={`verification-card ${isVerified ? 'ver-passed' : isFailed || isBlocked ? 'ver-failed' : 'ver-pending'}`}>
      <div className="ver-header">
        <div className="ver-title-wrap">
          <span className="ver-icon">
            {isVerified ? '🛡️' : isFailed ? '⚠️' : isBlocked ? '🚫' : '⏳'}
          </span>
          <div>
            <h3 className="ver-title">
              {isVerified 
                ? 'Independent Verification Gate: PASSED' 
                : isFailed 
                ? 'Independent Verification Gate: REJECTED / FAILED' 
                : isBlocked
                ? 'Action Blocked by Safety Guard'
                : 'Verification In Progress...'}
            </h3>
            <p className="ver-sub">
              {isVerified
                ? 'Finance database record read back & asserted against extracted invoice values.'
                : isFailed
                ? 'Integrity check prevented false completion acknowledgment.'
                : isBlocked
                ? 'Write operation prevented due to missing user authorization.'
                : 'Awaiting database read-back verification...'}
            </p>
          </div>
        </div>

        <div className="ver-status-badge">
          {isVerified && <span className="badge-pill tag-green">VERIFIED ✓</span>}
          {isFailed && <span className="badge-pill tag-red">DISCREPANCY DETECTED ✗</span>}
          {isBlocked && <span className="badge-pill tag-amber">SAFETY BLOCKED</span>}
        </div>
      </div>

      {/* Extracted Evidence Table */}
      {extracted && Object.keys(extracted).length > 0 && (
        <div className="evidence-grid">
          <div className="evidence-item">
            <span className="ev-label">Target Invoice</span>
            <span className="ev-val font-mono">{extracted.invoice_number || 'N/A'}</span>
          </div>
          <div className="evidence-item">
            <span className="ev-label">Company / Vendor</span>
            <span className="ev-val">{extracted.company || 'N/A'}</span>
          </div>
          <div className="evidence-item">
            <span className="ev-label">Extracted Amount</span>
            <span className="ev-val text-green font-mono">
              ${extracted.amount ? Number(extracted.amount).toLocaleString('en-US', { minimumFractionDigits: 2 }) : '0.00'}
            </span>
          </div>
          <div className="evidence-item">
            <span className="ev-label">Extracted Due Date</span>
            <span className="ev-val font-mono">{extracted.due_date || 'N/A'}</span>
          </div>
        </div>
      )}

      {/* Final Summary */}
      {state.final_summary && (
        <div className="summary-box">
          <span className="summary-label">Final Outcome & Evidence:</span>
          <pre className="summary-pre">{state.final_summary}</pre>
        </div>
      )}
    </div>
  );
}
