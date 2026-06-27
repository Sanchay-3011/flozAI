# Supabase Quick Start

Get up and running with Supabase in 5 minutes!

## Step-by-Step Setup

### 1. Create Supabase Account (2 min)

```
1. Go to https://supabase.com/dashboard
2. Click "New Project"
3. Name it "flozai" or similar
4. Set strong password
5. Choose region closest to you
6. Wait for project creation
```

### 2. Get API Keys (1 min)

Once project is created:
```
1. Go to Settings → API
2. Copy "Project URL" → SUPABASE_URL
3. Copy "Anon key" → SUPABASE_KEY
4. Copy "Service role key" → SUPABASE_SERVICE_ROLE_KEY (keep secret!)
```

### 3. Configure Environment (1 min)

**Backend (.env):**
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
```

**Frontend (.env.local):**
```env
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
```

### 4. Create Database Schema (1 min)

```sql
1. In Supabase dashboard, go to SQL Editor
2. Click "New Query"
3. Paste contents of: docs/database_schema.sql
4. Click "Run"
5. Wait for tables to be created
```

### 5. Install Dependencies (1 min)

Backend:
```bash
pip install supabase>=2.0.0 python-dotenv email-validator
```

Frontend:
```bash
npm install @supabase/supabase-js
```

## Verify Setup

### Test Backend Connection

```python
from flozai.services.supabase_client import get_supabase_client

client = get_supabase_client()
response = client.table('users').select('count').execute()
print("✅ Connected to Supabase!")
```

### Test Frontend Connection

```javascript
import { supabase } from '@/services/supabaseClient'

const { data, error } = await supabase.auth.getSession()
console.log(error ? '❌ Error' : '✅ Connected!')
```

## Common Errors & Fixes

| Error | Solution |
|-------|----------|
| "Missing SUPABASE_URL" | Check your `.env` file has both URL and KEY |
| "Invalid authorization" | Prefix token with "Bearer " |
| "RLS policy blocking" | Ensure auth.uid() matches user ID |
| CORS errors | Try in incognito mode or check dashboard CORS settings |

## Next Steps

### Backend
1. Add routes from `docs/example_api_routes.py` to your app
2. Create FastAPI dependency for extracting current user
3. Start using AuthService and DatabaseService in handlers

### Frontend
1. Create login/signup pages using `authService.js`
2. Use `useWorkflows` hook for workflows
3. Use `useExecutionLogs` hook for logs
4. Set up route protection with auth state

## File Structure

```
src/flozai/
├── services/
│   ├── supabase_client.py      # Singleton client
│   ├── auth_service.py         # Authentication
│   └── database_service.py     # CRUD operations

frontend/src/
├── services/
│   ├── supabaseClient.js       # JS client config
│   ├── authService.js          # Auth functions
│   └── databaseService.js      # CRUD functions
├── hooks/
│   └── useWorkflows.js         # React hooks

docs/
├── database_schema.sql          # SQL schema
├── example_api_routes.py        # Route examples
└── SUPABASE_INTEGRATION_GUIDE.md # Full guide
```

## Key Features

✅ **Authentication**
- Sign up / Login / Logout
- JWT token management
- Password reset
- Email verification ready

✅ **Database**
- CRUD for workflows, tasks, logs
- Proper indexing for performance
- Foreign key constraints

✅ **Security**
- Row-Level Security on all tables
- User data isolation
- No cross-user access possible

✅ **Real-time** (Built-in)
- Subscribe to database changes
- Real-time updates in frontend
- Live workflow status

## Pro Tips

1. **Test RLS**: Try accessing another user's data via SQL - should fail
2. **Use AsyncIO**: All services are async - use `await` everywhere
3. **Error Handling**: Always catch `AuthError` and `DatabaseError`
4. **Pagination**: Use limit/offset for large datasets
5. **Subscriptions**: Unsubscribe on component unmount to avoid leaks

## Troubleshooting

**Can't create tables?**
- Check SQL syntax in database_schema.sql
- Verify you're in the right database
- Check Supabase project status

**Authentication failing?**
- Verify SUPABASE_KEY is the "Anon key", not service role
- Check email/password are correct
- Verify user exists in Supabase Auth

**RLS blocking queries?**
- Check policies in Supabase dashboard
- Verify auth.uid() returns correct value
- Test policy with specific user ID

---

**Full Documentation**: See `docs/SUPABASE_INTEGRATION_GUIDE.md` for complete guide.

**Code Examples**: See `docs/example_api_routes.py` for FastAPI integration.

**Need Help?** Check [Supabase Docs](https://supabase.com/docs)
