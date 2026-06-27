/**
 * Database Service
 * Frontend JavaScript service for CRUD operations
 * 
 * This service handles data operations for workflows, tasks, and logs
 */

import { supabase } from './supabaseClient'

/**
 * Workflow Operations
 */
export const workflowService = {
  /**
   * Get all workflows for the current user
   * @param {number} limit - Number of results
   * @param {number} offset - Pagination offset
   * @returns {Promise<{data, error, count}>}
   */
  async getAll(limit = 50, offset = 0) {
    try {
      const { data, error, count } = await supabase
        .from('workflows')
        .select('*', { count: 'exact' })
        .order('created_at', { ascending: false })
        .range(offset, offset + limit - 1)

      if (error) throw error

      return { data, error: null, count }
    } catch (error) {
      console.error('Get workflows error:', error)
      return { data: null, error: error.message, count: 0 }
    }
  },

  /**
   * Get a specific workflow by ID
   * @param {string} workflowId - Workflow UUID
   * @returns {Promise<{data, error}>}
   */
  async get(workflowId) {
    try {
      const { data, error } = await supabase
        .from('workflows')
        .select('*')
        .eq('id', workflowId)
        .single()

      if (error) throw error

      return { data, error: null }
    } catch (error) {
      console.error('Get workflow error:', error)
      return { data: null, error: error.message }
    }
  },

  /**
   * Create a new workflow
   * @param {Object} workflow - Workflow data {name, description}
   * @returns {Promise<{data, error}>}
   */
  async create(workflow) {
    try {
      const { data, error } = await supabase
        .from('workflows')
        .insert([workflow])
        .select()
        .single()

      if (error) throw error

      return { data, error: null }
    } catch (error) {
      console.error('Create workflow error:', error)
      return { data: null, error: error.message }
    }
  },

  /**
   * Update a workflow
   * @param {string} workflowId - Workflow UUID
   * @param {Object} updates - Fields to update
   * @returns {Promise<{data, error}>}
   */
  async update(workflowId, updates) {
    try {
      const { data, error } = await supabase
        .from('workflows')
        .update({ ...updates, updated_at: new Date().toISOString() })
        .eq('id', workflowId)
        .select()
        .single()

      if (error) throw error

      return { data, error: null }
    } catch (error) {
      console.error('Update workflow error:', error)
      return { data: null, error: error.message }
    }
  },

  /**
   * Delete a workflow
   * @param {string} workflowId - Workflow UUID
   * @returns {Promise<{error}>}
   */
  async delete(workflowId) {
    try {
      const { error } = await supabase
        .from('workflows')
        .delete()
        .eq('id', workflowId)

      if (error) throw error

      return { error: null }
    } catch (error) {
      console.error('Delete workflow error:', error)
      return { error: error.message }
    }
  }
}

/**
 * Task Operations
 */
export const taskService = {
  /**
   * Get all tasks for a workflow
   * @param {string} workflowId - Workflow UUID
   * @returns {Promise<{data, error}>}
   */
  async getByWorkflow(workflowId) {
    try {
      const { data, error } = await supabase
        .from('tasks')
        .select('*')
        .eq('workflow_id', workflowId)
        .order('order_index', { ascending: true })

      if (error) throw error

      return { data, error: null }
    } catch (error) {
      console.error('Get tasks error:', error)
      return { data: null, error: error.message }
    }
  },

  /**
   * Create a new task
   * @param {Object} task - Task data {workflow_id, step_name, status, order_index}
   * @returns {Promise<{data, error}>}
   */
  async create(task) {
    try {
      const { data, error } = await supabase
        .from('tasks')
        .insert([task])
        .select()
        .single()

      if (error) throw error

      return { data, error: null }
    } catch (error) {
      console.error('Create task error:', error)
      return { data: null, error: error.message }
    }
  },

  /**
   * Update a task
   * @param {string} taskId - Task UUID
   * @param {Object} updates - Fields to update
   * @returns {Promise<{data, error}>}
   */
  async update(taskId, updates) {
    try {
      const { data, error } = await supabase
        .from('tasks')
        .update({ ...updates, updated_at: new Date().toISOString() })
        .eq('id', taskId)
        .select()
        .single()

      if (error) throw error

      return { data, error: null }
    } catch (error) {
      console.error('Update task error:', error)
      return { data: null, error: error.message }
    }
  },

  /**
   * Delete a task
   * @param {string} taskId - Task UUID
   * @returns {Promise<{error}>}
   */
  async delete(taskId) {
    try {
      const { error } = await supabase
        .from('tasks')
        .delete()
        .eq('id', taskId)

      if (error) throw error

      return { error: null }
    } catch (error) {
      console.error('Delete task error:', error)
      return { error: error.message }
    }
  }
}

