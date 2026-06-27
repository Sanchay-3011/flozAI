import { useState, useEffect } from 'react'
import AppLayout from './components/app/AppLayout'
import Dashboard from './components/app/Dashboard'
import WorkspaceLayout from './components/app/WorkspaceLayout'
import WorkflowsView from './components/app/WorkflowsView'
import IntegrationsView from './components/app/IntegrationsView'
import SettingsView from './components/app/SettingsView'
import ActivityView from './components/app/ActivityView'
import { flozApi } from './services/api'
import { useAppData } from './hooks/useAppData'
import { supabase } from './services/supabaseClient'
import { onAuthStateChange, logout } from './services/authService'
import AuthModal from './components/app/AuthModal'
import './styles/global.css'

/*
  Two-state UI:
    'prompt'    → Full-screen centered prompt (ChatGPT-style)
    'workspace' → 3-panel layout (Chat | Canvas | Logs)
*/
export default function App() {
  const [session, setSession]       = useState(null)
  const [authChecked, setAuthChecked] = useState(false)
  const [view, setView]             = useState('dashboard') // dashboard|workflows|workspace|integrations|settings|activity
  const [isLoading, setIsLoading]   = useState(false)
  const [initialPrompt, setInitialPrompt] = useState('')
  const [activeWorkflowData, setActiveWorkflowData] = useState(null)
  const [transitioning, setTransitioning] = useState(false)

  const appData = useAppData()

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session: activeSession } }) => {
      setSession(activeSession)
      setAuthChecked(true)
    })

    const unsubscribe = onAuthStateChange(({ event, session: activeSession }) => {
      setSession(activeSession)
      if (event === 'SIGNED_OUT') {
        setSession(null)
        setView('dashboard')
      }
    })

    return () => unsubscribe()
  }, [])

  const handleLogout = async () => {
    await logout()
  }

  const navigateTo = (newView) => {
    if (newView === 'create') {
      // Map 'create' intent from sidebar to 'dashboard' but focusing prompt could be done later
      setView('dashboard')
      return;
    }
    setView(newView)
  }

  const handleGenerate = async (prompt) => {
    setIsLoading(true)
    setInitialPrompt(prompt)

    try {
      const response = await flozApi.parseIntent(prompt)
      const { intent, workflow, explanation, missing_integrations } = response

      const t = new Date().toLocaleTimeString('en-US', {
        hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit',
      })

      const logs = [
        { timestamp: `[${t}]`, message: 'FlozAI Orchestrator: Processing intent...', status: 'SUCCESS' },
      ]

      const messages = [
        { role: 'user', text: prompt },
      ]

      if (intent.status === 'clear' && workflow) {
        logs.push({ timestamp: `[${t}]`, message: 'Intent parsed successfully.', status: 'SUCCESS' })
        logs.push({ timestamp: `[${t}]`, message: 'Workflow built and validated.', status: 'SUCCESS' })
        logs.push({ timestamp: `[${t}]`, message: `Workflow "${workflow.name}" ready.`, status: 'SUCCESS' })

        messages.push({
          role: 'agent',
          text: explanation || `I've built your workflow: "${workflow.name}". You can refine it by chatting here.`
        })

        if (missing_integrations && missing_integrations.length > 0) {
          const first = missing_integrations[0];
          messages.push({
            role: 'agent',
            text: `To get this workflow running, I need you to set up ${first.name}.`,
            setupAction: first
          });
        }

        const workflowData = {
          name: workflow.name || intent.workflow_name || 'Generated Workflow',
          explanation: explanation || intent.workflow_description || '',
          steps: buildSteps(intent, workflow),
        }

        // Add to persistent storage
        const savedWf = await appData.addWorkflow(workflowData);
        
        setActiveWorkflowData({ 
          workflow: savedWf, 
          logs, 
          messages,
          missingIntegrations: missing_integrations || []
        })

        setTransitioning(true)
        setTimeout(() => {
          setView('workspace')
          setIsLoading(false)
          setTransitioning(false)
        }, 600)

      } else {
        // ... (simplified error/clarification blocks for brevity)
        const msg = intent.status === 'needs_clarification' ? intent.clarification_question : 'Request out of scope'
        messages.push({ role: 'agent', text: msg || 'Can you provide more details?' })
        logs.push({ timestamp: `[${t}]`, message: msg, status: 'RUNNING' })

        setActiveWorkflowData({ workflow: null, logs, messages })
        setTransitioning(true)
        setTimeout(() => {
          setView('workspace')
          setIsLoading(false)
          setTransitioning(false)
        }, 600)
      }

    } catch (err) {
      const msg = err instanceof Error ? err.message : 'An unexpected error occurred.'
      const t = new Date().toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' })

      setActiveWorkflowData({
        workflow: null,
        logs: [{ timestamp: `[${t}]`, message: `Error: ${msg}`, status: 'FAILED' }],
        messages: [
          { role: 'user', text: prompt },
          { role: 'agent', text: `Sorry, something went wrong: ${msg}` }
        ],
      })
      setTransitioning(true)
      setTimeout(() => {
        setView('workspace')
        setIsLoading(false)
        setTransitioning(false)
      }, 600)
    }
  }
  
  const handleOpenWorkflow = (id) => {
    const wf = appData.workflows.find(w => w.id === id);
    if (wf) {
       setActiveWorkflowData({ workflow: wf, logs: [], messages: [] })
       setView('workspace')
    }
  }

  // Render current view
  const renderView = () => {
    switch (view) {
      case 'dashboard':
        return (
          <div style={{
            opacity: transitioning ? 0 : 1, transform: transitioning ? 'scale(0.98)' : 'scale(1)',
            transition: 'opacity 0.4s ease, transform 0.4s ease', height: '100%'
          }}>
            <Dashboard 
              onGenerate={handleGenerate} 
              isLoading={isLoading} 
              appData={appData}
              onOpenWorkflow={handleOpenWorkflow}
            />
          </div>
        )
      case 'workspace':
        return (
          <WorkspaceLayout 
            initialPrompt={initialPrompt} 
            initialData={activeWorkflowData} 
            appData={appData}
            onNavigate={navigateTo}
          />
        )
      case 'workflows':
        return (
          <WorkflowsView 
            appData={appData} 
            onOpenWorkflow={handleOpenWorkflow}
            onCreateNew={() => navigateTo('dashboard')}
          />
        )
      case 'integrations':
        return <IntegrationsView />
      case 'settings':
        return <SettingsView />
      case 'activity':
        return (
          <ActivityView 
            appData={appData}
            onOpenWorkflow={handleOpenWorkflow}
          />
        )
      default:
        return <div style={{padding: '40px', color: 'white'}}>Not Found</div>
    }
  }

  if (!authChecked) {
    return (
      <div style={{ display: 'flex', height: '100vh', width: '100vw', alignItems: 'center', justifyContent: 'center', background: '#030508', color: 'rgba(255,255,255,0.7)', fontFamily: 'sans-serif' }}>
        <div style={{ textAlign: 'center' }}>
          <p style={{ fontSize: '15px', fontWeight: '500' }}>Verifying account session...</p>
        </div>
      </div>
    )
  }

  if (!session) {
    return <AuthModal onAuthSuccess={(newSession) => setSession(newSession)} />
  }

  return (
    <div className="app">
      <AppLayout 
        activeTab={view === 'workspace' ? 'create' : view} 
        onNavigate={navigateTo}
        user={session.user}
        onLogout={handleLogout}
      >
        {renderView()}
      </AppLayout>
    </div>
  )
}

