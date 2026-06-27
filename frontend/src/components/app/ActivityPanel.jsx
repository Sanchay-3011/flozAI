import { useEffect, useRef } from 'react'
import { ChevronRight, ChevronLeft, Activity, TrendingUp, Clock, CheckCircle2, X } from 'lucide-react'
import styles from './ActivityPanel.module.css'

const STATUS_COLOR = {
  RUNNING: 'var(--accent-blue)',
  SUCCESS: 'var(--accent-green)',
  FAILED:  'var(--accent-red)',
  PENDING: 'var(--text-muted)',
}

function LogEntry({ entry, index }) {
  return (
    <div className={styles.entry} style={{ animationDelay: `${index * 0.06}s` }}>
      <span className={styles.time}>{entry.timestamp}</span>
      <div className={styles.entryBody}>
        <span className={styles.msg}>{entry.message}</span>
        <span
          className={`${styles.status} ${styles[`status_${entry.status}`]}`}
        >
          {entry.status === 'RUNNING' && <span className={styles.statusDot} />}
          {entry.status}
        </span>
      </div>
    </div>
  )
}

export default function ActivityPanel({ logs = [], isDrawerOpen, onToggle }) {
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [logs])

  const successCount = logs.filter(l => l.status === 'SUCCESS').length
  const totalCount = logs.length
  const successRate = totalCount > 0 ? Math.round((successCount / totalCount) * 100) : 0

  return (
    <div className={`${styles.panel} ${isDrawerOpen ? styles.open : styles.closed}`}>
      {/* Header */}
      <div className={styles.header}>
        <div className={styles.headerLeft}>
          <Activity size={15} className={styles.headerIcon} />
          <span className={styles.headerTitle}>Activity Log</span>
        </div>
        <div className={styles.headerRight}>
          {logs.length > 0 && <span className={styles.count}>{logs.length}</span>}
          <button className={styles.toggleBtn} onClick={onToggle} title="Close panel">
            {isDrawerOpen ? <X size={16} /> : <ChevronLeft size={16} />}
          </button>
        </div>
      </div>

      {/* Performance metrics */}
      {logs.length > 0 && (
        <div className={styles.metricsBar}>
          <div className={styles.metric}>
            <CheckCircle2 size={12} />
            <span className={styles.metricValue}>{successRate}%</span>
            <span className={styles.metricLabel}>Success</span>
          </div>
          <div className={styles.metric}>
            <TrendingUp size={12} />
            <span className={styles.metricValue}>{totalCount}</span>
            <span className={styles.metricLabel}>Steps</span>
          </div>
          <div className={styles.metric}>
            <Clock size={12} />
            <span className={styles.metricValue}>&lt;1s</span>
            <span className={styles.metricLabel}>Avg</span>
          </div>
        </div>
      )}

      {/* Log entries */}
      <div className={styles.entries}>
        {logs.length === 0 ? (
          <div className={styles.empty}>
            <p className={styles.emptyText}>Awaiting execution...</p>
          </div>
        ) : (
          logs.map((entry, i) => (
            <LogEntry key={i} entry={entry} index={i} />
          ))
        )}
        <div ref={bottomRef} />
      </div>
    </div>
  )
}
