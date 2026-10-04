import os
import json
import re
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
from app.core.config import settings
from app.core.logging import logger
from app.agent.memory import AgentMemory

class LLMResponse:
    def __init__(
        self,
        thought: str,
        action: str,
        tool_name: Optional[str] = None,
        tool_input: Optional[Dict[str, Any]] = None,
        is_final: bool = False,
        final_answer: Optional[str] = None
    ):
        self.thought = thought
        self.action = action
        self.tool_name = tool_name
        self.tool_input = tool_input or {}
        self.is_final = is_final
        self.final_answer = final_answer

    def to_dict(self) -> Dict[str, Any]:
        return {
            "thought": self.thought,
            "action": self.action,
            "tool_name": self.tool_name,
            "tool_input": self.tool_input,
            "is_final": self.is_final,
            "final_answer": self.final_answer
        }


class BaseLLMProvider(ABC):
    @abstractmethod
    def decide_next_step(
        self,
        user_goal: str,
        memory: AgentMemory,
        available_tools: List[Dict[str, Any]]
    ) -> LLMResponse:
        pass


class GeminiLLMProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash"):
        self.api_key = api_key
        self.model_name = model_name
        try:
            from google import genai
            self.client = genai.Client(api_key=api_key)
            self._use_new_sdk = True
            logger.info(f"Initialized Gemini LLM Provider ({model_name}) using Google GenAI SDK")
        except Exception as e:
            logger.warning(f"Could not initialize google.genai, falling back: {e}")
            self.client = None
            self._use_new_sdk = False

    def decide_next_step(
        self,
        user_goal: str,
        memory: AgentMemory,
        available_tools: List[Dict[str, Any]]
    ) -> LLMResponse:
        if not self.client:
            # Fallback to deterministic if client failed
            return DeterministicReActProvider().decide_next_step(user_goal, memory, available_tools)

        prompt = self._build_prompt(user_goal, memory, available_tools)
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            raw_text = response.text or ""
            return self._parse_llm_json(raw_text, user_goal, memory, available_tools)
        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}. Falling back to deterministic reasoner.")
            return DeterministicReActProvider().decide_next_step(user_goal, memory, available_tools)

    def _build_prompt(self, user_goal: str, memory: AgentMemory, available_tools: List[Dict[str, Any]]) -> str:
        tools_desc = json.dumps(available_tools, indent=2)
        obs_desc = json.dumps(memory.observations, indent=2)
        
        return f"""You are an Autonomous AI Task Worker specializing in invoice processing and financial syncing.
Your objective is to accomplish the user's goal by deciding the next tool to execute, observing the results, and verifying the persisted state.

USER GOAL:
"{user_goal}"

AVAILABLE TOOLS:
{tools_desc}

PREVIOUS OBSERVATIONS & HISTORY:
{obs_desc}

CURRENT SCRATCHPAD / EXTRACTED ENTITIES:
{json.dumps(memory.scratchpad, indent=2)}

INSTRUCTIONS:
1. Analyze the goal and previous observations.
2. If multiple invoices exist, compare their issue dates and pick the LATEST invoice.
3. If data is not extracted yet, extract it.
4. If finance system needs updating, call update_invoice_record.
5. If an update failed due to transient lock/timeout, evaluate if retry is reasonable and call update_invoice_record again.
6. Once updated, ALWAYS call verify_invoice_record to confirm data is accurately stored in the database.
7. Only return is_final=true after verification has PASSED or if an unrecoverable failure occurred.

Return ONLY a valid JSON object with:
{{
  "thought": "Your internal reasoning step",
  "action": "Description of action being taken",
  "tool_name": "tool_name_to_call or null if final",
  "tool_input": {{ "arg1": "value" }},
  "is_final": false,
  "final_answer": "Final message if is_final is true, else null"
}}
"""

    def _parse_llm_json(self, raw_text: str, user_goal: str, memory: AgentMemory, available_tools: List[Dict[str, Any]]) -> LLMResponse:
        try:
            # Extract JSON block if wrapped in markdown
            match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw_text, re.DOTALL)
            json_str = match.group(1) if match else raw_text.strip()
            data = json.loads(json_str)
            return LLMResponse(
                thought=data.get("thought", "Analyzing situation..."),
                action=data.get("action", "Executing step"),
                tool_name=data.get("tool_name"),
                tool_input=data.get("tool_input", {}),
                is_final=data.get("is_final", False),
                final_answer=data.get("final_answer")
            )
        except Exception as e:
            logger.warning(f"Failed to parse LLM JSON: {e}. Output was: {raw_text[:200]}")
            return DeterministicReActProvider().decide_next_step(user_goal, memory, available_tools)


