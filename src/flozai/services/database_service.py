"""
Database Service
CRUD operations for users, workflows, tasks, and execution logs
Implements Row-Level Security (RLS) patterns
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field
import logging

from flozai.services.supabase_client import get_supabase_client

logger = logging.getLogger(__name__)


# ─── Data Models ───

class UserProfile(BaseModel):
    """User profile model"""
    id: str
    email: str
    created_at: datetime
    updated_at: Optional[datetime] = None


class Workflow(BaseModel):
    """Workflow model"""
    id: Optional[str] = None
    user_id: str
    name: str
    description: str
    nodes: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    edges: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    steps: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class WorkflowTask(BaseModel):
    """Task/step in a workflow"""
    id: Optional[str] = None
    workflow_id: str
    step_name: str
    status: str = Field(default="pending")  # pending, running, completed, failed
    order_index: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ExecutionLog(BaseModel):
    """Execution log entry"""
    id: Optional[str] = None
    workflow_id: str
    execution_time: datetime
    status: str  # success, failure, partial
    output: Dict[str, Any] = Field(default_factory=dict)
    error_message: Optional[str] = None
    created_at: Optional[datetime] = None


class DatabaseError(Exception):
    """Custom database error"""
    pass


class DatabaseService:
    """
    Service for database operations with RLS support.
    All operations use user_id for RLS filtering.
    """

    def __init__(self):
        self.client = get_supabase_client()

    # ─── User Operations ───

    async def get_or_create_user(self, user_id: str, email: str) -> Dict[str, Any]:
        """
        Get existing user or create new one.
        RLS Policy: User can only access their own data
        
        Args:
            user_id: UUID from auth system
            email: User email
            
        Returns:
            User data
            
        Raises:
            DatabaseError: If operation fails
        """
        try:
            # Try to fetch existing user
            response = self.client.table("users").select("*").eq("id", user_id).execute()
            
            if response.data:
                return response.data[0]
            
            # Create new user if doesn't exist
            user_data = {
                "id": user_id,
                "email": email,
                "created_at": datetime.utcnow().isoformat()
            }
            
            response = self.client.table("users").insert(user_data).execute()
            
            if not response.data:
                raise DatabaseError("Failed to create user")
            
            logger.info(f"User created or retrieved: {user_id}")
            return response.data[0]
        except Exception as e:
            logger.error(f"User operation error: {str(e)}")
            raise DatabaseError(f"User operation failed: {str(e)}")

    async def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user profile by ID.
        RLS Policy: User can only read their own profile
        
        Args:
            user_id: User UUID
            
        Returns:
            User profile or None if not found
        """
        try:
            response = self.client.table("users").select("*").eq("id", user_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Get user profile error: {str(e)}")
            raise DatabaseError(f"Failed to get user profile: {str(e)}")

    # ─── Workflow Operations ───

    async def create_workflow(self, user_id: str, workflow: Workflow) -> Dict[str, Any]:
        """
        Create a new workflow.
        RLS Policy: Only the user can create workflows for themselves
        
        Args:
            user_id: User UUID
            workflow: Workflow data
            
        Returns:
            Created workflow with ID
            
        Raises:
            DatabaseError: If creation fails
        """
        try:
            workflow_data = {
                "user_id": user_id,
                "name": workflow.name,
                "description": workflow.description,
                "nodes": workflow.nodes or [],
                "edges": workflow.edges or [],
                "steps": workflow.steps or [],
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            response = self.client.table("workflows").insert(workflow_data).execute()
            
            if not response.data:
                raise DatabaseError("Failed to create workflow")
            
            logger.info(f"Workflow created for user {user_id}: {response.data[0]['id']}")
            return response.data[0]
        except Exception as e:
            logger.error(f"Create workflow error: {str(e)}")
            raise DatabaseError(f"Failed to create workflow: {str(e)}")

    async def get_workflow(self, user_id: str, workflow_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific workflow by ID.
        RLS Policy: User can only read their own workflows
        
        Args:
            user_id: User UUID
            workflow_id: Workflow UUID
            
        Returns:
            Workflow data or None if not found
        """
        try:
            response = (self.client.table("workflows")
                       .select("*")
                       .eq("id", workflow_id)
                       .eq("user_id", user_id)
                       .execute())
            
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Get workflow error: {str(e)}")
            raise DatabaseError(f"Failed to get workflow: {str(e)}")

    async def list_workflows(self, user_id: str, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """
        List all workflows for a user with pagination.
        RLS Policy: User can only read their own workflows
        
        Args:
            user_id: User UUID
            limit: Number of results to return
            offset: Pagination offset
            
        Returns:
            List of workflows
        """
        try:
            response = (self.client.table("workflows")
                       .select("*")
                       .eq("user_id", user_id)
                       .order("created_at", desc=True)
                       .range(offset, offset + limit - 1)
                       .execute())
            
            return response.data or []
        except Exception as e:
            logger.error(f"List workflows error: {str(e)}")
            raise DatabaseError(f"Failed to list workflows: {str(e)}")

    async def update_workflow(self, user_id: str, workflow_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a workflow.
        RLS Policy: User can only update their own workflows
        
        Args:
            user_id: User UUID
            workflow_id: Workflow UUID
            update_data: Fields to update
            
        Returns:
            Updated workflow
            
        Raises:
            DatabaseError: If update fails
        """
        try:
            update_data["updated_at"] = datetime.utcnow().isoformat()
            
            response = (self.client.table("workflows")
                       .update(update_data)
                       .eq("id", workflow_id)
                       .eq("user_id", user_id)
                       .execute())
            
            if not response.data:
                raise DatabaseError("Workflow not found or update failed")
            
            logger.info(f"Workflow updated: {workflow_id}")
            return response.data[0]
        except Exception as e:
            logger.error(f"Update workflow error: {str(e)}")
            raise DatabaseError(f"Failed to update workflow: {str(e)}")

    async def delete_workflow(self, user_id: str, workflow_id: str) -> bool:
        """
        Delete a workflow and associated tasks/logs.
        RLS Policy: User can only delete their own workflows
        
        Args:
            user_id: User UUID
            workflow_id: Workflow UUID
            
        Returns:
            True if deleted
            
        Raises:
            DatabaseError: If deletion fails
        """
        try:
            # Delete associated tasks
            await self.delete_tasks_by_workflow(user_id, workflow_id)
            
            # Delete associated logs
            await self.delete_logs_by_workflow(user_id, workflow_id)
            
            # Delete workflow
            response = (self.client.table("workflows")
                       .delete()
                       .eq("id", workflow_id)
                       .eq("user_id", user_id)
                       .execute())
            
            logger.info(f"Workflow deleted: {workflow_id}")
            return True
        except Exception as e:
            logger.error(f"Delete workflow error: {str(e)}")
            raise DatabaseError(f"Failed to delete workflow: {str(e)}")

    # ─── Task Operations ───

    async def create_task(self, user_id: str, task: WorkflowTask) -> Dict[str, Any]:
        """
        Create a new task/step in a workflow.
        RLS Policy: Task must belong to user's workflow
        
        Args:
            user_id: User UUID
            task: Task data (without ID)
            
        Returns:
            Created task with ID
        """
        try:
            # Verify workflow ownership
            workflow = await self.get_workflow(user_id, task.workflow_id)
            if not workflow:
                raise DatabaseError("Workflow not found")
            
            task_data = {
                "workflow_id": task.workflow_id,
                "step_name": task.step_name,
                "status": task.status,
                "order_index": task.order_index,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            response = self.client.table("tasks").insert(task_data).execute()
            
            if not response.data:
                raise DatabaseError("Failed to create task")
            
            logger.info(f"Task created: {response.data[0]['id']}")
            return response.data[0]
        except DatabaseError:
            raise
        except Exception as e:
            logger.error(f"Create task error: {str(e)}")
            raise DatabaseError(f"Failed to create task: {str(e)}")

    async def list_workflow_tasks(self, user_id: str, workflow_id: str) -> List[Dict[str, Any]]:
        """
        List all tasks for a workflow.
        RLS Policy: User can only read tasks in their workflows
        
        Args:
            user_id: User UUID
            workflow_id: Workflow UUID
            
        Returns:
            List of tasks ordered by order_index
        """
        try:
            # Verify workflow ownership
            workflow = await self.get_workflow(user_id, workflow_id)
            if not workflow:
                raise DatabaseError("Workflow not found")
            
            response = (self.client.table("tasks")
                       .select("*")
                       .eq("workflow_id", workflow_id)
                       .order("order_index", desc=False)
                       .execute())
            
            return response.data or []
        except DatabaseError:
            raise
        except Exception as e:
            logger.error(f"List tasks error: {str(e)}")
            raise DatabaseError(f"Failed to list tasks: {str(e)}")

    async def update_task(self, user_id: str, workflow_id: str, task_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a task.
        RLS Policy: User can only update tasks in their workflows
        
        Args:
            user_id: User UUID
            workflow_id: Workflow UUID
            task_id: Task UUID
            update_data: Fields to update
            
        Returns:
            Updated task
        """
        try:
            # Verify workflow ownership
            workflow = await self.get_workflow(user_id, workflow_id)
            if not workflow:
                raise DatabaseError("Workflow not found")
            
            update_data["updated_at"] = datetime.utcnow().isoformat()
            
            response = (self.client.table("tasks")
                       .update(update_data)
                       .eq("id", task_id)
                       .eq("workflow_id", workflow_id)
                       .execute())
            
            if not response.data:
                raise DatabaseError("Task not found or update failed")
            
            return response.data[0]
        except DatabaseError:
            raise
        except Exception as e:
            logger.error(f"Update task error: {str(e)}")
            raise DatabaseError(f"Failed to update task: {str(e)}")

    async def delete_tasks_by_workflow(self, user_id: str, workflow_id: str) -> bool:
        """
        Delete all tasks for a workflow.
        
        Args:
            user_id: User UUID
            workflow_id: Workflow UUID
            
        Returns:
            True if deleted
        """
        try:
            # Verify workflow ownership first
            workflow = await self.get_workflow(user_id, workflow_id)
            if not workflow:
                raise DatabaseError("Workflow not found")
            
            self.client.table("tasks").delete().eq("workflow_id", workflow_id).execute()
            return True
        except Exception as e:
            logger.error(f"Delete tasks error: {str(e)}")
            raise DatabaseError(f"Failed to delete tasks: {str(e)}")

    # ─── Execution Log Operations ───

    async def create_execution_log(self, user_id: str, log: ExecutionLog) -> Dict[str, Any]:
        """
        Create an execution log entry.
        RLS Policy: Log must belong to user's workflow
        
        Args:
            user_id: User UUID
            log: Log data
            
        Returns:
            Created log entry
        """
        try:
            # Verify workflow ownership
            workflow = await self.get_workflow(user_id, log.workflow_id)
            if not workflow:
                raise DatabaseError("Workflow not found")
            
            log_data = {
                "workflow_id": log.workflow_id,
                "execution_time": log.execution_time.isoformat(),
                "status": log.status,
                "output": log.output,
                "error_message": log.error_message,
                "created_at": datetime.utcnow().isoformat()
            }
            
            response = self.client.table("logs").insert(log_data).execute()
            
            if not response.data:
                raise DatabaseError("Failed to create log")
            
            logger.info(f"Execution log created: {response.data[0]['id']}")
            return response.data[0]
        except DatabaseError:
            raise
        except Exception as e:
            logger.error(f"Create log error: {str(e)}")
            raise DatabaseError(f"Failed to create log: {str(e)}")

    async def list_workflow_logs(self, user_id: str, workflow_id: str, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        List execution logs for a workflow.
        RLS Policy: User can only read logs for their workflows
        
        Args:
            user_id: User UUID
            workflow_id: Workflow UUID
            limit: Number of results
            offset: Pagination offset
            
        Returns:
            List of logs sorted by execution_time descending
        """
        try:
            # Verify workflow ownership
            workflow = await self.get_workflow(user_id, workflow_id)
            if not workflow:
                raise DatabaseError("Workflow not found")
            
            response = (self.client.table("logs")
                       .select("*")
                       .eq("workflow_id", workflow_id)
                       .order("execution_time", desc=True)
                       .range(offset, offset + limit - 1)
                       .execute())
            
            return response.data or []
        except DatabaseError:
            raise
        except Exception as e:
            logger.error(f"List logs error: {str(e)}")
            raise DatabaseError(f"Failed to list logs: {str(e)}")

    async def get_workflow_logs_stats(self, user_id: str, workflow_id: str) -> Dict[str, Any]:
        """
        Get execution statistics for a workflow.
        
        Args:
            user_id: User UUID
            workflow_id: Workflow UUID
            
        Returns:
            Statistics including success count, failure count, average execution time
        """
        try:
            logs = await self.list_workflow_logs(user_id, workflow_id, limit=1000)
            
            if not logs:
                return {
                    "total": 0,
                    "success": 0,
                    "failed": 0,
                    "partial": 0,
                    "success_rate": 0.0
                }
            
            success_count = sum(1 for log in logs if log["status"] == "success")
            failed_count = sum(1 for log in logs if log["status"] == "failure")
            partial_count = sum(1 for log in logs if log["status"] == "partial")
            
            return {
                "total": len(logs),
                "success": success_count,
                "failed": failed_count,
                "partial": partial_count,
                "success_rate": success_count / len(logs) if logs else 0.0
            }
        except Exception as e:
            logger.error(f"Get logs stats error: {str(e)}")
            raise DatabaseError(f"Failed to get logs stats: {str(e)}")

    async def delete_logs_by_workflow(self, user_id: str, workflow_id: str) -> bool:
        """
        Delete all logs for a workflow.
        
        Args:
            user_id: User UUID
            workflow_id: Workflow UUID
            
        Returns:
            True if deleted
        """
        try:
            # Verify workflow ownership first
            workflow = await self.get_workflow(user_id, workflow_id)
            if not workflow:
                raise DatabaseError("Workflow not found")
            
            self.client.table("logs").delete().eq("workflow_id", workflow_id).execute()
            return True
        except Exception as e:
            logger.error(f"Delete logs error: {str(e)}")
            raise DatabaseError(f"Failed to delete logs: {str(e)}")
