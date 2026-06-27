import React from 'react';
import ActivityTimeline from './ActivityTimeline';
import styles from './ActivityView.module.css';

export default function ActivityView({ appData, onOpenWorkflow }) {
  return (
    <div className={styles.viewContainer}>
      <header className={styles.header}>
        <div>
          <h1 className={styles.title}>Activity Log</h1>
          <p className={styles.subtitle}>Trace every action taken by your automations</p>
        </div>
      </header>

      <div className={styles.timelineWrapper}>
         <ActivityTimeline 
           logs={appData?.activityLogs} 
           metrics={appData?.metrics}
           onOpenWorkflow={onOpenWorkflow} 
         />
      </div>
    </div>
  );
}
