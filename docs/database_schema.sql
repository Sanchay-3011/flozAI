-- ═════════════════════════════════════════════════════════════════════════════
-- Supabase Database Schema for FlozAI
-- ═════════════════════════════════════════════════════════════════════════════
--
-- This schema includes:
-- 1. Tables for users, workflows, tasks, and execution logs
-- 2. Row-Level Security (RLS) policies to ensure users can only access their data
-- 3. Proper indexes for performance
-- 4. Automatic timestamp management
--
-- Instructions:
-- 1. Go to your Supabase project dashboard
-- 2. Click "SQL Editor" → "New Query"
-- 3. Copy and paste this entire script
-- 4. Click "Run" to execute
--
-- ═════════════════════════════════════════════════════════════════════════════

-- ─────────────────────────────────────────────────────────────────────────────
-- 1. Users Table
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email TEXT NOT NULL UNIQUE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE users IS 'User profiles synced from Supabase Auth';

-- ─────────────────────────────────────────────────────────────────────────────
-- 2. Workflows Table
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS workflows (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  description TEXT,
  nodes JSONB DEFAULT '[]',
  edges JSONB DEFAULT '[]',
  steps JSONB DEFAULT '[]',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE workflows IS 'Workflow definitions created by users';

CREATE INDEX idx_workflows_user_id ON workflows(user_id);
CREATE INDEX idx_workflows_created_at ON workflows(created_at DESC);

-- ─────────────────────────────────────────────────────────────────────────────
-- 3. Tasks Table
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS tasks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workflow_id UUID NOT NULL REFERENCES workflows(id) ON DELETE CASCADE,
  step_name TEXT NOT NULL,
  status TEXT DEFAULT 'pending',
  order_index INT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE tasks IS 'Individual steps/tasks within workflows';
COMMENT ON COLUMN tasks.status IS 'Status: pending, running, completed, failed';

CREATE INDEX idx_tasks_workflow_id ON tasks(workflow_id);
CREATE INDEX idx_tasks_order_index ON tasks(workflow_id, order_index);

-- ─────────────────────────────────────────────────────────────────────────────
-- 4. Execution Logs Table
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workflow_id UUID NOT NULL REFERENCES workflows(id) ON DELETE CASCADE,
  execution_time TIMESTAMP WITH TIME ZONE NOT NULL,
  status TEXT NOT NULL,
  output JSONB DEFAULT '{}',
  error_message TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE logs IS 'Execution history and logs for workflows';
COMMENT ON COLUMN logs.status IS 'Status: success, failure, partial';
COMMENT ON COLUMN logs.output IS 'JSON output from workflow execution';

CREATE INDEX idx_logs_workflow_id ON logs(workflow_id);
CREATE INDEX idx_logs_execution_time ON logs(execution_time DESC);
CREATE INDEX idx_logs_status ON logs(status);

-- ═════════════════════════════════════════════════════════════════════════════
-- ROW-LEVEL SECURITY (RLS) POLICIES
-- ═════════════════════════════════════════════════════════════════════════════
-- These policies ensure each user can only access their own data

-- Enable RLS on all tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE workflows ENABLE ROW LEVEL SECURITY;
ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE logs ENABLE ROW LEVEL SECURITY;

-- ─────────────────────────────────────────────────────────────────────────────
-- Users Table RLS
-- ─────────────────────────────────────────────────────────────────────────────

-- Users can SELECT their own profile
CREATE POLICY "Users can view their own profile"
  ON users FOR SELECT
  USING (auth.uid() = id);

-- Users can UPDATE their own profile
CREATE POLICY "Users can update their own profile"
  ON users FOR UPDATE
  USING (auth.uid() = id)
  WITH CHECK (auth.uid() = id);

-- Auth trigger creates user on signup (handled via Supabase Auth)
-- Service role can insert new users
CREATE POLICY "Service role can create users"
  ON users FOR INSERT
  WITH CHECK (true);

-- ─────────────────────────────────────────────────────────────────────────────
-- Workflows Table RLS
-- ─────────────────────────────────────────────────────────────────────────────

-- Users can SELECT their own workflows
CREATE POLICY "Users can view their own workflows"
  ON workflows FOR SELECT
  USING (auth.uid() = user_id);

-- Users can INSERT workflows
CREATE POLICY "Users can create workflows"
  ON workflows FOR INSERT
  WITH CHECK (auth.uid() = user_id);

-- Users can UPDATE their own workflows
CREATE POLICY "Users can update their own workflows"
  ON workflows FOR UPDATE
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

-- Users can DELETE their own workflows
CREATE POLICY "Users can delete their own workflows"
  ON workflows FOR DELETE
  USING (auth.uid() = user_id);

-- ─────────────────────────────────────────────────────────────────────────────
-- Tasks Table RLS
-- ─────────────────────────────────────────────────────────────────────────────

-- Users can SELECT tasks in their workflows
CREATE POLICY "Users can view tasks in their workflows"
  ON tasks FOR SELECT
  USING (
    workflow_id IN (
      SELECT id FROM workflows WHERE user_id = auth.uid()
    )
  );

-- Users can INSERT tasks in their workflows
CREATE POLICY "Users can create tasks in their workflows"
  ON tasks FOR INSERT
  WITH CHECK (
    workflow_id IN (
      SELECT id FROM workflows WHERE user_id = auth.uid()
    )
  );

-- Users can UPDATE tasks in their workflows
CREATE POLICY "Users can update tasks in their workflows"
  ON tasks FOR UPDATE
  USING (
    workflow_id IN (
      SELECT id FROM workflows WHERE user_id = auth.uid()
    )
  )
  WITH CHECK (
    workflow_id IN (
      SELECT id FROM workflows WHERE user_id = auth.uid()
    )
  );

-- Users can DELETE tasks in their workflows
CREATE POLICY "Users can delete tasks in their workflows"
  ON tasks FOR DELETE
  USING (
    workflow_id IN (
      SELECT id FROM workflows WHERE user_id = auth.uid()
    )
  );

-- ─────────────────────────────────────────────────────────────────────────────
-- Logs Table RLS
-- ─────────────────────────────────────────────────────────────────────────────

-- Users can SELECT logs for their workflows
CREATE POLICY "Users can view logs for their workflows"
  ON logs FOR SELECT
  USING (
    workflow_id IN (
      SELECT id FROM workflows WHERE user_id = auth.uid()
    )
  );

-- Users can INSERT logs for their workflows
CREATE POLICY "Users can create logs for their workflows"
  ON logs FOR INSERT
  WITH CHECK (
    workflow_id IN (
      SELECT id FROM workflows WHERE user_id = auth.uid()
    )
  );

-- Users can DELETE logs for their workflows
CREATE POLICY "Users can delete logs for their workflows"
  ON logs FOR DELETE
  USING (
    workflow_id IN (
      SELECT id FROM workflows WHERE user_id = auth.uid()
    )
  );

-- ─────────────────────────────────────────────────────────────────────────────
-- 5. Integrations Table
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS integrations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  integration_type TEXT NOT NULL,
  credential_data JSONB NOT NULL DEFAULT '{}',
  status TEXT DEFAULT 'connected',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE (user_id, integration_type)
);