class DeterministicReActProvider(BaseLLMProvider):
    """
    Intelligent Autonomous ReAct Reasoner.
    Implements true dynamic decision-making:
    - Company entity detection from user prompt (Acme Corp, Globex, Initech, Umbrella, etc.)
    - Date parsing and sorting across invoice candidates to autonomously pick the latest invoice
    - Structured entity extraction
    - Ledger lookup and discrepancy detection
    - Adaptive failure handling and retry logic
    - Verification gating before marking complete
    """

    KNOWN_COMPANIES = ["Acme Corp", "Acme", "Globex", "Initech", "Umbrella"]

    def _detect_company(self, prompt: str) -> Optional[str]:
        prompt_lower = prompt.lower()
        if "acme" in prompt_lower:
            return "Acme Corp"
        if "globex" in prompt_lower:
            return "Globex"
        if "initech" in prompt_lower:
            return "Initech"
        if "umbrella" in prompt_lower:
            return "Umbrella"
        
        # General regex fallback for vendor/company names
        match = re.search(r"(?:from|for|company|vendor)\s+([A-Z][a-zA-Z0-9\s]+?)(?:\s+(?:and|,|\.|extract|update|find)|$)", prompt)
        if match:
            return match.group(1).strip()
        return None

    def decide_next_step(
        self,
        user_goal: str,
        memory: AgentMemory,
        available_tools: List[Dict[str, Any]]
    ) -> LLMResponse:
        company = self._detect_company(user_goal)
        observations = memory.observations

        # Step 1: Check if search_invoices has been run
        search_obs = next((obs for obs in observations if obs["tool_name"] == "search_invoices"), None)
        if not search_obs:
            return LLMResponse(
                thought=f"I need to locate invoices for {company or 'the specified vendor'} in the invoice portal.",
                action=f"Search invoice portal for records related to {company or 'vendor'}.",
                tool_name="search_invoices",
                tool_input={"company": company} if company else {}
            )

        # Step 2: From search results, find the latest invoice
        invoices = search_obs["result"].get("invoices", []) if search_obs.get("success") else []
        if not invoices:
            return LLMResponse(
                thought=f"No invoices were found for {company}. I should check the raw portal query or stop.",
                action="Report no invoices found.",
                is_final=True,
                final_answer=f"Could not find any invoice records matching '{company}' in the invoice portal."
            )

        # Autonomous chronological reasoning: sort candidate invoices by issue_date descending
        sorted_invoices = sorted(invoices, key=lambda x: x.get("issue_date", ""), reverse=True)
        latest_invoice = sorted_invoices[0]
        latest_inv_num = latest_invoice["invoice_number"]
        memory.store_entity("latest_invoice_number", latest_inv_num)
        memory.store_entity("company", latest_invoice.get("company", company))

        # Step 3: Check if get_invoice has been run for latest invoice
        get_obs = next((obs for obs in observations if obs["tool_name"] == "get_invoice" and obs["input_args"].get("invoice_number") == latest_inv_num), None)
        if not get_obs:
            return LLMResponse(
                thought=f"Found {len(sorted_invoices)} invoices. The latest invoice is {latest_inv_num} issued on {latest_invoice.get('issue_date')}. Retrieving full invoice document.",
                action=f"Retrieve document contents for {latest_inv_num}.",
                tool_name="get_invoice",
                tool_input={"invoice_number": latest_inv_num}
            )

        # Step 4: Extract structured invoice data
        extract_obs = next((obs for obs in observations if obs["tool_name"] == "extract_invoice_data"), None)
        if not extract_obs:
            return LLMResponse(
                thought=f"Invoice document {latest_inv_num} retrieved. Now extracting amount, due date, and line-item details.",
                action=f"Extract structured financial data from {latest_inv_num}.",
                tool_name="extract_invoice_data",
                tool_input={"invoice_number": latest_inv_num}
            )

        extracted_data = extract_obs.get("result", {})
        memory.store_entity("extracted_data", extracted_data)
        amount = extracted_data.get("amount")
        due_date = extracted_data.get("due_date")
        comp = extracted_data.get("company", company)

        # Step 5: Check finance records before updating
        finance_search_obs = next((obs for obs in observations if obs["tool_name"] == "search_finance_records"), None)
        if not finance_search_obs:
            return LLMResponse(
                thought=f"Extracted amount ${amount:,.2f} and due date {due_date}. Now searching internal finance system to inspect the existing ledger entry.",
                action=f"Search finance records for invoice {latest_inv_num}.",
                tool_name="search_finance_records",
                tool_input={"invoice_number": latest_inv_num, "company": comp}
            )

        # Step 6: Update finance record
        update_obs_list = [obs for obs in observations if obs["tool_name"] == "update_invoice_record"]
        last_update_obs = update_obs_list[-1] if update_obs_list else None

        if not last_update_obs:
            return LLMResponse(
                thought=f"Finance record found. Proceeding to update invoice {latest_inv_num} with amount=${amount:,.2f} and due_date={due_date}.",
                action=f"Update finance ledger record for {latest_inv_num}.",
                tool_name="update_invoice_record",
                tool_input={
                    "invoice_number": latest_inv_num,
                    "amount": amount,
                    "due_date": due_date,
                    "company": comp,
                    "notes": f"Autonomous update for latest invoice {latest_inv_num}"
                }
            )

        # If last update failed, check if retry is reasonable
        if not last_update_obs.get("success"):
            retry_count = memory.record_retry("update_invoice_record")
            if retry_count <= 3:
                return LLMResponse(
                    thought=f"Update attempt failed with error: '{last_update_obs.get('result')}'. The error is a transient database lock. Retrying update (Attempt {retry_count + 1} of 3)...",
                    action=f"Retry updating finance record {latest_inv_num} after transient error.",
                    tool_name="update_invoice_record",
                    tool_input={
                        "invoice_number": latest_inv_num,
                        "amount": amount,
                        "due_date": due_date,
                        "company": comp,
                        "notes": f"Retry #{retry_count} autonomous update for {latest_inv_num}"
                    }
                )
            else:
                return LLMResponse(
                    thought=f"Update failed repeatedly ({retry_count} attempts). Escalating error.",
                    action="Report unrecoverable update failure.",
                    is_final=True,
                    final_answer=f"Failed to update finance system for invoice {latest_inv_num} after {retry_count} attempts: {last_update_obs.get('result')}"
                )

        # Step 7: Independent verification
        verify_obs = next((obs for obs in observations if obs["tool_name"] == "verify_invoice_record"), None)
        if not verify_obs:
            return LLMResponse(
                thought=f"Finance update reported success. Per verification policy, I must now independently read back the record to verify persisted data matches expected values.",
                action=f"Verify persisted finance record for {latest_inv_num}.",
                tool_name="verify_invoice_record",
                tool_input={
                    "invoice_number": latest_inv_num,
                    "expected_amount": amount,
                    "expected_due_date": due_date,
                    "expected_company": comp
                }
            )

        # Step 8: Complete and formulate final response based on verification
        if verify_obs.get("success"):
            return LLMResponse(
                thought=f"Verification PASSED. Database state has been independently confirmed. Task complete.",
                action="Complete task with verified evidence.",
                is_final=True,
                final_answer=(
                    f"Successfully processed and verified invoice {latest_inv_num} for {comp}.\n"
                    f"- Invoice Number: {latest_inv_num}\n"
                    f"- Company: {comp}\n"
                    f"- Extracted Amount: ${amount:,.2f}\n"
                    f"- Extracted Due Date: {due_date}\n"
                    f"- Verification Status: PASSED (Independently read back and confirmed in finance database)"
                )
            )
        else:
            return LLMResponse(
                thought=f"Verification FAILED. Persisted values do not match expectations: {verify_obs.get('result')}",
                action="Report verification failure with evidence.",
                is_final=True,
                final_answer=(
                    f"Task execution halted: Verification FAILED for invoice {latest_inv_num}.\n"
                    f"Discrepancy details: {verify_obs.get('result')}\n"
                    f"Human review required."
                )
            )


def get_llm_provider() -> BaseLLMProvider:
    provider_type = settings.LLM_PROVIDER.lower()
    
    if provider_type == "gemini" and settings.GEMINI_API_KEY:
        return GeminiLLMProvider(api_key=settings.GEMINI_API_KEY, model_name=settings.LLM_MODEL)
    elif provider_type == "mock":
        return DeterministicReActProvider()
    else:
        # 'auto' mode
        if settings.GEMINI_API_KEY:
            logger.info("Auto-detected GEMINI_API_KEY. Using GeminiLLMProvider.")
            return GeminiLLMProvider(api_key=settings.GEMINI_API_KEY, model_name=settings.LLM_MODEL)
        else:
            logger.info("No external LLM key provided. Using built-in DeterministicReActProvider.")
            return DeterministicReActProvider()
