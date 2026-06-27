import React, { useState, useEffect } from 'react';
import {
  Zap, Settings, CheckCircle2, AlertTriangle, Sparkles, Edit3, 
  Activity, ArrowRight
} from 'lucide-react';
import styles from './ActivityTimeline.module.css';

const timeAgo = (dateStr) => {
  if (!dateStr) return 'Just now';
  const seconds = Math.floor((new Date() - new Date(dateStr)) / 1000);
  if (seconds < 60) return 'Just now';
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes} min${minutes > 1 ? 's' : ''} ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours} hr${hours > 1 ? 's' : ''} ago`;
  const days = Math.floor(hours / 24);
  return `${days} day${days > 1 ? 's' : ''} ago`;
};

export default function ActivityTimeline({ logs = [], metrics, onOpenWorkflow }) {
  const [filter, setFilter] = useState('All');

  const getIcon = (type) => {
    switch(type) {
      case 'workflow_triggered': return <Zap size={14} className={styles.iconTrigger} />;
      case 'workflow_step_executed': return <Settings size={14} className={styles.iconExec} />;
      case 'workflow_completed': return <CheckCircle2 size={14} className={styles.iconSuccess} />;
      case 'workflow_failed': return <AlertTriangle size={14} className={styles.iconError} />;
      case 'ai_suggestion': return <Sparkles size={14} className={styles.iconAi} />;
      case 'workflow_updated': return <Edit3 size={14} className={styles.iconUpdate} />;
      default: return <Activity size={14} />;
    }
  };

  const filteredEvents = filter === 'All' 
    ? logs 
    : logs.filter(e => {
        if (filter === 'Errors') return e.type === 'workflow_failed';
        if (filter === 'Workflows') return e.type !== 'ai_suggestion' && e.type !== 'workflow_failed';
        if (filter === 'AI') return e.type === 'ai_suggestion';
        return true;
      });

  return (
    <div className={styles.timelineContainer}>
      {/* Health Indicator */}
      <div className={styles.healthStats}>
        <div className={styles.statBox}>
          <span className={styles.statLabel}>Running</span>
          <span className={styles.statVal}>{metrics?.activeWorkflows || 0} <span className={styles.liveDot}></span></span>
        </div>
        <div className={styles.statBox}>
          <span className={styles.statLabel}>Success Rate</span>
          <span className={styles.statValSuccess}>{metrics?.successRate || 0}%</span>
        </div>
        <div className={styles.statBox}>
          <span className={styles.statLabel}>Errors (24h)</span>
          <span className={styles.statValError}>{metrics?.errors24h || 0}</span>
        </div>
      </div>

      <div className={styles.header}>
        <h3>Recent Activity</h3>
        <div className={styles.filters}>
          {['All', 'Workflows', 'Errors', 'AI'].map(f => (
            <button 
              key={f} 
              className={`${styles.filterBtn} ${filter === f ? styles.activeFilter : ''}`}
              onClick={() => setFilter(f)}
            >
              {f}
            </button>
          ))}
        </div>
      </div>

      <div className={styles.feed}>
        {filteredEvents.length === 0 ? (
          <div className={styles.emptyState}>
            <Activity size={24} />
            <p>No matching activity found.</p>
          </div>
        ) : (
          filteredEvents.map((evt, idx) => (
            <div 
              key={evt.id || idx} 
              className={`${styles.eventCard} ${evt.isNew ? styles.animateIn : ''}`}
              onClick={() => onOpenWorkflow?.(evt.title)}
            >
              <div className={styles.eventIconArea}>
                {getIcon(evt.type)}
                {/* Connector line, except for last item */}
                {idx !== filteredEvents.length - 1 && <div className={styles.timelineLine} />}
              </div>
              <div className={styles.eventContent}>
                <div className={styles.eventHead}>
                  <span className={styles.eventTitle}>{evt.title}</span>
                  <span className={styles.eventTime}>{timeAgo(evt.timestamp)}</span>
                </div>
                <p className={styles.eventDetail}>{evt.detail}</p>
              </div>
              <div className={styles.hoverArrow}>
                <ArrowRight size={14} />
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
