"""
Example API Routes using Supabase services
Add these routes to your FastAPI application
"""

from fastapi import APIRouter, HTTPException, Depends, Header
from typing import Optional
from datetime import datetime
import logging

from flozai.services.auth_service import AuthService, AuthError, LoginRequest, SignUpRequest
from flozai.services.database_service import (
    DatabaseService,
    DatabaseError,
    Workflow,
    WorkflowTask,
    ExecutionLog
)

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api", tags=["supabase"])

# Dependency to verify auth token
async def get_current_user_id(authorization: Optional[str] = Header(None)):
    """
    Extract and verify JWT token from Authorization header.
    Expected format: Bearer <token>
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authorization scheme")
        
        auth_service = AuthService()
        user = await auth_service.get_current_user(token)
        
        if not user:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        
        return user['id']
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authorization format")
    except Exception as e:
        logger.error(f"Auth verification error: {str(e)}")
        raise HTTPException(status_code=401, detail="Authentication failed")


# ─────────────────────────────────────────────────────────────────────────────
# Authentication Endpoints
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/auth/signup")
async def signup(request: SignUpRequest):
    """
    Sign up a new user.
    
    Returns:
        {user, session} on success
        
    Example:
        POST /api/auth/signup
        {
            "email": "user@example.com",
            "password": "securepassword123"
        }
    """
    try:
        auth_service = AuthService()
        result = await auth_service.sign_up(request.email, request.password)
        return result
    except AuthError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Signup error: {str(e)}")
        raise HTTPException(status_code=500, detail="Sign up failed")


@router.post("/auth/login")
async def login(request: LoginRequest):
    """
    Log in a user.
    
    Returns:
        {user, session} on success
        
    Example:
        POST /api/auth/login
        {
            "email": "user@example.com",
            "password": "securepassword123"
        }
    """
    try:
        auth_service = AuthService()
        result = await auth_service.login(request.email, request.password)
        return result
    except AuthError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(status_code=500, detail="Login failed")


@router.post("/auth/logout")
async def logout(current_user_id: str = Depends(get_current_user_id)):
    """
    Log out the current user.
    """
    try:
        auth_service = AuthService()
        await auth_service.logout()
        return {"message": "Logged out successfully"}
    except AuthError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/auth/me")
async def get_current_user(current_user_id: str = Depends(get_current_user_id)):
    """
    Get current user information.
    """
    try:
        db_service = DatabaseService()
        user = await db_service.get_user_profile(current_user_id)
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return user
    except Exception as e:
        logger.error(f"Get user error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get user")


# ─────────────────────────────────────────────────────────────────────────────
# Workflow Endpoints
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/workflows")
async def list_workflows(
    limit: int = 50,
    offset: int = 0,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Get all workflows for the current user with pagination.
    """
    try:
        db_service = DatabaseService()
        workflows = await db_service.list_workflows(current_user_id, limit=limit, offset=offset)
        return {"workflows": workflows, "total": len(workflows)}
    except DatabaseError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"List workflows error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to list workflows")


@router.get("/workflows/{workflow_id}")
async def get_workflow(
    workflow_id: str,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Get a specific workflow by ID.
    """
    try:
        db_service = DatabaseService()
        workflow = await db_service.get_workflow(current_user_id, workflow_id)
        
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        return workflow
    except HTTPException:
        raise
    except DatabaseError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Get workflow error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get workflow")


@router.post("/workflows")
async def create_workflow(
    workflow: Workflow,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Create a new workflow.
    
    Example:
        POST /api/workflows
        {
            "name": "Email Notification Workflow",
            "description": "Send emails when tasks complete"
        }
    """
    try:
        workflow.user_id = current_user_id
        db_service = DatabaseService()
        created = await db_service.create_workflow(current_user_id, workflow)
        return created
    except DatabaseError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Create workflow error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create workflow")


@router.patch("/workflows/{workflow_id}")
async def update_workflow(
    workflow_id: str,
    update_data: dict,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Update a workflow.
    """
    try:
        db_service = DatabaseService()
        updated = await db_service.update_workflow(current_user_id, workflow_id, update_data)
        return updated
    except DatabaseError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Update workflow error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update workflow")


@router.delete("/workflows/{workflow_id}")
async def delete_workflow(
    workflow_id: str,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Delete a workflow and all associated tasks and logs.
    """
    try:
        db_service = DatabaseService()
        await db_service.delete_workflow(current_user_id, workflow_id)
        return {"message": "Workflow deleted successfully"}
    except DatabaseError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Delete workflow error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete workflow")


# ─────────────────────────────────────────────────────────────────────────────
# Task Endpoints
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/workflows/{workflow_id}/tasks")
async def list_tasks(
    workflow_id: str,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Get all tasks for a workflow.
    """
    try:
        db_service = DatabaseService()
        tasks = await db_service.list_workflow_tasks(current_user_id, workflow_id)
        return {"tasks": tasks}
    except DatabaseError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"List tasks error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to list tasks")


@router.post("/workflows/{workflow_id}/tasks")
async def create_task(
    workflow_id: str,
    task: WorkflowTask,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Create a new task in a workflow.
    """
    try:
        task.workflow_id = workflow_id
        db_service = DatabaseService()
        created = await db_service.create_task(current_user_id, task)
        return created
    except DatabaseError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Create task error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create task")


@router.patch("/workflows/{workflow_id}/tasks/{task_id}")
async def update_task(
    workflow_id: str,
    task_id: str,
    update_data: dict,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Update a task.
    """
    try:
        db_service = DatabaseService()
        updated = await db_service.update_task(current_user_id, workflow_id, task_id, update_data)
        return updated
    except DatabaseError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Update task error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update task")


# ─────────────────────────────────────────────────────────────────────────────
# Execution Log Endpoints
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/workflows/{workflow_id}/logs")
async def list_logs(
    workflow_id: str,
    limit: int = 100,
    offset: int = 0,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Get execution logs for a workflow.
    """
    try:
        db_service = DatabaseService()
        logs = await db_service.list_workflow_logs(current_user_id, workflow_id, limit=limit, offset=offset)
        return {"logs": logs}
    except DatabaseError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"List logs error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to list logs")


@router.post("/workflows/{workflow_id}/logs")
async def create_log(
    workflow_id: str,
    log: ExecutionLog,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Create a new execution log entry.
    """
    try:
        log.workflow_id = workflow_id
        db_service = DatabaseService()
        created = await db_service.create_execution_log(current_user_id, log)
        return created
    except DatabaseError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Create log error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create log")


@router.get("/workflows/{workflow_id}/logs/stats")
async def get_log_stats(
    workflow_id: str,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Get execution statistics for a workflow.
    """
    try:
        db_service = DatabaseService()
        stats = await db_service.get_workflow_logs_stats(current_user_id, workflow_id)
        return stats
    except DatabaseError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Get stats error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get stats")


# ─────────────────────────────────────────────────────────────────────────────
# Health Check
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/health")
async def health_check():
    """
    Health check endpoint to verify Supabase connection.
    """
    try:
        from flozai.services.supabase_client import get_supabase_client
        client = get_supabase_client()
        # Try a simple query to verify connection
        client.table('users').select('count').limit(1).execute()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}
