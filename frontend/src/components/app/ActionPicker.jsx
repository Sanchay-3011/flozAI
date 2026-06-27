import React, { useState, useEffect, useMemo } from 'react';
import { 
  X, Search, Zap, Bot, ArrowRight, Settings, Info, Loader2,
  Star, Database, MessageCircle, Megaphone, CheckSquare,
  Headphones, DollarSign, Sparkles, Share2, Calendar, Terminal, Network,
  Mail, Target, FileText, Brain, AlertTriangle
} from 'lucide-react';
import { BRAND_LOGOS } from './brandLogos';
import { flozApi } from '../../services/api';
import styles from './ActionPicker.module.css';

const CATEGORY_MAP = {
  "All Apps": { icon: Network, ids: [] },
  "Favorites": { icon: Star, ids: ["slack", "google_sheets", "hubspot", "notion", "airtable"] },
  "CRM": { icon: Database, ids: ["hubspot", "salesforce", "crm"] },
  "Messaging": { icon: MessageCircle, ids: ["slack", "whatsapp"] },
  "Marketing": { icon: Megaphone, ids: ["mailchimp"] },
  "Productivity": { icon: CheckSquare, ids: ["notion", "airtable", "google_sheets", "google_forms", "typeform"] },
  "Support": { icon: Headphones, ids: ["zendesk", "intercom", "jira"] },
  "Finance": { icon: DollarSign, ids: ["stripe", "quickbooks"] },
  "AI": { icon: Sparkles, ids: ["openai", "perplexity"] },
  "Social": { icon: Share2, ids: ["linkedin", "twitter", "instagram"] },
  "Scheduling": { icon: Calendar, ids: ["calendly", "google_calendar", "scheduler"] },
  "Developer": { icon: Terminal, ids: ["webhook"] }
};

