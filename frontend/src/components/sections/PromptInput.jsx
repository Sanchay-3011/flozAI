import { useState, useRef, useEffect } from 'react'
import styles from './PromptInput.module.css'

const EXAMPLES = [
  'Organize new leads from Gmail into Salesforce and notify Slack',
  'When a HubSpot lead scores above 80, enrich with Clearbit and assign to sales',
  'Sync Stripe payments to QuickBooks and alert on failed charges',
]

export default function PromptInput({ onSubmit, isLoading, clarification, onClarify }) {
  const [messages, setMessages]   = useState([])  // conversation history
  const [input, setInput]         = useState('')
  const [started, setStarted]     = useState(false)
  const inputRef                  = useRef(null)
  const bottomRef                 = useRef(null)

  // When backend sends a clarification, add it as an agent message
  useEffect(() => {
    if (!clarification) return
    setMessages(prev => {
      // Avoid duplicates
      const last = prev[prev.length - 1]
      if (last?.role === 'agent' && last?.text === clarification) return prev
      return [...prev, { role: 'agent', text: clarification }]
    })
  }, [clarification])

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Focus input on mount
  useEffect(() => {
    inputRef.current?.focus()
  }, [])

  const handleSend = () => {
    const text = input.trim()
    if (!text || isLoading) return

    // Add user message to thread
    const updatedMessages = [...messages, { role: 'user', text }]
    setMessages(updatedMessages)
    setInput('')
    setStarted(true)

    // If this is a follow-up answer to a clarification
    if (clarification && messages.some(m => m.role === 'agent')) {
      // Build full context: original prompt + clarification + answer
      const originalPrompt = messages.find(m => m.role === 'user')?.text || ''
      const fullPrompt = `${originalPrompt}. To clarify: ${text}`
      onClarify(fullPrompt)
    } else {
      // First message — fresh intent
      onSubmit(text)
    }
  }

  const handleKey = (e) => {
    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleExample = (ex) => {
    setInput(ex)
    inputRef.current?.focus()
  }

  const handleReset = () => {
    setMessages([])
    setInput('')
    setStarted(false)
  }

  return (
    <div className={`${styles.wrapper} ${started ? styles.active : ''}`}>

      {/* Conversation thread */}
      {messages.length > 0 && (
        <div className={styles.thread}>
          {messages.map((msg, i) => (
            <div
              key={i}
              className={`${styles.bubble} ${msg.role === 'user' ? styles.userBubble : styles.agentBubble}`}
            >
              {msg.role === 'agent' && (
                <div className={styles.agentHeader}>
                  <div className={styles.agentDot} />
                  <span className={styles.agentName}>FlozAI</span>
                </div>
              )}
              <p className={styles.bubbleText}>{msg.text}</p>
            </div>
          ))}

          {/* Loading indicator inside thread */}
          {isLoading && (
            <div className={`${styles.bubble} ${styles.agentBubble}`}>
              <div className={styles.agentHeader}>
                <div className={styles.agentDot} />
                <span className={styles.agentName}>FlozAI</span>
              </div>
              <div className={styles.thinking}>
                <span /><span /><span />
              </div>
            </div>
          )}

          <div ref={bottomRef} />
        </div>
      )}

      {/* Input area */}
      <div className={`${styles.inputBox} ${isLoading ? styles.loading : ''}`}>
        {!started && (
          <div className={styles.inputHeader}>
            <span className={styles.inputLabel}>Describe your automation</span>
            <span className={styles.inputHint}>⌘ + Enter to send</span>
          </div>
        )}

        <textarea
          ref={inputRef}
          className={styles.textarea}
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKey}
          placeholder={
            clarification && started
              ? 'Type your answer...'
              : 'When a new lead is detected in HubSpot, enrich with Salesforce data...'
          }
          rows={started ? 2 : 4}
          disabled={isLoading}
        />

        <div className={styles.inputFooter}>
          {started ? (
            <button className={styles.resetBtn} onClick={handleReset}>
              ↩ Start over
            </button>
          ) : (
            <span className={styles.charCount}>{input.length} / 500</span>
          )}

          <button
            className={`${styles.sendBtn} ${isLoading ? styles.busy : ''}`}
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
          >
            {isLoading ? (
              <><span className={styles.spinner} /> Building...</>
            ) : clarification && started ? (
              <>Answer →</>
            ) : (
              <>Build Workflow →</>
            )}
          </button>
        </div>
      </div>

      {/* Example chips — only before first message */}
      {!started && (
        <div className={styles.chips}>
          <span className={styles.chipLabel}>Try:</span>
          {EXAMPLES.map((ex, i) => (
            <button key={i} className={styles.chip} onClick={() => handleExample(ex)}>
              {ex.length > 52 ? ex.slice(0, 52) + '…' : ex}
            </button>
          ))}
        </div>
      )}

    </div>
  )
}