/* ── Helpers ──────────────────────────── */
function buildSteps(intent, workflow) {
  const steps = []

  const triggers = workflow?.triggers?.length
    ? workflow.triggers
    : intent?.triggers?.length
      ? intent.triggers
      : intent?.trigger ? [intent.trigger] : []

  triggers.forEach(t => {
    steps.push({
      integration: t.integration, // Keep raw ID for matching
      displayName: formatIntegration(t.integration), // Dedicated display field
      action: t.type,
      type: 'TRIGGER',
    })
  })

  const actions = workflow?.actions?.length ? workflow.actions : intent?.actions || []
  actions.forEach(a => {
    steps.push({
      integration: a.integration, // Keep raw ID for matching
      displayName: formatIntegration(a.integration), // Dedicated display field
      action: a.type,
      type: 'ACTION',
    })
  })

  return steps
}

function formatIntegration(raw) {
  if (!raw) return 'Unknown'
  const map = {
    hubspot: 'HubSpot', salesforce: 'Salesforce', gmail: 'Gmail',
    slack: 'Slack', mailchimp: 'Mailchimp', stripe: 'Stripe',
    google_sheets: 'Google_Sheets', clearbit: 'Clearbit',
    quickbooks: 'QuickBooks', linkedin: 'LinkedIn',
    twitter: 'Twitter', instagram: 'Instagram',
    notion: 'Notion', airtable: 'Airtable',
    asana: 'Asana', trello: 'Trello', jira: 'Jira',
    zendesk: 'Zendesk', openai: 'OpenAI', perplexity: 'Perplexity',
    scheduler: 'Scheduler', webhook: 'Webhook',
    google_forms: 'Google_Forms', whatsapp: 'WhatsApp',
    typeform: 'Typeform', calendly: 'Calendly',
    intercom: 'Intercom', crm: 'CRM',
  }
  return map[raw.toLowerCase()] || raw.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())
}

function formatType(raw) {
  if (!raw) return 'Unknown'
  return raw.replace(/_/g, ' ').replace(/^\w/, c => c.toUpperCase())
}