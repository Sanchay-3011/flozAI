"""
FastAPI Routes
Main API endpoints for FlozAI
"""
from fastapi import FastAPI, HTTPException, APIRouter, Depends, Header
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware
from flozai.schemas.api_schemas import (
    ParseIntentRequest,
    ParseIntentResponse,
)
from flozai.schemas.intent_schema import IntentStatus
from flozai.core.intent_parser import IntentParser
from flozai.core.workflow_builder import WorkflowBuilder
from flozai.core.validator import WorkflowValidator
from flozai.core.integrations import (
    analyze_workflow_requirements, 
    get_user_integrations, 
    save_integration, 
    delete_integration
)
from flozai.core.oauth import (
    get_authorization_url,
    exchange_code_for_token,
    OAUTH_PROVIDERS
)
from flozai.api.supabase_routes import router as supabase_router
from flozai.utils.logger import get_logger

app = FastAPI(
    title="FlozAI",
    description="AI reasoning layer for workflow automation",
    version="0.1.0"
)

app.include_router(supabase_router)

core_router = APIRouter(prefix="/api")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger = get_logger(__name__)

# ── Instantiate fresh on every request — no stale singletons ──────────
def get_intent_parser():
    return IntentParser()

def get_workflow_builder():
    return WorkflowBuilder()

def get_validator():
    return WorkflowValidator()

async def get_optional_user_id(authorization: Optional[str] = Header(default=None)) -> str:
    if not authorization:
        return "default_user"
    try:
        parts = authorization.split(" ", 1)
        if len(parts) == 2 and parts[0].lower() == "bearer":
            token = parts[1]
            from flozai.services.auth_service import AuthService
            from flozai.services.database_service import DatabaseService
            auth_service = AuthService()
            user = await auth_service.get_current_user(token)
            if user and "user" in user and user["user"] and "id" in user["user"]:
                user_id = str(user["user"]["id"])
                email = str(user["user"].get("email", ""))
                
                try:
                    db_service = DatabaseService()
                    await db_service.get_or_create_user(user_id, email)
                except Exception as db_e:
                    logger.error(f"Failed to sync user to public.users: {db_e}")
                    
                return user_id
    except Exception as e:
        logger.error(f"Error in get_optional_user_id: {e}")
    return "default_user"


@app.get("/")
async def root():
    return {"service": "FlozAI", "status": "running", "version": "0.1.0"}


@core_router.get("/capabilities")
async def get_capabilities_endpoint():
    from flozai.schemas.capabilities import get_capabilities
    caps = get_capabilities()
    return {
        "triggers": [
            {"id": t.id, "name": t.display_name, "description": t.description}
            for t in caps.triggers
        ],
        "actions": [
            {"id": a.id, "name": a.display_name, "description": a.description}
            for a in caps.actions
        ],
        "integrations": [
            {
                "id": i.id,
                "name": i.display_name,
                "supported_triggers": i.supported_triggers,
                "supported_actions": i.supported_actions
            }
            for i in caps.integrations
        ]
    }


