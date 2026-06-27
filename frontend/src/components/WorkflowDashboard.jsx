/**
 * Example: Complete Workflow Component
 * Demonstrates how to use Supabase, workflows, tasks, and logs together
 * 
 * This is a minimal example - expand as needed for your use case
 */

import React, { useState, useEffect } from 'react'
import { useWorkflows, useWorkflowTasks, useExecutionLogs } from '@/hooks/useWorkflows'
import { logout } from '@/services/authService'
import './WorkflowDashboard.css'

/**
 * Main Dashboard Component
 * Shows user workflows with task management and execution history
 */
export function WorkflowDashboard() {
  const [selectedWorkflow, setSelectedWorkflow] = useState(null)
  const [newWorkflowName, setNewWorkflowName] = useState('')
  const { workflows, loading: wfLoading, createWorkflow, updateWorkflow, deleteWorkflow } = useWorkflows()

  const handleCreateWorkflow = async () => {
    if (!newWorkflowName.trim()) return

    const workflow = await createWorkflow(newWorkflowName, `Created at ${new Date().toLocaleString()}`)
    if (workflow) {
      setNewWorkflowName('')
      alert('Workflow created successfully!')
    }
  }

  const handleSelectWorkflow = (workflow) => {
    setSelectedWorkflow(workflow)
  }

  const handleDeleteWorkflow = async (workflowId) => {
    if (window.confirm('Are you sure? This will delete all tasks and logs.')) {
      const success = await deleteWorkflow(workflowId)
      if (success) {
        alert('Workflow deleted!')
        setSelectedWorkflow(null)
      }
    }
  }

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <h1>FlozAI Workflow Dashboard</h1>
        <button onClick={logout} className="logout-btn">Logout</button>
      </header>

      <div className="dashboard-content">
        {/* Workflows List */}
        <section className="workflows-section">
          <h2>My Workflows</h2>

          {wfLoading ? (
            <p>Loading workflows...</p>
          ) : workflows.length === 0 ? (
            <p className="empty-state">No workflows yet. Create one below!</p>
          ) : (
            <div className="workflows-list">
              {workflows.map(workflow => (
                <WorkflowCard
                  key={workflow.id}
                  workflow={workflow}
                  isSelected={selectedWorkflow?.id === workflow.id}
                  onSelect={() => handleSelectWorkflow(workflow)}
                  onDelete={() => handleDeleteWorkflow(workflow.id)}
                />
              ))}
            </div>
          )}

          {/* Create New Workflow */}
          <div className="create-workflow">
            <h3>Create New Workflow</h3>
            <input
              type="text"
              value={newWorkflowName}
              onChange={e => setNewWorkflowName(e.target.value)}
              placeholder="Enter workflow name..."
              onKeyPress={e => e.key === 'Enter' && handleCreateWorkflow()}
            />
            <button onClick={handleCreateWorkflow} className="btn-primary">
              Create Workflow
            </button>
          </div>
        </section>

        {/* Workflow Details */}
        {selectedWorkflow ? (
          <WorkflowDetails workflow={selectedWorkflow} onUpdate={updateWorkflow} />
        ) : (
          <div className="placeholder">
            <p>Select a workflow to view details</p>
          </div>
        )}
      </div>
    </div>
  )
}

/**
 * Workflow Card Component
 * Displays workflow summary
 */
function WorkflowCard({ workflow, isSelected, onSelect, onDelete }) {
  return (
    <div
      className={`workflow-card ${isSelected ? 'selected' : ''}`}
      onClick={onSelect}
    >
      <h4>{workflow.name}</h4>
      <p>{workflow.description}</p>
      <small>{new Date(workflow.created_at).toLocal String()}</small>
      <button
        className="delete-btn"
        onClick={e => {
          e.stopPropagation()
          onDelete()
        }}
      >
        Delete
      </button>
    </div>
  )
}

/**
 * Workflow Details Component
 * Shows tasks and execution logs for selected workflow
 */