COMMENT ON TABLE integrations IS 'Credentials and status for user integrations';

CREATE INDEX idx_integrations_user_id ON integrations(user_id);

-- Enable RLS
ALTER TABLE integrations ENABLE ROW LEVEL SECURITY;

-- Users can SELECT their own integrations
CREATE POLICY "Users can view their own integrations"
  ON integrations FOR SELECT
  USING (auth.uid() = user_id);

-- Users can INSERT their own integrations
CREATE POLICY "Users can create their own integrations"
  ON integrations FOR INSERT
  WITH CHECK (auth.uid() = user_id);

-- Users can UPDATE their own integrations
CREATE POLICY "Users can update their own integrations"
  ON integrations FOR UPDATE
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

-- Users can DELETE their own integrations
CREATE POLICY "Users can delete their own integrations"
  ON integrations FOR DELETE
  USING (auth.uid() = user_id);

-- ═════════════════════════════════════════════════════════════════════════════
-- USEFUL QUERIES FOR TESTING
-- ═════════════════════════════════════════════════════════════════════════════

-- View all tables in public schema
-- SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';

-- Example: Check RLS policies on workflows table
-- SELECT * FROM pg_policies WHERE tablename = 'workflows';

-- Example: View workflows created in last 24 hours
-- SELECT * FROM workflows WHERE created_at > now() - interval '1 day' ORDER BY created_at DESC;

-- Example: Get workflow execution statistics
-- SELECT 
--   w.name,
--   COUNT(l.id) as total_executions,
--   COUNT(CASE WHEN l.status = 'success' THEN 1 END) as successful,
--   COUNT(CASE WHEN l.status = 'failure' THEN 1 END) as failed
-- FROM workflows w
-- LEFT JOIN logs l ON w.id = l.workflow_id
-- GROUP BY w.id, w.name;
