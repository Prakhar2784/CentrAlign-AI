import React, { useState } from 'react';

export default function PortalsOverview({ portalInvoices, financeRecords, onRefresh, activeTab, setActiveTab }) {
  const [selectedInvoice, setSelectedInvoice] = useState(null);

  return (
    <div className="portals-card">
      <div className="portals-header">
        <div className="tab-buttons">
          <button
            className={`tab-btn ${activeTab === 'portal' ? 'tab-active' : ''}`}
            onClick={() => setActiveTab('portal')}
          >
            <span className="tab-icon">📄</span>
            <span>Simulated Invoice Portal ({portalInvoices.length})</span>
          </button>
          <button
            className={`tab-btn ${activeTab === 'finance' ? 'tab-active' : ''}`}
            onClick={() => setActiveTab('finance')}
          >
            <span className="tab-icon">💼</span>
            <span>Internal Finance System ({financeRecords.length})</span>
          </button>
        </div>

        <button onClick={onRefresh} className="btn-icon-refresh" title="Refresh portal data">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="23 4 23 10 17 10"></polyline>
            <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path>
          </svg>
        </button>
      </div>

      {/* Tab 1: Invoice Portal */}
      {activeTab === 'portal' && (
        <div className="table-responsive">
          <table className="portal-table">
            <thead>
              <tr>
                <th>Invoice #</th>
                <th>Company</th>
                <th>Issue Date</th>
                <th>Due Date</th>
                <th>Amount</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {portalInvoices.map((inv) => (
                <tr key={inv.id}>
                  <td className="font-mono font-bold text-accent">{inv.invoice_number}</td>
                  <td>{inv.company}</td>
                  <td>{inv.issue_date}</td>
                  <td>{inv.due_date}</td>
                  <td className="font-mono font-semibold">${inv.amount?.toLocaleString()}</td>
                  <td>
                    <span className={`status-tag ${inv.status === 'PAID' ? 'status-paid' : 'status-issued'}`}>
                      {inv.status}
                    </span>
                  </td>
                  <td>
                    <button
                      onClick={() => setSelectedInvoice(inv)}
                      className="btn-view-doc"
                    >
                      View Doc
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Tab 2: Finance System Ledger */}
      {activeTab === 'finance' && (
        <div className="table-responsive">
          <table className="portal-table">
            <thead>
              <tr>
                <th>Invoice #</th>
                <th>Company</th>
                <th>Stored Amount</th>
                <th>Stored Due Date</th>
                <th>Sync Status</th>
                <th>Last Verified</th>
                <th>Notes</th>
              </tr>
            </thead>
            <tbody>
              {financeRecords.map((rec) => (
                <tr key={rec.id} className={rec.sync_status === 'SYNCED' ? 'row-synced' : ''}>
                  <td className="font-mono font-bold">{rec.invoice_number}</td>
                  <td>{rec.company}</td>
                  <td className="font-mono font-semibold">
                    {rec.amount > 0 ? `$${rec.amount?.toLocaleString()}` : <span className="text-muted">$0.00 (Unset)</span>}
                  </td>
                  <td className="font-mono">{rec.due_date || <span className="text-muted">Unset</span>}</td>
                  <td>
                    <span className={`status-tag ${rec.sync_status === 'SYNCED' ? 'status-synced' : 'status-pending'}`}>
                      {rec.sync_status}
                    </span>
                  </td>
                  <td className="text-xs text-muted font-mono">
                    {rec.last_verified_at ? new Date(rec.last_verified_at).toLocaleTimeString() : 'Never'}
                  </td>
                  <td className="text-xs text-secondary">{rec.notes}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Document Viewer Modal */}
      {selectedInvoice && (
        <div className="modal-backdrop" onClick={() => setSelectedInvoice(null)}>
          <div className="modal-card" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Invoice Document: {selectedInvoice.invoice_number}</h3>
              <button onClick={() => setSelectedInvoice(null)} className="btn-close">✕</button>
            </div>
            <div className="modal-body">
              <pre className="doc-raw-pre">{selectedInvoice.raw_content}</pre>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