/**
 * Execution Log Operations
 */
export const logService = {
  /**
   * Get execution logs for a workflow
   * @param {string} workflowId - Workflow UUID
   * @param {number} limit - Number of results
   * @param {number} offset - Pagination offset
   * @returns {Promise<{data, error, count}>}
   */
  async getByWorkflow(workflowId, limit = 100, offset = 0) {
    try {
      const { data, error, count } = await supabase
        .from('logs')
        .select('*', { count: 'exact' })
        .eq('workflow_id', workflowId)
        .order('execution_time', { ascending: false })
        .range(offset, offset + limit - 1)

      if (error) throw error

      return { data, error: null, count }
    } catch (error) {
      console.error('Get logs error:', error)
      return { data: null, error: error.message, count: 0 }
    }
  },

  /**
   * Create a new log entry
   * @param {Object} log - Log data {workflow_id, execution_time, status, output, error_message}
   * @returns {Promise<{data, error}>}
   */
  async create(log) {
    try {
      const { data, error } = await supabase
        .from('logs')
        .insert([log])
        .select()
        .single()

      if (error) throw error

      return { data, error: null }
    } catch (error) {
      console.error('Create log error:', error)
      return { data: null, error: error.message }
    }
  },

  /**
   * Get execution statistics for a workflow
   * @param {string} workflowId - Workflow UUID
   * @returns {Promise<{data, error}>}
   */
  async getStats(workflowId) {
    try {
      const { data, error } = await supabase
        .from('logs')
        .select('status')
        .eq('workflow_id', workflowId)

      if (error) throw error

      if (!data || data.length === 0) {
        return {
          data: {
            total: 0,
            success: 0,
            failed: 0,
            partial: 0,
            successRate: 0
          },
          error: null
        }
      }

      const stats = {
        total: data.length,
        success: data.filter(log => log.status === 'success').length,
        failed: data.filter(log => log.status === 'failure').length,
        partial: data.filter(log => log.status === 'partial').length
      }

      stats.successRate = (stats.success / stats.total * 100).toFixed(2)

      return { data: stats, error: null }
    } catch (error) {
      console.error('Get stats error:', error)
      return { data: null, error: error.message }
    }
  }
}

/**
 * Real-time subscription for workflows
 * @param {string} workflowId - Workflow UUID (optional, subscribe to all if not provided)
 * @param {Function} callback - Callback function for updates
 * @returns {Function} Unsubscribe function
 */
export const subscribeToWorkflows = (workflowId = null, callback) => {
  let query = supabase.from('workflows').on('*', payload => {
    callback(payload)
  })

  if (workflowId) {
    query = query.eq('id', workflowId)
  }

  const subscription = query.subscribe()

  return () => {
    supabase.removeSubscription(subscription)
  }
}

/**
 * Real-time subscription for logs
 * @param {string} workflowId - Workflow UUID
 * @param {Function} callback - Callback function for updates
 * @returns {Function} Unsubscribe function
 */
export const subscribeToLogs = (workflowId, callback) => {
  const subscription = supabase
    .from(`logs:workflow_id=eq.${workflowId}`)
    .on('*', payload => {
      callback(payload)
    })
    .subscribe()

  return () => {
    supabase.removeSubscription(subscription)
  }
}
