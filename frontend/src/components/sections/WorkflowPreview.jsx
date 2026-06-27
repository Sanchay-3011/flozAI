import styles from './WorkflowPreview.module.css'

const COLORS = {
  HubSpot: '#ff7a59', Salesforce: '#009edb', Gmail: '#ea4335',
  Slack: '#6ecadc', Mailchimp: '#ffe01b', Stripe: '#635bff',
  LinkedIn: '#0077b5', Twitter: '#1da1f2', Instagram: '#e1306c',
  Clearbit: '#4fa8d5', QuickBooks: '#2ca01c', Notion: '#ffffff',
  Airtable: '#18bfff', Asana: '#fc636b', Jira: '#0052cc',
  Zendesk: '#03363d', OpenAI: '#10a37f', Perplexity: '#6366f1',
  Scheduler: '#8b6fcb', Webhook: '#f59e0b', WhatsApp: '#25d366',
  Google_Sheets: '#34a853', Google_Forms: '#673ab7', Trello: '#0052cc',
  Intercom: '#286efa', Typeform: '#262627', Calendly: '#006bff',
  default: '#4fa8d5',
}

const BrandIcon = ({ name }) => {
  const icons = {
    HubSpot: (
      <svg viewBox="0 0 100 100" fill="none">
        <circle cx="50" cy="50" r="50" fill="#ff7a59"/>
        <path d="M62 38.5V32a6 6 0 10-12 0v6.5a14 14 0 00-8 12.5 14 14 0 008 12.5V76a6 6 0 0012 0V63a14 14 0 008-12.5 14 14 0 00-8-12z" fill="white"/>
        <circle cx="56" cy="51" r="7" fill="#ff7a59"/>
      </svg>
    ),
    Salesforce: (
      <svg viewBox="0 0 100 100" fill="none">
        <rect width="100" height="100" rx="20" fill="#009edb"/>
        <path d="M50 20c-7 0-13 4-16 10a14 14 0 00-2-.2c-8 0-14 6-14 14s6 14 14 14h36c6 0 11-5 11-11s-5-11-11-11c-.5 0-1 0-1.5.1C65 29 58 20 50 20z" fill="white"/>
      </svg>
    ),
    Gmail: (
      <svg viewBox="0 0 100 100" fill="none">
        <rect width="100" height="100" rx="20" fill="white"/>
        <path d="M16 30l34 25 34-25H16z" fill="#ea4335"/>
        <path d="M16 30v40h15V45L50 60l19-15v25h15V30" fill="white"/>
        <path d="M16 70V30l34 25" fill="#c5221f"/>
        <path d="M84 70V30L50 55" fill="#c5221f"/>
      </svg>
    ),
    Slack: (
      <svg viewBox="0 0 100 100" fill="none">
        <rect width="100" height="100" rx="20" fill="white"/>
        <path d="M29 57a8 8 0 110-16 8 8 0 010 16zm0-8v-20a8 8 0 1116 0v20H29z" fill="#e01e5a"/>
        <path d="M43 29a8 8 0 110 16 8 8 0 010-16zm8 0h20a8 8 0 110 16H51V29z" fill="#36c5f0"/>
        <path d="M71 43a8 8 0 110 16 8 8 0 010-16zm-8 8v20a8 8 0 11-16 0V51h16z" fill="#2eb67d"/>
        <path d="M57 71a8 8 0 110-16 8 8 0 010 16zm-8 0H29a8 8 0 110-16h20v16z" fill="#ecb22e"/>
      </svg>
    ),
    Stripe: (
      <svg viewBox="0 0 100 100" fill="none">
        <rect width="100" height="100" rx="20" fill="#635bff"/>
        <path d="M47 38c0-3 2.5-4.5 6-4.5 5 0 10 2 14 5V24a38 38 0 00-14-2.5c-12 0-20 6-20 16 0 16 21 13 21 20 0 3-2.5 4.5-6.5 4.5-5.5 0-12-2.5-16-6v15a38 38 0 0016 3.5c12 0 20.5-6 20.5-16.5C68 41 47 44 47 38z" fill="white"/>
      </svg>
    ),
    LinkedIn: (
      <svg viewBox="0 0 100 100" fill="none">
        <rect width="100" height="100" rx="20" fill="#0077b5"/>
        <rect x="18" y="38" width="14" height="44" fill="white"/>
        <circle cx="25" cy="24" r="9" fill="white"/>
        <path d="M42 38h13v6s4-7 14-7c12 0 17 8 17 20v24H72V59c0-6-2-10-8-10s-9 4-9 10v23H42V38z" fill="white"/>
      </svg>
    ),
    Twitter: (
      <svg viewBox="0 0 100 100" fill="none">
        <rect width="100" height="100" rx="20" fill="black"/>
        <path d="M20 20h18l12 17 14-17h8L54 44l26 36H62L48 61 33 80h-8l20-27L20 20zm8 5l38 50h6L34 25h-6z" fill="white"/>
      </svg>
    ),
    Instagram: (
      <svg viewBox="0 0 100 100" fill="none">
        <defs>
          <linearGradient id="ig" x1="0" y1="100" x2="100" y2="0" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#feda75"/>
            <stop offset="25%" stopColor="#fa7e1e"/>
            <stop offset="50%" stopColor="#d62976"/>
            <stop offset="75%" stopColor="#962fbf"/>
            <stop offset="100%" stopColor="#4f5bd5"/>
          </linearGradient>
        </defs>
        <rect width="100" height="100" rx="22" fill="url(#ig)"/>
        <rect x="18" y="18" width="64" height="64" rx="18" stroke="white" strokeWidth="5" fill="none"/>
        <circle cx="50" cy="50" r="16" stroke="white" strokeWidth="5" fill="none"/>
        <circle cx="72" cy="28" r="5" fill="white"/>
      </svg>
    ),
    WhatsApp: (
      <svg viewBox="0 0 100 100" fill="none">
        <rect width="100" height="100" rx="20" fill="#25d366"/>
        <path d="M50 18C32 18 18 32 18 50c0 6 1.5 11.5 4.5 16.5L18 82l16-4.5A32 32 0 0050 82c18 0 32-14 32-32S68 18 50 18zm17 43c-.7 2-4 3.8-5.5 4-1.4.2-3 .3-5-.3-1.2-.4-2.7-1-4.6-1.8-8-3.5-13.3-11.5-13.7-12-.4-.5-3.3-4.4-3.3-8.4 0-4 2-5.9 2.8-6.7.7-.8 1.5-1 2-1 .5 0 1 0 1.4.1.5 0 1 0 1.5 1.2.6 1.3 2 4.7 2.2 5 .2.4.3.8.1 1.3-.2.5-.3.8-.7 1.2-.4.5-.8.9-1.1 1.2-.4.4-.8.8-.3 1.5.4.7 2 3.4 4.3 5.4 3 2.7 5.4 3.5 6.2 3.9.8.4 1.2.3 1.7-.2.4-.5 1.8-2.1 2.3-2.8.5-.7 1-.6 1.7-.3.7.3 4.5 2.1 5.3 2.5.7.4 1.2.6 1.4 1 .2.4.2 2-.5 4z" fill="white"/>
      </svg>
    ),
    Notion: (
      <svg viewBox="0 0 100 100" fill="none">
        <rect width="100" height="100" rx="20" fill="white"/>
        <path d="M24 22l44 3c5 .4 6 1 6 5v50c0 3-.5 5-4 5l-48-3c-3-.2-4-1-4-4V27c0-3 1.5-5 6-5zm8 10v38l32 2V34L32 32zm4 4l24 1.5v4L36 40v-4zm0 10l24 1.5v4L36 50v-4zm0 10l16 1v4l-16-1v-4z" fill="black"/>
      </svg>
    ),
    Airtable: (
      <svg viewBox="0 0 100 100" fill="none">
        <rect width="100" height="100" rx="20" fill="#18bfff"/>
        <rect x="18" y="18" width="64" height="22" rx="4" fill="white"/>
        <rect x="18" y="46" width="30" height="36" rx="4" fill="white"/>
        <rect x="52" y="46" width="30" height="17" rx="4" fill="white" opacity="0.6"/>
      </svg>
    ),
    Asana: (
      <svg viewBox="0 0 100 100" fill="none">
        <rect width="100" height="100" rx="20" fill="#fc636b"/>
        <circle cx="50" cy="35" r="14" fill="white"/>
        <circle cx="26" cy="62" r="14" fill="white"/>
        <circle cx="74" cy="62" r="14" fill="white"/>
      </svg>
    ),
    Jira: (
      <svg viewBox="0 0 100 100" fill="none">
        <rect width="100" height="100" rx="20" fill="#0052cc"/>
        <path d="M50 20L20 50l30 30 30-30L50 20zm0 10l20 20-20 20-20-20 20-20z" fill="white"/>
      </svg>
    ),
    Zendesk: (
      <svg viewBox="0 0 100 100" fill="none">
        <rect width="100" height="100" rx="20" fill="#03363d"/>
        <path d="M50 22c-10 0-18 7-18 16 0 5 2.5 9.5 6.5 12.5L22 78h28V38c10 0 18-7 18-16S60 22 50 22z" fill="#78a300"/>
        <path d="M50 78c10 0 18-7 18-16 0-5-2.5-9.5-6.5-12.5L68 22H40v40c-10 0-18 7-18 16s8 16 18 16h28" fill="white"/>
      </svg>
    ),
    OpenAI: (
      <svg viewBox="0 0 100 100" fill="none">
        <rect width="100" height="100" rx="20" fill="#10a37f"/>
        <path d="M50 20a30 30 0 000 60A30 30 0 0050 20zm0 8a22 22 0 010 44 22 22 0 010-44zm0 7a15 15 0 100 30 15 15 0 000-30z" fill="white"/>
      </svg>
    ),
    Perplexity: (
      <svg viewBox="0 0 100 100" fill="none">
        <rect width="100" height="100" rx="20" fill="#6366f1"/>
        <path d="M50 18v64M18 50h64M30 30l40 40M70 30L30 70" stroke="white" strokeWidth="5" strokeLinecap="round"/>
        <circle cx="50" cy="50" r="12" fill="#6366f1" stroke="white" strokeWidth="5"/>
      </svg>
    ),
    Scheduler: (
      <svg viewBox="0 0 100 100" fill="none">
        <rect width="100" height="100" rx="20" fill="#8b6fcb"/>
        <circle cx="50" cy="50" r="28" stroke="white" strokeWidth="5" fill="none"/>
        <path d="M50 28v22l14 14" stroke="white" strokeWidth="5" strokeLinecap="round"/>
        <rect x="35" y="18" width="8" height="12" rx="4" fill="white"/>
        <rect x="57" y="18" width="8" height="12" rx="4" fill="white"/>
      </svg>
    ),
    Mailchimp: (
      <svg viewBox="0 0 100 100" fill="none">
        <rect width="100" height="100" rx="20" fill="#ffe01b"/>
        <path d="M65 42c1-1 2-3 1-5-1-3-5-4-8-3l-2 1c-2-5-6-9-11-9-7 0-12 7-12 15 0 1 0 2 .2 3C28 45 24 49 24 54c0 6 6 10 14 10h26c6 0 10-4 10-9 0-6-5-11-9-13z" fill="#241c15"/>
        <circle cx="41" cy="52" r="3" fill="white"/>
        <circle cx="59" cy="52" r="3" fill="white"/>
        <path d="M44 60c1 3 4 5 6 5s5-2 6-5" stroke="white" strokeWidth="2" fill="none" strokeLinecap="round"/>
      </svg>
    ),
    Clearbit: (
      <svg viewBox="0 0 100 100" fill="none">
        <rect width="100" height="100" rx="20" fill="#4fa8d5"/>
        <circle cx="50" cy="42" r="16" fill="white"/>
        <path d="M26 74c0-13 11-24 24-24s24 11 24 24" stroke="white" strokeWidth="6" fill="none" strokeLinecap="round"/>
      </svg>
    ),
    QuickBooks: (
      <svg viewBox="0 0 100 100" fill="none">
        <rect width="100" height="100" rx="20" fill="#2ca01c"/>
        <circle cx="50" cy="50" r="26" fill="white"/>
        <path d="M38 38h10c8 0 14 5 14 12s-6 12-14 12H44v8h-6V38zm6 18h4c5 0 8-3 8-6s-3-6-8-6h-4v12z" fill="#2ca01c"/>
      </svg>
    ),
    Google_Sheets: (
      <svg viewBox="0 0 100 100" fill="none">
        <rect width="100" height="100" rx="20" fill="#34a853"/>
        <rect x="25" y="20" width="50" height="60" rx="4" fill="white"/>
        <rect x="33" y="35" width="34" height="5" rx="1" fill="#34a853"/>
        <rect x="33" y="46" width="34" height="5" rx="1" fill="#34a853"/>
        <rect x="33" y="57" width="34" height="5" rx="1" fill="#34a853"/>
        <path d="M55 20v16h16L55 20z" fill="#1e8e3e"/>
      </svg>
    ),
    Google_Forms: (
      <svg viewBox="0 0 100 100" fill="none">
        <rect width="100" height="100" rx="20" fill="#673ab7"/>
        <rect x="25" y="20" width="50" height="60" rx="4" fill="white"/>
        <rect x="33" y="35" width="20" height="5" rx="2" fill="#673ab7"/>
        <rect x="33" y="48" width="34" height="4" rx="2" fill="#e0e0e0"/>
        <rect x="33" y="58" width="34" height="4" rx="2" fill="#e0e0e0"/>
        <path d="M55 20v16h16L55 20z" fill="#4527a0"/>
      </svg>
    ),
    Trello: (
      <svg viewBox="0 0 100 100" fill="none">
        <rect width="100" height="100" rx="20" fill="#0052cc"/>
        <rect x="18" y="22" width="27" height="38" rx="5" fill="white"/>
        <rect x="55" y="22" width="27" height="26" rx="5" fill="white"/>
      </svg>
    ),
    Intercom: (
      <svg viewBox="0 0 100 100" fill="none">
        <rect width="100" height="100" rx="20" fill="#286efa"/>
        <rect x="20" y="20" width="60" height="60" rx="14" fill="white"/>
        <rect x="32" y="38" width="8" height="22" rx="4" fill="#286efa"/>
        <rect x="46" y="32" width="8" height="28" rx="4" fill="#286efa"/>
        <rect x="60" y="38" width="8" height="22" rx="4" fill="#286efa"/>
      </svg>
    ),
    Typeform: (
      <svg viewBox="0 0 100 100" fill="none">
        <rect width="100" height="100" rx="20" fill="#262627"/>
        <path d="M28 35h44M28 50h44M28 65h28" stroke="white" strokeWidth="6" strokeLinecap="round"/>
      </svg>
    ),
    Calendly: (
      <svg viewBox="0 0 100 100" fill="none">
        <rect width="100" height="100" rx="20" fill="#006bff"/>
        <rect x="20" y="28" width="60" height="52" rx="8" fill="white"/>
        <rect x="20" y="28" width="60" height="18" rx="8" fill="#006bff"/>
        <rect x="35" y="18" width="8" height="18" rx="4" fill="white"/>
        <rect x="57" y="18" width="8" height="18" rx="4" fill="white"/>
        <rect x="30" y="56" width="12" height="12" rx="3" fill="#006bff"/>
        <rect x="48" y="56" width="12" height="12" rx="3" fill="#006bff"/>
      </svg>
    ),
    Webhook: (
      <svg viewBox="0 0 100 100" fill="none">
        <rect width="100" height="100" rx="20" fill="#f59e0b"/>
        <path d="M50 20v20M50 60v20M20 50h20M60 50h20" stroke="white" strokeWidth="6" strokeLinecap="round"/>
        <circle cx="50" cy="50" r="12" fill="white"/>
        <circle cx="50" cy="50" r="6" fill="#f59e0b"/>
      </svg>
    ),
  }

  const key = name?.replace(' ', '_')
  return icons[key] || icons[name] || (
    <svg viewBox="0 0 100 100" fill="none">
      <rect width="100" height="100" rx="20" fill="#4fa8d5"/>
      <path d="M30 50h40M50 30v40" stroke="white" strokeWidth="8" strokeLinecap="round"/>
    </svg>
  )
}

