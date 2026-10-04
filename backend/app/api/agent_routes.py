import json
import asyncio
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from app.core.database import get_db, SessionLocal
from app.agent.orchestrator import AgentOrchestrator
from app.agent.state import AgentState
from app.tools.registry import default_tool_registry
from app.core.logging import logger

router = APIRouter(prefix="/api/agent", tags=["Agent Execution"])

class AgentTaskRequest(BaseModel):
    goal: str = Field(..., json_schema_extra={"example": "Find the latest invoice from Acme Corp, extract the amount and due date, update the invoice record in the finance system, and tell me when it is done."})
    fail_first_update: bool = False
    fail_verification: bool = False

@router.get("/tools", summary="List available tools and schemas")
def list_available_tools():
    return {
        "tools": default_tool_registry.get_schemas()
    }

@router.post("/run", response_model=AgentState, summary="Execute autonomous task synchronously")
def run_task(request: AgentTaskRequest, db: Session = Depends(get_db)):
    orchestrator = AgentOrchestrator()
    sim_ctx = {
        "fail_first_update": request.fail_first_update,
        "fail_verification": request.fail_verification
    }
    state = orchestrator.execute_task(
        db=db,
        user_goal=request.goal,
        simulation_context=sim_ctx
    )
    return state

@router.get("/stream", summary="Stream autonomous task execution events via SSE")
async def stream_task_events(
    goal: str = Query(..., description="Natural language task goal"),
    fail_first_update: bool = Query(False, description="Simulate transient lock failure on 1st update"),
    fail_verification: bool = Query(False, description="Simulate verification failure")
):
    """
    Executes task with Server-Sent Events (SSE) streaming progress updates to UI in real-time.
    """
    queue = asyncio.Queue()

    def step_callback(state: AgentState):
        queue.put_nowait(state.model_dump())

    async def event_generator():
        db = SessionLocal()
        orchestrator = AgentOrchestrator()
        sim_ctx = {
            "fail_first_update": fail_first_update,
            "fail_verification": fail_verification
        }

        async def worker():
            try:
                await asyncio.to_thread(
                    orchestrator.execute_task,
                    db=db,
                    user_goal=goal,
                    simulation_context=sim_ctx,
                    step_callback=step_callback
                )
            except Exception as e:
                logger.error(f"Task stream error: {e}")
                queue.put_nowait({"error": str(e), "status": "FAILED"})
            finally:
                db.close()
                queue.put_nowait(None)

        task = asyncio.create_task(worker())

        while True:
            item = await queue.get()
            if item is None:
                yield "event: end\ndata: {}\n\n"
                break
            yield f"event: update\ndata: {json.dumps(item)}\n\n"
            await asyncio.sleep(0.05)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }
    )
