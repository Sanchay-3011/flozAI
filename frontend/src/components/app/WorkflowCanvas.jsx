import React, { useCallback, useState, useEffect } from 'react';
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  applyNodeChanges,
  applyEdgeChanges,
  addEdge,
  Handle,
  Position,
  MarkerType,
  ReactFlowProvider,
  useReactFlow
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import {
  Plus,
  Zap,
  Settings,
  Trash2,
  Download,
  Play,
  Share2,
  Bot,
  GitBranch,
  Layers,
  Copy,
  Pencil,
  CheckCircle2,
  AlertCircle,
  Loader2,
  Clock,
  ArrowRight,
  Bug,
  Eye,
  History,
  ShieldCheck,
  AlertTriangle,
  Filter
} from 'lucide-react';
import { useWorkflowAnalyzer } from '../../hooks/useWorkflowAnalyzer'
import { flozApi } from '../../services/api';
import dagre from 'dagre';
import ActionPicker from './ActionPicker';
import ConfigPanel from './ConfigPanel';
import VersionHistory from './VersionHistory';
import { BRAND_LOGOS, BRAND_COLORS } from './brandLogos';
import styles from './WorkflowCanvas.module.css';

/* ═══════════════════════════════════════════
   NODE COMPONENTS — Premium glassmorphism design
   ═══════════════════════════════════════════ */

const STATUS_ICONS = {
  idle:    null,
  running: <Loader2 size={14} className={styles.spinIcon} />,
  success: <CheckCircle2 size={14} />,
  error:   <AlertCircle size={14} />,
};

function BaseNode({ children, integration, displayName, label, type, status = 'idle', isDebug, conditions }) {
  const [hovered, setHovered] = useState(false);
  const brandColor = BRAND_COLORS[integration?.toLowerCase()] || 'var(--accent-blue)';

  return (
    <div
      className={`${styles.node} ${styles[`${type}Node`]} ${styles[`status_${status}`]}`}
      style={{ '--brand-color': brandColor }}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
    >
      {/* Gradient top accent */}
      <div className={styles.nodeAccent} />

      <div className={styles.nodeInner}>
        {/* Header: Logo + Integration name */}
        <div className={styles.nodeHeader}>
          <div className={styles.integrationLogo}>
            {BRAND_LOGOS[integration?.toLowerCase()] || <Settings size={24} />}
          </div>
          <div className={styles.headerInfo}>
            <span className={styles.integrationName}>{displayName || integration || 'Integration'}</span>
            <span className={styles.nodeTypeBadge}>
              {type === 'trigger' && <Zap size={10} />}
              {type === 'action' && <ArrowRight size={10} />}
              {type === 'agent' && <Bot size={10} />}
              {type.toUpperCase()}
            </span>
          </div>
        </div>

        {/* Body: Action label */}
        <div className={styles.nodeBody}>
          <span className={styles.nodeLabel}>{label || 'Untitled Step'}</span>
          {isDebug && (
            <div className={styles.debugData}>
              <div className={styles.debugLabel}>INPUT: <span>{`{ id: 123 }`}</span></div>
              <div className={styles.debugLabel}>OUTPUT: <span>{`{ status: "ok" }`}</span></div>
            </div>
          )}
        </div>

        {/* Condition Badges */}
        {conditions && conditions.length > 0 && conditions.some(c => c.enabled && c.field) && (
          <div className={styles.conditionBadges}>
            {conditions.filter(c => c.enabled && c.field).map((cond, i) => (
              <div key={i} className={styles.conditionBadge}>
                <Filter size={10} />
                <span>{cond.natural_language || 'Conditional'}</span>
              </div>
            ))}
          </div>
        )}

        {/* Footer: Status */}
        <div className={styles.nodeFooter}>
          <div className={`${styles.statusIndicator} ${styles[`statusColor_${status}`]}`}>
            {STATUS_ICONS[status]}
            <span>{status === 'idle' ? 'Ready' : status.charAt(0).toUpperCase() + status.slice(1)}</span>
          </div>
          <div className={styles.stepNumber}>Step</div>
        </div>
      </div>

      {/* Hover quick actions */}
      <div className={`${styles.quickActions} ${hovered ? styles.quickActionsVisible : ''}`}>
        <button className={styles.quickBtn} title="Edit"><Pencil size={12} /></button>
        <button className={styles.quickBtn} title="Duplicate"><Copy size={12} /></button>
        <button className={styles.quickBtn} title="Delete"><Trash2 size={12} /></button>
      </div>

      {children}
    </div>
  );
}

