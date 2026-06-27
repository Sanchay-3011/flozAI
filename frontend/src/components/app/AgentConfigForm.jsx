import React, { useState, useEffect } from 'react';
import {
  Bot, Zap, Scale, Trophy, Loader2,
  CheckCircle2, AlertCircle, Play,
  Mail, Target, FileText, Search, Brain,
  ChevronDown
} from 'lucide-react';
import { flozApi } from '../../services/api';
import styles from './AgentConfigForm.module.css';

const AGENT_EMOJIS = {
  email_writer: '✉️',
  lead_qualifier: '🎯',
  text_summarizer: '📄',
  data_extractor: '🔍',
  decision_maker: '🧠',
};

const AGENT_COLORS = {
  email_writer: '#818cf8',
  lead_qualifier: '#f472b6',
  text_summarizer: '#34d399',
  data_extractor: '#fbbf24',
  decision_maker: '#a78bfa',
};

const TIER_CONFIG = [
  { id: 'fast', label: 'Fast', emoji: '⚡', desc: 'Quick & affordable', icon: Zap },
  { id: 'balanced', label: 'Balanced', emoji: '⚖️', desc: 'Best of both', icon: Scale },
  { id: 'quality', label: 'High Quality', emoji: '🏆', desc: 'Premium output', icon: Trophy },
];

export default function AgentConfigForm({ node, onUpdateNodeData }) {
  const [agentMeta, setAgentMeta] = useState(null);
  const [inputs, setInputs] = useState({});
  const [tier, setTier] = useState(node?.data?.model_tier || 'fast');
  const [isTesting, setIsTesting] = useState(false);
  const [testResult, setTestResult] = useState(null);
  const agentType = node?.data?.agent_type;

  // Fetch agent metadata
  useEffect(() => {
    if (!agentType) return;
    flozApi.getAgents()
      .then(data => {
        const agent = (data.agents || []).find(a => a.agent_type === agentType);
        if (agent) {
          setAgentMeta(agent);
          // Initialize inputs from existing params
          const existing = node?.data?.params || {};
          const initial = {};
          Object.keys(agent.input_schema).forEach(k => {
            initial[k] = existing[k] || '';
          });
          setInputs(initial);
        }
      })
      .catch(console.error);
  }, [agentType]);

  // Sync tier changes to node
  useEffect(() => {
    if (onUpdateNodeData && node) {
      onUpdateNodeData(node.id, { model_tier: tier });
    }
  }, [tier]);

  const handleInputChange = (field, value) => {
    setInputs(prev => {
      const next = { ...prev, [field]: value };
      // Persist to node data
      if (onUpdateNodeData && node) {
        onUpdateNodeData(node.id, { params: next });
      }
      return next;
    });
  };

  const handleTest = async () => {
    setIsTesting(true);
    setTestResult(null);
    try {
      const data = await flozApi.testAgent(agentType, inputs, null, tier);
      setTestResult(data);
    } catch (err) {
      setTestResult({ status: 'error', error: err.message });
    } finally {
      setIsTesting(false);
    }
  };

  if (!agentMeta) {
    return (
      <div className={styles.loading}>
        <Loader2 size={20} className={styles.spinner} />
        <span>Loading agent configuration...</span>
      </div>
    );
  }

  const color = AGENT_COLORS[agentType] || '#818cf8';

  return (
    <div className={styles.agentForm}>
      {/* Agent Header */}
      <div className={styles.agentHeader} style={{ borderColor: `${color}22` }}>
        <div className={styles.agentIcon} style={{ background: `${color}15`, color }}>
          <span className={styles.emoji}>{AGENT_EMOJIS[agentType]}</span>
        </div>
        <div className={styles.agentHeaderInfo}>
          <h3 className={styles.agentName}>{agentMeta.name}</h3>
          <p className={styles.agentDesc}>{agentMeta.description}</p>
        </div>
      </div>

      {/* Input Fields */}
      <div className={styles.inputSection}>
        <h4 className={styles.sectionTitle}>Configuration</h4>
        {Object.entries(agentMeta.input_schema).map(([field, config]) => (
          <div key={field} className={styles.fieldGroup}>
            <label className={styles.fieldLabel}>
              {config.label}
              {config.required && <span className={styles.required}>*</span>}
            </label>
            {config.type === 'textarea' ? (
              <textarea
                className={styles.textarea}
                value={inputs[field] || ''}
                onChange={e => handleInputChange(field, e.target.value)}
                placeholder={config.placeholder}
                rows={3}
              />
            ) : config.type === 'select' ? (
              <div className={styles.selectWrapper}>
                <select
                  className={styles.select}
                  value={inputs[field] || ''}
                  onChange={e => handleInputChange(field, e.target.value)}
                >
                  <option value="">{config.placeholder || 'Select...'}</option>
                  {(config.options || []).map(opt => (
                    <option key={opt} value={opt}>{opt}</option>
                  ))}
                </select>
                <ChevronDown size={14} className={styles.selectArrow} />
              </div>
            ) : (
              <input
                type="text"
                className={styles.input}
                value={inputs[field] || ''}
                onChange={e => handleInputChange(field, e.target.value)}
                placeholder={config.placeholder}
              />
            )}
          </div>
        ))}
      </div>

      {/* AI Quality Tier */}
      <div className={styles.tierSection}>
        <h4 className={styles.sectionTitle}>Which AI should run this?</h4>
        <div className={styles.tierGrid}>
          {TIER_CONFIG.map(t => (
            <button
              key={t.id}
              className={`${styles.tierCard} ${tier === t.id ? styles.tierActive : ''}`}
              onClick={() => setTier(t.id)}
            >
              <span className={styles.tierEmoji}>{t.emoji}</span>
              <span className={styles.tierLabel}>{t.label}</span>
              <span className={styles.tierDesc}>{t.desc}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Output Preview */}
      <div className={styles.outputSection}>
        <h4 className={styles.sectionTitle}>Expected Output</h4>
        <pre className={styles.outputPreview}>
          {JSON.stringify(agentMeta.output_schema, null, 2)}
        </pre>
      </div>

      {/* Test Button */}
      <button
        className={styles.testBtn}
        onClick={handleTest}
        disabled={isTesting}
      >
        {isTesting ? (
          <><Loader2 size={14} className={styles.spinner} /> Running agent...</>
        ) : (
          <><Play size={14} /> Test this agent</>
        )}
      </button>

      {/* Test Result */}
      {testResult && (
        <div className={`${styles.testResult} ${styles[`result_${testResult.status}`]}`}>
          <div className={styles.testResultHeader}>
            {testResult.status === 'success' ? (
              <><CheckCircle2 size={14} /> Agent ran successfully</>
            ) : (
              <><AlertCircle size={14} /> {testResult.error || 'Agent failed'}</>
            )}
            {testResult.provider && (
              <span className={styles.testProvider}>via {testResult.provider}</span>
            )}
          </div>
          {testResult.output && (
            <pre className={styles.testResultBody}>
              {JSON.stringify(testResult.output, null, 2)}
            </pre>
          )}
        </div>
      )}
    </div>
  );
}
