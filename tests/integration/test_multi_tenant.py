"""
Integration tests for multi-tenant isolation in DatabaseService.
Verifies that users cannot access or modify other users' workflows, tasks, or logs.
"""
import pytest
import uuid
from flozai.services.database_service import DatabaseService, Workflow, WorkflowTask, ExecutionLog, DatabaseError
from datetime import datetime

@pytest.mark.anyio
async def test_multi_tenant_isolation():
    db_service = DatabaseService()
    auth_admin = db_service.client.auth.admin

    # Generate unique emails
    u1_email = f"test_tenant1_{uuid.uuid4().hex[:8]}@example.com"
    u2_email = f"test_tenant2_{uuid.uuid4().hex[:8]}@example.com"

    user1_id = None
    user2_id = None

    try:
        # 1. Create two actual users in Supabase Auth to satisfy FK constraints
        u1_auth = auth_admin.create_user({
            "email": u1_email,
            "password": "password123",
            "email_confirm": True
        })
        user1_id = u1_auth.user.id

        u2_auth = auth_admin.create_user({
            "email": u2_email,
            "password": "password123",
            "email_confirm": True
        })
        user2_id = u2_auth.user.id

        # Verify profiles exist or retrieve them
        u1 = await db_service.get_or_create_user(user1_id, u1_email)
        u2 = await db_service.get_or_create_user(user2_id, u2_email)
        
        assert u1["id"] == user1_id
        assert u2["id"] == user2_id

        # 2. User 1 creates a workflow
        wf1_data = Workflow(
            user_id=user1_id,
            name="User 1 Private Workflow",
            description="Should not be visible or modifiable by User 2",
            nodes=[{"id": "node1", "type": "trigger", "data": {"label": "U1 Trigger"}}],
            edges=[],
            steps=[]
        )
        wf1 = await db_service.create_workflow(user1_id, wf1_data)
        wf1_id = wf1["id"]
        assert wf1_id is not None

        # 3. User 2 attempts to retrieve User 1's workflow
        wf_fetched_by_u2 = await db_service.get_workflow(user2_id, wf1_id)
        assert wf_fetched_by_u2 is None

        # User 1 should be able to retrieve it
        wf_fetched_by_u1 = await db_service.get_workflow(user1_id, wf1_id)
        assert wf_fetched_by_u1 is not None
        assert wf_fetched_by_u1["name"] == "User 1 Private Workflow"

        # 4. User 2 attempts to update User 1's workflow
        with pytest.raises(DatabaseError) as exc_info:
            await db_service.update_workflow(
                user2_id,
                wf1_id,
                {"name": "Hacked Name"}
            )
        assert "not found or update failed" in str(exc_info.value)

        # 5. User 2 attempts to list User 1's workflow (should not be in User 2's list)
        u2_workflows = await db_service.list_workflows(user2_id)
        assert not any(w["id"] == wf1_id for w in u2_workflows)

        # User 1's list should contain it
        u1_workflows = await db_service.list_workflows(user1_id)
        assert any(w["id"] == wf1_id for w in u1_workflows)

        # 6. User 2 attempts to create a task under User 1's workflow
        task_data = WorkflowTask(
            workflow_id=wf1_id,
            step_name="Illegal Task",
            order_index=1
        )
        with pytest.raises(DatabaseError) as exc_info:
            await db_service.create_task(user2_id, task_data)
        assert "Workflow not found" in str(exc_info.value)

        # User 1 should be able to create a task
        u1_task_data = WorkflowTask(
            workflow_id=wf1_id,
            step_name="Legal U1 Task",
            order_index=1
        )
        task1 = await db_service.create_task(user1_id, u1_task_data)
        task1_id = task1["id"]
        assert task1_id is not None

        # 7. User 2 attempts to list tasks for User 1's workflow
        with pytest.raises(DatabaseError) as exc_info:
            await db_service.list_workflow_tasks(user2_id, wf1_id)
        assert "Workflow not found" in str(exc_info.value)

        # User 1 should be able to list tasks
        u1_tasks = await db_service.list_workflow_tasks(user1_id, wf1_id)
        assert len(u1_tasks) == 1
        assert u1_tasks[0]["id"] == task1_id

        # 8. User 2 attempts to update a task in User 1's workflow
        with pytest.raises(DatabaseError) as exc_info:
            await db_service.update_task(user2_id, wf1_id, task1_id, {"status": "completed"})
        assert "Workflow not found" in str(exc_info.value)

        # 9. User 2 attempts to create an execution log for User 1's workflow
        log_data = ExecutionLog(
            workflow_id=wf1_id,
            execution_time=datetime.utcnow(),
            status="success",
            output={"result": "U2 output"}
        )
        with pytest.raises(DatabaseError) as exc_info:
            await db_service.create_execution_log(user2_id, log_data)
        assert "Workflow not found" in str(exc_info.value)

        # User 1 should be able to create a log
        u1_log_data = ExecutionLog(
            workflow_id=wf1_id,
            execution_time=datetime.utcnow(),
            status="success",
            output={"result": "U1 output"}
        )
        log1 = await db_service.create_execution_log(user1_id, u1_log_data)
        log1_id = log1["id"]
        assert log1_id is not None

        # 10. User 2 attempts to list logs or get stats for User 1's workflow
        with pytest.raises(DatabaseError) as exc_info:
            await db_service.list_workflow_logs(user2_id, wf1_id)
        assert "Workflow not found" in str(exc_info.value)

        with pytest.raises(DatabaseError) as exc_info:
            await db_service.get_workflow_logs_stats(user2_id, wf1_id)
        assert "Workflow not found" in str(exc_info.value)

        # User 1 should be able to list logs and get stats
        u1_logs = await db_service.list_workflow_logs(user1_id, wf1_id)
        assert len(u1_logs) == 1
        assert u1_logs[0]["id"] == log1_id

        stats = await db_service.get_workflow_logs_stats(user1_id, wf1_id)
        assert stats["total"] == 1
        assert stats["success"] == 1

        # 11. User 2 attempts to delete User 1's workflow
        with pytest.raises(DatabaseError) as exc_info:
            await db_service.delete_workflow(user2_id, wf1_id)
        assert "Workflow not found" in str(exc_info.value)

        # User 1 should be able to delete their own workflow
        delete_result = await db_service.delete_workflow(user1_id, wf1_id)
        assert delete_result is True

        # Verify it is deleted
        assert await db_service.get_workflow(user1_id, wf1_id) is None

    finally:
        # Clean up created auth users, which cascades to delete all DB data
        if user1_id:
            try:
                auth_admin.delete_user(user1_id)
            except Exception:
                pass
        if user2_id:
            try:
                auth_admin.delete_user(user2_id)
            except Exception:
                pass
