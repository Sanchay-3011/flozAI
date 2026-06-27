import React, { useState, useEffect } from 'react';
import { User, Briefcase, Key, Bell, Shield, LogOut, Brain, CheckCircle2, XCircle, Loader2, Eye, EyeOff, Star } from 'lucide-react';
import { BRAND_LOGOS } from './brandLogos';
import { flozApi } from '../../services/api';
import styles from './SettingsView.module.css';

/* ═══════════════════════════════════════════
   AI Provider Logo Components (official)
   ═══════════════════════════════════════════ */
const PROVIDER_LOGOS = {
  openai: (
    <svg viewBox="0 0 24 24" width="32" height="32">
      <path fill="#10a37f" d="M22.282 9.821a5.985 5.985 0 0 0-.516-4.91 6.046 6.046 0 0 0-6.51-2.9A6.065 6.065 0 0 0 4.981 4.18a5.998 5.998 0 0 0-3.998 2.9 6.046 6.046 0 0 0 .743 7.097 5.98 5.98 0 0 0 .516 4.911 6.046 6.046 0 0 0 6.51 2.9A6.065 6.065 0 0 0 19.019 19.82a5.998 5.998 0 0 0 3.998-2.9 6.046 6.046 0 0 0-.735-7.098zM12.204 22.15a4.53 4.53 0 0 1-2.917-1.064l.145-.084 4.847-2.798a.789.789 0 0 0 .4-.687v-6.83l2.049 1.182a.072.072 0 0 1 .04.054v5.658a4.555 4.555 0 0 1-4.564 4.57zM3.88 18.116a4.527 4.527 0 0 1-.542-3.042l.145.087 4.847 2.799a.786.786 0 0 0 .79 0l5.919-3.417v2.366a.078.078 0 0 1-.03.06L10.12 19.76a4.555 4.555 0 0 1-6.24-1.644zM2.5 7.965a4.526 4.526 0 0 1 2.372-1.994v5.77a.78.78 0 0 0 .39.677l5.919 3.417-2.05 1.182a.072.072 0 0 1-.069.006L4.177 14.23A4.556 4.556 0 0 1 2.5 7.965zm16.6 3.865L13.18 8.412l2.05-1.183a.072.072 0 0 1 .069-.006l4.885 2.794A4.552 4.552 0 0 1 18.5 16.4v-5.77a.787.787 0 0 0-.4-.8zm2.038-3.05-.145-.086-4.847-2.8a.786.786 0 0 0-.79 0L9.437 9.312V6.946a.072.072 0 0 1 .03-.06l4.886-2.793a4.553 4.553 0 0 1 6.785 4.688zM8.309 12.74l-2.05-1.183a.072.072 0 0 1-.04-.054V5.845a4.553 4.553 0 0 1 7.47-3.504l-.144.084L8.698 5.223a.789.789 0 0 0-.4.687l.011 6.83zm1.113-2.395 2.637-1.523 2.637 1.523v3.046l-2.637 1.523-2.637-1.523z"/>
    </svg>
  ),
  groq: (
    <svg viewBox="0 0 24 24" width="32" height="32">
      <circle cx="12" cy="12" r="11" fill="#F55036"/>
      <path fill="#fff" d="M8 7h2.5v5.5H8zm5.5 0H16v9h-2.5zm-5.5 7h2.5v2H8z"/>
    </svg>
  ),
  anthropic: (
    <svg viewBox="0 0 24 24" width="32" height="32">
      <rect width="24" height="24" rx="4" fill="#D4A27F"/>
      <path d="M14.005 5.476h2.352l3.816 13.048h-2.352l-.918-3.276h-4.176l-.918 3.276H9.457L14.005 5.476zm2.448 7.728L15.181 8.54l-1.272 4.664h2.544z" fill="#191918"/>
      <path d="M4.827 5.476h2.351l3.816 13.048H8.643L7.725 15.2H5z" fill="#191918"/>
    </svg>
  ),
  gemini: (
    <svg viewBox="0 0 24 24" width="32" height="32">
      <defs>
        <linearGradient id="gGrad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#4285F4"/>
          <stop offset="35%" stopColor="#9B72CB"/>
          <stop offset="65%" stopColor="#D96570"/>
          <stop offset="100%" stopColor="#E8710A"/>
        </linearGradient>
      </defs>
      <path fill="url(#gGrad)" d="M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20zm0 3a7 7 0 1 1 0 14 7 7 0 0 1 0-14z"/>
      <circle fill="url(#gGrad)" cx="12" cy="12" r="5"/>
    </svg>
  ),
};