@core_router.post("/parse", response_model=ParseIntentResponse)
async def parse_intent(request: ParseIntentRequest, user_id: str = Depends(get_optional_user_id)):
    try:
        if not request.user_id or request.user_id == "default_user":
            request.user_id = user_id
        logger.info(f"Parsing intent: {request.user_input[:100]}... for user {request.user_id}")

        # Fresh instances on every request
        intent_parser    = get_intent_parser()
        workflow_builder = get_workflow_builder()
        validator        = get_validator()

        # Step 1: Parse intent
        intent = intent_parser.parse(
            user_input=request.user_input,
            user_language="en"
        )

        logger.info(f"Intent parsed with status: {intent.status}")

        workflow    = None
        explanation = ""
        missing_integrations = []

        if intent.status == IntentStatus.CLEAR:
            workflow = workflow_builder.build(intent)

            is_valid, errors = validator.validate(workflow)

            if not is_valid:
                logger.error(f"Validation failed: {errors}")
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "Workflow validation failed",
                        "details": errors
                    }
                )
            
            # Analyze missing integrations
            missing_integrations = analyze_workflow_requirements(workflow, request.user_id or "default_user")

            # Build trigger description for multi-trigger support
            all_triggers = intent.get_all_triggers()
            trigger_desc = " or ".join(
                t.type.replace('_', ' ') for t in all_triggers if t.type
            )

            desc = (intent.workflow_description or "process your request").lower()
            explanation = (
                f"I'll {desc}. "
                f"This workflow will trigger when {trigger_desc} "
                f"and perform {len(workflow.actions)} action(s)."
            )

        elif intent.status == IntentStatus.NEEDS_CLARIFICATION:
            explanation = intent.clarification_question

        elif intent.status == IntentStatus.OUT_OF_SCOPE:
            explanation = (
                f"{intent.out_of_scope_reason} "
                f"{intent.suggested_alternative or ''}"
            )

        return ParseIntentResponse(
            intent=intent,
            workflow=workflow,
            explanation=explanation,
            missing_integrations=missing_integrations
        )

    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Validation or parsing error: {e}")
        raise HTTPException(
            status_code=400,
            detail={"error": "Invalid request or parsing failure", "details": str(e)}
        )
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        logger.error(f"Unexpected error parsing intent: {e}\n{error_trace}")
        
        # Check for common environment issues
        import os
        if not os.getenv("GROQ_API_KEY"):
            raise HTTPException(
                status_code=500,
                detail={"error": "Configuration error", "details": "GROQ_API_KEY is not set in the environment."}
            )

        raise HTTPException(
            status_code=500,
            detail={"error": "Internal server error", "details": str(e)}
        )


@core_router.post("/validate")
async def validate_workflow(workflow_json: dict):
    try:
        from flozai.schemas.workflow_schema import WorkflowDefinition
        workflow = WorkflowDefinition(**workflow_json)
        is_valid, errors = WorkflowValidator().validate(workflow)
        return {"valid": is_valid, "errors": errors}
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail={"error": "Invalid workflow JSON", "details": str(e)}
        )


@core_router.get("/integrations/registry")
async def get_integration_registry():
    """Returns the full integration registry with all 15 core integrations."""
    from flozai.core.integration_registry import get_all_integrations
    integrations = get_all_integrations()
    # Strip handler info (internal detail) before sending to frontend
    return [{k: v for k, v in i.items() if k not in ("handler", "handlerArgs")} for i in integrations]


@core_router.get("/integrations")
async def get_integrations(user_id: str = Depends(get_optional_user_id)):
    return get_user_integrations(user_id)


@core_router.post("/integrations/{integration_type}")
async def connect_integration(integration_type: str, credential_data: dict, user_id: str = Depends(get_optional_user_id)):
    try:
        save_integration(integration_type, credential_data, user_id)
        return {"status": "success", "message": f"Connected to {integration_type}"}
    except ValueError as e:
        # Validation failed (invalid API key)
        raise HTTPException(status_code=400, detail={"error": "Validation failed", "message": str(e)})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@core_router.delete("/integrations/{integration_type}")
async def disconnect_integration(integration_type: str, user_id: str = Depends(get_optional_user_id)):
    delete_integration(integration_type, user_id)
    return {"status": "success", "message": f"Disconnected from {integration_type}"}


# ── OAuth Routes ──────────────────────────────────────────────────────

@core_router.get("/oauth/{provider}/authorize")
async def oauth_authorize(provider: str, user_id: str = Depends(get_optional_user_id)):
    """Returns the OAuth authorization URL for the given provider."""
    try:
        result = get_authorization_url(provider, user_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail={"error": str(e)})
 
 