export default function ActionPicker({ isOpen, onClose, onSelect, onNavigate, type = 'action' }) {
  const [search, setSearch] = useState('');
  const [activeCategory, setActiveCategory] = useState('All Apps');
  
  const [capabilities, setCapabilities] = useState({ integrations: [], actions: [], triggers: [] });
  const [loading, setLoading] = useState(true);

  // Agent mode state
  const [agents, setAgents] = useState([]);
  const [aiConnected, setAiConnected] = useState(false);

  // For when an integration is clicked to select specific action/trigger
  const [selectedIntegration, setSelectedIntegration] = useState(null);

  const AGENT_ICONS = {
    mail: <Mail size={24} />,
    target: <Target size={24} />,
    'file-text': <FileText size={24} />,
    search: <Search size={24} />,
    brain: <Brain size={24} />,
  };

  const AGENT_COLORS = {
    email_writer: '#818cf8',
    lead_qualifier: '#f472b6',
    text_summarizer: '#34d399',
    data_extractor: '#fbbf24',
    decision_maker: '#a78bfa',
  };

  const AGENT_EMOJIS = {
    email_writer: '✉️',
    lead_qualifier: '🎯',
    text_summarizer: '📄',
    data_extractor: '🔍',
    decision_maker: '🧠',
  };

  useEffect(() => {
    if (isOpen) {
      setSearch('');
      setActiveCategory('All Apps');
      setSelectedIntegration(null);
      
      if (type === 'agent') {
        // Load agents + check if AI is connected
        setLoading(true);
        Promise.all([
          flozApi.getAgents(),
          flozApi.getAiProviders(),
        ]).then(([agentData, providerData]) => {
          setAgents(agentData.agents || []);
          const connected = (providerData.providers || []).some(p => p.connected);
          setAiConnected(connected);
          setLoading(false);
        }).catch(() => setLoading(false));
      } else {
        // Load integrations
        flozApi.getCapabilities()
          .then(data => {
            setCapabilities(data);
            setLoading(false);
          })
          .catch(err => {
            console.error("Failed to fetch integrations", err);
            setLoading(false);
          });
      }
    }
  }, [isOpen, type]);

  // Derived filtered integrations based on context type (trigger vs action)
  const availableIntegrations = useMemo(() => {
    return capabilities.integrations.filter(integ => {
      if (type === 'trigger') return integ.supported_triggers && integ.supported_triggers.length > 0;
      if (type === 'action') return integ.supported_actions && integ.supported_actions.length > 0;
      return true; // For agent or others
    });
  }, [capabilities, type]);

  // Apply search and category filters
  const filteredIntegrations = useMemo(() => {
    let result = availableIntegrations;
    
    // Search overrides category filter if active
    if (search.trim()) {
      result = result.filter(i => 
        i.name.toLowerCase().includes(search.toLowerCase()) ||
        i.id.toLowerCase().includes(search.toLowerCase())
      );
    } else {
      // Apply category filter if no search
      if (activeCategory !== 'All Apps') {
        const catIds = CATEGORY_MAP[activeCategory].ids;
        result = result.filter(i => catIds.includes(i.id));
      }
    }
    
    return result;
  }, [availableIntegrations, search, activeCategory]);


  if (!isOpen) return null;

  // Render specific child items (actions/triggers) when an integration is selected
  const renderItemSelector = () => {
    const items = type === 'trigger' 
      ? capabilities.triggers.filter(t => selectedIntegration.supported_triggers?.includes(t.id))
      : capabilities.actions.filter(a => selectedIntegration.supported_actions?.includes(a.id));

    return (
      <div className={styles.subSelector}>
        <div className={styles.subSelectorHeader}>
          <button 
            className={styles.backBtn} 
            onClick={() => setSelectedIntegration(null)}
          >
            &larr; Back
          </button>
          <div className={styles.subIntegrationInfo}>
            <div className={styles.subIntegrationLogoWrapper}>
              {BRAND_LOGOS[selectedIntegration.id] || <span className={styles.placeholderLogo}>{selectedIntegration.name.charAt(0)}</span>}
            </div>
            <h4>{selectedIntegration.name} {type === 'trigger' ? 'Triggers' : 'Actions'}</h4>
          </div>
        </div>
        <div className={styles.itemList}>
          {items.map(item => (
            <button
              key={item.id}
              className={styles.actionItem}
              onClick={() => {
                onSelect({ ...selectedIntegration, selectedAction: item.id, selectedLabel: item.name });
                onClose();
              }}
            >
              <div className={styles.actionItemTokens}>
                <span className={styles.actionItemName}>{item.name}</span>
                <span className={styles.actionItemDesc}>{item.description}</span>
              </div>
              <ArrowRight size={16} className={styles.actionArrow} />
            </button>
          ))}
          {items.length === 0 && (
             <div className={styles.noResults}>
               <p>No {type}s available for this integration.</p>
             </div>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className={styles.overlay} onClick={onClose} onKeyDown={e => e.key === 'Escape' && onClose()}>
      <div className={styles.modal} onClick={e => e.stopPropagation()}>
        
        <header className={styles.header}>
          <div className={styles.titleArea}>
            <div className={`${styles.typeIcon} ${styles[type]}`}>
              {type === 'trigger' && <Zap size={16} />}
              {type === 'agent' && <Bot size={16} />}
              {type === 'action' && <ArrowRight size={16} />}
            </div>
            <div>
              <h3>Add {type.charAt(0).toUpperCase() + type.slice(1)}</h3>
              <p>Select an integration from the library</p>
            </div>
          </div>
          <button className={styles.closeBtn} onClick={onClose}><X size={20} /></button>
        </header>

        {/* ═══ AGENT MODE ═══ */}
        {type === 'agent' ? (
          <div className={styles.agentBody}>
            {loading ? (
              <div className={styles.loadingState}>
                <Loader2 size={32} className={styles.spinner} />
                <p>Loading AI agents...</p>
              </div>
            ) : !aiConnected ? (
              <div className={styles.aiNotConnected}>
                <div className={styles.aiNotConnectedIcon}>
                  <AlertTriangle size={40} />
                </div>
                <h3>Connect an AI Provider</h3>
                <p>To use AI agents in your workflows, connect at least one AI provider (OpenAI, Groq, Claude, or Gemini).</p>
                <button className={styles.goToSettingsBtn} onClick={() => { onClose(); onNavigate && onNavigate('settings'); }}>
                  <Sparkles size={16} /> Go to AI Settings
                </button>
              </div>
            ) : (
              <>
                <div className={styles.agentGridHeader}>
                  <Bot size={18} />
                  <span>Choose a smart agent for your workflow</span>
                </div>
                <div className={styles.agentGrid}>
                  {agents.map(agent => (
                    <button
                      key={agent.agent_type}
                      className={styles.agentCard}
                      onClick={() => {
                        onSelect({
                          id: `ai_${agent.agent_type}`,
                          name: agent.name,
                          agent_type: agent.agent_type,
                          selectedAction: agent.agent_type,
                          selectedLabel: agent.name,
                          isAgent: true,
                        });
                        onClose();
                      }}
                    >
                      <div className={styles.agentCardIcon} style={{ background: `${AGENT_COLORS[agent.agent_type]}15`, color: AGENT_COLORS[agent.agent_type] }}>
                        <span className={styles.agentEmoji}>{AGENT_EMOJIS[agent.agent_type]}</span>
                      </div>
                      <div className={styles.agentCardInfo}>
                        <span className={styles.agentCardName}>{agent.name}</span>
                        <span className={styles.agentCardDesc}>{agent.description}</span>
                      </div>
                      <ArrowRight size={16} className={styles.agentCardArrow} />
                    </button>
                  ))}
                </div>
              </>
            )}
          </div>
        ) : (
        /* ═══ ORIGINAL INTEGRATION MODE ═══ */
        <>
        <div className={styles.searchArea}>
          <Search size={18} className={styles.searchIcon} />
          <input 
            autoFocus
            type="text" 
            placeholder={`Search ${availableIntegrations.length} integrations...`} 
            value={search} 
            onChange={e => setSearch(e.target.value)}
            className={styles.searchInput}
          />
        </div>

        <div className={styles.body}>
          {/* Categories Sidebar */}
          <div className={styles.sidebar}>
            {Object.entries(CATEGORY_MAP).map(([catMenu, catMeta]) => {
              const Icon = catMeta.icon;
              const isActive = activeCategory === catMenu && search === '';
              return (
                <button
                  key={catMenu}
                  className={`${styles.categoryBtn} ${isActive ? styles.activeCategory : ''}`}
                  onClick={() => {
                    setSearch('');
                    setActiveCategory(catMenu);
                    setSelectedIntegration(null);
                  }}
                >
                  <Icon size={14} className={styles.categoryIcon} />
                  <span>{catMenu}</span>
                </button>
              );
            })}
          </div>

          {/* Integration Grid or Action Selector */}
          <div className={styles.content}>
            {loading ? (
              <div className={styles.loadingState}>
                <Loader2 size={32} className={styles.spinner} />
                <p>Loading integration library...</p>
              </div>
            ) : selectedIntegration ? (
              renderItemSelector()
            ) : (
              <div className={styles.grid}>
                {filteredIntegrations.map(item => (
                  <button 
                    key={item.id} 
                    className={styles.integrationCard}
                    onClick={() => {
                      const possibleItems = type === 'trigger' ? item.supported_triggers : item.supported_actions;
                      if (possibleItems && possibleItems.length > 1) {
                        setSelectedIntegration(item);
                      } else {
                        // If only 1 action or default, just return it directly
                        const defaultId = possibleItems?.[0] || `new_${item.id}_${type}`;
                        onSelect({ ...item, selectedAction: defaultId });
                        onClose();
                      }
                    }}
                  >
                    <div className={styles.cardLogoWrapper}>
                      {BRAND_LOGOS[item.id] || <span className={styles.placeholderLogo}>{item.name.charAt(0)}</span>}
                    </div>
                    <span className={styles.cardName}>{item.name}</span>
                  </button>
                ))}
                
                {filteredIntegrations.length === 0 && !loading && (
                  <div className={styles.noResults}>
                    <Info size={32} />
                    <p>No integrations found matching "{search}" in {activeCategory}</p>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        </>
        )}
      </div>
    </div>
  );
}