const PROVIDER_ORDER = ['openai', 'groq', 'anthropic', 'gemini'];
const PROVIDER_LABELS = {
  openai: 'OpenAI',
  groq: 'Groq',
  anthropic: 'Anthropic',
  gemini: 'Google Gemini',
};
const PROVIDER_DESCRIPTIONS = {
  openai: 'GPT-4o, GPT-4o-mini — most popular models',
  groq: 'Llama 3.3 70B — blazing fast inference',
  anthropic: 'Claude Sonnet, Claude Haiku — thoughtful AI',
  gemini: 'Gemini 2.0 Flash, Gemini 2.5 Pro — multimodal',
};
const PROVIDER_KEY_LINKS = {
  openai: 'https://platform.openai.com/api-keys',
  groq: 'https://console.groq.com/keys',
  anthropic: 'https://console.anthropic.com/settings/keys',
  gemini: 'https://aistudio.google.com/apikey',
};

export default function SettingsView() {
  const [activeTab, setActiveTab] = useState('profile');
  const [providers, setProviders] = useState([]);
  const [loadingProviders, setLoadingProviders] = useState(false);
  const [connectingId, setConnectingId] = useState(null);
  const [keyInputs, setKeyInputs] = useState({});
  const [showKeys, setShowKeys] = useState({});
  const [connectError, setConnectError] = useState({});
  const [connectSuccess, setConnectSuccess] = useState({});

  // Fetch providers when AI tab is opened
  useEffect(() => {
    if (activeTab === 'ai') {
      setLoadingProviders(true);
      flozApi.getAiProviders()
        .then(data => { setProviders(data.providers || []); setLoadingProviders(false); })
        .catch(() => setLoadingProviders(false));
    }
  }, [activeTab]);

  const handleConnect = async (providerId) => {
    const apiKey = keyInputs[providerId]?.trim();
    if (!apiKey) return;
    setConnectingId(providerId);
    setConnectError(prev => ({ ...prev, [providerId]: null }));
    setConnectSuccess(prev => ({ ...prev, [providerId]: null }));
    try {
      const data = await flozApi.connectAiProvider(providerId, apiKey);
      setConnectSuccess(prev => ({ ...prev, [providerId]: data.message }));
      setKeyInputs(prev => ({ ...prev, [providerId]: '' }));
      // Refresh providers
      const rData = await flozApi.getAiProviders();
      setProviders(rData.providers || []);
    } catch (err) {
      setConnectError(prev => ({ ...prev, [providerId]: err.message }));
    } finally {
      setConnectingId(null);
    }
  };

  const handleDisconnect = async (providerId) => {
    try {
      await flozApi.disconnectAiProvider(providerId);
      const rData = await flozApi.getAiProviders();
      setProviders(rData.providers || []);
      setConnectSuccess(prev => ({ ...prev, [providerId]: null }));
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className={styles.settingsLayout}>
      <aside className={styles.settingsSidebar}>
        <div className={styles.sidebarSection}>
          <h3 className={styles.sectionTitle}>Account settings</h3>
          <button 
            className={`${styles.navBtn} ${activeTab === 'profile' ? styles.active : ''}`}
            onClick={() => setActiveTab('profile')}
          >
            <User size={16} /> Profile
          </button>
          <button 
            className={`${styles.navBtn} ${activeTab === 'workspace' ? styles.active : ''}`}
            onClick={() => setActiveTab('workspace')}
          >
            <Briefcase size={16} /> Workspace
          </button>
          <button 
            className={`${styles.navBtn} ${activeTab === 'apikeys' ? styles.active : ''}`}
            onClick={() => setActiveTab('apikeys')}
          >
            <Key size={16} /> API Keys
          </button>
        </div>

        <div className={styles.sidebarSection}>
          <h3 className={styles.sectionTitle}>AI & Automation</h3>
          <button 
            className={`${styles.navBtn} ${activeTab === 'ai' ? styles.active : ''}`}
            onClick={() => setActiveTab('ai')}
          >
            <Brain size={16} /> AI Providers
          </button>
        </div>

        <div className={styles.sidebarSection}>
          <h3 className={styles.sectionTitle}>Preferences</h3>
          <button className={styles.navBtn}><Bell size={16} /> Notifications</button>
          <button className={styles.navBtn}><Shield size={16} /> Security</button>
        </div>
        
        <div className={styles.sidebarFooter}>
          <button className={styles.logoutBtn}><LogOut size={16} /> Log out</button>
        </div>
      </aside>

      <main className={styles.settingsContent}>
        {activeTab === 'profile' && (
          <div className={styles.panel}>
            <h2>Profile Settings</h2>
            <p className={styles.panelDesc}>Manage your personal information and preferences.</p>
            
            <div className={styles.formGroup}>
              <div className={styles.avatarSection}>
                <img src="https://api.dicebear.com/7.x/notionists/svg?seed=Floz&backgroundColor=transparent" alt="Avatar" className={styles.avatar} />
                <div>
                  <button className={styles.btnSecondary}>Upload new picture</button>
                  <p className={styles.helpText}>JPG, GIF or PNG. Max size of 800K</p>
                </div>
              </div>
            </div>

            <div className={styles.formRow}>
              <div className={styles.formCol}>
                <label>First Name</label>
                <input type="text" defaultValue="Alex" className={styles.input} />
              </div>
              <div className={styles.formCol}>
                <label>Last Name</label>
                <input type="text" defaultValue="Smith" className={styles.input} />
              </div>
            </div>

            <div className={styles.formGroup}>
              <label>Email Address</label>
              <input type="email" defaultValue="alex@example.com" className={styles.input} disabled />
            </div>

            <div className={styles.formActions}>
              <button className={styles.btnPrimary}>Save Changes</button>
            </div>
          </div>
        )}

        {activeTab === 'workspace' && (
          <div className={styles.panel}>
            <h2>Workspace Configuration</h2>
            <p className={styles.panelDesc}>Manage settings for your default workspace.</p>
            
            <div className={styles.formGroup}>
              <label>Workspace Name</label>
              <input type="text" defaultValue="Personal Workspace" className={styles.input} />
            </div>

            <div className={styles.formGroup}>
              <label>Workspace URL</label>
              <div className={styles.inputGroup}>
                <span className={styles.inputAddon}>flozai.com/w/</span>
                <input type="text" defaultValue="alex-personal" className={styles.input} />
              </div>
            </div>

            <div className={styles.formActions}>
              <button className={styles.btnPrimary}>Save Changes</button>
            </div>
          </div>
        )}

        {activeTab === 'apikeys' && (
          <div className={styles.panel}>
            <h2>API Keys</h2>
            <p className={styles.panelDesc}>Use these keys to trigger workflows externally or connect your own apps.</p>
            
            <div className={styles.keyList}>
              <div className={styles.keyItem}>
                <div className={styles.keyInfo}>
                  <h4>Production Key</h4>
                  <code>fk_live_8f92j21...</code>
                  <span>Created Oct 12, 2025 • Last used 2 hours ago</span>
                </div>
                <button className={styles.btnSecondary}>Revoke</button>
              </div>
            </div>

            <div className={styles.formActions}>
              <button className={styles.btnPrimary}>Generate New Key</button>
            </div>
          </div>
        )}

        {/* ═══════════════════════════════════════ */}
        {/*   AI PROVIDERS TAB                      */}
        {/* ═══════════════════════════════════════ */}
        {activeTab === 'ai' && (
          <div className={styles.panel}>
            <h2>AI Providers</h2>
            <p className={styles.panelDesc}>
              Connect your AI provider to power smart agents in your workflows. 
              Your API keys are encrypted and stored securely.
            </p>

            {loadingProviders ? (
              <div className={styles.aiLoadingState}>
                <Loader2 size={24} className={styles.aiSpinner} />
                <span>Loading providers...</span>
              </div>
            ) : (
              <div className={styles.providerGrid}>
                {PROVIDER_ORDER.map(pid => {
                  const prov = providers.find(p => p.id === pid) || { id: pid, connected: false };
                  const isConnecting = connectingId === pid;
                  const error = connectError[pid];
                  const success = connectSuccess[pid];
                  return (
                    <div key={pid} className={`${styles.providerCard} ${prov.connected ? styles.providerConnected : ''}`}>
                      <div className={styles.providerHeader}>
                        <div className={styles.providerLogoWrapper}>
                          {PROVIDER_LOGOS[pid]}
                        </div>
                        <div className={styles.providerInfo}>
                          <h3 className={styles.providerName}>{PROVIDER_LABELS[pid]}</h3>
                          <p className={styles.providerDesc}>{PROVIDER_DESCRIPTIONS[pid]}</p>
                        </div>
                        <div className={styles.providerStatus}>
                          {prov.connected ? (
                            <span className={styles.statusConnected}><CheckCircle2 size={14} /> Connected</span>
                          ) : (
                            <span className={styles.statusDisconnected}><XCircle size={14} /> Not connected</span>
                          )}
                        </div>
                      </div>

                      {prov.connected ? (
                        <div className={styles.providerBody}>
                          <div className={styles.maskedKeyRow}>
                            <code className={styles.maskedKey}>{prov.masked_key || '••••••••••'}</code>
                            <button className={styles.disconnectBtn} onClick={() => handleDisconnect(pid)}>
                              Disconnect
                            </button>
                          </div>
                          {success && <div className={styles.successMsg}><CheckCircle2 size={12} /> {success}</div>}
                        </div>
                      ) : (
                        <div className={styles.providerBody}>
                          <div className={styles.keyInputRow}>
                            <div className={styles.keyInputWrapper}>
                              <input
                                type={showKeys[pid] ? 'text' : 'password'}
                                className={styles.keyInput}
                                placeholder="Paste your API key here..."
                                value={keyInputs[pid] || ''}
                                onChange={e => setKeyInputs(prev => ({ ...prev, [pid]: e.target.value }))}
                                onKeyDown={e => e.key === 'Enter' && handleConnect(pid)}
                              />
                              <button 
                                className={styles.keyToggle}
                                onClick={() => setShowKeys(prev => ({ ...prev, [pid]: !prev[pid] }))}
                              >
                                {showKeys[pid] ? <EyeOff size={14} /> : <Eye size={14} />}
                              </button>
                            </div>
                            <button
                              className={styles.connectBtn}
                              onClick={() => handleConnect(pid)}
                              disabled={isConnecting || !keyInputs[pid]?.trim()}
                            >
                              {isConnecting ? <Loader2 size={14} className={styles.aiSpinner} /> : 'Connect'}
                            </button>
                          </div>
                          <a href={PROVIDER_KEY_LINKS[pid]} target="_blank" rel="noopener noreferrer" className={styles.getKeyLink}>
                            Get your {PROVIDER_LABELS[pid]} API key →
                          </a>
                          {error && <div className={styles.errorMsg}><XCircle size={12} /> {error}</div>}
                          {success && <div className={styles.successMsg}><CheckCircle2 size={12} /> {success}</div>}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            )}

            <div className={styles.aiNote}>
              <Brain size={14} />
              <span>Your API keys are validated on connection and stored securely. They are never shared or sent to FlozAI servers.</span>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