@core_router.get("/oauth/callback")
async def oauth_callback(code: str = None, state: str = None, error: str = None):
    """Handles the OAuth redirect callback."""
    from fastapi.responses import HTMLResponse
    
    if error:
        return HTMLResponse(f"""
            <html><body><script>
                window.opener.postMessage({{ type: 'oauth_error', error: '{error}' }}, '*');
                window.close();
            </script><p>Authorization failed: {error}. This window will close.</p></body></html>
        """)
    
    if not code or not state:
        return HTMLResponse("<html><body><p>Missing code or state parameter.</p></body></html>")
    
    # Parse provider and user_id from state (format: "provider:user_id:random_hex")
    parts = state.split(":") if state else []
    provider = parts[0] if len(parts) >= 1 else ""
    user_id = parts[1] if len(parts) >= 2 else "default_user"
    
    try:
        token_data = exchange_code_for_token(provider, code)
        
        # Save the OAuth tokens as integration credentials
        save_integration(provider, {
            "oauth": True,
            "access_token": token_data["access_token"],
            "refresh_token": token_data.get("refresh_token"),
            "expires_in": token_data.get("expires_in"),
        }, user_id)
        
        provider_name = OAUTH_PROVIDERS.get(provider, {}).get("name", provider)
        
        return HTMLResponse(f"""
            <html><body><script>
                window.opener.postMessage({{ type: 'oauth_success', provider: '{provider}' }}, '*');
                window.close();
            </script><p>{provider_name} connected successfully! This window will close.</p></body></html>
        """)
    except Exception as e:
        logger.error(f"OAuth callback error: {e}")
        return HTMLResponse(f"""
            <html><body><script>
                window.opener.postMessage({{ type: 'oauth_error', error: '{str(e)[:100]}' }}, '*');
                window.close();
            </script><p>Error: {str(e)[:200]}. This window will close.</p></body></html>
        """)


# ── Workflow Execution Routes ─────────────────────────────────────────

@core_router.post("/execute")
async def execute_workflow(workflow: dict, user_id: str = Depends(get_optional_user_id)):
    """Execute a workflow using real integration APIs."""
    from flozai.core.executor import WorkflowExecutor
    try:
        executor = WorkflowExecutor(user_id=user_id)
        result = executor.execute(workflow)
        return result
    except Exception as e:
        logger.error(f"Workflow execution error: {e}")
        raise HTTPException(status_code=500, detail={"error": "Execution failed", "message": str(e)})


@core_router.get("/executions")
async def get_executions(workflow_name: str = None):
    """Get execution history, optionally filtered by workflow name."""
    from flozai.core.executor import get_execution_history
    return get_execution_history(workflow_name)


# ── Condition Routes ──────────────────────────────────────────────────

@core_router.post("/conditions/parse")
async def parse_condition_text(body: dict):
    """Parse natural language condition into structured condition object."""
    from flozai.core.condition_parser import parse_condition
    text = body.get("text", "")
    try:
        result = parse_condition(text)
        return result
    except Exception as e:
        logger.error(f"Condition parse error: {e}")
        raise HTTPException(status_code=400, detail={"error": "Failed to parse condition", "message": str(e)})


@core_router.post("/conditions/validate")
async def validate_condition(body: dict):
    """Validate a structured condition object."""
    from flozai.core.condition_evaluator import evaluate_condition

    condition = body.get("condition", {})
    test_context = body.get("context", {})

    errors = []
    valid_operators = {"equals", "not_equals", "contains", "greater_than", "exists", "not_exists"}

    if not condition.get("field"):
        errors.append("Missing 'field' — which data field should be checked?")
    if not condition.get("operator"):
        errors.append("Missing 'operator' — what comparison should be made?")
    elif condition["operator"] not in valid_operators:
        errors.append(f"Invalid operator '{condition['operator']}'. Must be one of: {', '.join(sorted(valid_operators))}")
    if condition.get("operator") not in ("exists", "not_exists") and not condition.get("value"):
        errors.append("Missing 'value' — what should the field be compared to?")

    if errors:
        return {"valid": False, "errors": errors}

    # If test_context provided, do a dry-run evaluation
    dry_run = None
    if test_context:
        dry_run = evaluate_condition(condition, test_context)

    return {"valid": True, "errors": [], "dry_run": dry_run}


