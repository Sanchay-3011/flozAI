/**
 * Custom React Hook: useWorkflows
 * Example hook for managing workflows in React components
 * 
 * Usage:
 * const { workflows, loading, createWorkflow, updateWorkflow } = useWorkflows()
 */

import { useState, useEffect, useCallback } from 'react'
import { workflowService, subscribeToWorkflows } from '@/services/databaseService'

export const useWorkflows = () => {
  const [workflows, setWorkflows] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  // Fetch workflows
  const fetchWorkflows = useCallback(async (limit = 50, offset = 0) => {
    setLoading(true)
    try {
      const { data, error } = await workflowService.getAll(limit, offset)

      if (error) {
        setError(error)
        return
      }

      setWorkflows(data || [])
      setError(null)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [])

  // Create workflow
  const createWorkflow = useCallback(async (name, description) => {
    setLoading(true)
    try {
      const { data, error } = await workflowService.create({
        name,
        description
      })

      if (error) {
        setError(error)
        return null
      }

      setWorkflows(prev => [data, ...prev])
      setError(null)
      return data
    } catch (err) {
      setError(err.message)
      return null
    } finally {
      setLoading(false)
    }
  }, [])

  // Update workflow
  const updateWorkflow = useCallback(async (workflowId, updates) => {
    setLoading(true)
    try {
      const { data, error } = await workflowService.update(workflowId, updates)

      if (error) {
        setError(error)
        return null
      }

      setWorkflows(prev =>
        prev.map(w => (w.id === workflowId ? data : w))
      )
      setError(null)
      return data
    } catch (err) {
      setError(err.message)
      return null
    } finally {
      setLoading(false)
    }
  }, [])

  // Delete workflow
  const deleteWorkflow = useCallback(async (workflowId) => {
    setLoading(true)
    try {
      const { error } = await workflowService.delete(workflowId)

      if (error) {
        setError(error)
        return false
      }

      setWorkflows(prev => prev.filter(w => w.id !== workflowId))
      setError(null)
      return true
    } catch (err) {
      setError(err.message)
      return false
    } finally {
      setLoading(false)
    }
  }, [])

  // Subscribe to real-time updates
  useEffect(() => {
    const unsubscribe = subscribeToWorkflows(null, payload => {
      // Handle real-time updates
      console.log('Workflow update:', payload)
      // Re-fetch workflows on changes
      fetchWorkflows()
    })

    return () => unsubscribe()
  }, [fetchWorkflows])

  // Initial fetch
  useEffect(() => {
    fetchWorkflows()
  }, [fetchWorkflows])

  return {
    workflows,
    loading,
    error,
    fetchWorkflows,
    createWorkflow,
    updateWorkflow,
    deleteWorkflow
  }
}

/**
 * Custom React Hook: useWorkflowTasks
 * Manage tasks for a specific workflow
 */

export const useWorkflowTasks = (workflowId) => {
  const [tasks, setTasks] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const { taskService } = await import('@/services/databaseService')

  // Fetch tasks
  const fetchTasks = useCallback(async () => {
    if (!workflowId) return

    setLoading(true)
    try {
      const { data, error } = await taskService.getByWorkflow(workflowId)

      if (error) {
        setError(error)
        return
      }

      setTasks(data || [])
      setError(null)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [workflowId])

  // Create task
  const createTask = useCallback(async (stepName, orderIndex, status = 'pending') => {
    setLoading(true)
    try {
      const { data, error } = await taskService.create({
        workflow_id: workflowId,
        step_name: stepName,
        order_index: orderIndex,
        status
      })

      if (error) {
        setError(error)
        return null
      }

      setTasks(prev => [...prev, data].sort((a, b) => a.order_index - b.order_index))
      setError(null)
      return data
    } catch (err) {
      setError(err.message)
      return null
    } finally {
      setLoading(false)
    }
  }, [workflowId])

  // Update task
  const updateTask = useCallback(async (taskId, updates) => {
    setLoading(true)
    try {
      const { data, error } = await taskService.update(taskId, updates)

      if (error) {
        setError(error)
        return null
      }

      setTasks(prev => prev.map(t => (t.id === taskId ? data : t)))
      setError(null)
      return data
    } catch (err) {
      setError(err.message)
      return null
    } finally {
      setLoading(false)
    }
  }, [])

  // Delete task
  const deleteTask = useCallback(async (taskId) => {
    setLoading(true)
    try {
      const { error } = await taskService.delete(taskId)

      if (error) {
        setError(error)
        return false
      }

      setTasks(prev => prev.filter(t => t.id !== taskId))
      setError(null)
      return true
    } catch (err) {
      setError(err.message)
      return false
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchTasks()
  }, [fetchTasks])

  return {
    tasks,
    loading,
    error,
    fetchTasks,
    createTask,
    updateTask,
    deleteTask
  }
}

/**
 * Custom React Hook: useExecutionLogs
 * Manage execution logs for a workflow
 */

export const useExecutionLogs = (workflowId) => {
  const [logs, setLogs] = useState([])
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const { logService, subscribeToLogs } = await import('@/services/databaseService')

  // Fetch logs
  const fetchLogs = useCallback(async (limit = 100, offset = 0) => {
    if (!workflowId) return

    setLoading(true)
    try {
      const { data, error } = await logService.getByWorkflow(workflowId, limit, offset)

      if (error) {
        setError(error)
        return
      }

      setLogs(data || [])
      setError(null)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [workflowId])

  // Fetch statistics
  const fetchStats = useCallback(async () => {
    if (!workflowId) return

    try {
      const { data, error } = await logService.getStats(workflowId)

      if (error) {
        setError(error)
        return
      }

      setStats(data)
      setError(null)
    } catch (err) {
      setError(err.message)
    }
  }, [workflowId])

  // Create log
  const createLog = useCallback(async (status, output, errorMessage = null) => {
    try {
      const { data, error } = await logService.create({
        workflow_id: workflowId,
        execution_time: new Date().toISOString(),
        status,
        output,
        error_message: errorMessage
      })

      if (error) {
        setError(error)
        return null
      }

      setLogs(prev => [data, ...prev])
      setError(null)
      return data
    } catch (err) {
      setError(err.message)
      return null
    }
  }, [workflowId])

  // Subscribe to real-time log updates
  useEffect(() => {
    if (!workflowId) return

    const unsubscribe = subscribeToLogs(workflowId, payload => {
      console.log('Log update:', payload)
      fetchLogs()
      fetchStats()
    })

    return () => unsubscribe()
  }, [workflowId, fetchLogs, fetchStats])

  // Initial fetch
  useEffect(() => {
    fetchLogs()
    fetchStats()
  }, [fetchLogs, fetchStats])

  return {
    logs,
    stats,
    loading,
    error,
    fetchLogs,
    fetchStats,
    createLog
  }
}

/**
 * Example usage in a React component:
 * 
 * function WorkflowDashboard() {
 *   const { workflows, loading, createWorkflow } = useWorkflows()
 * 
 *   const handleCreate = async () => {
 *     const workflow = await createWorkflow('My Workflow', 'Description')
 *     if (workflow) {
 *       console.log('Created:', workflow)
 *     }
 *   }
 * 
 *   return (
 *     <div>
 *       {loading && <p>Loading...</p>}
 *       <button onClick={handleCreate}>Create Workflow</button>
 *       {workflows.map(w => (
 *         <div key={w.id}>
 *           <h3>{w.name}</h3>
 *           <p>{w.description}</p>
 *         </div>
 *       ))}
 *     </div>
 *   )
 * }
 */
