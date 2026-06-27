import { useState, useRef, useEffect } from 'react'
import styles from './PromptScreen.module.css'
import ParticleField from '../ui/ParticleField'

const EXAMPLES = [
  'When a lead submits my form, add them to CRM and notify Slack',
  'Send follow-up emails to new leads after 24 hours',
  'Sync new CRM contacts to Google Sheets and notify the team',
]

const PROCESSING_STEPS = [
  'Understanding your request...',
  'Identifying integrations...',
  'Building workflow logic...',
  'Validating connections...',
]

export default function PromptScreen({ onGenerate, isLoading }) {
  const [input, setInput] = useState('')
  const [processingStep, setProcessingStep] = useState(0)
  const textareaRef = useRef(null)

  useEffect(() => {
    textareaRef.current?.focus()
  }, [])

  // Cycle through processing steps during loading
  useEffect(() => {
    if (!isLoading) { setProcessingStep(0); return }
    const interval = setInterval(() => {
      setProcessingStep(prev => (prev + 1) % PROCESSING_STEPS.length)
    }, 1800)
    return () => clearInterval(interval)
  }, [isLoading])

  const handleSubmit = () => {
    const text = input.trim()
    if (!text || isLoading) return
    onGenerate(text)
  }

  const handleKey = (e) => {
    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
      e.preventDefault()
      handleSubmit()
    }
  }

  return (
    <div className={styles.screen}>
      <ParticleField />

      <div className={styles.content}>
        {/* Badge */}
        <div className={styles.badge}>
          <span className="status-dot" />
          AI-POWERED AUTOMATION
        </div>

        {/* Headline */}
        <h1 className={styles.headline}>
          What would you like to{' '}
          <span className={`${styles.accent} glow-text`}>automate</span>?
        </h1>

        <p className={styles.subtitle}>
          Describe any business process in plain language. FlozAI builds the workflow.
        </p>

        {/* Prompt Box */}
        <div className={`${styles.promptBox} ${isLoading ? styles.loading : ''}`}>
          <div className={styles.promptGlow} />

          <textarea
            ref={textareaRef}
            className={styles.textarea}
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKey}
            placeholder="When someone fills my website form, add them to my CRM, send a WhatsApp message, and notify my sales team on Slack..."
            rows={4}
            disabled={isLoading}
          />

          <div className={styles.promptFooter}>
            <span className={styles.hint}>⌘ + Enter to generate</span>
            <button
              className={styles.generateBtn}
              onClick={handleSubmit}
              disabled={!input.trim() || isLoading}
            >
              {isLoading ? (
                <>
                  <span className={styles.spinner} />
                  Generating...
                </>
              ) : (
                <>
                  Generate Workflow
                  <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                    <path d="M3 8H13M9 4L13 8L9 12" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Processing state */}
        {isLoading && (
          <div className={styles.processing}>
            <div className={styles.processingDot} />
            <span className={styles.processingText}>
              {PROCESSING_STEPS[processingStep]}
            </span>
          </div>
        )}

        {/* Example chips */}
        {!isLoading && (
          <div className={styles.examples}>
            <span className={styles.exampleLabel}>Try an example:</span>
            <div className={styles.chips}>
              {EXAMPLES.map((ex, i) => (
                <button
                  key={i}
                  className={styles.chip}
                  onClick={() => {
                    setInput(ex)
                    textareaRef.current?.focus()
                  }}
                >
                  {ex}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
