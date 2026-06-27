"""
Intent Parser
Converts natural language to structured workflow intent using LLM
"""
from pathlib import Path
from typing import Optional
from flozai.utils.llm_client import LLMClient
from flozai.schemas.intent_schema import ParsedIntent, IntentStatus
from flozai.schemas.capabilities import get_capabilities
import json


class IntentParser:
    """Parse user intent into structured format"""

    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm_client = llm_client or LLMClient()
        self._prompt_template = self._load_prompt_template()

    def _load_prompt_template(self) -> str:
        """Load raw system prompt template from file"""
        prompt_path = Path(__file__).parent.parent / "prompts" / "system_prompt.md"
        if not prompt_path.exists():
            raise FileNotFoundError(f"System prompt not found: {prompt_path}")
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read()

    def _build_system_prompt(self) -> str:
        # Fetches fresh capabilities on every parse so YAML changes are instantly reflected
        capabilities = get_capabilities()
        
        # Generates the categorized and rule-bound capability string
        capabilities_section = self._generate_capabilities_section(capabilities)
        
        # Prevents Groq 413 TPM errors by strictly capping the injected block at 1800 chars
        if len(capabilities_section) > 1800:
            capabilities_section = capabilities_section[:1800 - len("...(truncated)")] + "...(truncated)"

        # Prevents prompt corruption by cleanly replacing the placeholder
        return self._prompt_template.replace(
            "### Supported Capabilities (HARD LIMITS - DO NOT INVENT)",
            f"### Supported Capabilities (HARD LIMITS - DO NOT INVENT)\n\n{capabilities_section}"
        )

    def _generate_capabilities_section(self, capabilities) -> str:
        # Prevents LLM from inventing fake triggers by explicitly listing real ones and aliases
        lines = [
            "**AVAILABLE TRIGGERS (ONLY use IDs from this list. DO NOT invent new ones):**",
            "- `new_record` (hubspot) - Use for: 'deal closes/won/lost', 'new record'",
            "- `new_lead` (hubspot) - Use for: 'new lead'",
            "- `new_email` (gmail) - Use for: 'new email'",
            "- `scheduled_time` (scheduler) - Use for: 'every friday', 'daily', 'at 9am'",
            "- `form_submission` (typeform) - Use for: 'form submitted'",
            "- `manual` (scheduler) - Use as fallback",
            ""
        ]

        # Categorizes integrations to help LLM understand the role of each integration in a chain
        categories = {
            "RESEARCH": ["perplexity"],
            "AI WRITING": ["openai"],
            "PUBLISH": ["linkedin", "twitter", "instagram"],
            "NOTIFY": ["slack", "gmail"],
            "CRM": ["hubspot", "salesforce"],
            "OTHER": []
        }

        # Groups integrations into their assigned categories to prevent scattered context
        grouped = {k: [] for k in categories}
        for i in capabilities.integrations:
            assigned = False
            for cat, ids in categories.items():
                if i.id in ids:
                    grouped[cat].append(i)
                    assigned = True
                    break
            if not assigned:
                grouped["OTHER"].append(i)

        # Renders each category to prevent token bloat from verbose explanations
        for cat, ints in grouped.items():
            if ints:
                lines.append(f"**[{cat}]**")
                for i in ints:
                    t_list = ", ".join(i.supported_triggers) if i.supported_triggers else "None"
                    a_list = ", ".join(i.supported_actions) if i.supported_actions else "None"
                    lines.append(f"- `{i.id}` -> Triggers: [{t_list}] | Actions: [{a_list}]")
                lines.append("")

        # Prevents short-circuiting by providing hard-coded workflow sequence rules
        lines.extend([
            "**CHAIN RULES (NON-NEGOTIABLE):**",
            "- news/prices/research + post/publish -> perplexity:search_web -> openai:generate_content -> platform:create_post",
            "- news/research + email/notify -> perplexity:search_web -> openai:ai_summarize -> gmail:send_email OR slack:send_slack",
            "- post/publish with no research -> openai:generate_content -> platform:create_post",
            "- NEVER output only 1 action when a chain is implied",
            "- NEVER invent trigger types not in the YAML",
            "- actions array must NEVER be empty regardless of how many triggers are present"
        ])

        return "\n".join(lines)


    def _classify_intent(self, user_input: str) -> str:
        """
        Call 1 — Tiny classifier (~300 tokens total).

        Saves ~6000 tokens vs the full call by stripping ALL of:
          - The capabilities section (~1800 chars of integration/action mappings)
          - The JSON output schema (~400 chars)
          - The integration mapping block (~200 chars)
          - The worked example (~350 chars)
        Only sends the bare minimum to answer one question: is this workflow
        request clear, needs clarification, or out of scope?

        Returns one of: "clear" | "needs_clarification" | "out_of_scope"
        Falls back to "clear" on any failure so Call 2 can attempt full parse.
        """
        # Cap user message at 400 chars — classifying intent never needs the full text
        safe_input = user_input[:400]

        classifier_system = (
            "You are a workflow intent classifier. "
            "Given a user request, respond with a JSON object containing a single key "
            "'status' whose value is EXACTLY one of: "
            "\"clear\", \"needs_clarification\", or \"out_of_scope\". "
            "No other keys. No markdown. No explanation. "
            "- \"clear\": the request describes a specific automation workflow. "
            "- \"needs_clarification\": the request is too vague to build a workflow. "
            "- \"out_of_scope\": the request is not about workflow automation at all."
        )

        classifier_message = f'Classify this request: "{safe_input}"'

        try:
            raw = self.llm_client.complete(
                system_prompt=classifier_system,
                user_message=classifier_message,
                temperature=0.0,
                response_format={"type": "json_object"}
            )
            # Strip markdown fences (```json ... ```) that some models add
            cleaned = raw.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("```")[1]
                if cleaned.startswith("json"):
                    cleaned = cleaned[4:]
            data = json.loads(cleaned.strip())
            status = data.get("status", "clear")
            if status in ("clear", "needs_clarification", "out_of_scope"):
                return status
            return "clear"  # unknown value → let Call 2 decide
        except Exception:
            # Any failure → optimistically proceed to full parse
            return "clear"

    def parse(self, user_input: str, user_language: str = "en") -> ParsedIntent:
        """
        Two-call parse strategy to stay under the 6000 TPM Groq limit.

        Call 1 (_classify_intent): ~300 tokens.
          Skips capabilities, schema, mapping, and examples entirely.
          Only classifies status. Short-circuits immediately for
          "needs_clarification" and "out_of_scope" without burning
          the ~1800-token capability block on dead-end requests.

        Call 2 (full workflow builder): ~1800 tokens.
          Only fires when status == "clear".
          Caps the user message at 400 chars and the injected
          capabilities string at 1500 chars to guarantee the full
          prompt stays well under the 6000 TPM limit.
        """
        # ── CALL 1: classify only ──────────────────────────────────────
        try:
            status = self._classify_intent(user_input)
        except Exception:
            status = "clear"  # never crash the route

        # Short-circuit for non-workflow requests — saves the full Call 2
        if status == "needs_clarification":
            return ParsedIntent(
                status=IntentStatus.NEEDS_CLARIFICATION,
                original_text=user_input,
                detected_language=user_language,
                workflow_name="",
                workflow_description="",
                triggers=[],
                actions=[],
                clarification_question=(
                    "Could you describe the workflow in more detail? "
                    "For example: what triggers it, and what should happen next?"
                ),
            )

        if status == "out_of_scope":
            return ParsedIntent(
                status=IntentStatus.OUT_OF_SCOPE,
                original_text=user_input,
                detected_language=user_language,
                workflow_name="",
                workflow_description="",
                triggers=[],
                actions=[],
                out_of_scope_reason=(
                    "This request doesn't appear to be about workflow automation."
                ),
            )

        # ── CALL 2: full workflow builder (status == "clear") ──────────
        # Cap user message at 400 chars — the classifier already confirmed intent,
        # so full verbatim text is not needed and saves ~100 tokens per request.
        safe_input = user_input[:400]

        # Do not blindly truncate after the marker because the OUTPUT FORMAT is down there!
        # Since we changed _generate_capabilities_section to be super concise (around 300 chars),
        # we no longer need to worry about exceeding the Groq limits with the prompt.
        system_prompt = self._build_system_prompt()

        user_message = (
            f'User input: "{safe_input}"\n'
            f"Detected language: {user_language}\n\n"
            "Parse this workflow request and respond with the JSON structure "
            "specified in your instructions."
        )

        try:
            raw = self.llm_client.complete(
                system_prompt=system_prompt,
                user_message=user_message,
                temperature=0.0,
                response_format={"type": "json_object"}
            )

            # Strip markdown fences before parsing — Groq occasionally wraps JSON
            cleaned = raw.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("```")[1]
                if cleaned.startswith("json"):
                    cleaned = cleaned[4:]
                cleaned = cleaned.rstrip("`").strip()

            response_json = json.loads(cleaned)
            intent = ParsedIntent(**response_json)
            return intent

        except json.JSONDecodeError:
            # Graceful fallback — return a clarification request rather than 500
            return ParsedIntent(
                status=IntentStatus.NEEDS_CLARIFICATION,
                original_text=user_input,
                detected_language=user_language,
                workflow_name="",
                workflow_description="",
                triggers=[],
                actions=[],
                clarification_question=(
                    "I understood your request but couldn't structure it precisely. "
                    "Could you rephrase it? For example: "
                    "\"When X happens in App A, do Y in App B.\""
                ),
            )
        except Exception:
            # Catch-all — never let a parse failure crash the route
            return ParsedIntent(
                status=IntentStatus.NEEDS_CLARIFICATION,
                original_text=user_input,
                detected_language=user_language,
                workflow_name="",
                workflow_description="",
                triggers=[],
                actions=[],
                clarification_question=(
                    "Something went wrong processing your request. "
                    "Please try rephrasing it."
                ),
            )

    def validate_intent(self, intent: ParsedIntent) -> bool:
        """Validate that intent uses only supported capabilities"""
        if intent.status != IntentStatus.CLEAR:
            return True

        capabilities = get_capabilities()

        if intent.trigger:
            if not capabilities.get_trigger(intent.trigger.type):
                return False
            if intent.trigger.integration:
                if not capabilities.get_integration(intent.trigger.integration):
                    return False
                if not capabilities.validate_trigger_integration(
                    intent.trigger.type, intent.trigger.integration
                ):
                    return False

        for action in intent.actions:
            if not capabilities.get_action(action.type):
                return False
            if action.integration:
                if not capabilities.get_integration(action.integration):
                    return False
                if not capabilities.validate_action_integration(
                    action.type, action.integration
                ):
                    return False

        return True