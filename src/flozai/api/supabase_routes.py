"""Supabase API routes for auth and CRUD operations."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional, List

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from pydantic import BaseModel, EmailStr, Field

from flozai.services.auth_service import AuthError, AuthService
from flozai.services.database_service import DatabaseError, DatabaseService

router = APIRouter(prefix="/api", tags=["supabase"])


class SignUpBody(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


class LoginBody(BaseModel):
    email: EmailStr
    password: str


class WorkflowCreateBody(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=2000)
    nodes: Optional[List[dict]] = None
    edges: Optional[List[dict]] = None
    steps: Optional[List[dict]] = None


class WorkflowUpdateBody(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    nodes: Optional[List[dict]] = None
    edges: Optional[List[dict]] = None
    steps: Optional[List[dict]] = None


class TaskCreateBody(BaseModel):
    step_name: str = Field(min_length=1, max_length=200)
    status: str = Field(default="pending")
    order_index: int = Field(ge=0)


class TaskUpdateBody(BaseModel):
    step_name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    status: Optional[str] = None
    order_index: Optional[int] = Field(default=None, ge=0)


class LogCreateBody(BaseModel):
    execution_time: datetime
    status: str = Field(min_length=1)
    output: dict[str, Any] = Field(default_factory=dict)
    error_message: Optional[str] = None


def _extract_bearer_token(authorization: Optional[str]) -> str:
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    parts = authorization.split(" ", 1)
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid authorization format")
    return parts[1]


async def get_current_user_id(authorization: Optional[str] = Header(default=None)) -> str:
    token = _extract_bearer_token(authorization)
    auth_service = AuthService()
    user = await auth_service.get_current_user(token)
    if not user or "user" not in user or not user["user"] or "id" not in user["user"]:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return str(user["user"]["id"])


@router.post("/auth/signup")
async def sign_up(body: SignUpBody):
    try:
        auth_service = AuthService()
        db_service = DatabaseService()
        result = await auth_service.sign_up(body.email, body.password)

        user_payload = result.get("user") or {}
        user_id = user_payload.get("id")
        email = user_payload.get("email", body.email)
        if user_id:
            await db_service.get_or_create_user(str(user_id), str(email))

        return result
    except AuthError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except DatabaseError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/auth/login")
async def login(body: LoginBody):
    try:
        auth_service = AuthService()
        return await auth_service.login(body.email, body.password)
    except AuthError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/auth/logout")
async def logout(_: str = Depends(get_current_user_id)):
    try:
        auth_service = AuthService()
        await auth_service.logout()
        return {"ok": True}
    except AuthError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/auth/me")
async def get_current_user(authorization: Optional[str] = Header(default=None)):
    token = _extract_bearer_token(authorization)
    auth_service = AuthService()
    user = await auth_service.get_current_user(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return user


@router.get("/workflows")
async def list_workflows(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    user_id: str = Depends(get_current_user_id),
):
    try:
        db_service = DatabaseService()
        data = await db_service.list_workflows(user_id=user_id, limit=limit, offset=offset)
        return {"items": data, "count": len(data)}
    except DatabaseError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/workflows")
async def create_workflow(body: WorkflowCreateBody, user_id: str = Depends(get_current_user_id)):
    try:
        db_service = DatabaseService()
        response = (
            db_service.client.table("workflows")
            .insert(
                {
                    "user_id": user_id,
                    "name": body.name,
                    "description": body.description,
                    "nodes": body.nodes or [],
                    "edges": body.edges or [],
                    "steps": body.steps or [],
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat(),
                }
            )
            .execute()
        )
        if not response.data:
            raise DatabaseError("Failed to create workflow")
        return response.data[0]
    except DatabaseError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.patch("/workflows/{workflow_id}")
async def update_workflow(workflow_id: str, body: WorkflowUpdateBody, user_id: str = Depends(get_current_user_id)):
    update_map = body.model_dump(exclude_none=True)
    if not update_map:
        raise HTTPException(status_code=400, detail="No fields provided")
    try:
        db_service = DatabaseService()
        updated = await db_service.update_workflow(user_id=user_id, workflow_id=workflow_id, update_data=update_map)
        return updated
    except DatabaseError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.delete("/workflows/{workflow_id}")
async def delete_workflow(workflow_id: str, user_id: str = Depends(get_current_user_id)):
    try:
        db_service = DatabaseService()
        await db_service.delete_workflow(user_id=user_id, workflow_id=workflow_id)
        return {"ok": True}
    except DatabaseError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/workflows/{workflow_id}/tasks")
async def list_tasks(workflow_id: str, user_id: str = Depends(get_current_user_id)):
    try:
        db_service = DatabaseService()
        data = await db_service.list_workflow_tasks(user_id=user_id, workflow_id=workflow_id)
        return {"items": data, "count": len(data)}
    except DatabaseError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/workflows/{workflow_id}/tasks")
async def create_task(workflow_id: str, body: TaskCreateBody, user_id: str = Depends(get_current_user_id)):
    try:
        db_service = DatabaseService()
        workflow = await db_service.get_workflow(user_id=user_id, workflow_id=workflow_id)
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")

        response = (
            db_service.client.table("tasks")
            .insert(
                {
                    "workflow_id": workflow_id,
                    "step_name": body.step_name,
                    "status": body.status,
                    "order_index": body.order_index,
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat(),
                }
            )
            .execute()
        )
        if not response.data:
            raise DatabaseError("Failed to create task")
        return response.data[0]
    except DatabaseError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.patch("/workflows/{workflow_id}/tasks/{task_id}")
async def update_task(
    workflow_id: str,
    task_id: str,
    body: TaskUpdateBody,
    user_id: str = Depends(get_current_user_id),
):
    try:
        update_map = body.model_dump(exclude_none=True)
        if not update_map:
            raise HTTPException(status_code=400, detail="No fields provided")
        db_service = DatabaseService()
        updated = await db_service.update_task(
            user_id=user_id,
            workflow_id=workflow_id,
            task_id=task_id,
            update_data=update_map,
        )
        return updated
    except DatabaseError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/workflows/{workflow_id}/logs")
async def list_logs(
    workflow_id: str,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    user_id: str = Depends(get_current_user_id),
):
    try:
        db_service = DatabaseService()
        data = await db_service.list_workflow_logs(user_id=user_id, workflow_id=workflow_id, limit=limit, offset=offset)
        return {"items": data, "count": len(data)}
    except DatabaseError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/workflows/{workflow_id}/logs")
async def create_log(workflow_id: str, body: LogCreateBody, user_id: str = Depends(get_current_user_id)):
    try:
        db_service = DatabaseService()
        workflow = await db_service.get_workflow(user_id=user_id, workflow_id=workflow_id)
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")

        response = (
            db_service.client.table("logs")
            .insert(
                {
                    "workflow_id": workflow_id,
                    "execution_time": body.execution_time.isoformat(),
                    "status": body.status,
                    "output": body.output,
                    "error_message": body.error_message,
                    "created_at": datetime.utcnow().isoformat(),
                }
            )
            .execute()
        )
        if not response.data:
            raise DatabaseError("Failed to create log")
        return response.data[0]
    except DatabaseError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/workflows/{workflow_id}/logs/stats")
async def get_log_stats(workflow_id: str, user_id: str = Depends(get_current_user_id)):
    try:
        db_service = DatabaseService()
        return await db_service.get_workflow_logs_stats(user_id=user_id, workflow_id=workflow_id)
    except DatabaseError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/health/supabase")
async def supabase_health():
    try:
        db_service = DatabaseService()
        _ = db_service.client.table("users").select("id").limit(1).execute()
        return {"ok": True}
    except Exception as exc:  # pragma: no cover - health endpoint fallback
        raise HTTPException(status_code=500, detail=f"Supabase connection failed: {exc}") from exc
