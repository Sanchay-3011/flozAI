import React, { useState } from 'react';
import { Search, Plus, Filter, MoreHorizontal, Play, ArrowRight, Grid, Zap } from 'lucide-react';
import styles from './WorkflowsView.module.css';

export default function WorkflowsView({ appData, onOpenWorkflow, onCreateNew }) {
  const [query, setQuery] = useState('');
  const workflows = appData?.workflows || [];

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

  const filtered = workflows.filter(w => 
    w.name.toLowerCase().includes(query.toLowerCase())
  );

  return (
    <div className={styles.viewContainer}>
      <header className={styles.header}>
        <div>
          <h1 className={styles.title}>Workflows</h1>
          <p className={styles.subtitle}>Manage, monitor, and create automation routines</p>
        </div>
        <button className={styles.createBtn} onClick={onCreateNew}>
          <Plus size={16} /> Create Workflow
        </button>
      </header>

      <div className={styles.controls}>
        <div className={styles.searchBar}>
          <Search size={16} className={styles.searchIcon} />
          <input 
            type="text" 
            placeholder="Search workflows..." 
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className={styles.searchInput}
          />
        </div>
        <button className={styles.filterBtn}>
          <Filter size={16} /> Filter
        </button>
      </div>

      <div className={styles.tableContainer}>
        <table className={styles.table}>
          <thead>
            <tr>
              <th>Name</th>
              <th>Status</th>
              <th>Task Run (24h)</th>
              <th>Last Executed</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filtered.length === 0 ? (
              <tr>
                <td colSpan="5" className={styles.emptyState}>
                  <Grid size={32} />
                  <h3>No workflows yet</h3>
                  <p>Create your first workflow to get started with FlozAI automation.</p>
                  <button className={styles.createBtnEmpty} onClick={onCreateNew}>
                    <Plus size={16} /> Create Workflow
                  </button>
                </td>
              </tr>
            ) : (
              filtered.map(wf => (
                <tr key={wf.id} onClick={() => onOpenWorkflow?.(wf.id)} className={styles.tableRow}>
                  <td className={styles.nameCell}>
                    <div className={styles.wfIcon}><Zap size={14} /></div>
                    <div className={styles.wfNameBlock}>
                      <span className={styles.wfName}>{wf.name}</span>
                      <span className={styles.wfSteps}>{wf.nodes?.length || 0} steps</span>
                    </div>
                  </td>
                  <td>
                    <div className={styles.statusBadge}>
                      <span 
                        className={styles.statusDot} 
                        style={{ background: wf.status === 'Running' || wf.status === 'Active' ? '#10b981' : '#fcd34d' }}
                      />
                      {wf.status || 'Draft'}
                    </div>
                  </td>
                  <td className={styles.execCell}>
                    {wf.executionHistory?.length || 0}
                  </td>
                  <td className={styles.timeCell}>
                    {timeAgo(wf.lastRun)}
                  </td>
                  <td className={styles.actionsCell} onClick={e => e.stopPropagation()}>
                    <button className={styles.iconBtn} title="Run" onClick={() => onOpenWorkflow?.(wf.id)}>
                      <Play size={16} />
                    </button>
                    <button className={styles.iconBtn} title="Edit workflow" onClick={() => onOpenWorkflow?.(wf.id)}>
                      <ArrowRight size={16} />
                    </button>
                    <button className={styles.iconBtn} title="More options">
                      <MoreHorizontal size={16} />
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
