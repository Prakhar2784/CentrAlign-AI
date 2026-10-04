import uuid
import time
from typing import Dict, Any, Optional, Callable
from sqlalchemy.orm import Session
from app.agent.state import AgentState, AgentStepLog, AgentPlanStep
from app.agent.memory import AgentMemory
from app.agent.planner import TaskPlanner
from app.agent.safety import SafetyGuard
from app.agent.verifier import TaskVerifier
from app.agent.llm_provider import get_llm_provider, BaseLLMProvider
from app.tools.registry import default_tool_registry, ToolRegistry
from app.core.logging import logger

class AgentOrchestrator:
    """
    Main Autonomous Agent Orchestrator.
    Drives the complete ReAct execution lifecycle:
    Goal -> Understand -> Plan -> Select Tool -> Execute -> Observe -> Adapt -> Verify -> Complete.
    """

    def __init__(
        self,
        tool_registry: Optional[ToolRegistry] = None,
        llm_provider: Optional[BaseLLMProvider] = None,
        max_steps: int = 15
    ):
        self.tool_registry = tool_registry or default_tool_registry
        self.llm_provider = llm_provider or get_llm_provider()
        self.max_steps = max_steps

    def execute_task(
        self,
        db: Session,
        user_goal: str,
        task_id: Optional[str] = None,
        simulation_context: Optional[Dict[str, Any]] = None,
        step_callback: Optional[Callable[[AgentState], None]] = None
    ) -> AgentState:
        task_id = task_id or f"task_{uuid.uuid4().hex[:8]}"
        logger.info(f"Starting autonomous task execution [{task_id}]: '{user_goal}'")
        
        sim_ctx = simulation_context or {}
        fail_first_update = sim_ctx.get("fail_first_update", False)
        fail_verification = sim_ctx.get("fail_verification", False)
        update_attempt_count = 0

        # Initialize State & Memory
        state = AgentState(
            task_id=task_id,
            user_goal=user_goal,
            status="PLANNING",
            plan=TaskPlanner.create_initial_plan(user_goal)
        )
        memory = AgentMemory(user_goal=user_goal)
        available_tools = self.tool_registry.get_schemas()

        if step_callback:
            step_callback(state)

        step_count = 0
        state.status = "EXECUTING"

        while step_count < self.max_steps:
            step_count += 1
            step_start = time.time()
            
            # 1. LLM Cognitive Step (Reasoning & Tool Selection)
            llm_decision = self.llm_provider.decide_next_step(
                user_goal=user_goal,
                memory=memory,
                available_tools=available_tools
            )

            # 2. Check if LLM decided task is complete or terminated
            if llm_decision.is_final:
                state.status = "COMPLETED" if "PASSED" in (llm_decision.final_answer or "") else "FAILED"
                state.final_summary = llm_decision.final_answer
                
                # Check verification state
                extracted = memory.get_entity("extracted_data", {})
                if extracted and state.status == "COMPLETED":
                    verified, ver_details = TaskVerifier.verify_persisted_state(db, extracted)
                    state.verification_passed = verified
                    state.verification_details = ver_details
                    if not verified:
                        state.status = "FAILED"
                        state.final_summary = f"Execution finished but post-verification failed: {ver_details.get('reason')}"
                
                # Log final step
                final_log = AgentStepLog(
                    step_index=step_count,
                    thought=llm_decision.thought,
                    action=llm_decision.action,
                    tool_result=llm_decision.final_answer,
                    success=state.status == "COMPLETED",
                    duration_ms=round((time.time() - step_start) * 1000, 2)
                )
                state.add_log(final_log)
                
                # Mark all remaining plan steps as completed or failed
                for p in state.plan:
                    if p.status != "COMPLETED":
                        p.status = "COMPLETED" if state.status == "COMPLETED" else "FAILED"
                
                if step_callback:
                    step_callback(state)
                break

            # 3. Tool Selected: Check Safety & Permissions
            tool_name = llm_decision.tool_name
            tool_input = llm_decision.tool_input or {}
            target_tool = self.tool_registry.get_tool(tool_name)
            is_mutation = target_tool.is_mutation if target_tool else False

            is_safe, safety_err = SafetyGuard.check_authorization(
                user_goal=user_goal,
                action_name=tool_name or "unknown",
                is_mutation=is_mutation
            )

            if not is_safe:
                state.status = "BLOCKED_SAFETY"
                state.is_safety_cleared = False
                state.safety_message = safety_err
                state.error = safety_err
                
                safety_log = AgentStepLog(
                    step_index=step_count,
                    thought=llm_decision.thought,
                    action=f"Blocked by Safety Guard: {tool_name}",
                    tool_name=tool_name,
                    tool_input=tool_input,
                    success=False,
                    error=safety_err,
                    duration_ms=round((time.time() - step_start) * 1000, 2)
                )
                state.add_log(safety_log)
                if step_callback:
                    step_callback(state)
                break

            # 4. Handle Demo Simulation Triggers (Failure / Retry & Verification Failure)
            tool_exec_ctx = {}
            if tool_name == "update_invoice_record":
                update_attempt_count += 1
                if fail_first_update and update_attempt_count == 1:
                    tool_exec_ctx["simulate_failure"] = True
                    logger.warning(f"Demo Mode: Injecting transient failure on update attempt #{update_attempt_count}")
            
            if tool_name == "verify_invoice_record" and fail_verification:
                tool_exec_ctx["simulate_verification_failure"] = True
                logger.warning("Demo Mode: Injecting simulated verification failure")

            # 5. Execute Tool
            tool_result = self.tool_registry.execute_tool(
                tool_name=tool_name,
                db=db,
                arguments=tool_input,
                context=tool_exec_ctx
            )

            duration_ms = round((time.time() - step_start) * 1000, 2)

            # 6. Capture Observation in Agent Memory
            obs_data = tool_result.data if tool_result.success else tool_result.error
            memory.add_observation(
                tool_name=tool_name,
                input_args=tool_input,
                result=obs_data,
                success=tool_result.success
            )

            # Update extracted data entity if applicable
            if tool_name == "extract_invoice_data" and tool_result.success:
                state.extracted_data = tool_result.data
                memory.store_entity("extracted_data", tool_result.data)

            if tool_name == "verify_invoice_record":
                state.verification_passed = tool_result.success
                state.verification_details = tool_result.data or {"error": tool_result.error}

            # 7. Record Step Log
            step_log = AgentStepLog(
                step_index=step_count,
                thought=llm_decision.thought,
                action=llm_decision.action,
                tool_name=tool_name,
                tool_input=tool_input,
                tool_result=tool_result.data,
                success=tool_result.success,
                error=tool_result.error,
                retry_count=memory.get_retry_count(tool_name) if not tool_result.success else 0,
                duration_ms=duration_ms
            )
            state.add_log(step_log)

            # 8. Update Plan Step Status
            self._sync_plan_progress(state, tool_name, tool_result.success)

            if step_callback:
                step_callback(state)

        if step_count >= self.max_steps and state.status == "EXECUTING":
            state.status = "FAILED"
            state.error = f"Agent exceeded maximum step limit ({self.max_steps}) without completing goal."
            if step_callback:
                step_callback(state)

        logger.info(f"Task [{task_id}] execution finished with status={state.status}")
        return state

    def _sync_plan_progress(self, state: AgentState, tool_name: str, success: bool):
        tool_to_step = {
            "search_invoices": 1,
            "get_invoice": 2,
            "extract_invoice_data": 3,
            "search_finance_records": 4,
            "update_invoice_record": 5,
            "verify_invoice_record": 6
        }
        step_num = tool_to_step.get(tool_name)
        if step_num:
            status = "COMPLETED" if success else "IN_PROGRESS"
            state.update_plan_status(step_num, status)