function WorkflowDetails({ workflow, onUpdate }) {
  const { tasks, createTask, updateTask, deleteTask } = useWorkflowTasks(workflow.id)
  const { logs, stats, createLog } = useExecutionLogs(workflow.id)
  const [newTaskName, setNewTaskName] = useState('')

  const handleAddTask = async () => {
    if (!newTaskName.trim()) return

    const task = await createTask(newTaskName, tasks.length)
    if (task) {
      setNewTaskName('')
    }
  }

  const handleUpdateTaskStatus = async (taskId, newStatus) => {
    await updateTask(taskId, { status: newStatus })
  }

  const handleRunWorkflow = async () => {
    // Simulate workflow execution
    const success = Math.random() > 0.2 // 80% success rate
    const log = await createLog(
      success ? 'success' : 'failure',
      {
        executedAt: new Date().toISOString(),
        tasksCompleted: tasks.length,
        duration: Math.floor(Math.random() * 5000)
      },
      success ? null : 'Simulated execution error'
    )

    if (log) {
      alert(`Workflow executed: ${success ? 'SUCCESS' : 'FAILED'}`)
    }
  }

  return (
    <section className="workflow-details">
      <div className="details-header">
        <h2>{workflow.name}</h2>
        <button onClick={handleRunWorkflow} className="btn-success">
          Run Workflow
        </button>
      </div>

      <div className="details-grid">
        {/* Tasks Section */}
        <div className="tasks-section">
          <h3>Workflow Steps</h3>

          {tasks.length === 0 ? (
            <p className="empty-state">No tasks yet</p>
          ) : (
            <div className="tasks-list">
              {tasks.map((task, index) => (
                <TaskItem
                  key={task.id}
                  task={task}
                  index={index}
                  onUpdateStatus={handleUpdateTaskStatus}
                  onDelete={() => deleteTask(task.id)}
                />
              ))}
            </div>
          )}

          <div className="add-task">
            <input
              type="text"
              value={newTaskName}
              onChange={e => setNewTaskName(e.target.value)}
              placeholder="Add new step..."
              onKeyPress={e => e.key === 'Enter' && handleAddTask()}
            />
            <button onClick={handleAddTask} className="btn-primary">
              Add Step
            </button>
          </div>
        </div>

        {/* Execution Stats */}
        <div className="stats-section">
          <h3>Execution Statistics</h3>
          {stats ? (
            <div className="stats-grid">
              <div className="stat-card">
                <label>Total Executions</label>
                <p className="stat-value">{stats.total}</p>
              </div>
              <div className="stat-card success">
                <label>Successful</label>
                <p className="stat-value">{stats.success}</p>
              </div>
              <div className="stat-card failed">
                <label>Failed</label>
                <p className="stat-value">{stats.failed}</p>
              </div>
              <div className="stat-card">
                <label>Success Rate</label>
                <p className="stat-value">{stats.successRate}%</p>
              </div>
            </div>
          ) : (
            <p>No execution data yet</p>
          )}
        </div>
      </div>

      {/* Execution Logs */}
      <div className="logs-section">
        <h3>Recent Executions</h3>
        {logs.length === 0 ? (
          <p className="empty-state">No execution log yet</p>
        ) : (
          <div className="logs-list">
            {logs.slice(0, 10).map(log => (
              <LogEntry key={log.id} log={log} />
            ))}
          </div>
        )}
      </div>
    </section>
  )
}

/**
 * Task Item Component
 */
function TaskItem({ task, index, onUpdateStatus, onDelete }) {
  return (
    <div className="task-item">
      <div className="task-info">
        <span className="task-index">{index + 1}.</span>
        <span className="task-name">{task.step_name}</span>
      </div>
      <select
        value={task.status}
        onChange={e => onUpdateStatus(task.id, e.target.value)}
        className={`status-select status-${task.status}`}
      >
        <option value="pending">Pending</option>
        <option value="running">Running</option>
        <option value="completed">Completed</option>
        <option value="failed">Failed</option>
      </select>
      <button
        onClick={() => onDelete()}
        className="delete-btn"
        title="Delete task"
      >
        ✕
      </button>
    </div>
  )
}

/**
 * Log Entry Component
 */
function LogEntry({ log }) {
  return (
    <div className={`log-entry log-${log.status}`}>
      <div className="log-info">
        <span className="log-status">{log.status.toUpperCase()}</span>
        <span className="log-time">
          {new Date(log.execution_time).toLocaleString()}
        </span>
      </div>
      {log.error_message && (
        <p className="log-error">{log.error_message}</p>
      )}
      {log.output && Object.keys(log.output).length > 0 && (
        <details className="log-output">
          <summary>Details</summary>
          <pre>{JSON.stringify(log.output, null, 2)}</pre>
        </details>
      )}
    </div>
  )
}

export default WorkflowDashboard
