import { useEffect, useRef } from 'react'
import styles from './ExecutionLog.module.css'

const STATUS_COLOR = {
  RUNNING: 'var(--accent-blue)',
  SUCCESS: 'var(--accent-green)',
  FAILED:  '#f87171',
  PENDING: 'var(--text-muted)',
}

function Entry({ entry, index }) {
  return (
    <div className={styles.entry} style={{ animationDelay: `${index * 0.05}s` }}>
      <span className={styles.time}>{entry.timestamp}</span>
      <div className={styles.body}>
        <span className={styles.msg}>{entry.message}</span>
        <span className={styles.status} style={{ color: STATUS_COLOR[entry.status] }}>
          {entry.status}
        </span>
      </div>
    </div>
  )
}

export default function ExecutionLog({ logs = [] }) {
  const bottomRef = useRef(null)
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [logs])

  return (
    <div className={styles.log}>
      <div className={styles.header}>
        <span className={styles.title}>Execution Log</span>
        {logs.length > 0 && <span className={styles.count}>{logs.length} events</span>}
      </div>
      <div className={styles.entries}>
        {logs.length === 0
          ? <div className={styles.empty}>Awaiting execution...</div>
          : logs.map((e, i) => <Entry key={i} entry={e} index={i}/>)
        }
        <div ref={bottomRef}/>
      </div>
    </div>
  )
}