import { useState, useEffect } from 'react';
import { supabase } from '../services/supabaseClient';
import { workflowService } from '../services/databaseService';
import { flozApi } from '../services/api';

const STORAGE_KEYS = {
  ACTIVITY_LOGS: 'flozai_activity_logs'
};

export function useAppData() {
  const [workflows, setWorkflows] = useState([]);
  const [activityLogs, setActivityLogs] = useState([]);
  const [integrations, setIntegrations] = useState({});
  const [session, setSession] = useState(null);

  // Sync auth session changes
  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session: activeSession } }) => {
      setSession(activeSession);
    });

    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, activeSession) => {
      setSession(activeSession);
    });

    return () => subscription.unsubscribe();
  }, []);

  // Fetch initial workflows and integrations when session changes
  useEffect(() => {
    const fetchData = async () => {
      if (!session) {
        setWorkflows([]);
        setIntegrations({});
        return;
      }

      try {
        const storedLogs = localStorage.getItem(STORAGE_KEYS.ACTIVITY_LOGS);
        if (storedLogs) setActivityLogs(JSON.parse(storedLogs));

        // 1. Fetch workflows from Supabase DB
        const { data: wfData, error: wfError } = await workflowService.getAll();
        if (!wfError && wfData) {
          const formatted = wfData.map(item => ({
            id: item.id,
            name: item.name,
            explanation: item.description,
            nodes: item.nodes || [],
            edges: item.edges || [],
            steps: item.steps || [],
            status: item.status || 'Active',
            createdAt: item.created_at,
            lastRun: item.updated_at,
            executionHistory: item.executionHistory || []
          }));
          setWorkflows(formatted);
        }

        // 2. Fetch integrations from backend via relative path proxy
        const backendIntegrations = await flozApi.getIntegrations();
        if (backendIntegrations) {
          setIntegrations(backendIntegrations);
        }
      } catch (e) {
        console.error('Failed to load user cloud data:', e);
      }
    };
    fetchData();
  }, [session]);

  // Sync activity logs to localStorage
  useEffect(() => {
    localStorage.setItem(STORAGE_KEYS.ACTIVITY_LOGS, JSON.stringify(activityLogs));
  }, [activityLogs]);

  const addWorkflow = async (workflow) => {
    try {
      const { data: { session: currentSession } } = await supabase.auth.getSession();
      
      const { data, error } = await workflowService.create({
        user_id: currentSession?.user?.id,
        name: workflow.name || 'Generated Workflow',
        description: workflow.explanation || '',
        nodes: workflow.nodes || workflow.steps || [],
        edges: workflow.edges || [],
        steps: workflow.steps || []
      });

      if (error) throw new Error(error);

      const savedWorkflow = {
        ...workflow,
        id: data.id,
        status: 'Active',
        createdAt: data.created_at,
        lastRun: data.updated_at,
        executionHistory: data.executionHistory || []
      };

      setWorkflows(prev => [savedWorkflow, ...prev]);

      logActivity({
        type: 'workflow_created',
        title: 'Workflow Created',
        detail: `Created "${savedWorkflow.name}"`
      });

      return savedWorkflow;
    } catch (e) {
      console.error('Failed to create workflow:', e);
      throw e;
    }
  };

  const updateWorkflow = async (id, updates) => {
    // Update local state optimistically
    setWorkflows(prev => prev.map(wf => 
      wf.id === id ? { ...wf, ...updates } : wf
    ));

    try {
      const { error } = await workflowService.update(id, updates);
      if (error) throw new Error(error);
    } catch (e) {
      console.error('Failed to update workflow on Supabase:', e);
    }
  };

  const deleteWorkflow = async (id) => {
    const wf = workflows.find(w => w.id === id);
    setWorkflows(prev => prev.filter(w => w.id !== id));
    
    try {
      const { error } = await workflowService.delete(id);
      if (error) throw new Error(error);
      
      if (wf) {
        logActivity({
          type: 'workflow_deleted',
          title: 'Workflow Deleted',
          detail: `Deleted "${wf.name}"`
        });
      }
    } catch (e) {
      console.error('Failed to delete workflow from Supabase:', e);
    }
  };

  const logActivity = (event) => {
    const newEvent = {
      ...event,
      id: Date.now().toString() + Math.random().toString(),
      timestamp: new Date().toISOString()
    };
    setActivityLogs(prev => [newEvent, ...prev].slice(0, 50));
  };

  const saveIntegration = async (type, data) => {
    const integrationObj = {
      ...data,
      connectedAt: new Date().toISOString(),
      status: 'connected'
    };
    
    const previousIntegrations = { ...integrations };
    setIntegrations(prev => ({
      ...prev,
      [type]: integrationObj
    }));

    try {
      await flozApi.saveIntegration(type, data);
    } catch (e) {
      setIntegrations(previousIntegrations);
      throw e;
    }
    
    logActivity({
      type: 'integration_connected',
      title: 'Integration Connected',
      detail: `Connected to ${type}`
    });
  };

  const removeIntegration = async (type) => {
    setIntegrations(prev => {
      const next = { ...prev };
      delete next[type];
      return next;
    });

    try {
      await flozApi.deleteIntegration(type);
    } catch (e) {
      console.error('Failed to remove integration from backend', e);
    }

    logActivity({
      type: 'integration_disconnected',
      title: 'Integration Disconnected',
      detail: `Disconnected from ${type}`
    });
  };

  // Compute metrics
  const activeWorkflowsCount = workflows.filter(w => w.status === 'Active' || w.status === 'Running').length;
  
  const today = new Date().setHours(0, 0, 0, 0);
  let executionsTodayCount = 0;
  let successCount = 0;
  let totalExecutions = 0;
  let errors24h = 0;
  const yesterday = new Date(Date.now() - 24 * 60 * 60 * 1000);

  workflows.forEach(wf => {
    if (wf.executionHistory) {
      wf.executionHistory.forEach(exec => {
        totalExecutions++;
        const execDate = new Date(exec.timestamp);
        if (execDate.getTime() >= today) {
          executionsTodayCount++;
        }
        if (exec.status === 'success') {
          successCount++;
        } else if (exec.status === 'error' && execDate.getTime() >= yesterday.getTime()) {
          errors24h++;
        }
      });
    }
  });

  const successRate = totalExecutions > 0 
    ? Math.round((successCount / totalExecutions) * 100) 
    : 0;

  const metrics = {
    activeWorkflows: activeWorkflowsCount,
    executionsToday: executionsTodayCount,
    successRate,
    errors24h
  };

  return {
    workflows,
    activityLogs,
    integrations,
    metrics,
    addWorkflow,
    updateWorkflow,
    deleteWorkflow,
    logActivity,
    saveIntegration,
    removeIntegration
  };
}
