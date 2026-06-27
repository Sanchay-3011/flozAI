"""Integration tests for DatabaseService using Supabase connection"""
import pytest
import uuid
from flozai.services.database_service import DatabaseService, Workflow
from flozai.schemas.workflow_schema import WorkflowTrigger, WorkflowAction

@pytest.mark.anyio
async def test_database_service_workflow_crud():
    # 1. Initialize DatabaseService
    db_service = DatabaseService()
    
    # 2. Use a unique test user ID and email
    test_user_id = "363c201c-5885-40a0-bf64-2477b269f316"  # Existing test user id from the database query
    test_email = "copilot.dbtest.19045d03@gmail.com"
    
    # Verify user exists or create them
    user = await db_service.get_or_create_user(test_user_id, test_email)
    assert user["id"] == test_user_id
    
    # 3. Create a test workflow
    test_wf = Workflow(
        user_id=test_user_id,
        name="Integration Test Workflow",
        description="Created during automated E2E tests",
        nodes=[{"id": "1", "type": "trigger", "data": {"label": "Trigger"}}],
        edges=[],
        steps=[{"id": "1", "type": "trigger"}]
    )
    
    created_wf = await db_service.create_workflow(test_user_id, test_wf)
    assert created_wf["name"] == "Integration Test Workflow"
    assert created_wf["id"] is not None
    
    wf_id = created_wf["id"]
    
    # 4. Fetch the created workflow
    fetched_wf = await db_service.get_workflow(test_user_id, wf_id)
    assert fetched_wf is not None
    assert fetched_wf["name"] == "Integration Test Workflow"
    
    # 5. List workflows
    all_wfs = await db_service.list_workflows(test_user_id)
    assert len(all_wfs) > 0
    assert any(wf["id"] == wf_id for wf in all_wfs)
    
    # 6. Update the workflow
    updated_wf = await db_service.update_workflow(
        test_user_id, 
        wf_id, 
        {"description": "Updated description in test"}
    )
    assert updated_wf["description"] == "Updated description in test"
    
    # 7. Delete the workflow
    delete_result = await db_service.delete_workflow(test_user_id, wf_id)
    assert delete_result is True
    
    # Verify it is deleted
    deleted_wf = await db_service.get_workflow(test_user_id, wf_id)
    assert deleted_wf is None
