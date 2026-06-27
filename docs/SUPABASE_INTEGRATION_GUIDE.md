# Supabase Integration Guide for FlozAI

Complete guide to integrate and use Supabase in your FlozAI project.

## Table of Contents

1. [Setup](#setup)
2. [Backend Integration](#backend-integration)
3. [Frontend Integration](#frontend-integration)
4. [Database Schema](#database-schema)
5. [API Routes](#api-routes)
6. [Authentication](#authentication)
7. [Row-Level Security (RLS)](#row-level-security)
8. [Error Handling](#error-handling)
9. [Best Practices](#best-practices)

---

## Setup

### Step 1: Create a Supabase Project

1. Go to [supabase.com](https://supabase.com)
2. Click "New Project"
3. Enter project name, password, and region
4. Wait for project initialization
5. Go to Settings → API to find your:
   - `SUPABASE_URL` (Project URL)
   - `SUPABASE_KEY` (Anon key)

### Step 2: Install Dependencies

**Backend:**
```bash
pip install supabase>=2.0.0 python-dotenv>=1.0.0 email-validator>=2.0.0
```

**Frontend:**
```bash
npm install @supabase/supabase-js
```

### Step 3: Configure Environment Variables

**Backend (.env):**
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key-here
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here
```

**Frontend (.env.local):**
```env
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key-here
```

### Step 4: Create Database Schema

1. Go to your Supabase project dashboard
2. Click "SQL Editor" → "New Query"
3. Copy the entire content from `docs/database_schema.sql`
4. Paste and execute

This creates:
- `users` table
- `workflows` table
- `tasks` table
- `logs` table
- RLS policies for all tables

---

## Backend Integration

### 1. Supabase Client

The `supabase_client.py` provides a singleton client manager:

```python
from flozai.services.supabase_client import get_supabase_client

# Get the client anywhere in your app
client = get_supabase_client()

# Use it for direct queries
users = client.table('users').select('*').execute()
```

**Features:**
- Singleton pattern for efficient resource usage
- Automatic token refresh
- Error handling and validation
- Environment variable configuration

### 2. Authentication Service

`auth_service.py` handles user authentication:

```python
from flozai.services.auth_service import AuthService

auth_service = AuthService()

# Sign up
user_data = await auth_service.sign_up("user@example.com", "password123")

# Login
session = await auth_service.login("user@example.com", "password123")

# Get current user
user = await auth_service.get_current_user(access_token)

# Logout
await auth_service.logout()

# Refresh token
new_session = await auth_service.refresh_token(refresh_token)

# Reset password
await auth_service.reset_password("user@example.com")
```

**Key Methods:**
- `sign_up(email, password)` - Register new user
- `login(email, password)` - Authenticate user
- `logout()` - Sign out
- `get_current_user(token)` - Get authenticated user
- `refresh_token(refresh_token)` - Get new access token
- `reset_password(email)` - Send reset email
- `update_user_email(token, new_email)` - Change email
- `update_user_password(token, new_password)` - Change password

### 3. Database Service

`database_service.py` provides CRUD operations with RLS:

```python
from flozai.services.database_service import DatabaseService, Workflow, WorkflowTask, ExecutionLog

db_service = DatabaseService()

# Workflows
workflow = await db_service.create_workflow(
    user_id="uuid",
    workflow=Workflow(
        user_id="uuid",
        name="My Workflow",
        description="Description"
    )
)

workflows = await db_service.list_workflows(user_id="uuid")
workflow = await db_service.get_workflow(user_id="uuid", workflow_id="wf-id")
await db_service.update_workflow(user_id="uuid", workflow_id="wf-id", {"name": "New Name"})
await db_service.delete_workflow(user_id="uuid", workflow_id="wf-id")

# Tasks
task = await db_service.create_task(
    user_id="uuid",
    task=WorkflowTask(
        workflow_id="wf-id",
        step_name="Step 1",
        status="pending",
        order_index=0
    )
)

tasks = await db_service.list_workflow_tasks(user_id="uuid", workflow_id="wf-id")
await db_service.update_task(user_id="uuid", workflow_id="wf-id", task_id="task-id", {"status": "completed"})

# Logs
log = await db_service.create_execution_log(
    user_id="uuid",
    log=ExecutionLog(
        workflow_id="wf-id",
        execution_time=datetime.now(),
        status="success",
        output={"result": "data"},
        error_message=None
    )
)

logs = await db_service.list_workflow_logs(user_id="uuid", workflow_id="wf-id")
stats = await db_service.get_workflow_logs_stats(user_id="uuid", workflow_id="wf-id")
```

**Key Features:**
- RLS-aware (automatically filters by user)
- Comprehensive error handling
- Pagination support
- Async/await throughout
- Transaction support for cascading deletes

---

## Frontend Integration

### 1. Supabase Client

`frontend/src/services/supabaseClient.js` provides the Supabase instance:

```javascript
import { supabase } from '@/services/supabaseClient'

// Direct access to Supabase client
const { data, error } = await supabase.auth.getUser()
```

### 2. Auth Service

`frontend/src/services/authService.js` handles authentication:

```javascript
import {
  signUp,
  login,
  logout,
  getCurrentUser,
  getSession,
  onAuthStateChange,
  refreshToken,
  sendPasswordResetEmail,
  updatePassword,
  updateEmail
} from '@/services/authService'

// Sign up
const { user, session, error } = await signUp("user@example.com", "password123")

// Login
const { user, session, error } = await login("user@example.com", "password123")

// Get current user
const { user, error } = await getCurrentUser()

// Logout
const { error } = await logout()

// Subscribe to auth changes
const unsubscribe = onAuthStateChange(({ event, session }) => {
  console.log('Auth event:', event)
  console.log('Session:', session)
})

// Password reset
const { error } = await sendPasswordResetEmail("user@example.com")

// Update password
const { user, error } = await updatePassword("newpassword123")
```

### 3. Database Service

`frontend/src/services/databaseService.js` provides CRUD operations:

```javascript
import { workflowService, taskService, logService } from '@/services/databaseService'

// Workflows
const { data: workflows, error } = await workflowService.getAll(50, 0)
const { data: workflow } = await workflowService.get(workflowId)
const { data: created } = await workflowService.create({ name: "My Workflow", description: "..." })
const { data: updated } = await workflowService.update(workflowId, { name: "Updated" })
const { error } = await workflowService.delete(workflowId)

// Tasks
const { data: tasks } = await taskService.getByWorkflow(workflowId)
const { data: task } = await taskService.create({ workflow_id, step_name, status, order_index })
const { data: updated } = await taskService.update(taskId, { status: "completed" })
const { error } = await taskService.delete(taskId)

// Logs
const { data: logs, count } = await logService.getByWorkflow(workflowId, 100, 0)
const { data: stats } = await logService.getStats(workflowId)
const { data: log } = await logService.create({
  workflow_id: workflowId,
  execution_time: new Date(),
  status: "success",
  output: { result: "data" },
  error_message: null
})

// Real-time subscriptions
const unsubscribe = subscribeToWorkflows(null, (payload) => {
  console.log('Workflow updated:', payload)
})

const unsubscribeLogs = subscribeToLogs(workflowId, (payload) => {
  console.log('Log created:', payload)
})
```

### 4. Custom React Hooks

Use the provided hooks for simplicity:

```javascript
import { useWorkflows, useWorkflowTasks, useExecutionLogs } from '@/hooks/useWorkflows'

function MyComponent() {
  const { workflows, loading, createWorkflow } = useWorkflows()
  const { tasks, createTask } = useWorkflowTasks(workflowId)
  const { logs, stats, createLog } = useExecutionLogs(workflowId)

  return (
    <div>
      {/* Your component code */}
    </div>
  )
}
```

---

## Database Schema

### Users Table
```
id (UUID)          - Primary key, references auth.users
email (TEXT)       - User email, unique
created_at (TIMESTAMP) - Account creation time
updated_at (TIMESTAMP) - Last update time
```

### Workflows Table
```
id (UUID)          - Primary key
user_id (UUID)     - Foreign key to users, required
name (TEXT)        - Workflow name
description (TEXT) - Workflow description
created_at (TIMESTAMP) - Creation time
updated_at (TIMESTAMP) - Last update time
```

### Tasks Table
```
id (UUID)          - Primary key
workflow_id (UUID) - Foreign key to workflows, required
step_name (TEXT)   - Name of the step
status (TEXT)      - One of: pending, running, completed, failed
order_index (INT)  - Position in workflow sequence
created_at (TIMESTAMP)
updated_at (TIMESTAMP)
```

### Logs Table
```
id (UUID)          - Primary key
workflow_id (UUID) - Foreign key to workflows, required
execution_time (TIMESTAMP) - When execution occurred
status (TEXT)      - One of: success, failure, partial
output (JSONB)     - Execution results
error_message (TEXT) - Error details if applicable
created_at (TIMESTAMP)
```

---

## API Routes

Example API routes are in `docs/example_api_routes.py`:

### Authentication Endpoints
```
POST /api/auth/signup       - Register new user
POST /api/auth/login        - Login user
POST /api/auth/logout       - Logout user
GET  /api/auth/me           - Get current user
```

### Workflow Endpoints
```
GET    /api/workflows           - List all workflows
GET    /api/workflows/{id}      - Get specific workflow
POST   /api/workflows           - Create workflow
PATCH  /api/workflows/{id}      - Update workflow
DELETE /api/workflows/{id}      - Delete workflow
```

### Task Endpoints
```
GET    /api/workflows/{wf_id}/tasks        - List tasks
POST   /api/workflows/{wf_id}/tasks        - Create task
PATCH  /api/workflows/{wf_id}/tasks/{id}   - Update task
DELETE /api/workflows/{wf_id}/tasks/{id}   - Delete task
```

### Log Endpoints
```
GET    /api/workflows/{wf_id}/logs        - List logs
POST   /api/workflows/{wf_id}/logs        - Create log
GET    /api/workflows/{wf_id}/logs/stats  - Get statistics
```

### Health Check
```
GET /api/health - Verify Supabase connection
```

---

## Authentication

### Supabase Auth Features

Supabase Auth handles:
- Email/password authentication
- Session management
- JWT tokens
- Refresh tokens
- Password reset emails
- Email verification (optional)
- Multi-factor authentication (optional)

### Flow:

1. **Sign Up**: User provides email + password → Auth creates user → Trigger creates user profile
2. **Login**: Email + password → JWT token in session
3. **API Access**: Include token in `Authorization: Bearer <token>` header
4. **Token Refresh**: Refresh token → New access token
5. **Logout**: Clear session

### Backend Protection:

```python
from fastapi import Depends, Header

async def get_current_user_id(authorization: str = Header(...)):
    # Extract and verify JWT token
    scheme, token = authorization.split()
    auth_service = AuthService()
    user = await auth_service.get_current_user(token)
    return user['id']

@app.get("/api/protected")
async def protected_route(current_user_id: str = Depends(get_current_user_id)):
    # This endpoint requires authentication
    return {"user_id": current_user_id}
```

---

## Row-Level Security (RLS)

RLS policies ensure users can only access their own data:

### Users Table
- Users can view/update their own profile

### Workflows Table
- Users can only view/modify workflows they created
- Policy: `auth.uid() = user_id`

### Tasks Table
- Users can only access tasks in their workflows
- Policy: `workflow_id IN (SELECT id FROM workflows WHERE user_id = auth.uid())`

### Logs Table
- Users can only access logs for their workflows
- Policy: `workflow_id IN (SELECT id FROM workflows WHERE user_id = auth.uid())`

### Testing RLS:

```sql
-- Enable RLS mode in Supabase SQL editor
-- Run as authenticated user

-- This should work (his own workflow)
SELECT * FROM workflows WHERE user_id = auth.uid();

-- This should be blocked by RLS (another user's workflow)
-- (Attempted if you bypass authentication somehow)
```

---

## Error Handling

### Backend Error Handling:

```python
from flozai.services.auth_service import AuthError
from flozai.services.database_service import DatabaseError

try:
    await auth_service.login(email, password)
except AuthError as e:
    # Handle authentication errors
    return {"error": str(e)}, 400

try:
    await db_service.create_workflow(user_id, workflow)
except DatabaseError as e:
    # Handle database errors
    return {"error": str(e)}, 500
```

### Frontend Error Handling:

```javascript
try {
  const { data, error } = await workflowService.getAll()

  if (error) {
    console.error('Error fetching workflows:', error)
    // Show user-friendly error message
    return
  }

  // Process data
} catch (err) {
  console.error('Unexpected error:', err)
}

// Or using React hooks:
const { workflows, error } = useWorkflows()

if (error) {
  return <div>Error: {error}</div>
}
```

---

## Best Practices

### 1. Environment Variables
- ✅ Store in `.env` file (gitignored)
- ✅ Provide `.env.example` with placeholders
- ❌ Never commit real keys
- ✅ Use different keys for dev/prod

### 2. Token Security
- ✅ Store JWT in httpOnly cookie (harder to steal)
- ✅ Include token in `Authorization` header
- ✅ Refresh tokens before expiration
- ❌ Don't store tokens in localStorage if sensitive
- ✅ Use HTTPS in production

### 3. Database Security
- ✅ Always use RLS policies
- ✅ Use service role key only in backend
- ✅ Validate all user inputs
- ✅ Use parameterized queries (built-in with Supabase)
- ❌ Never expose service role key to frontend

### 4. API Design
- ✅ Validate request data with Pydantic
- ✅ Return appropriate HTTP status codes
- ✅ Include error details in responses
- ✅ Use consistent response format
- ✅ Paginate large result sets

### 5. Real-time Features
- ✅ Use subscriptions for live updates
- ✅ Clean up subscriptions when component unmounts
- ✅ Handle connection drops gracefully
- ✅ Test with slow/unstable connections

### 6. Performance
- ✅ Use pagination for large datasets
- ✅ Create indexes on frequently queried columns
- ✅ Use real-time sparingly (can impact performance)
- ✅ Cache frequently accessed data
- ✅ Monitor slow queries using Supabase dashboard

### 7. Error Handling
- ✅ Use custom error classes
- ✅ Log errors with context
- ✅ Show user-friendly error messages
- ✅ Handle network errors gracefully
- ✅ Implement retry logic for transient errors

### 8. Testing
- ✅ Use test user accounts
- ✅ Test RLS policies
- ✅ Test error scenarios
- ✅ Mock Supabase in unit tests
- ✅ Test with different user roles

---

## Example: Complete Workflow

### Backend Initialization

```python
# main.py
from flozai.api.routes import app
from flozai.services.auth_service import AuthService
from flozai.services.database_service import DatabaseService

# These are initialized on first use (lazy loading)
# Environment variables must be set before first request

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Frontend Setup

```javascript
// App.jsx
import { useEffect, useState } from 'react'
import { onAuthStateChange } from '@/services/authService'
import { useWorkflows } from '@/hooks/useWorkflows'

export default function App() {
  const [user, setUser] = useState(null)
  const { workflows, loading } = useWorkflows()

  useEffect(() => {
    const unsubscribe = onAuthStateChange(({ session }) => {
      setUser(session?.user || null)
    })

    return unsubscribe
  }, [])

  if (!user) {
    return <LoginPage />
  }

  return (
    <div>
      <h1>Welcome, {user.email}!</h1>
      {loading ? <p>Loading workflows...</p> : <WorkflowList workflows={workflows} />}
    </div>
  )
}
```

---

## Troubleshooting

### Issue: "Missing SUPABASE_URL" Error
**Solution**: Check `.env` file has `SUPABASE_URL` and `SUPABASE_KEY` set correctly

### Issue: "Invalid authorization format" (401)
**Solution**: Send token as `Authorization: Bearer <token>` (exact format)

### Issue: RLS policies blocking queries
**Solution**: Verify `auth.uid()` matches user ID in table. Check policy SQL.

### Issue: CORS errors
**Solution**: Configure CORS in Supabase project settings, or use proxy in development

### Issue: Real-time subscriptions not working
**Solution**: Ensure RLS policies allow read access, check WebSocket connection

---

## Next Steps

1. ✅ Set up Supabase project
2. ✅ Configure environment variables
3. ✅ Create database schema
4. ✅ Install dependencies
5. ✅ Add routes from `example_api_routes.py`
6. ✅ Create frontend components using hooks
7. ✅ Test authentication flow
8. ✅ Monitor logs in Supabase dashboard
9. ✅ Set up monitoring/alerting
10. ✅ Deploy to production

---

## Resources

- [Supabase Documentation](https://supabase.com/docs)
- [Supabase Python Client](https://github.com/supabase-community/supabase-py)
- [Supabase JavaScript Client](https://supabase.com/docs/reference/javascript/introduction)
- [Row-Level Security Guide](https://supabase.com/docs/guides/auth/row-level-security)
- [Authentication Best Practices](https://supabase.com/docs/guides/auth/concepts)

---

## Support

For issues:
1. Check Supabase documentation
2. Review error messages carefully
3. Check `.env` file configuration
4. Test with Supabase SQL Editor
5. Look at logs in Supabase dashboard