function TriggerNode({ data }) {
  return (
    <BaseNode integration={data.integration} displayName={data.displayName} label={data.label} type="trigger" status={data.status} isDebug={data.isDebug} conditions={data.conditions}>
      <Handle type="source" position={Position.Right} className={styles.handle} />
    </BaseNode>
  );
}

function ActionNode({ data }) {
  return (
    <BaseNode integration={data.integration} displayName={data.displayName} label={data.label} type="action" status={data.status} isDebug={data.isDebug} conditions={data.conditions}>
      <Handle type="target" position={Position.Left} className={styles.handle} />
      <Handle type="source" position={Position.Right} className={styles.handle} />
    </BaseNode>
  );
}

function AgentNode({ data }) {
  return (
    <BaseNode integration={data.integration} displayName={data.displayName} label={data.label} type="agent" status={data.status} isDebug={data.isDebug} conditions={data.conditions}>
      <Handle type="target" position={Position.Left} className={styles.handle} />
      <Handle type="source" position={Position.Right} className={styles.handle} />
    </BaseNode>
  );
}

function MergeNode({ data }) {
  return (
    <div className={`${styles.node} ${styles.mergeNode}`}>
      <Handle type="target" position={Position.Left} className={styles.handle} />
      <div className={styles.mergeContent}>
        <div className={styles.mergeDiamond}>
          <Layers size={18} />
        </div>
        <span>Merge</span>
      </div>
      <Handle type="source" position={Position.Right} className={styles.handle} />
    </div>
  );
}

const nodeTypes = { trigger: TriggerNode, action: ActionNode, agent: AgentNode, merge: MergeNode };

/* ═══════════════════════════════════════════
   DAGRE AUTO-LAYOUT — Stable v0.8.5
   ═══════════════════════════════════════════ */

function getLayoutedElements(nodes, edges, direction = 'LR') {
  if (!nodes.length) return { nodes: [], edges: [] };

  const g = new dagre.graphlib.Graph();
  g.setGraph({ rankdir: direction, ranksep: 120, nodesep: 60, marginx: 40, marginy: 40 });
  g.setDefaultEdgeLabel(() => ({}));

  const isH = direction === 'LR';
  nodes.forEach(n => g.setNode(n.id, { width: 260, height: 160 }));
  edges.forEach(e => g.setEdge(e.source, e.target));
  dagre.layout(g);

  return {
    nodes: nodes.map(n => {
      const pos = g.node(n.id);
      return {
        ...n,
        targetPosition: isH ? Position.Left : Position.Top,
        sourcePosition: isH ? Position.Right : Position.Bottom,
        position: { x: (pos?.x ?? 0) - 130, y: (pos?.y ?? 0) - 80 },
      };
    }),
    edges,
  };
}

/* ═══════════════════════════════════════════
   MAIN CANVAS COMPONENT
   ═══════════════════════════════════════════ */

