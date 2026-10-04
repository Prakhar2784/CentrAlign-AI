import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import DemoControls from './components/DemoControls';
import TaskInput from './components/TaskInput';
import PlanSteps from './components/PlanSteps';
import LiveLogs from './components/LiveLogs';
import VerificationBadge from './components/VerificationBadge';
import PortalsOverview from './components/PortalsOverview';
import './App.css';

const API_BASE = "http://localhost:8000/api";

export default function App() {
  const [goal, setGoal] = useState("Find the latest invoice from Acme Corp, extract the amount and due date, update the invoice record in the finance system, and tell me when it is done.");
  const [failFirstUpdate, setFailFirstUpdate] = useState(false);
  const [failVerification, setFailVerification] = useState(false);
  const [isRunning, setIsRunning] = useState(false);
  const [isResetting, setIsResetting] = useState(false);
  
  const [agentState, setAgentState] = useState(null);
  const [portalInvoices, setPortalInvoices] = useState([]);
  const [financeRecords, setFinanceRecords] = useState([]);
  const [systemHealth, setSystemHealth] = useState(null);
  const [activeTab, setActiveTab] = useState('portal');

  // Load initial portal and finance records
  const fetchPortalData = async () => {
    try {
      const [invRes, finRes, healthRes] = await Promise.all([
        fetch(`${API_BASE}/portal/invoices`),
        fetch(`${API_BASE}/finance/records`),
        fetch(`http://localhost:8000/health`)
      ]);
      if (invRes.ok) setPortalInvoices(await invRes.json());
      if (finRes.ok) setFinanceRecords(await finRes.json());
      if (healthRes.ok) setSystemHealth(await healthRes.json());
    } catch (e) {
      console.warn("Could not load portal data from backend:", e);
    }
  };

  useEffect(() => {
    fetchPortalData();
  }, []);

  const handleReset = async () => {
    setIsResetting(true);
    try {
      await fetch(`${API_BASE}/system/reset`, { method: "POST" });
      setAgentState(null);
      await fetchPortalData();
    } catch (e) {
      console.error("Error resetting database:", e);
    } finally {
      setIsResetting(false);
    }
  };

  const handleSelectScenario = (scenario) => {
    setGoal(scenario.goal);
    setFailFirstUpdate(scenario.failFirstUpdate);
    setFailVerification(scenario.failVerification);
  };

  const handleRunTask = async () => {
    if (!goal.trim() || isRunning) return;
    setIsRunning(true);
    
    // Initialize temporary state
    setAgentState({
      task_id: "task_live",
      user_goal: goal,
      status: "EXECUTING",
      plan: [],
      logs: [],
      extracted_data: {},
      verification_passed: false
    });

    try {
      // Use SSE for real-time streaming
      const params = new URLSearchParams({
        goal: goal,
        fail_first_update: failFirstUpdate,
        fail_verification: failVerification
      });

      const eventSource = new EventSource(`${API_BASE}/agent/stream?${params.toString()}`);

      eventSource.addEventListener("update", (event) => {
        try {
          const data = JSON.parse(event.data);
          setAgentState(data);
          // Periodically refresh finance records to show live database sync
          fetch(`${API_BASE}/finance/records`)
            .then(res => res.json())
            .then(records => setFinanceRecords(records))
            .catch(() => {});
        } catch (err) {
          console.error("Error parsing SSE event:", err);
        }
      });

      eventSource.addEventListener("end", () => {
        eventSource.close();
        setIsRunning(false);
        fetchPortalData();
      });

      eventSource.onerror = (err) => {
        console.warn("SSE stream closed or encountered error, falling back to POST /api/agent/run:", err);
        eventSource.close();
        
        // Fallback to synchronous execution
        fetch(`${API_BASE}/agent/run`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            goal: goal,
            fail_first_update: failFirstUpdate,
            fail_verification: failVerification
          })
        })
        .then(res => res.json())
        .then(data => {
          setAgentState(data);
          fetchPortalData();
        })
        .catch(error => {
          console.error("Task execution failed:", error);
        })
        .finally(() => {
          setIsRunning(false);
        });
      };

    } catch (e) {
      console.error("Task trigger failed:", e);
      setIsRunning(false);
    }
  };

  return (
    <div className="app-layout">
      <Header
        systemHealth={systemHealth}
        isResetting={isResetting}
        onReset={handleReset}
      />

      <main className="main-content">
        {/* Top Control Section: Demo Presets & Task Input */}
        <div className="grid-top">
          <DemoControls
            onSelectScenario={handleSelectScenario}
            isRunning={isRunning}
          />
          
          <TaskInput
            goal={goal}
            setGoal={setGoal}
            onRunTask={handleRunTask}
            isRunning={isRunning}
            failFirstUpdate={failFirstUpdate}
            setFailFirstUpdate={setFailFirstUpdate}
            failVerification={failVerification}
            setFailVerification={setFailVerification}
          />
        </div>

        {/* Verification Banner */}
        {agentState && <VerificationBadge state={agentState} />}

        {/* Execution View: Plan Steps & Live ReAct Logs */}
        <div className="grid-execution">
          <div className="col-plan">
            <PlanSteps
              plan={agentState?.plan || []}
              currentStatus={agentState?.status}
            />
          </div>

          <div className="col-logs">
            <LiveLogs logs={agentState?.logs || []} />
          </div>
        </div>

        {/* Live Portals / Database Inspector */}
        <div className="section-portals">
          <PortalsOverview
            portalInvoices={portalInvoices}
            financeRecords={financeRecords}
            onRefresh={fetchPortalData}
            activeTab={activeTab}
            setActiveTab={setActiveTab}
          />
        </div>
      </main>
    </div>
  );
}
