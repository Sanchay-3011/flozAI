import React, { useState, useRef, useEffect } from 'react';
import { 
  Play, CheckCircle2, Zap, ArrowRight, Grid, LayoutDashboard
} from 'lucide-react';
import styles from './Dashboard.module.css';
import ActivityTimeline from './ActivityTimeline';

const EXAMPLES = [
  'When a lead submits my form, add them to CRM and notify Slack',
  'Send follow-up emails to new leads after 24 hours',
  'Customer support routing based on Zendesk tickets',
];

const PROCESSING_STEPS = [
  'Understanding your request...',
  'Identifying integrations...',
  'Building workflow logic...',
  'Validating connections...',
];

const timeAgo = (dateStr) => {
  if (!dateStr) return 'Never';
  const seconds = Math.floor((new Date() - new Date(dateStr)) / 1000);
  if (seconds < 60) return 'Just now';
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes} min${minutes > 1 ? 's' : ''} ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours} hr${hours > 1 ? 's' : ''} ago`;
  const days = Math.floor(hours / 24);
  return `${days} day${days > 1 ? 's' : ''} ago`;
};

export default function Dashboard({ onGenerate, isLoading, appData, onOpenWorkflow }) {
  const [input, setInput] = useState('');
  const [processingStep, setProcessingStep] = useState(0);
  const textareaRef = useRef(null);

  useEffect(() => {
    // We don't focus automatically on dashboard so users can look around
  }, []);

  useEffect(() => {
    if (!isLoading) { setProcessingStep(0); return; }
    const interval = setInterval(() => {
      setProcessingStep(prev => (prev + 1) % PROCESSING_STEPS.length);
    }, 1800);
    return () => clearInterval(interval);
  }, [isLoading]);

  const handleSubmit = () => {
    const text = input.trim();
    if (!text || isLoading) return;
    onGenerate(text);
  };

  const handleKey = (e) => {
    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const recentWorkflows = [...(appData?.workflows || [])]
    .sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt))
    .slice(0, 5);

  return (
    <div className={styles.dashboard}>
      <div className={styles.inner}>
        
        {/* Top Header & Stats */}
        <header className={styles.header}>
          <div>
            <h1 className={styles.title}>Workspace Overview</h1>
            <p className={styles.subtitle}>Manage your AI automation system</p>
          </div>
        </header>

        <div className={styles.statsGrid}>
          <div className={styles.statCard}>
            <div className={styles.statIconWrapper}><Zap size={18} color="#fcd34d" /></div>
            <div>
              <span className={styles.statValue}>{appData?.metrics?.activeWorkflows || 0}</span>
              <span className={styles.statLabel}>Active Workflows</span>
            </div>
          </div>
          <div className={styles.statCard}>
            <div className={styles.statIconWrapper}><Play size={18} color="#22d3ee" /></div>
            <div>
              <span className={styles.statValue}>{appData?.metrics?.executionsToday || 0}</span>
              <span className={styles.statLabel}>Executions Today</span>
            </div>
          </div>
          <div className={styles.statCard}>
            <div className={styles.statIconWrapper}><CheckCircle2 size={18} color="#10b981" /></div>
            <div>
              <span className={styles.statValue}>{appData?.metrics?.successRate || 0}%</span>
              <span className={styles.statLabel}>Success Rate</span>
            </div>
          </div>
        </div>

        {/* Central Prompt Area */}
        <section className={styles.promptSection}>
          <div className={`${styles.promptBox} ${isLoading ? styles.loading : ''}`}>
            <div className={styles.promptGlow} />

            <textarea
              ref={textareaRef}
              className={styles.textarea}
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={handleKey}
              placeholder="What would you like to automate? e.g. 'When someone fills my website form, add them to HubSpot...'"
              rows={3}
              disabled={isLoading}
            />

            <div className={styles.promptFooter}>
              <div className={styles.examples}>
                {EXAMPLES.map((ex, i) => (
                  <button
                    key={i}
                    className={styles.chip}
                    onClick={() => {
                      setInput(ex);
                      textareaRef.current?.focus();
                    }}
                    disabled={isLoading}
                  >
                    {ex}
                  </button>
                ))}
              </div>

              <button
                className={styles.generateBtn}
                onClick={handleSubmit}
                disabled={!input.trim() || isLoading}
              >
                {isLoading ? (
                  <>
                    <span className={styles.spinner} />
                    {PROCESSING_STEPS[processingStep]}
                  </>
                ) : (
                  <>
                    Generate
                    <svg width="14" height="14" viewBox="0 0 16 16" fill="none">
                      <path d="M3 8H13M9 4L13 8L9 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                    </svg>
                  </>
                )}
              </button>
            </div>
          </div>
        </section>

        {/* Lower Split View: Recent Workflows & Activity Timeline */}
        <div className={styles.lowerGrid}>
          
          <div className={styles.recentWorkflows}>
            <div className={styles.sectionHeader}>
              <Grid size={16} className={styles.sectionIcon} />
              <h3>Recent Workflows</h3>
            </div>
            <div className={styles.workflowList}>
              {recentWorkflows.length === 0 ? (
                <div className={styles.emptyWorkflows}>
                  <Grid size={24} />
                  <p>No workflows yet. Create your first automation above.</p>
                </div>
              ) : (
                recentWorkflows.map((wf) => (
                  <div key={wf.id} className={styles.workflowCard} onClick={() => onOpenWorkflow?.(wf.id)}>
                    <div className={styles.wfInfo}>
                      <h4>{wf.name}</h4>
                      <div className={styles.wfMeta}>
                        <span>Last run: {timeAgo(wf.lastRun)}</span>
                        <span className={styles.wfStatusDot} 
                              style={{ background: wf.status === 'Running' || wf.status === 'Active' ? '#10b981' : '#94a3b8' }}/>
                        <span>{wf.status}</span>
                      </div>
                    </div>
                    <button className={styles.iconBtn}><ArrowRight size={16} /></button>
                  </div>
                ))
              )}
            </div>
          </div>

          <div className={styles.activityFeed}>
            <ActivityTimeline 
              logs={appData?.activityLogs} 
              metrics={appData?.metrics}
              onOpenWorkflow={onOpenWorkflow} 
            />
          </div>

        </div>

      </div>
    </div>
  );
}
