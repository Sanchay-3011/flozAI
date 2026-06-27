import React, { useState, useEffect, useRef } from 'react';
import { 
  X, Settings, Database, Play, Code, Trash2, Save, Info, ChevronLeft, 
  Link as LinkIcon, AlertTriangle, CheckCircle2, Braces, ChevronDown, ChevronRight,
  Activity, Clock, RotateCcw, Bot
} from 'lucide-react';
import ConditionBuilder from './ConditionBuilder';
import AgentConfigForm from './AgentConfigForm';
import styles from './ConfigPanel.module.css';

// Simple inner JSON viewer
const JsonNode = ({ label, value, defaultExpanded = false }) => {
  const [expanded, setExpanded] = useState(defaultExpanded);
  const isObject = value && typeof value === 'object';
  const isArray = Array.isArray(value);

  if (!isObject) {
    let displayValue = String(value);
    if (typeof value === 'string') displayValue = `"${value}"`;
    return (
      <div className={styles.jsonRow}>
        {label && <span className={styles.jsonKey}>{label}: </span>}
        <span className={typeof value === 'string' ? styles.jsonStr : styles.jsonVal}>{displayValue}</span>
      </div>
    );
  }

  const keys = Object.keys(value);
  if (keys.length === 0) {
    return (
      <div className={styles.jsonRow}>
        {label && <span className={styles.jsonKey}>{label}: </span>}
        <span>{isArray ? '[]' : '{}'}</span>
      </div>
    );
  }

  return (
    <div className={styles.jsonWrapper}>
      <div className={styles.jsonToggle} onClick={(e) => { e.stopPropagation(); setExpanded(!expanded); }}>
        {expanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
        {label && <span className={styles.jsonKey}>{label}: </span>}
        <span className={styles.jsonBracket}>{isArray ? '[' : '{'}</span>
        {!expanded && <span className={styles.jsonCollapsed}>...</span>}
        {!expanded && <span className={styles.jsonBracket}>{isArray ? ']' : '}'}</span>}
      </div>
      {expanded && (
        <div className={styles.jsonChildren}>
          {keys.map((k) => (
            <JsonNode key={k} label={isArray ? null : k} value={value[k]} />
          ))}
        </div>
      )}
      {expanded && <div className={styles.jsonToggle}><span className={styles.jsonBracket}>{isArray ? ']' : '}'}</span></div>}
    </div>
  );
};

export default function ConfigPanel({ node, nodes = [], isOpen, onClose, onDelete, onUpdateNodeData, appData }) {
  const [activeTab, setActiveTab] = useState('settings'); // settings, data, test
  const [showVarPicker, setShowVarPicker] = useState(false);
  const [promptVal, setPromptVal] = useState('');
  const [isTesting, setIsTesting] = useState(false);
  const [testResult, setTestResult] = useState(null);
  const textareaRef = useRef(null);

  const handleConditionsChange = (conditionsData) => {
    // Persist through React state via WorkflowCanvas
    if (node && onUpdateNodeData) {
      onUpdateNodeData(node.id, { conditions: conditionsData });
    }
  };
  
  // Close var picker if clicked outside (simplified)
  useEffect(() => {
    const handler = () => setShowVarPicker(false);
    window.addEventListener('click', handler);
    return () => window.removeEventListener('click', handler);
  }, []);

  if (!isOpen || !node) return null;

  const { data, type } = node;
  const integrationId = data.integration?.toLowerCase() || 'unknown';
  const integrationName = data.displayName || data.integration || 'Step';
  
  // Connection Status
  let connectionStatus = 'none';
  let connectionText = 'No connection required';
  const noAuth = ['scheduler', 'webhook'].includes(integrationId);
  
  if (noAuth) {
    connectionStatus = 'connected';
    connectionText = 'Built-in step';
  } else if (appData?.integrations?.[integrationId]?.status === 'connected') {
    connectionStatus = 'connected';
    connectionText = 'Connected securely';
  } else {
    connectionStatus = 'missing';
    connectionText = 'Setup required';
  }

  // Find previous nodes for variable mapping
  const currentNodeIndex = nodes.findIndex(n => n.id === node.id);
  const previousNodes = currentNodeIndex > 0 ? nodes.slice(0, currentNodeIndex) : [];

  const handleInsertVariable = (varName) => {
    if (!textareaRef.current) return;
    const start = textareaRef.current.selectionStart;
    const end = textareaRef.current.selectionEnd;
    const text = promptVal;
    const before = text.substring(0, start);
    const after = text.substring(end, text.length);
    const newText = before + `{{${varName}}}` + after;
    setPromptVal(newText);
    setShowVarPicker(false);
    
    setTimeout(() => {
      textareaRef.current.focus();
      textareaRef.current.setSelectionRange(start + varName.length + 4, start + varName.length + 4);
    }, 0);
  };

  const runTest = () => {
    setIsTesting(true);
    setTestResult(null);
    setTimeout(() => {
      setIsTesting(false);
      setTestResult({
        status: 'Success',
        output: {
          mock_result: `Execution of ${integrationName} completed.`,
          timestamp: new Date().toISOString()
        }
      });
    }, 1500);
  };

  return (
    <div className={`${styles.panel} ${isOpen ? styles.open : ''}`}>
      {/* Header */}
      <header className={styles.header}>
        <div className={styles.headerLeft}>
          <button className={styles.backBtn} onClick={onClose} title="Go Back">
            <ChevronLeft size={18} />
          </button>
          <div className={styles.headerTitles}>
            <h3>{data.label || 'Untitled Step'}</h3>
            <span className={styles.headerSub}>{integrationName} • {type.toUpperCase()}</span>
          </div>
        </div>
        <div className={styles.headerActions}>
           <div className={`${styles.statusBadge} ${styles[connectionStatus]}`}>
             {connectionStatus === 'connected' && <CheckCircle2 size={12}/>}
             {connectionStatus === 'missing' && <AlertTriangle size={12}/>}
             <span>{connectionStatus === 'connected' ? 'Connected' : connectionStatus === 'missing' ? 'Action Required' : 'Ready'}</span>
           </div>
           <button className={styles.closeBtn} onClick={onClose} title="Close"><X size={18} /></button>
        </div>
      </header>

      {/* Tabs */}
      <div className={styles.tabs}>
        <button className={activeTab === 'settings' ? styles.activeTab : ''} onClick={() => setActiveTab('settings')}>
          <Settings size={14}/> Settings
        </button>
        <button className={activeTab === 'data' ? styles.activeTab : ''} onClick={() => setActiveTab('data')}>
          <Database size={14}/> Data Inspector
        </button>
        <button className={activeTab === 'test' ? styles.activeTab : ''} onClick={() => setActiveTab('test')}>
          <Play size={14}/> Test & Logs
        </button>
      </div>

      <div className={styles.content}>
        
        {activeTab === 'settings' && (
          <div className={styles.tabContent}>
            {/* AI Agent Config — shown instead of generic settings */}
            {data.agent_type ? (
              <AgentConfigForm node={node} onUpdateNodeData={onUpdateNodeData} />
            ) : (
            <>
            {/* Connection Card */}
            <div className={styles.card}>
               <div className={styles.cardHeader}>
                  <LinkIcon size={14} className={styles.cardIcon}/>
                  <span>Integration Connection</span>
               </div>
               <div className={styles.cardBody}>
                  <div className={styles.connectionBlock}>
                    <div className={styles.connDetails}>
                      <span className={styles.connName}>{integrationName}</span>
                      <span className={styles.connStatus}>{connectionText}</span>
                    </div>
                    {connectionStatus === 'missing' && (
                      <button className={styles.connectBtn}>Connect</button>
                    )}
                  </div>
               </div>
            </div>

            {/* Node Settings */}
            <div className={styles.card}>
               <div className={styles.cardHeader}>
                 <Settings size={14} className={styles.cardIcon}/>
                 <span>Node Config</span>
               </div>
               <div className={styles.cardBody}>
                 <div className={styles.configItem}>
                   <label>Action</label>
                   <div className={styles.staticField}>{data.action || 'Default Action'}</div>
                 </div>
                 
                 <div className={styles.configItem}>
                   <label>Prompt / Template</label>
                   <div className={styles.variableInputWrapper}>
                     <textarea 
                       ref={textareaRef}
                       className={styles.input} 
                       placeholder="Enter value or map variables..." 
                       value={promptVal}
                       onChange={(e) => setPromptVal(e.target.value)}
                     />
                     <div className={styles.varPickerContainer}>
                       <button 
                         className={styles.insertVarBtn} 
                         title="Insert Variable"
                         onClick={(e) => { e.stopPropagation(); setShowVarPicker(!showVarPicker); }}
                       >
                         <Braces size={14}/>
                       </button>
                       {showVarPicker && (
                         <div className={styles.varDropdown} onClick={e => e.stopPropagation()}>
                           <div className={styles.varDropdownHeader}>Insert Variable</div>
                           {previousNodes.length === 0 ? (
                             <div className={styles.varItemEmpty}>No prior steps</div>
                           ) : (
                             previousNodes.map(prev => (
                               <div key={prev.id} className={styles.varGroup}>
                                 <div className={styles.varGroupTitle}>{prev.data.displayName || prev.data.integration}</div>
                                 <div className={styles.varItem} onClick={() => handleInsertVariable(`${prev.data.integration || 'node'}.output`)}>• mapped_output</div>
                                 <div className={styles.varItem} onClick={() => handleInsertVariable(`${prev.data.integration || 'node'}.raw`)}>• raw_payload</div>
                               </div>
                             ))
                           )}
                         </div>
                       )}
                     </div>
                   </div>
                 </div>
               </div>
            </div>

            {/* Condition */}
            <ConditionBuilder
              conditions={node?.data?.conditions || []}
              onChange={handleConditionsChange}
            />

            {/* Advanced */}
            <div className={styles.card}>
               <div className={styles.cardHeader}>
                 <Settings size={14} className={styles.cardIcon}/>
                 <span>Advanced Error Handling</span>
               </div>
               <div className={styles.cardBody}>
                  <div className={styles.advancedGrid}>
                    <div className={styles.configItem}>
                      <label>Retry Attempts</label>
                      <input type="number" className={styles.shortInput} defaultValue={0} min={0} max={5}/>
                    </div>
                    <div className={styles.configItem}>
                      <label>Timeout (s)</label>
                      <input type="number" className={styles.shortInput} defaultValue={30} min={5} />
                    </div>
                  </div>
               </div>
            </div>
            </>
            )}
          </div>
        )}

        {activeTab === 'data' && (
          <div className={styles.tabContent}>
             <div className={styles.card}>
               <div className={styles.cardHeader}>
                  <ChevronDown size={14}/> <span>Input Data (Simulated)</span>
               </div>
               <div className={styles.jsonViewerBox}>
                  <JsonNode value={{ example_input: "Testing Data", nested: { a: 1, b: 2 } }} defaultExpanded={true} />
               </div>
             </div>
             <div className={styles.card}>
               <div className={styles.cardHeader}>
                  <ChevronDown size={14}/> <span>Output Data (Mock)</span>
               </div>
               <div className={styles.jsonViewerBox}>
                  <JsonNode value={{ summary: "Mock output for testing." }} defaultExpanded={true} />
               </div>
             </div>
          </div>
        )}

        {activeTab === 'test' && (
          <div className={styles.tabContent}>
             <div className={styles.card}>
                <div className={styles.cardHeader}>
                  <Play size={14} className={styles.cardIcon}/> <span>Test Independent Step</span>
                </div>
                <div className={styles.cardBody}>
                   <p className={styles.testDesc}>Execute this node independently using simulated input data to verify its configuration.</p>
                   <button 
                     className={styles.testBtn} 
                     onClick={runTest}
                     disabled={isTesting}
                   >
                     {isTesting ? <Activity size={14} className="spin" /> : <Play size={14} fill="currentColor"/>} 
                     {isTesting ? 'Running...' : 'Run Test'}
                   </button>

                   {testResult && (
                     <div className={styles.testResultBox}>
                       <div className={styles.testResultHeader}>
                         <span>Result:</span>
                         <span className={styles.testSuccess}><CheckCircle2 size={12}/> {testResult.status}</span>
                       </div>
                       <div className={styles.jsonViewerBoxMock}>
                         <JsonNode value={testResult.output} defaultExpanded={true} />
                       </div>
                     </div>
                   )}
                </div>
             </div>

             <div className={styles.card}>
                <div className={styles.cardHeader}>
                   <Clock size={14} className={styles.cardIcon}/> <span>Execution Logs</span>
                </div>
                <div className={styles.cardBody}>
                   <div className={styles.emptyLog}>No execution history for this node.</div>
                </div>
             </div>
          </div>
        )}

      </div>
      
      {/* Footer */}
      <footer className={styles.footer}>
        <button className={styles.deleteBtn} onClick={() => onDelete(node.id)}>
          <Trash2 size={14} /> Remove Step
        </button>
        <button className={styles.saveBtn} onClick={onClose}>
          <Save size={14} /> Save Changes
        </button>
      </footer>
    </div>
  );
}