# ╔═══════════════════════════════════════════════════════════════════╗
#   AI PROVIDERS — Multi-provider LLM management
# ╚═══════════════════════════════════════════════════════════════════╝

AI_PROVIDER_META = {
    "openai":    {"name": "OpenAI", "description": "GPT-4o, GPT-4o-mini", "key_prefix": "sk-"},
    "groq":      {"name": "Groq", "description": "Llama 3.3 70B — blazing fast", "key_prefix": "gsk_"},
    "anthropic": {"name": "Anthropic", "description": "Claude Sonnet, Claude Haiku", "key_prefix": "sk-ant-"},
    "gemini":    {"name": "Google Gemini", "description": "Gemini 2.0 Flash, Gemini 2.5 Pro", "key_prefix": "AI"},
}


@core_router.get("/ai/providers")
async def get_ai_providers(user_id: str = Depends(get_optional_user_id)):
    """List all AI providers with connection status."""
    integrations = get_user_integrations(user_id)
    providers = []
    for pid, meta in AI_PROVIDER_META.items():
        config = integrations.get(pid, {})
        api_key = config.get("credential_data", {}).get("apiKey", "")
        is_connected = bool(api_key)
        masked_key = f"{api_key[:8]}...{api_key[-4:]}" if api_key and len(api_key) > 12 else ""
        providers.append({
            "id": pid,
            "name": meta["name"],
            "description": meta["description"],
            "connected": is_connected,
            "masked_key": masked_key,
        })
    return {"providers": providers}


@core_router.post("/ai/providers/connect")
async def connect_ai_provider(request: dict, user_id: str = Depends(get_optional_user_id)):
    """Connect an AI provider by saving and validating its API key."""
    provider = request.get("provider", "").lower()
    api_key = request.get("api_key", "").strip()

    if provider not in AI_PROVIDER_META:
        raise HTTPException(400, f"Unknown provider: {provider}")
    if not api_key:
        raise HTTPException(400, "API key is required")

    try:
        save_integration(provider, {"apiKey": api_key}, user_id)
        return {"success": True, "message": f"{AI_PROVIDER_META[provider]['name']} connected successfully!"}
    except ValueError as e:
        raise HTTPException(400, str(e))


@core_router.delete("/ai/providers/{provider}")
async def disconnect_ai_provider(provider: str, user_id: str = Depends(get_optional_user_id)):
    """Disconnect an AI provider."""
    if provider not in AI_PROVIDER_META:
        raise HTTPException(400, f"Unknown provider: {provider}")
    delete_integration(provider, user_id)
    return {"success": True, "message": f"{AI_PROVIDER_META[provider]['name']} disconnected."}


# ╔═══════════════════════════════════════════════════════════════════╗
#   AI AGENTS — Smart workflow steps
# ╚═══════════════════════════════════════════════════════════════════╝

@core_router.get("/agents")
async def get_agents():
    """Return all available AI agents with their metadata."""
    from flozai.core.agents.agent_registry import get_all_agents_metadata
    return {"agents": get_all_agents_metadata()}


@core_router.post("/agents/test")
async def test_agent(request: dict, user_id: str = Depends(get_optional_user_id)):
    """Test-run an agent with sample input."""
    agent_type = request.get("agent_type")
    inputs = request.get("inputs", {})
    provider = request.get("provider")
    tier = request.get("tier", "fast")

    if not agent_type:
        raise HTTPException(400, "agent_type is required")

    from flozai.core.agents.agent_registry import get_agent
    from flozai.core.llm.llm_factory import get_llm_client

    try:
        agent = get_agent(agent_type)
    except ValueError as e:
        raise HTTPException(400, str(e))

    try:
        llm = get_llm_client(user_id, provider=provider, tier=tier)
    except ValueError as e:
        raise HTTPException(400, str(e))

    result = agent.execute(inputs, llm)
    return result


# Include core_router after all its endpoints have been decorated
app.include_router(core_router)