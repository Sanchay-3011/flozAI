import { useState, useRef, useEffect } from 'react'
import { Sparkles, Key, Link as LinkIcon, CheckCircle, AlertCircle, ArrowRight } from 'lucide-react'
import { flozApi } from '../../services/api'
import styles from './ChatSidebar.module.css'

const SUGGESTIONS = [
  'Add email notification after this',
  'Add error handling to each step',
  'Replace with a different integration',
  'Add a delay between steps',
]

const TEMPLATES = [
  { icon: '🎯', label: 'Lead capture automation' },
  { icon: '🎫', label: 'Support ticket routing' },
  { icon: '📧', label: 'Marketing email campaign' },
  { icon: '🔄', label: 'Data sync pipeline' },
]

export default function ChatSidebar({ messages, onSend, isLoading, missingRequirements, onSaveIntegration }) {
  const [input, setInput] = useState('')
  const [apiKeyInput, setApiKeyInput] = useState('')
  const [bypassInputs, setBypassInputs] = useState({})
  const [showBypass, setShowBypass] = useState({})
  const [setupStep, setSetupStep] = useState(0) // Index of missingRequirement being handled
  const bottomRef = useRef(null)
  const inputRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSend = (text) => {
    const msg = (text || input).trim()
    if (!msg || isLoading) return
    onSend(msg)
    setInput('')
  }

  const handleKey = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const isEmpty = messages.length === 0
  const lastMessage = messages[messages.length - 1]
  const isSettingUp = lastMessage?.setupAction != null

  return (
    <div className={styles.sidebar}>
      {/* Header */}
      <div className={styles.header}>
        <div className={styles.headerDot} />
        <span className={styles.headerTitle}>FlozAI Assistant</span>
      </div>

      {/* Messages area */}
      <div className={styles.messages}>
        {/* Empty state: templates */}
        {isEmpty && !isLoading && (
          <div className={styles.emptyState}>
            <Sparkles size={20} className={styles.emptyIcon} />
            <p className={styles.emptyText}>Try a workflow template</p>
            <div className={styles.templateGrid}>
              {TEMPLATES.map((t, i) => (
                <button
                  key={i}
                  className={styles.templateCard}
                  onClick={() => handleSend(t.label)}
                >
                  <span className={styles.templateIcon}>{t.icon}</span>
                  <span className={styles.templateLabel}>{t.label}</span>
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg, i) => (
          <div
            key={i}
            className={`${styles.message} ${msg.role === 'user' ? styles.userMsg : styles.agentMsg}`}
            style={{ animationDelay: `${i * 0.05}s` }}
          >
            {msg.role === 'agent' && (
              <div className={styles.agentLabel}>
                <div className={styles.agentDot} />
                <span>FlozAI</span>
              </div>
            )}
            <div className={styles.bubble}>
              {msg.text}
              
              {msg.setupAction && (
                <div className={styles.setupActionContainer}>
                  {msg.setupAction.type === 'apikey' ? (
                    <div className={styles.setupCard}>
                      <div className={styles.setupHeader}>
                        <Key size={14} className={styles.setupIcon} />
                        <span>Step: Connect {msg.setupAction.name}</span>
                      </div>
                      <p className={styles.setupDesc}>
                        <strong>Why is this needed?</strong> {msg.setupAction.description}
                      </p>
                      
                      {msg.setupAction.setup_instructions && (
                        <div className={styles.setupInstructions}>
                          <p className={styles.setupStepsTitle}>How to get your API Key:</p>
                          <ol className={styles.setupStepsList}>
                            {msg.setupAction.setup_instructions.steps.map((step, idx) => (
                              <li key={idx}>{step}</li>
                            ))}
                          </ol>
                          <a 
                            href={msg.setupAction.setup_instructions.url} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            className={styles.setupDocsLink}
                          >
                            Get Key →
                          </a>
                        </div>
                      )}

                      <div className={styles.setupInputWrapper}>
                        <input 
                          type="password"
                          placeholder={`Enter your ${msg.setupAction.name} API Key`}
                          className={styles.setupInput}
                          value={apiKeyInput}
                          onChange={(e) => setApiKeyInput(e.target.value)}
                        />
                        <button 
                          className={styles.setupSaveBtn}
                          onClick={() => {
                            onSaveIntegration(msg.setupAction.id, { apiKey: apiKeyInput });
                            setApiKeyInput('');
                          }}
                        >
                          Save Key
                        </button>
                      </div>
                      <p className={styles.setupTip}>
                        <small>Your keys are encrypted and stored safely.</small>
                      </p>
                    </div>
                  ) : (
                    <div className={styles.setupCard}>
                      <div className={styles.setupHeader}>
                        <LinkIcon size={14} className={styles.setupIcon} />
                        <span>Step: Link {msg.setupAction.name} Account</span>
                      </div>
                      <p className={styles.setupDesc}>
                        <strong>Why is this needed?</strong> {msg.setupAction.description}
                      </p>
                      
                      {msg.setupAction.setup_instructions && (
                        <div className={styles.setupInstructions}>
                          <p className={styles.setupStepsTitle}>How to connect:</p>
                          <ol className={styles.setupStepsList}>
                            {msg.setupAction.setup_instructions.steps.map((step, idx) => (
                              <li key={idx}>{step}</li>
                            ))}
                          </ol>
                        </div>
                      )}

                      {showBypass[i] ? (
                        <div className={styles.setupInputWrapper} style={{ marginTop: '12px' }}>
                          <p className={styles.setupTip} style={{ marginBottom: '8px', color: 'rgba(255,255,255,0.6)' }}>
                            <small>OAuth client credentials are not configured on the server. You can connect by entering a token or API key directly below:</small>
                          </p>
                          <input 
                            type="password"
                            placeholder={`Enter your ${msg.setupAction.name} API Key / Token`}
                            className={styles.setupInput}
                            value={bypassInputs[i] || ''}
                            onChange={(e) => setBypassInputs(prev => ({ ...prev, [i]: e.target.value }))}
                          />
                          <div style={{ display: 'flex', gap: '8px', marginTop: '8px', width: '100%' }}>
                            <button 
                              className={styles.setupSaveBtn}
                              style={{ flex: 1, padding: '8px' }}
                              onClick={() => {
                                onSaveIntegration(msg.setupAction.id, { apiKey: bypassInputs[i] });
                                setBypassInputs(prev => ({ ...prev, [i]: '' }));
                                setShowBypass(prev => ({ ...prev, [i]: false }));
                              }}
                              disabled={!(bypassInputs[i]?.trim())}
                            >
                              Connect Key
                            </button>
                            <button 
                              className={styles.setupSaveBtn}
                              style={{ flex: 1, padding: '8px', background: 'rgba(255,255,255,0.05)', color: 'rgba(255,255,255,0.7)' }}
                              onClick={() => setShowBypass(prev => ({ ...prev, [i]: false }))}
                            >
                              Cancel
                            </button>
                          </div>
                        </div>
                      ) : (
                        <button 
                          className={styles.setupLinkBtn}
                          onClick={async () => {
                            try {
                              const data = await flozApi.getOAuthAuthorizeUrl(msg.setupAction.id);
                              if (data.url) {
                                const popup = window.open(data.url, 'oauth_popup', 'width=600,height=700');
                                
                                const listener = (event) => {
                                  if (event.data?.type === 'oauth_success' && event.data?.provider === msg.setupAction.id) {
                                    window.removeEventListener('message', listener);
                                    onSaveIntegration(msg.setupAction.id, { oauth: true, verified: true });
                                  } else if (event.data?.type === 'oauth_error') {
                                    window.removeEventListener('message', listener);
                                    alert(`Authorization failed: ${event.data.error}`);
                                  }
                                };
                                window.addEventListener('message', listener);
                              } else {
                                setShowBypass(prev => ({ ...prev, [i]: true }));
                              }
                            } catch (e) {
                              const errMsg = e.message || '';
                              if (errMsg.includes('OAuth not configured') || errMsg.includes('400')) {
                                setShowBypass(prev => ({ ...prev, [i]: true }));
                              } else {
                                alert(`Could not start authorization: ${e.message}`);
                              }
                            }
                          }}
                        >
                          Click to Authorize {msg.setupAction.name}
                        </button>
                      )}
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        ))}

        {/* Guided Setup Summary */}
        {missingRequirements && missingRequirements.length > 0 && !isLoading && !isSettingUp && (
          <div className={`${styles.message} ${styles.agentMsg}`}>
            <div className={styles.agentLabel}>
              <div className={styles.agentDot} />
              <span>Setup Guide</span>
            </div>
            <div className={styles.bubble}>
              <div className={styles.setupSummaryHeader}>
                <AlertCircle size={14} className={styles.alertIcon} />
                <span>Integration Setup Guide</span>
              </div>
              <p className={styles.setupIntro}>
                I've detected that your workflow needs a few connections before it can run successfully. 
                Don't worry, I'll guide you through each one!
              </p>
              <div className={styles.setupList}>
                {missingRequirements.map((req) => (
                  <div key={req.id} className={styles.setupListItem}>
                    <div className={styles.setupListInfo}>
                      <span className={styles.setupListName}>{req.name}</span>
                      <span className={styles.setupListType}>{req.type === 'oauth' ? 'Account Connection' : 'API Key'}</span>
                    </div>
                    <button 
                      className={styles.setupActionBtn}
                      onClick={() => onSend(`I want to set up ${req.name}`, { setupAction: req })}
                    >
                      Connect Now
                    </button>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Thinking indicator */}
        {isLoading && (
          <div className={`${styles.message} ${styles.agentMsg}`}>
            <div className={styles.agentLabel}>
              <div className={styles.agentDot} />
              <span>FlozAI</span>
            </div>
            <div className={styles.thinking}>
              <span /><span /><span />
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Suggestion chips */}
      {messages.length > 0 && !isLoading && (
        <div className={styles.suggestions}>
          {SUGGESTIONS.map((s, i) => (
            <button
              key={i}
              className={styles.suggestionChip}
              onClick={() => handleSend(s)}
            >
              {s}
            </button>
          ))}
        </div>
      )}

      {/* Input */}
      <div className={styles.inputArea}>
        <textarea
          ref={inputRef}
          className={styles.input}
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKey}
          placeholder="Refine your workflow..."
          rows={2}
          disabled={isLoading}
        />
        <button
          className={styles.sendBtn}
          onClick={() => handleSend()}
          disabled={!input.trim() || isLoading}
          title="Send"
        >
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path d="M2 8L14 2L8 14L7 9L2 8Z" fill="currentColor"/>
          </svg>
        </button>
      </div>
    </div>
  )
}
