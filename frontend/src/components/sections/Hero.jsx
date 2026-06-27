import styles from './Hero.module.css'
import ParticleField from '../ui/ParticleField'

export default function Hero() {
  return (
    <section className={styles.hero}>
      <ParticleField />
      <div className={styles.content}>

        <div className={styles.badge}>
          <span className="status-dot" />
          AI-POWERED AUTOMATION PLATFORM
        </div>

        <h1 className={styles.headline}>
          <span className={styles.l1}>Elevate Your</span>
          <span className={`${styles.l2} glow-text`}>Automation</span>
          <span className={styles.l3}>Experience</span>
        </h1>

        <p className={styles.sub}>
          From sentence to system in minutes.<br/>
          Build intelligent cross-functional workflows with plain language.
        </p>

        <div className={styles.cta}>
          <a href="#workspace" className="btn-primary">
            Start Automating
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path d="M3 8H13M9 4L13 8L9 12" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </a>
          <button className="btn-ghost">Watch how it works →</button>
        </div>

        <div className={styles.stats}>
          <div className={styles.stat}>
            <div className={styles.statVal}>96%</div>
            <div className={styles.statLbl}>Execution Success</div>
          </div>
          <div className={styles.divider}/>
          <div className={styles.stat}>
            <div className={styles.statVal}>46</div>
            <div className={styles.statLbl}>Runs Today</div>
          </div>
          <div className={styles.divider}/>
          <div className={styles.stat}>
            <div className={styles.statVal}>&lt;2s</div>
            <div className={styles.statLbl}>Build Time</div>
          </div>
        </div>

      </div>
    </section>
  )
}