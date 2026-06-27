"""
Workflow Execution Engine
Executes workflow actions using real API integrations.
"""
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
from flozai.core.integrations import get_user_integrations
from flozai.utils.logger import get_logger

logger = get_logger(__name__)

# Execution history storage
EXECUTION_LOG_PATH = Path("tmp/execution_history.json")


def _ensure_exec_storage():
    if not EXECUTION_LOG_PATH.parent.exists():
        EXECUTION_LOG_PATH.parent.mkdir(parents=True)
    if not EXECUTION_LOG_PATH.exists():
        with open(EXECUTION_LOG_PATH, 'w') as f:
            json.dump([], f)


class WorkflowExecutor:
    """Executes a workflow by running each action handler sequentially."""
    
    def __init__(self, user_id: str = "default_user"):
        self.user_id = user_id
        self.integrations = get_user_integrations(user_id)
        self._handlers = {}
        self._register_handlers()
    
    def _register_handlers(self):
        """Register action handlers for all 15 core integrations."""
        from flozai.core.action_handlers.gmail_handler import GmailHandler
        from flozai.core.action_handlers.slack_handler import SlackHandler
        from flozai.core.action_handlers.openai_handler import OpenAIHandler
        from flozai.core.action_handlers.crm_handler import CRMHandler
        from flozai.core.action_handlers.webhook_handler import WebhookHandler
        from flozai.core.action_handlers.google_sheets_handler import GoogleSheetsHandler
        from flozai.core.action_handlers.scheduler_handler import SchedulerHandler
        from flozai.core.action_handlers.perplexity_handler import PerplexityHandler
        from flozai.core.action_handlers.notion_handler import NotionHandler
        from flozai.core.action_handlers.airtable_handler import AirtableHandler
        from flozai.core.action_handlers.stripe_handler import StripeHandler
        from flozai.core.action_handlers.linkedin_handler import LinkedInHandler
        from flozai.core.action_handlers.whatsapp_handler import WhatsAppHandler
        from flozai.core.action_handlers.google_calendar_handler import GoogleCalendarHandler
        from flozai.core.action_handlers.weather_handler import WeatherHandler
        
        self._handlers = {
            # Communication
            "gmail": GmailHandler(),
            "slack": SlackHandler(),
            "whatsapp": WhatsAppHandler(),
            "linkedin": LinkedInHandler(),
            # CRM
            "salesforce": CRMHandler("salesforce"),
            "hubspot": CRMHandler("hubspot"),
            "crm": CRMHandler("generic"),
            # Data & Storage
            "google_sheets": GoogleSheetsHandler(),
            "notion": NotionHandler(),
            "airtable": AirtableHandler(),
            # AI
            "openai": OpenAIHandler(),
            "perplexity": PerplexityHandler(),
            # Payments
            "stripe": StripeHandler(),
            # Scheduling & Utility
            "scheduler": SchedulerHandler(),
            "google_calendar": GoogleCalendarHandler(),
            "webhook": WebhookHandler(),
            "weather": WeatherHandler(),
        }
        
        # Integrations that don't require external credentials
        self._no_auth = {"scheduler", "webhook", "weather"}
    
    def execute(self, workflow: Dict) -> Dict:
        """
        Execute a workflow. Returns an execution result with per-step logs.
        """
        execution_id = uuid.uuid4().hex[:12]
        execution = {
            "execution_id": execution_id,
            "workflow_name": workflow.get("name", "Untitled"),
            "started_at": datetime.now().isoformat(),
            "status": "running",
            "steps": [],
            "context": {}
        }
        
        steps = workflow.get("steps", [])
        
        for i, step in enumerate(steps):
            step_type = step.get("type", "ACTION")
            integration = step.get("integration", "").lower()
            action = step.get("action", "")
            
            step_result = {
                "step_index": i,
                "integration": integration,
                "action": action,
                "type": step_type,
                "status": "running",
                "result": None,
                "error": None,
            }
            
            # Built-in triggers (scheduler, webhook) — execute through handler
            if step_type == "TRIGGER" and integration in self._no_auth:
                handler = self._handlers.get(integration)
                if handler:
                    try:
                        result = handler.execute(action or "trigger", {}, step.get("params", {}), execution["context"])
                        step_result["status"] = "success"
                        step_result["result"] = result
                        execution["context"][f"step_{i}_{integration}"] = result
                    except Exception as e:
                        step_result["status"] = "skipped"
                        step_result["result"] = f"Trigger ({integration}): {str(e)}"
                else:
                    step_result["status"] = "skipped"
                    step_result["result"] = f"Trigger ({integration}) — will listen for events when deployed."
                execution["steps"].append(step_result)
                continue
            
            # Regular triggers — skip execution (they're event sources)
            if step_type == "TRIGGER":
                step_result["status"] = "skipped"
                step_result["result"] = f"Trigger ({integration}) — will listen for events when deployed."
                execution["steps"].append(step_result)
                continue
            
            # ── Condition Check (supports array `conditions` and legacy `condition`) ──
            from flozai.core.condition_evaluator import evaluate_condition
            
            step_conditions = step.get("conditions", [])
            # Backwards compat: single `condition` field
            legacy_cond = step.get("condition")
            if legacy_cond and not step_conditions:
                step_conditions = [legacy_cond]
            
            # Filter to enabled conditions only
            active_conditions = [c for c in step_conditions if c.get("enabled", True) and c.get("field")]
            
            if active_conditions:
                all_passed = True
                condition_results = []
                
                for cond in active_conditions:
                    cond_result = evaluate_condition(cond, execution["context"])
                    condition_results.append(cond_result)
                    if not cond_result["passed"]:
                        all_passed = False
                
                step_result["condition_results"] = condition_results
                
                if not all_passed:
                    failed = [r for r in condition_results if not r["passed"]]
                    reason = "; ".join(r["reason"] for r in failed)
                    step_result["status"] = "skipped"
                    step_result["result"] = f"Condition not met: {reason}"
                    logger.info(f"Step {i} ({integration}.{action}) skipped — {reason}")
                    execution["steps"].append(step_result)
                    continue
                else:
                    logger.info(f"Step {i} ({integration}.{action}) all {len(active_conditions)} condition(s) passed")

            # ── AI Agent Execution ──
            if step_type.lower() == "ai_agent":
                agent_type = step.get("agent_type", "")
                try:
                    from flozai.core.agents.agent_registry import get_agent
                    from flozai.core.llm.llm_factory import get_llm_client

                    agent = get_agent(agent_type)

                    # Resolve input mapping from context
                    input_mapping = step.get("input_mapping", {})
                    agent_inputs = step.get("params", {}).copy()
                    for key, template in input_mapping.items():
                        if isinstance(template, str) and template.startswith("{{") and template.endswith("}}"):
                            path = template[2:-2].strip()  # e.g. "step_0_gmail.content"
                            parts = path.split(".", 1)
                            ctx_val = execution["context"].get(parts[0], {})
                            if len(parts) > 1 and isinstance(ctx_val, dict):
                                agent_inputs[key] = ctx_val.get(parts[1], template)
                            else:
                                agent_inputs[key] = ctx_val if ctx_val else template
                        else:
                            agent_inputs[key] = template

                    # Get LLM client
                    provider = step.get("provider")
                    tier = step.get("model_tier", "fast")
                    llm = get_llm_client(self.user_id, provider=provider, tier=tier)

                    # Execute
                    result = agent.execute(agent_inputs, llm)
                    step_result["status"] = "success" if result.get("status") == "success" else "error"
                    step_result["result"] = result
                    execution["context"][f"step_{i}_agent"] = result.get("output", {})

                except Exception as e:
                    logger.error(f"Step {i} AI agent ({agent_type}) failed: {e}")
                    step_result["status"] = "error"
                    step_result["error"] = str(e)

                execution["steps"].append(step_result)
                continue

            # Get credentials (skip for no-auth integrations)
            if integration in self._no_auth:
                creds = {}
            else:
                creds = self.integrations.get(integration, {}).get("credential_data", {})
                if not creds:
                    step_result["status"] = "error"
                    step_result["error"] = f"No credentials found for {integration}. Please connect it first."
                    execution["steps"].append(step_result)
                    execution["status"] = "failed"
                    break
            
            # Get handler
            handler = self._handlers.get(integration)
            if not handler:
                step_result["status"] = "error"
                step_result["error"] = f"No handler available for {integration}."
                execution["steps"].append(step_result)
                execution["status"] = "failed"
                break
            
            # Execute!
            try:
                result = handler.execute(action, creds, step.get("params", {}), execution["context"])
                step_result["status"] = "success"
                step_result["result"] = result
                
                # Store result in context for subsequent steps
                execution["context"][f"step_{i}_{integration}"] = result
                
            except Exception as e:
                logger.error(f"Step {i} failed ({integration}.{action}): {e}")
                step_result["status"] = "error"
                step_result["error"] = str(e)
                execution["steps"].append(step_result)
                execution["status"] = "failed"
                break
            
            execution["steps"].append(step_result)
        
        # Final status
        if execution["status"] == "running":
            execution["status"] = "completed"
        
        execution["completed_at"] = datetime.now().isoformat()
        
        # Save execution log
        self._save_execution(execution)
        
        return execution
    
    def _save_execution(self, execution: Dict):
        _ensure_exec_storage()
        try:
            with open(EXECUTION_LOG_PATH, 'r') as f:
                history = json.load(f)
            history.append(execution)
            # Keep last 100 executions
            history = history[-100:]
            with open(EXECUTION_LOG_PATH, 'w') as f:
                json.dump(history, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save execution log: {e}")


def get_execution_history(workflow_name: Optional[str] = None) -> List[Dict]:
    _ensure_exec_storage()
    try:
        with open(EXECUTION_LOG_PATH, 'r') as f:
            history = json.load(f)
        if workflow_name:
            history = [h for h in history if h.get("workflow_name") == workflow_name]
        return history
    except Exception:
        return []