function WorkflowCanvasInner({ workflow, appData, onFixSetup, onNavigate }) {
  const [nodes, setNodes] = useState(workflow?.nodes || []);
  const [edges, setEdges] = useState(workflow?.edges || []);
  const [isDebug, setIsDebug] = useState(false);
  const [isPickerOpen, setIsPickerOpen] = useState(false);
  const [isVersionHistoryOpen, setIsVersionHistoryOpen] = useState(false);
  const [pickerType, setPickerType] = useState('action');
  const [selectedNode, setSelectedNode] = useState(null);
  const [parallax, setParallax] = useState({ x: 0, y: 0 });
  const [edgeHover, setEdgeHover] = useState(null);
  const reactFlowInstance = useReactFlow();

  const missingRequirements = useWorkflowAnalyzer(workflow, appData?.integrations);
  const isReady = missingRequirements.length === 0;

  const onEdgeMouseEnter = useCallback((event, edge) => {
    const sourceNode = nodes.find(n => n.id === edge.source);
    setEdgeHover({
      x: event.clientX,
      y: event.clientY,
      nodeName: sourceNode?.data?.displayName || 'Step',
      payload: `Mock output from ${sourceNode?.data?.displayName || 'prev step'}`
    });
  }, [nodes]);

  const onEdgeMouseLeave = useCallback(() => {
    setEdgeHover(null);
  }, []);

  const handleMouseMove = useCallback((e) => {
    const { clientX, clientY } = e;
    const x = (clientX - window.innerWidth / 2) / 50;
    const y = (clientY - window.innerHeight / 2) / 50;
    setParallax({ x, y });
  }, []);

  const onNodesChange = useCallback(c => {
    setNodes(ns => {
      const next = applyNodeChanges(c, ns);
      if (workflow?.id && appData) {
        const nextSteps = getStepsFromGraph(next, edges);
        appData.updateWorkflow(workflow.id, { nodes: next, steps: nextSteps });
      }
      return next;
    });
  }, [workflow?.id, edges, appData]);

  const onEdgesChange = useCallback(c => {
    setEdges(es => {
      const next = applyEdgeChanges(c, es);
      if (workflow?.id && appData) {
        const nextSteps = getStepsFromGraph(nodes, next);
        appData.updateWorkflow(workflow.id, { edges: next, steps: nextSteps });
      }
      return next;
    });
  }, [workflow?.id, nodes, appData]);

  const onConnect = useCallback(
    p => setEdges(es => {
      const next = addEdge({
        ...p, animated: true,
        markerEnd: { type: MarkerType.ArrowClosed, color: 'rgba(79,168,213,0.6)', width: 20, height: 20 },
        style: { stroke: 'url(#edge-gradient)', strokeWidth: 2 },
      }, es);
      if (workflow?.id && appData) {
        const nextSteps = getStepsFromGraph(nodes, next);
        appData.updateWorkflow(workflow.id, { edges: next, steps: nextSteps });
      }
      return next;
    }),
    [workflow?.id, nodes, appData]
  );

  const onNodeClick = useCallback((event, node) => {
    setSelectedNode(node);
  }, []);

  const deleteNode = useCallback((id) => {
    setNodes(nds => {
      const nextNodes = nds.filter(n => n.id !== id);
      setEdges(eds => {
        const nextEdges = eds.filter(e => e.source !== id && e.target !== id);
        if (workflow?.id && appData) {
          const nextSteps = getStepsFromGraph(nextNodes, nextEdges);
          appData.updateWorkflow(workflow.id, { nodes: nextNodes, edges: nextEdges, steps: nextSteps });
        }
        return nextEdges;
      });
      return nextNodes;
    });
    setSelectedNode(null);
  }, [workflow?.id, appData]);

  const updateNodeData = useCallback((nodeId, newData) => {
    setNodes(nds => {
      const next = nds.map(n => {
        if (n.id === nodeId) {
          return { ...n, data: { ...n.data, ...newData } };
        }
        return n;
      });
      if (workflow?.id && appData) {
        const nextSteps = getStepsFromGraph(next, edges);
        appData.updateWorkflow(workflow.id, { nodes: next, steps: nextSteps });
      }
      return next;
    });
    // Also update selectedNode so ConfigPanel stays in sync
    setSelectedNode(prev => {
      if (prev && prev.id === nodeId) {
        return { ...prev, data: { ...prev.data, ...newData } };
      }
      return prev;
    });
  }, [workflow?.id, edges, appData]);

  const toggleDebug = () => {
    setIsDebug(!isDebug);
    setNodes(nds => nds.map(n => ({
      ...n,
      data: { ...n.data, isDebug: !isDebug }
    })));
  };

  const openPicker = (type = 'action') => {
    setPickerType(type);
    setIsPickerOpen(true);
  };

  const addStep = (integration) => {
    const id = `action-${nodes.length}`;
    const isAgent = integration.isAgent || false;
    
    // Determine label text
    let labelText = `New ${integration.name} Action`;
    if (integration.selectedLabel) labelText = integration.selectedLabel;
    else if (pickerType === 'trigger') labelText = `New ${integration.name} Trigger`;

    const newNode = {
      id,
      type: isAgent ? 'agent' : pickerType,
      data: { 
        label: labelText, 
        integration: integration.id, 
        action: integration.selectedAction,
        displayName: integration.name, 
        status: 'idle',
        isDebug,
        ...(isAgent && {
          agent_type: integration.agent_type,
          model_tier: 'fast',
          input_mapping: {},
        }),
      },
      position: { x: Math.random() * 400, y: Math.random() * 400 },
    };

    setNodes(nds => {
      const nextNodes = [...nds, newNode];
      
      // Optionally connect to last node automatically
      const lastNode = nds[nds.length - 1];
      if (lastNode && pickerType !== 'trigger') {
        setEdges(es => {
          const nextEdges = addEdge({
            source: lastNode.id,
            target: id,
            animated: true,
            markerEnd: { type: MarkerType.ArrowClosed, color: 'rgba(79,168,213,0.5)', width: 16, height: 16 },
            style: { stroke: 'rgba(79,168,213,0.25)', strokeWidth: 2 },
          }, es);
          if (workflow?.id && appData) {
            const nextSteps = getStepsFromGraph(nextNodes, nextEdges);
            appData.updateWorkflow(workflow.id, { nodes: nextNodes, edges: nextEdges, steps: nextSteps });
          }
          return nextEdges;
        });
      } else {
        if (workflow?.id && appData) {
          const nextSteps = getStepsFromGraph(nextNodes, edges);
          appData.updateWorkflow(workflow.id, { nodes: nextNodes, steps: nextSteps });
        }
      }
      return nextNodes;
    });
  };

  // Build React Flow state from workflow.steps OR load from existing nodes
  useEffect(() => {
    if (workflow?.nodes && workflow.nodes.length > 0) {
      setNodes(workflow.nodes);
      setEdges(workflow.edges || []);
      setTimeout(() => {
        reactFlowInstance.fitView({ padding: 0.25, duration: 600 });
      }, 200);
      return;
    }

    if (!workflow?.steps || !Array.isArray(workflow.steps) || workflow.steps.length === 0) return;
    
    // Extremely safe string formatter
    const fmt = (str) => {
      if (typeof str !== 'string') return 'Step';
      return str.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    };

    const rfNodes = [];
    const rfEdges = [];
    const safeSteps = Array.isArray(workflow.steps) ? workflow.steps : [];
    const triggers = safeSteps.filter(s => s && s.type === 'TRIGGER');
    const actions  = safeSteps.filter(s => s && s.type !== 'TRIGGER');

    // Triggers
    triggers.forEach((t, i) => {
      rfNodes.push({
        id: `trigger-${i}`, type: 'trigger',
        data: { label: fmt(t.action || t.type), integration: t.integration, displayName: t.displayName || fmt(t.integration), status: 'idle' },
        position: { x: 0, y: 0 },
      });
    });

    // Multi-trigger merge
    let entry = triggers.length === 1 ? 'trigger-0' : null;
    if (triggers.length > 1) {
      entry = 'merge';
      rfNodes.push({ id: 'merge', type: 'merge', data: { label: 'Merge' }, position: { x: 0, y: 0 } });
      triggers.forEach((_, i) => {
        rfEdges.push({
          id: `e-t${i}-merge`, source: `trigger-${i}`, target: 'merge', animated: true,
          markerEnd: { type: MarkerType.ArrowClosed, color: 'rgba(79,168,213,0.5)', width: 16, height: 16 },
          style: { stroke: 'rgba(79,168,213,0.25)', strokeWidth: 2 },
        });
      });
    }

    // Actions
    let prev = entry;
    actions.forEach((a, i) => {
      const id = `action-${i}`;
      // Safe checks
      const typeStr = typeof a.type === 'string' ? a.type : '';
      const intStr = typeof a.integration === 'string' ? a.integration.toLowerCase() : '';
      const actStr = typeof a.action === 'string' ? a.action.toLowerCase() : '';
      
      const isAgent = typeStr === 'ai_agent' || typeStr === 'agent' || intStr === 'openai' || actStr.includes('generate');
      
      const nodeData = { 
        label: fmt(a.action || a.agent_type || a.type), 
        integration: a.integration || a.provider || 'ai', 
        action: a.action || 'default', 
        displayName: a.displayName || (isAgent ? 'AI Agent' : fmt(a.integration)), 
        status: 'idle',
        ...(isAgent && {
          agent_type: typeof a.agent_type === 'string' ? a.agent_type : (actStr.includes('email') ? 'email_writer' : 'decision_maker'),
          model_tier: typeof a.model_tier === 'string' ? a.model_tier : 'fast',
          input_mapping: a.input_mapping || {}
        })
      };

      rfNodes.push({
        id, type: isAgent ? 'agent' : 'action',
        data: nodeData,
        position: { x: 0, y: 0 },
      });
      if (prev) {
        rfEdges.push({
          id: `e-${prev}-${id}`, source: prev, target: id, animated: true,
          markerEnd: { type: MarkerType.ArrowClosed, color: 'rgba(79,168,213,0.5)', width: 16, height: 16 },
          style: { stroke: 'rgba(79,168,213,0.25)', strokeWidth: 2 },
        });
      }
      prev = id;
    });

    const laid = getLayoutedElements(rfNodes, rfEdges);
    const finalNodes = laid.nodes.map(n => ({ ...n, data: { ...n.data, isDebug } }));
    const finalEdges = laid.edges;

    setNodes(finalNodes);
    setEdges(finalEdges);

    if (workflow?.id && appData) {
      appData.updateWorkflow(workflow.id, { nodes: finalNodes, edges: finalEdges });
    }

    // FitView after React has rendered the new nodes
    setTimeout(() => {
      reactFlowInstance.fitView({ padding: 0.25, duration: 600 });
    }, 200);
  }, [workflow, reactFlowInstance]);

  // Keyboard Shortcuts
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Delete' || e.key === 'Backspace') {
        if (selectedNode && !['input', 'textarea'].includes(document.activeElement.tagName.toLowerCase())) {
          deleteNode(selectedNode.id);
        }
      }
      if (e.key === 'Escape') {
        setSelectedNode(null);
        setIsPickerOpen(false);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [selectedNode, deleteNode]);

  const handleDownload = () => {
    const data = {
      nodes: reactFlowInstance.getNodes(),
      edges: reactFlowInstance.getEdges(),
      workflow_name: workflow?.name || 'Untitled'
    };
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${workflow?.name || 'workflow'}_export.json`;
    link.click();
  };

  const summary = workflow?.explanation || (workflow?.name ? `Workflow: ${workflow.name}` : '');

  const handleActivate = async () => {
    if (!workflow?.id || !appData) return;
    
    if (!isReady) {
      if (onFixSetup) {
        onFixSetup(missingRequirements);
      } else {
        alert(`Cannot activate. Please connect missing integrations: ${missingRequirements.map(r => r.name).join(', ')}`);
      }
      return;
    }
    
    // Start real execution
    appData.logActivity({
      type: 'workflow_triggered',
      title: workflow.name,
      detail: `Triggered by: Manual Activation`
    });

    const latestSteps = getStepsFromGraph(nodes, edges);
    const executionWorkflow = {
      ...workflow,
      nodes,
      edges,
      steps: latestSteps
    };

    setNodes(ns => ns.map(n => ({ ...n, data: { ...n.data, status: 'running' } })));
    appData.updateWorkflow(workflow.id, { status: 'Running', nodes, edges, steps: latestSteps });

    try {
      const result = await flozApi.executeWorkflow(executionWorkflow);
      
      if (result.status === 'completed') {
        appData.logActivity({
          type: 'workflow_completed',
          title: workflow.name,
          detail: `Execution completed. ${result.steps?.length || 0} steps processed.`
        });
        setNodes(ns => ns.map(n => ({ ...n, data: { ...n.data, status: 'success' } })));
        
        const newHistory = [...(workflow.executionHistory || []), {
          status: 'success',
          execution_id: result.execution_id,
          timestamp: new Date().toISOString()
        }];
        appData.updateWorkflow(workflow.id, { 
          status: 'Active', 
          lastRun: new Date().toISOString(),
          executionHistory: newHistory
        });
      } else {
        // Failed execution
        const failedStep = result.steps?.find(s => s.status === 'error');
        const errorMsg = failedStep?.error || 'Unknown error';
        
        appData.logActivity({
          type: 'workflow_error',
          title: workflow.name,
          detail: `Execution failed at ${failedStep?.integration || 'unknown'}: ${errorMsg}`
        });
        
        setNodes(ns => ns.map((n, idx) => {
          const stepResult = result.steps?.[idx];
          return {
            ...n,
            data: {
              ...n.data,
              status: stepResult?.status === 'error' ? 'error' : stepResult?.status === 'success' ? 'success' : 'idle'
            }
          };
        }));
        
        const newHistory = [...(workflow.executionHistory || []), {
          status: 'error',
          error: errorMsg,
          timestamp: new Date().toISOString()
        }];
        appData.updateWorkflow(workflow.id, { 
          status: 'Active', 
          lastRun: new Date().toISOString(),
          executionHistory: newHistory
        });
      }
    } catch (err) {
      appData.logActivity({
        type: 'workflow_error',
        title: workflow.name,
        detail: `Execution request failed: ${err.message}`
      });
      setNodes(ns => ns.map(n => ({ ...n, data: { ...n.data, status: 'error' } })));
      appData.updateWorkflow(workflow.id, { status: 'Active' });
    }
    
    // Reset node status after a delay
    setTimeout(() => {
      setNodes(ns => ns.map(n => ({ ...n, data: { ...n.data, status: 'idle' } })));
    }, 5000);
  };

  return (
    <div className={styles.canvasContainer}>
      {/* Header */}
      <header className={styles.canvasHeader}>
        <div className={styles.headerLeft}>
          <h3 className={styles.workflowTitle}>{workflow?.name || 'Untitled Workflow'}</h3>
          <div className={styles.statusBadge}>
            <span className="status-dot" style={{ background: workflow?.status === 'Running' || workflow?.status === 'Active' ? '#10b981' : '#fcd34d' }}/>
            <span>{workflow?.status || 'Draft'}</span>
          </div>
          
          {/* Readiness Badge */}
          <div className={`${styles.readinessBadge} ${isReady ? styles.ready : styles.notReady}`}>
            {isReady ? <ShieldCheck size={12} className={styles.shieldIcon} /> : <AlertTriangle size={12} className={styles.alertIcon} />}
            <span>{isReady ? 'Ready to Run' : 'Setup Required'}</span>
            {!isReady && onFixSetup && (
              <button 
                className={styles.fixSetupBtn}
                onClick={() => onFixSetup(missingRequirements)}
              >
                Fix Setup
              </button>
            )}
          </div>
          
          {nodes.length > 0 && <span className={styles.nodeCount}>{nodes.length} steps</span>}
        </div>
        <div className={styles.headerActions}>
          <button className={`${styles.iconBtn} ${isDebug ? styles.activeBtn : ''}`} title="Debug Mode" onClick={toggleDebug}>
            <Bug size={16} />
          </button>
          <button 
            className={`${styles.iconBtn} ${isVersionHistoryOpen ? styles.activeBtn : ''}`} 
            title="Version History"
            onClick={() => setIsVersionHistoryOpen(!isVersionHistoryOpen)}
          >
            <History size={16} />
          </button>
          <button className={styles.iconBtn} title="Download" onClick={handleDownload}><Download size={16} /></button>
          <button 
            className={`${styles.activateBtn} ${!isReady ? styles.disabledActivate : ''}`} 
            onClick={handleActivate}
            disabled={!isReady}
          >
            <Play size={13} fill="currentColor" /> Activate
          </button>
        </div>
      </header>

      {/* Summary bar */}
      {summary && (
        <div className={styles.summaryBar}>
          <Bot size={14} className={styles.summaryIcon} />
          <span>{summary}</span>
        </div>
      )}

      {/* Canvas */}
      <div className={styles.flowWrapper} onMouseMove={handleMouseMove}>
        {/* SVG gradient def for edges */}
        <svg width="0" height="0" style={{ position: 'absolute' }}>
          <defs>
            <linearGradient id="edge-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="rgba(79,168,213,0.4)" />
              <stop offset="100%" stopColor="rgba(139,111,203,0.4)" />
            </linearGradient>
          </defs>
        </svg>

        <div 
          className={styles.parallaxContainer}
          style={{ transform: `translate(${parallax.x}px, ${parallax.y}px)` }}
        >
          <Background color="rgba(79,168,213,0.04)" gap={24} size={1.5} />
        </div>

        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onNodeClick={onNodeClick}
          onEdgeMouseEnter={onEdgeMouseEnter}
          onEdgeMouseLeave={onEdgeMouseLeave}
          nodeTypes={nodeTypes}
          fitView
          fitViewOptions={{ padding: 0.25 }}
          snapToGrid
          snapGrid={[20, 20]}
          minZoom={0.3}
          maxZoom={2}
          defaultEdgeOptions={{ animated: true }}
        >
          <Background color="rgba(79,168,213,0.04)" gap={24} size={1.5} />
          <Controls className={styles.controls} showInteractive={false} />
          <MiniMap
            className={styles.minimap}
            nodeColor={n => {
              if (n.type === 'trigger') return 'rgba(79,168,213,0.6)';
              if (n.type === 'agent')   return 'rgba(34,211,238,0.6)';
              if (n.type === 'merge')   return 'rgba(79,168,213,0.3)';
              return 'rgba(139,111,203,0.6)';
            }}
            maskColor="rgba(3,5,8,0.85)"
            style={{ background: 'rgba(10,12,18,0.9)' }}
          />
        </ReactFlow>

        {/* Edge Data Preview Tooltip */}
        {edgeHover && (
          <div 
            className={styles.edgeTooltip} 
            style={{ left: edgeHover.x + 15, top: edgeHover.y + 15 }}
          >
            <div className={styles.edgeTooltipHeader}>
              <span>Data Preview</span>
              <span className={styles.edgeTooltipSource}>from {edgeHover.nodeName}</span>
            </div>
            <div className={styles.edgeTooltipBody}>
              <pre>{`{\n  "payload": "${edgeHover.payload}"\n}`}</pre>
            </div>
          </div>
        )}

        {/* Floating toolbar */}
        <div className={styles.floatingControls}>
          <button className={styles.addBtn} onClick={() => openPicker('action')}><Plus size={14} /> Add Action</button>
          <button className={styles.addBtn} onClick={() => {
            // Open condition on the last action node
            const actionNodes = nodes.filter(n => n.type === 'action' || n.type === 'agent');
            const target = selectedNode || (actionNodes.length > 0 ? actionNodes[actionNodes.length - 1] : null);
            if (target) {
              setSelectedNode(target);
            } else {
              openPicker('action');
            }
          }}><Filter size={14} /> Add Condition</button>
          <button className={styles.addBtn} onClick={() => openPicker('agent')}><Bot size={14} /> Add AI Agent</button>
        </div>

        {/* Action Picker Modal */}
        <ActionPicker 
          isOpen={isPickerOpen} 
          onClose={() => setIsPickerOpen(false)} 
          onSelect={addStep}
          onNavigate={onNavigate}
          type={pickerType}
        />

        {/* Config Panel Drawer */}
        <ConfigPanel 
          node={selectedNode}
          nodes={nodes}
          isOpen={!!selectedNode}
          onClose={() => setSelectedNode(null)}
          onDelete={deleteNode}
          onUpdateNodeData={updateNodeData}
          appData={appData}
        />

        {/* Version History Panel */}
        <VersionHistory 
          isOpen={isVersionHistoryOpen}
          onClose={() => setIsVersionHistoryOpen(false)}
          onRestore={(v) => console.log('Restoring', v)}
        />
      </div>
    </div>
  );
}

export default function WorkflowCanvas(props) {
  return (
    <ReactFlowProvider>
      <WorkflowCanvasInner {...props} />
    </ReactFlowProvider>
  );
}

/* ═══════════════════════════════════════════
   HELPERS
   ═══════════════════════════════════════════ */
function fmt(raw) {
  if (!raw) return 'Untitled';
  return raw.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
}

function getStepsFromGraph(nodes, edges) {
  const adj = {};
  const inDegree = {};
  const nodeMap = {};

  nodes.forEach(n => {
    nodeMap[n.id] = n;
    adj[n.id] = [];
    inDegree[n.id] = 0;
  });

  edges.forEach(e => {
    if (adj[e.source] && adj[e.target] !== undefined) {
      adj[e.source].push(e.target);
      inDegree[e.target]++;
    }
  });

  const queue = [];
  nodes.forEach(n => {
    if (inDegree[n.id] === 0) {
      if (n.type === 'trigger') {
        queue.unshift(n.id);
      } else {
        queue.push(n.id);
      }
    }
  });

  const visited = new Set();
  const sortedIds = [];

  while (queue.length > 0) {
    queue.sort((a, b) => {
      const na = nodeMap[a];
      const nb = nodeMap[b];
      if (na.type === 'trigger' && nb.type !== 'trigger') return -1;
      if (na.type !== 'trigger' && nb.type === 'trigger') return 1;
      return 0;
    });

    const curr = queue.shift();
    if (visited.has(curr)) continue;
    visited.add(curr);
    sortedIds.push(curr);

    (adj[curr] || []).forEach(neighbor => {
      inDegree[neighbor]--;
      if (inDegree[neighbor] === 0) {
        queue.push(neighbor);
      } else if (inDegree[neighbor] < 0) {
        if (!visited.has(neighbor)) {
          queue.push(neighbor);
        }
      }
    });
  }

  nodes.forEach(n => {
    if (!visited.has(n.id)) {
      sortedIds.push(n.id);
    }
  });

  const steps = [];
  sortedIds.forEach(id => {
    const node = nodeMap[id];
    if (!node) return;
    if (node.type === 'merge') return;

    let stepType = 'ACTION';
    if (node.type === 'trigger') {
      stepType = 'TRIGGER';
    } else if (node.type === 'agent') {
      stepType = 'AI_AGENT';
    }

    const data = node.data || {};
    steps.push({
      integration: data.integration || '',
      displayName: data.displayName || data.integration || '',
      action: data.action || '',
      type: stepType,
      params: data.params || {},
      conditions: data.conditions || [],
      agent_type: data.agent_type,
      model_tier: data.model_tier,
      input_mapping: data.input_mapping,
      provider: data.provider,
    });
  });

  return steps;
}
