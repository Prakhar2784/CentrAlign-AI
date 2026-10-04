import React, { useState } from 'react';

export default function LiveLogs({ logs }) {
  const [expandedStep, setExpandedStep] = useState(null);

  if (!logs || logs.length === 0) {
    return (
      <div className="logs-container empty-logs">
        <p className="text-muted">Live execution logs and tool observations will stream here...</p>
      </div>
    );
  }

  const toggleExpand = (idx) => {
    setExpandedStep(expandedStep === idx ? null : idx);
  };

  return (
    <div className="logs-container">
      <div className="section-header-compact">
        <h4 className="section-subtitle">Agent ReAct Execution Logs ({logs.length} Steps)</h4>
      </div>

      <div className="logs-timeline">
        {logs.map((log, idx) => {
          const isExpanded = expandedStep === idx || idx === logs.length - 1;
          const isFinal = !log.tool_name;
          
          return (
            <div key={idx} className={`log-card ${log.success ? 'log-success' : 'log-error'} ${isFinal ? 'log-final' : ''}`}>
              <div className="log-card-header" onClick={() => toggleExpand(idx)}>
                <div className="log-header-left">
                  <span className="step-tag">Step {log.step_index}</span>
                  {log.tool_name ? (
                    <span className="tool-tag">
                      <code>{log.tool_name}</code>
                    </span>
                  ) : (
                    <span className="tool-tag tag-purple">Completion Summary</span>
                  )}
                  {log.retry_count > 0 && (
                    <span className="retry-pill">
                      ↻ Retry #{log.retry_count}
                    </span>
                  )}
                </div>

                <div className="log-header-right">
                  <span className="duration-pill">{log.duration_ms}ms</span>
                  <span className={`status-indicator ${log.success ? 'text-green' : 'text-red'}`}>
                    {log.success ? '✓' : '⚠'}
                  </span>
                </div>
              </div>

              {/* Collapsible Content */}
              {isExpanded && (
                <div className="log-card-body">
                  {/* Thought */}
                  <div className="thought-box">
                    <span className="thought-label">🧠 Agent Thought:</span>
                    <p className="thought-content">{log.thought}</p>
                  </div>

                  {/* Action */}
                  <div className="action-box">
                    <span className="action-label">⚡ Action:</span>
                    <span className="action-content">{log.action}</span>
                  </div>

                  {/* Tool Input */}
                  {log.tool_input && Object.keys(log.tool_input).length > 0 && (
                    <div className="json-block">
                      <span className="json-label">Parameters:</span>
                      <pre className="code-pre">{JSON.stringify(log.tool_input, null, 2)}</pre>
                    </div>
                  )}

                  {/* Tool Observation / Result */}
                  <div className="observation-box">
                    <span className="obs-label">👁️ Observation / Result:</span>
                    {log.error ? (
                      <div className="error-banner">
                        <strong>Error:</strong> {log.error}
                      </div>
                    ) : (
                      <pre className="code-pre">
                        {typeof log.tool_result === 'string' 
                          ? log.tool_result 
                          : JSON.stringify(log.tool_result, null, 2)}
                      </pre>
                    )}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