function downloadJSON(workflow) {
  const exportData = {
    name:        workflow.name,
    description: workflow.explanation || '',
    version:     '1.0',
    created_at:  new Date().toISOString(),
    triggers: workflow.steps
      ?.filter(s => s.type === 'TRIGGER')
      .map(s => ({ type: s.action, integration: s.integration })) || [],
    actions: workflow.steps
      ?.filter(s => s.type === 'ACTION')
      .map(s => ({ type: s.action, integration: s.integration })) || [],
  }
  const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' })
  const url  = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href     = url
  link.download = `${workflow.name?.replace(/\s+/g, '_').toLowerCase() || 'workflow'}.json`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

function Node({ node, index, allSteps }) {
  const colorKey = node.integration?.replace(' ', '_')
  const color    = COLORS[colorKey] || COLORS[node.integration] || COLORS.default

  const prevNode      = allSteps[index - 1]
  const isFirstAction = node.type === 'ACTION' && prevNode?.type === 'TRIGGER'
  const isMultiTrigger = node.isMulti
  const showOrBadge   = isMultiTrigger && index > 0 && allSteps[index - 1]?.type === 'TRIGGER'
  const showLine      = index > 0 && !showOrBadge && !isFirstAction

  return (
    <div className={styles.node} style={{ animationDelay: `${index * 0.12}s` }}>

      {showOrBadge && <div className={styles.orBadge}>OR</div>}

      {showLine && (
        <div className={styles.line}>
          <div className={styles.dot} style={{ background: color }} />
        </div>
      )}

      {isFirstAction && (
        <div className={styles.mergeLine}>
          <div className={styles.mergeArrow} style={{ background: color }} />
        </div>
      )}

      <div className={styles.card}>
        <div className={styles.icon} style={{ borderColor: `${color}30` }}>
          <BrandIcon name={node.integration} />
        </div>
        <div className={styles.body}>
          <div className={styles.integration} style={{ color }}>{node.integration}</div>
          <div className={styles.action}>{node.action}</div>
        </div>
        <span className={`${styles.badge} ${styles[node.type?.toLowerCase()]}`}>
          {node.type}
        </span>
      </div>
    </div>
  )
}

export default function WorkflowPreview({ workflow }) {
  if (!workflow) return (
    <div className={styles.empty}>
      <div className={styles.emptyIcon}>
        <svg width="30" height="30" viewBox="0 0 30 30" fill="none">
          <rect x="3" y="7"  width="24" height="4" rx="2" fill="rgba(79,168,213,0.15)" />
          <rect x="3" y="14" width="18" height="4" rx="2" fill="rgba(79,168,213,0.10)" />
          <rect x="3" y="21" width="12" height="4" rx="2" fill="rgba(79,168,213,0.06)" />
        </svg>
      </div>
      <p className={styles.emptyTitle}>Workflow preview</p>
      <p className={styles.emptyHint}>Describe your automation above to generate</p>
    </div>
  )

  return (
    <div className={styles.preview}>
      <div className={styles.header}>
        <span className={styles.name}>{workflow.name || 'Generated Workflow'}</span>
        <div className={styles.ready}>
          <span className="status-dot" />
          Ready
        </div>
      </div>

      <div className={styles.nodes}>
        {workflow.steps?.map((n, i) => (
          <Node key={i} node={n} index={i} allSteps={workflow.steps} />
        ))}
      </div>

      {workflow.explanation && (
        <div className={styles.explanation}>
          <div className={styles.explLabel}>What this does</div>
          <p>{workflow.explanation}</p>
        </div>
      )}

      <div className={styles.actions}>
        <button className="btn-primary" style={{ flex: 1, justifyContent: 'center' }}>
          Activate Workflow
        </button>
        <button
          className={styles.downloadBtn}
          onClick={() => downloadJSON(workflow)}
          title="Download JSON"
        >
          <svg width="15" height="15" viewBox="0 0 15 15" fill="none">
            <path d="M7.5 1v9M4 7l3.5 3.5L11 7M2 13h11"
              stroke="currentColor" strokeWidth="1.5"
              strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
          JSON
        </button>
      </div>
    </div>
  )
}