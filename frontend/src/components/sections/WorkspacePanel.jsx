import { useState } from 'react'
import PromptInput     from './PromptInput'
import WorkflowPreview from './WorkflowPreview'
import ExecutionLog    from './ExecutionLog'
import styles from './WorkspacePanel.module.css'
import { flozApi } from '../../services/api'

export default function WorkspacePanel() {
  const [workflow,      setWorkflow]      = useState(null)
  const [logs,          setLogs]          = useState([])
  const [isLoading,     setIsLoading]     = useState(false)
  const [error,         setError]         = useState(null)
  const [clarification, setClarification] = useState(null)

  const addLog = (message, status = 'RUNNING') => {
    const t = new Date().toLocaleTimeString('en-US', {
      hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit',
    })
    setLogs(prev => [...prev, { timestamp: `[${t}]`, message, status }])
  }

  const extractMessage = (err) => {
    if (err instanceof Error) return err.message
    if (typeof err === 'string') return err
    if (err?.message) return String(err.message)
    if (err?.detail) return typeof err.detail === 'string' ? err.detail : JSON.stringify(err.detail)
    return 'An unexpected error occurred.'
  }

  const processPrompt = async (prompt) => {
    setIsLoading(true)
    setError(null)
    setClarification(null)
    setWorkflow(null)
    setLogs([])

    addLog('FlozAI Orchestrator: Processing intent...', 'RUNNING')

    try {
      const response = await flozApi.parseIntent(prompt)
      const { intent, workflow, explanation } = response

      if (intent.status === 'clear' && workflow) {
        addLog('Intent parsed successfully.', 'SUCCESS')
        addLog('Workflow built and validated.', 'SUCCESS')

        const triggerCount = workflow.triggers?.length || 1
        if (triggerCount > 1) {
          addLog(`Multi-trigger workflow detected — ${triggerCount} triggers.`, 'SUCCESS')
        }

        setWorkflow({
          name:        workflow.name        || intent.workflow_name        || 'Generated Workflow',
          explanation: explanation          || intent.workflow_description || '',
          steps:       buildSteps(intent, workflow),
        })

        addLog(
          `Workflow "${workflow.name || 'Untitled'}" is ready to activate.`,
          'SUCCESS'
        )

      } else if (intent.status === 'needs_clarification') {
        setClarification(intent.clarification_question || 'Can you provide more details?')
        addLog('FlozAI needs more information.', 'RUNNING')

      } else if (intent.status === 'out_of_scope') {
        const msg = [intent.out_of_scope_reason, intent.suggested_alternative]
          .filter(Boolean).join(' ')
        addLog('Request is out of scope.', 'FAILED')
        setError(msg || "This automation is outside FlozAI's current capabilities.")

      } else {
        addLog('Could not process intent.', 'FAILED')
        setError('Could not understand the automation. Try rephrasing.')
      }

    } catch (err) {
      const msg = extractMessage(err)
      setError(msg)
      addLog(`Error: ${msg}`, 'FAILED')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <section id="workspace" className={styles.section}>
      <div className={styles.inner}>
        <div className={styles.label}>WORKFLOW BUILDER</div>
        <h2 className={styles.heading}>From Sentence to System</h2>
        <p className={styles.sub}>Describe any business process. FlozAI handles the rest.</p>

        <div className={styles.grid}>
          <div className={styles.left}>
            <PromptInput
              onSubmit={processPrompt}
              onClarify={processPrompt}
              isLoading={isLoading}
              clarification={clarification}
            />
            {error && (
              <div className={styles.error}>
                <svg width="15" height="15" viewBox="0 0 15 15" fill="none" style={{ flexShrink: 0 }}>
                  <circle cx="7.5" cy="7.5" r="6.5" stroke="#f87171" strokeWidth="1.5"/>
                  <path d="M7.5 4.5v3M7.5 10v.5" stroke="#f87171" strokeWidth="1.5" strokeLinecap="round"/>
                </svg>
                <span>{error}</span>
              </div>
            )}
          </div>

          <div className={styles.right}>
            <div className={styles.panel}>
              <WorkflowPreview workflow={workflow} />
            </div>
            <div className={styles.panel}>
              <ExecutionLog logs={logs} />
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}

function buildSteps(intent, workflow) {
  const steps = []

  // Handle triggers array (multi-trigger support)
  const triggers = workflow?.triggers?.length
    ? workflow.triggers
    : intent?.triggers?.length
      ? intent.triggers
      : intent?.trigger
        ? [intent.trigger]
        : []

  triggers.forEach((t, i) => {
    steps.push({
      integration: formatIntegration(t.integration),
      action:      formatType(t.type),
      type:        'TRIGGER',
      isMulti:     triggers.length > 1,
      triggerIndex: i,
    })
  })

  // Handle actions
  const actions = workflow?.actions?.length ? workflow.actions : intent?.actions || []
  actions.forEach(a => {
    steps.push({
      integration: formatIntegration(a.integration),
      action:      formatType(a.type),
      type:        'ACTION',
    })
  })

  return steps
}

function formatIntegration(raw) {
  if (!raw) return 'Unknown'
  const map = {
    hubspot: 'HubSpot', salesforce: 'Salesforce', gmail: 'Gmail',
    slack: 'Slack', mailchimp: 'Mailchimp', stripe: 'Stripe',
    google_sheets: 'Google Sheets', clearbit: 'Clearbit',
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