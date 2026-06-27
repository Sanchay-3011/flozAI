import { useState } from 'react'
import ChatSidebar from './ChatSidebar'
import WorkflowCanvas from './WorkflowCanvas'
import ActivityPanel from './ActivityPanel'
import styles from './WorkspaceLayout.module.css'
import { flozApi } from '../../services/api'
import { ListChecks } from 'lucide-react'
import { useWorkflowAnalyzer } from '../../hooks/useWorkflowAnalyzer'

export default function WorkspaceLayout({ initialPrompt, initialData, appData, onNavigate }) {
  const [workflow, setWorkflow]       = useState(initialData?.workflow || null)
  const [logs, setLogs]               = useState(initialData?.logs || [])
  const [messages, setMessages]       = useState(initialData?.messages || [])
  const [isLoading, setIsLoading]     = useState(false)
  const [error, setError]             = useState(null)
  const [isDrawerOpen, setIsDrawerOpen] = useState(false)
  const [pendingIntegrations, setPendingIntegrations] = useState(initialData?.missingIntegrations || [])

  const missingRequirements = useWorkflowAnalyzer(workflow, appData.integrations);

  const addLog = (message, status = 'RUNNING') => {
    const t = new Date().toLocaleTimeString('en-US', {
      hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit',
    })
    setLogs(prev => [...prev, { timestamp: `[${t}]`, message, status }])
  }

  const handleChatSend = async (text, meta = {}) => {
    // Add user message
    setMessages(prev => [...prev, { role: 'user', text, ...meta }])
    setIsLoading(true)
    setError(null)

    // If it's a "set up" intent from buttons, handle it specifically
    if (meta.setupAction) {
      setTimeout(() => {
        setMessages(prev => [...prev, {
          role: 'agent',
          text: `Sure, I can help you set up ${meta.setupAction.name}.`,
          setupAction: meta.setupAction
        }]);
        setIsLoading(false);
      }, 500);
      addLog(`Setup initiated for ${meta.setupAction.name}.`, 'RUNNING');
      return;
    }

    // Build combined context
    const originalPrompt = messages.find(m => m.role === 'user')?.text || initialPrompt
    const fullPrompt = `${originalPrompt}. Additional: ${text}`

    addLog('FlozAI Orchestrator: Processing refinement...', 'RUNNING')

    try {
      const response = await flozApi.parseIntent(fullPrompt)
      const { intent, workflow: wf, explanation, missing_integrations } = response

      if (intent.status === 'clear' && wf) {
        addLog('Intent updated successfully.', 'SUCCESS')
        addLog('Workflow rebuilt and validated.', 'SUCCESS')

        setWorkflow({
          name: wf.name || intent.workflow_name || 'Generated Workflow',
          explanation: explanation || intent.workflow_description || '',
          steps: buildSteps(intent, wf),
        })

        setMessages(prev => {
          const newMsgs = [...prev, {
            role: 'agent',
            text: explanation || `I've updated the workflow: "${wf.name}"`
          }];
          
          if (missing_integrations && missing_integrations.length > 0) {
            setPendingIntegrations(missing_integrations);
            const first = missing_integrations[0];
            newMsgs.push({
              role: 'agent',
              text: `To get this workflow running, I need you to set up ${first.name}.`,
              setupAction: first
            });
          } else {
            setPendingIntegrations([]);
          }
          return newMsgs;
        });

        addLog(`Workflow "${wf.name || 'Untitled'}" updated.`, 'SUCCESS')

      } else if (intent.status === 'needs_clarification') {
        setMessages(prev => [...prev, {
          role: 'agent',
          text: intent.clarification_question || 'Can you provide more details?'
        }])
        addLog('FlozAI needs more information.', 'RUNNING')

      } else if (intent.status === 'out_of_scope') {
        const msg = [intent.out_of_scope_reason, intent.suggested_alternative]
          .filter(Boolean).join(' ')
        setMessages(prev => [...prev, { role: 'agent', text: msg }])
        addLog('Request is out of scope.', 'FAILED')
      }

    } catch (err) {
      const msg = err instanceof Error ? err.message : 'An unexpected error occurred.'
      setError(msg)
      setMessages(prev => [...prev, { role: 'agent', text: `Error: ${msg}` }])
      addLog(`Error: ${msg}`, 'FAILED')
    } finally {
      setIsLoading(false)
    }
  }

  const toggleDrawer = () => setIsDrawerOpen(!isDrawerOpen)

  const handleFixSetup = (missing) => {
    if (!missing || missing.length === 0) return;
    
    // Trigger the assistant to start a guided setup
    const first = missing[0];
    handleChatSend(`I need to set up ${first.name}`, { setupAction: first });
  };

  return (
    <div className={styles.layout}>
      {/* Left: Chat Sidebar (AI Assistant) */}
      <aside className={styles.chatArea}>
        <ChatSidebar
          messages={messages}
          onSend={handleChatSend}
          isLoading={isLoading}
          missingRequirements={missingRequirements}
          onSaveIntegration={async (id, data) => {
            try {
              await appData.saveIntegration(id, data);
              
              // Use pendingIntegrations (from API response) instead of stale hook
              const nextMissing = pendingIntegrations.filter(r => r.id !== id);
              setPendingIntegrations(nextMissing);
              
              if (nextMissing.length > 0) {
                const next = nextMissing[0];
                setMessages(prev => [...prev, {
                  role: 'agent',
                  text: `✅ ${id.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())} connected! Now, let's set up ${next.name}.`,
                  setupAction: next
                }]);
              } else {
                setMessages(prev => [...prev, {
                  role: 'agent',
                  text: `✅ All integrations connected! Your workflow is now ready to run.`
                }]);
                addLog('All integrations connected. Workflow is READY.', 'SUCCESS');
              }
            } catch (err) {
              // Show the validation error and re-show the setup card
              const currentReq = pendingIntegrations.find(r => r.id === id);
              setMessages(prev => [...prev, {
                role: 'agent',
                text: `❌ ${err.message || 'Connection failed. Please try again.'}`,
                setupAction: currentReq || { id, name: id, type: 'apikey', description: '' }
              }]);
            }
          }}
        />
      </aside>

      {/* Center: Workflow Canvas */}
      <main className={styles.canvasArea}>
        <WorkflowCanvas 
          workflow={workflow} 
          appData={appData} 
          onFixSetup={handleFixSetup}
          onNavigate={onNavigate}
        />
        
        {/* Retractable Activity Panel (Slides from Right) */}
        <ActivityPanel 
          logs={logs} 
          isDrawerOpen={isDrawerOpen} 
          onToggle={toggleDrawer}
        />

        {/* Floating toggle for closed state */}
        {!isDrawerOpen && (
          <button className={styles.floatingToggle} onClick={toggleDrawer} title="Open Activity Log">
            <ListChecks size={20} />
            {logs.length > 0 && <span className={styles.badge}>{logs.length}</span>}
          </button>
        )}
      </main>

      {/* Error bar */}
      {error && (
        <div className={styles.errorBar}>
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
            <circle cx="7" cy="7" r="6" stroke="#f87171" strokeWidth="1.2" fill="none"/>
            <path d="M7 4.5v3M7 9.5v.5" stroke="#f87171" strokeWidth="1.2" strokeLinecap="round"/>
          </svg>
          <span>{error}</span>
          <button className={styles.errorClose} onClick={() => setError(null)}>×</button>
        </div>
      )}
    </div>
  )
}

/* ── Step builder (reused from original) ── */
function buildSteps(intent, workflow) {
  const steps = []

  const triggers = workflow?.triggers?.length
    ? workflow.triggers
    : intent?.triggers?.length
      ? intent.triggers
      : intent?.trigger ? [intent.trigger] : []

  triggers.forEach((t, i) => {
    steps.push({
      integration: t.integration,
      displayName: formatIntegration(t.integration),
      action: t.type,
      type: 'TRIGGER',
    })
  })

  const actions = workflow?.actions?.length ? workflow.actions : intent?.actions || []
  actions.forEach(a => {
    steps.push({
      integration: a.integration,
      displayName: formatIntegration(a.integration),
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
