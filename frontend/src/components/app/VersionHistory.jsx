import React from 'react';
import { X, History, RotateCcw, Clock, User, Check } from 'lucide-react';
import styles from './VersionHistory.module.css';

const VERSIONS = [
  { id: 'v3', time: '2 mins ago', user: 'FlozAI', change: 'Added Slack notification step', current: true },
  { id: 'v2', time: '15 mins ago', user: 'You', change: 'Updated Jira integration parameters', current: false },
  { id: 'v1', time: '1 hour ago', user: 'FlozAI', change: 'Initial workflow generation', current: false },
];

export default function VersionHistory({ isOpen, onClose, onRestore }) {
  return (
    <div className={`${styles.panel} ${isOpen ? styles.open : ''}`}>
      <header className={styles.header}>
        <div className={styles.headerLeft}>
          <History size={16} className={styles.headerIcon} />
          <h3>Version History</h3>
        </div>
        <button className={styles.closeBtn} onClick={onClose}><X size={18} /></button>
      </header>

      <div className={styles.content}>
        <p className={styles.description}>Restore previous versions of this workflow.</p>
        
        <div className={styles.list}>
          {VERSIONS.map((v) => (
            <div key={v.id} className={`${styles.item} ${v.current ? styles.currentItem : ''}`}>
              <div className={styles.itemHeader}>
                <div className={styles.itemMeta}>
                  <Clock size={12} />
                  <span>{v.time}</span>
                </div>
                {v.current && (
                  <div className={styles.currentBadge}>
                    <Check size={10} />
                    <span>Current</span>
                  </div>
                )}
              </div>
              
              <div className={styles.itemBody}>
                <p className={styles.changeText}>{v.change}</p>
                <div className={styles.userRef}>
                  <User size={10} />
                  <span>{v.user}</span>
                </div>
              </div>

              {!v.current && (
                <button className={styles.restoreBtn} onClick={() => onRestore(v)}>
                  <RotateCcw size={14} />
                  <span>Restore</span>
                </button>
              )}
            </div>
          ))}
        </div>
      </div>

      <footer className={styles.footer}>
        <p>Auto-saved at 9:15 PM</p>
      </footer>
    </div>
  );
}
