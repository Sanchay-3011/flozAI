# Supabase Integration - Getting Started Checklist

Complete this checklist to get Supabase running in your FlozAI project.

## Phase 1: Supabase Account & Project (5 minutes)

- [ ] Go to https://supabase.com/dashboard
- [ ] Sign up or log in
- [ ] Click "New Project"
- [ ] Fill in:
  - Project name: `flozai` (or your choice)
  - Password: Strong password (you'll need this)
  - Region: Choose closest to you
- [ ] Wait for project initialization (~2 minutes)
- [ ] Copy your Project URL and API keys

## Phase 2: Configuration (5 minutes)

### Backend Configuration
- [ ] Open `.env` in project root
- [ ] Find/create these lines:
  ```env
  SUPABASE_URL=https://your-project.supabase.co
  SUPABASE_KEY=your-anon-key-here
  ```
- [ ] Replace with YOUR actual values from Supabase dashboard
  - Go to Settings → API
  - Copy "Project URL"
  - Copy "Anon" key (NOT service role key)

### Frontend Configuration
- [ ] Check if `.env.local` exists in `frontend/` folder
- [ ] If not, create it
- [ ] Add:
  ```env
  VITE_SUPABASE_URL=https://your-project.supabase.co
  VITE_SUPABASE_ANON_KEY=your-anon-key-here
  ```

## Phase 3: Database Schema (5 minutes)

- [ ] Open Supabase dashboard
- [ ] Go to "SQL Editor"
- [ ] Click "New Query"
- [ ] Open file: `docs/database_schema.sql`
- [ ] Copy ALL content
- [ ] Paste into Supabase SQL editor
- [ ] Click "Run"
- [ ] Wait for success message ✅

### Verify Schema Created
- [ ] In Supabase, go to "Table Editor"
- [ ] You should see:
  - [ ] users table
  - [ ] workflows table
  - [ ] tasks table
  - [ ] logs table

## Phase 4: Install Dependencies (2 minutes)

### Backend
```bash
pip install supabase>=2.0.0 python-dotenv email-validator
```
- [ ] Command completed successfully

### Frontend
```bash
npm install @supabase/supabase-js
```
- [ ] Command completed successfully

## Phase 5: Test Supabase Connection (5 minutes)

### Verify Backend Connection
Create a test file `test_supabase.py`:
```python
from dotenv import load_dotenv
load_dotenv()

from flozai.services.supabase_client import get_supabase_client

try:
    client = get_supabase_client()
    response = client.table('users').select('count').limit(1).execute()
    print("✅ Backend connected to Supabase!")
except Exception as e:
    print(f"❌ Error: {e}")
```

Run it:
```bash
python test_supabase.py
```
- [ ] Prints "✅ Backend connected!"

### Verify Frontend Connection
In browser console (with frontend running):
```javascript
import { supabase } from '@/services/supabaseClient'
const { data, error } = await supabase.auth.getSession()
console.log(error ? '❌ Error' : '✅ Connected!')
```
- [ ] Prints "✅ Connected!" (or error message if no session yet)

## Phase 6: Integrate Backend Routes (10 minutes)

- [ ] Open `src/flozai/api/routes.py`
- [ ] Add import at top:
  ```python
  from docs.example_api_routes import router as supabase_router
  ```
- [ ] Add to app:
  ```python
  app.include_router(supabase_router)
  ```
- [ ] Or copy route patterns from `docs/example_api_routes.py`

## Phase 7: Test API Endpoints (10 minutes)

Use Postman or curl to test:

### Sign Up
```
POST http://localhost:8000/api/auth/signup
Content-Type: application/json

{
  "email": "test@example.com",
  "password": "testpass123"
}
```
- [ ] Returns user object and session

### Get Health
```
GET http://localhost:8000/api/health
```
- [ ] Returns {"status": "healthy", "database": "connected"}

### List Workflows (should fail without token)
```
GET http://localhost:8000/api/workflows
```
- [ ] Returns 401 error (expected, no auth token)

### List Workflows (with token)
```
GET http://localhost:8000/api/workflows
Authorization: Bearer <your_access_token>
```
- [ ] Returns workflows array (empty if new account)

## Phase 8: Frontend Integration (15 minutes)

### Create Login Component
- [ ] Create `frontend/src/pages/LoginPage.jsx`
- [ ] Use `authService.js` functions:
  ```javascript
  import { login, signUp } from '@/services/authService'
  ```

### Create Dashboard Component
- [ ] Use existing `WorkflowDashboard.jsx` from `frontend/src/components/`
- [ ] Import and use React hooks:
  ```javascript
  import { useWorkflows } from '@/hooks/useWorkflows'
  ```

### Set Up Auth State
- [ ] Create `AuthContext` or use state hook
- [ ] Subscribe to auth changes:
  ```javascript
  import { onAuthStateChange } from '@/services/authService'
  
  useEffect(() => {
    const unsubscribe = onAuthStateChange(({ session }) => {
      setUser(session?.user)
    })
    return unsubscribe
  }, [])
  ```

## Phase 9: Test Complete Flow (10 minutes)

### Full Workflow Test
1. [ ] Start backend: `python main.py`
2. [ ] Start frontend: `npm run dev`
3. [ ] Open http://localhost:3000
4. [ ] Sign up new account
5. [ ] Create a workflow
6. [ ] Add tasks to workflow
7. [ ] See tasks appear in list
8. [ ] Run workflow (creates log entry)
9. [ ] See execution log

### Verify RLS Works
1. [ ] In Supabase, create test user account manually:
   - Go to Authentication → Users → Add user manually
2. [ ] Get their user ID from the list
3. [ ] Query as another user - should see nothing
4. [ ] This confirms RLS is working

## Phase 10: Deploy Preparation (5 minutes)

- [ ] Verify `.env` is in `.gitignore` (don't commit keys!)
- [ ] Create `.env.production` with prod Supabase keys
- [ ] Test with production Supabase project
- [ ] Enable email verification in Supabase Auth
- [ ] Configure password reset email in Supabase
- [ ] Set production URL in Supabase CORS settings
- [ ] Review Security settings in Supabase dashboard

## Troubleshooting

### "Missing SUPABASE_URL" Error
```
✗ Check:
  - .env file exists in project root
  - SUPABASE_URL is set
  - SUPABASE_KEY is set
  - Restart Python/Node process
```

### CORS Errors
```
✗ Check:
  - Frontend URL matches CORS settings in Supabase
  - Project → Settings → API → CORS Allowed origins
  - Add your localhost and production URLs
```

### "RLS policy blocking" Errors
```
✗ Check:
  - User exists in auth.users
  - User record exists in public.users table
  - Query includes proper WHERE clauses
  - Check RLS policies in Supabase dashboard
```

### Authentication Not Working
```
✗ Check:
  - Using anon key, not service role key
  - JWT token is valid (not expired)
  - Authorization header format: "Bearer <token>"
  - Email/password are correct
```

## Resources

| Resource | Link |
|----------|------|
| Quick Start | `docs/SUPABASE_QUICKSTART.md` |
| Full Guide | `docs/SUPABASE_INTEGRATION_GUIDE.md` |
| API Examples | `docs/example_api_routes.py` |
| Database Schema | `docs/database_schema.sql` |
| Supabase Docs | https://supabase.com/docs |

## Files in Your Project

```
✅ Backend Services
   src/flozai/services/supabase_client.py
   src/flozai/services/auth_service.py
   src/flozai/services/database_service.py

✅ Frontend Services
   frontend/src/services/supabaseClient.js
   frontend/src/services/authService.js
   frontend/src/services/databaseService.js
   frontend/src/hooks/useWorkflows.js

✅ Example Components
   frontend/src/components/WorkflowDashboard.jsx
   frontend/src/components/WorkflowDashboard.css

✅ Documentation
   docs/database_schema.sql
   docs/SUPABASE_QUICKSTART.md
   docs/SUPABASE_INTEGRATION_GUIDE.md
   docs/SUPABASE_INTEGRATION_SUMMARY.md
   docs/example_api_routes.py
```

## Success Criteria

**✅ You're Done When:**
- [ ] Supabase account created and project running
- [ ] Environment variables configured
- [ ] Database schema created
- [ ] Backend can connect to Supabase
- [ ] Frontend can connect to Supabase
- [ ] Sign up endpoint works
- [ ] Can create workflows via API
- [ ] Can view workflows in frontend
- [ ] RLS policies are enforced
- [ ] Real-time updates work (optional but cool!)

---

## Next Steps After Setup

1. **Add More Features**
   - User profiles and settings
   - Workflow sharing/collaboration
   - Execution scheduler
   - Webhook support

2. **Enhance Security**
   - Rate limiting on auth endpoints
   - 2FA/MFA support
   - IP whitelisting
   - Audit logging

3. **Production Ready**
   - Setup monitoring
   - Configure backups
   - Set up CI/CD
   - Load testing

4. **Scale**
   - Database optimization
   - Caching strategy
   - CDN for frontend
   - Rate limit configuration

---

**Total Setup Time: ~45 minutes for first-time setup**

Good luck! 🚀
