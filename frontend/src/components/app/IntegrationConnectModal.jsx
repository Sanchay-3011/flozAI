import React, { useState, useEffect } from 'react';
import { X, Key, Info, Check, AlertCircle, Loader2, Eye, EyeOff, ExternalLink, ShieldCheck } from 'lucide-react';
import { BRAND_LOGOS, BRAND_COLORS } from './brandLogos';
import styles from './IntegrationConnectModal.module.css';

const BASE_URL = import.meta.env.VITE_API_URL || '/api';

export default function IntegrationConnectModal({ isOpen, onClose, integration, appData, onConnectSuccess }) {
  const [apiKey, setApiKey] = useState('');
  const [showKey, setShowKey] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  
  // Developer bypass state
  const [devBypass, setDevBypass] = useState(false);
  const [bypassKey, setBypassKey] = useState('');

  useEffect(() => {
    if (isOpen) {
      setApiKey('');
      setShowKey(false);
      setError(null);
      setSuccess(false);
      setDevBypass(false);
      setBypassKey('');
    }
  }, [isOpen, integration]);

  if (!isOpen || !integration) return null;

  const handleApiKeyConnect = async (keyToSubmit) => {
    if (!keyToSubmit?.trim()) return;
    setLoading(true);
    setError(null);

    try {
      await appData.saveIntegration(integration.id, { apiKey: keyToSubmit });
      setSuccess(true);
      setTimeout(() => {
        onConnectSuccess();
        onClose();
      }, 1500);
    } catch (err) {
      setError(err.message || 'Failed to connect integration. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  const handleOAuthConnect = async () => {
    setLoading(true);
    setError(null);

    try {
      // 1. Get OAuth authorization URL from backend
      const headers = { 'Content-Type': 'application/json' };
      const sessionRes = await appData.supabase?.auth?.getSession?.() || {};
      const token = sessionRes?.data?.session?.access_token;
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const res = await fetch(`${BASE_URL}/oauth/${integration.id}/authorize`, { headers });
      const data = await res.json();

      if (!res.ok) {
        // If OAuth credentials are not set on server, trigger Developer Bypass
        const errMsg = data.detail?.error || data.detail || '';
        if (errMsg.includes('OAuth not configured') || res.status === 400) {
          setDevBypass(true);
          setLoading(false);
          return;
        }
        throw new Error(errMsg || 'Failed to authorize OAuth provider.');
      }

      // 2. Open popup window for OAuth flow
      const popup = window.open(data.url, 'oauth_popup', 'width=600,height=700');
      if (!popup) {
        throw new Error('Popup blocked! Please allow popups for this site to complete authorization.');
      }

      // 3. Listen for postMessage callback from the OAuth callback window
      const handleOauthMessage = async (event) => {
        if (event.data?.type === 'oauth_success' && event.data?.provider === integration.id) {
          window.removeEventListener('message', handleOauthMessage);
          
          // Re-sync integrations state in frontend
          await appData.saveIntegration(integration.id, { oauth: true, verified: true });
          
          setSuccess(true);
          setLoading(false);
          setTimeout(() => {
            onConnectSuccess();
            onClose();
          }, 1500);
        } else if (event.data?.type === 'oauth_error') {
          window.removeEventListener('message', handleOauthMessage);
          setError(event.data.error || 'Authorization failed.');
          setLoading(false);
        }
      };

      window.addEventListener('message', handleOauthMessage);

      // Guard check to clear loading if user closes popup manually
      const checkPopupClosed = setInterval(() => {
        if (popup.closed) {
          clearInterval(checkPopupClosed);
          setLoading(false);
        }
      }, 1000);

    } catch (err) {
      setError(err.message || 'Authorization failed.');
      setLoading(false);
    }
  };

  const handleNoneConnect = async () => {
    setLoading(true);
    setError(null);
    try {
      await appData.saveIntegration(integration.id, { connected: true, noneAuth: true });
      setSuccess(true);
      setTimeout(() => {
        onConnectSuccess();
        onClose();
      }, 1500);
    } catch (err) {
      setError(err.message || 'Failed to connect.');
    } finally {
      setLoading(false);
    }
  };

  const renderFormContent = () => {
    if (success) {
      return (
        <div className={styles.successState}>
          <div className={styles.successCircle}>
            <Check size={36} />
          </div>
          <h3>Connected Successfully!</h3>
          <p>FlozAI is now connected to {integration.name}.</p>
        </div>
      );
    }

    if (devBypass) {
      return (
        <div className={styles.bypassContainer}>
          <div className={styles.bypassAlert}>
            <Info size={16} />
            <div>
              <strong>OAuth Keys Missing:</strong> Client credentials for {integration.name} are not set in the server <code>.env</code> file.
            </div>
          </div>
          <p className={styles.bypassText}>
            You can bypass this and connect instantly using a mock developer key to test workflows locally.
          </p>
          <div className={styles.inputLabelRow}>
            <label>Mock API / Access Token</label>
          </div>
          <div className={styles.inputWrapper}>
            <input
              type={showKey ? 'text' : 'password'}
              value={bypassKey}
              onChange={(e) => setBypassKey(e.target.value)}
              placeholder="e.g. mock_oauth_token_123"
              className={styles.keyInput}
              disabled={loading}
            />
            <button 
              type="button" 
              className={styles.keyToggle} 
              onClick={() => setShowKey(!showKey)}
            >
              {showKey ? <EyeOff size={16} /> : <Eye size={16} />}
            </button>
          </div>
          <div className={styles.modalActions}>
            <button 
              type="button" 
              className={styles.cancelBtn} 
              onClick={() => setDevBypass(false)}
              disabled={loading}
            >
              Back
            </button>
            <button
              type="button"
              className={`${styles.connectBtn} ${styles.btnPrimary}`}
              onClick={() => handleApiKeyConnect(bypassKey)}
              disabled={loading || !bypassKey.trim()}
            >
              {loading ? <Loader2 size={16} className={styles.spinner} /> : 'Connect with Mock Key'}
            </button>
          </div>
        </div>
      );
    }

    if (integration.authType === 'none') {
      return (
        <div className={styles.noneState}>
          <ShieldCheck size={40} className={styles.shieldIcon} />
          <h3>No credentials required</h3>
          <p>This utility integration is built-in and can be used immediately without additional keys.</p>
          <div className={styles.modalActions}>
            <button type="button" className={styles.cancelBtn} onClick={onClose} disabled={loading}>
              Cancel
            </button>
            <button
              type="button"
              className={`${styles.connectBtn} ${styles.btnPrimary}`}
              onClick={handleNoneConnect}
              disabled={loading}
            >
              {loading ? <Loader2 size={16} className={styles.spinner} /> : 'Connect Instantly'}
            </button>
          </div>
        </div>
      );
    }

    if (integration.authType === 'oauth') {
      return (
        <div className={styles.oauthState}>
          <p className={styles.oauthText}>
            Authorize FlozAI to interact with your {integration.name} account securely. You'll be redirected to authorize the application.
          </p>
          
          {integration.setup_instructions?.steps && (
            <div className={styles.stepsCard}>
              <h4>Setup Prerequisites:</h4>
              <ul className={styles.stepsList}>
                {integration.setup_instructions.steps.map((step, idx) => (
                  <li key={idx}>{step}</li>
                ))}
              </ul>
              {integration.setup_instructions.url && (
                <a 
                  href={integration.setup_instructions.url} 
                  target="_blank" 
                  rel="noopener noreferrer" 
                  className={styles.externalLink}
                >
                  Configure Developer Keys <ExternalLink size={12} />
                </a>
              )}
            </div>
          )}

          {error && (
            <div className={styles.errorAlert}>
              <AlertCircle size={16} />
              <span>{error}</span>
            </div>
          )}

          <div className={styles.modalActions}>
            <button type="button" className={styles.cancelBtn} onClick={onClose} disabled={loading}>
              Cancel
            </button>
            <button
              type="button"
              className={`${styles.connectBtn} ${styles.btnPrimary}`}
              onClick={handleOAuthConnect}
              disabled={loading}
            >
              {loading ? <Loader2 size={16} className={styles.spinner} /> : `Authorize ${integration.name}`}
            </button>
          </div>
        </div>
      );
    }

    // Default API Key Form
    return (
      <form onSubmit={(e) => { e.preventDefault(); handleApiKeyConnect(apiKey); }}>
        <p className={styles.helpText}>
          Enter your API Credentials to connect to {integration.name}. Keys are encrypted and stored securely.
        </p>

        {integration.setup_instructions?.steps && (
          <div className={styles.stepsCard}>
            <h4>Where to find your key:</h4>
            <ul className={styles.stepsList}>
              {integration.setup_instructions.steps.map((step, idx) => (
                <li key={idx}>{step}</li>
              ))}
            </ul>
            {integration.setup_instructions.url && (
              <a 
                href={integration.setup_instructions.url} 
                target="_blank" 
                rel="noopener noreferrer" 
                className={styles.externalLink}
              >
                Get API Key <ExternalLink size={12} />
              </a>
            )}
          </div>
        )}

        <div className={styles.inputLabelRow}>
          <label>API Key / Token</label>
        </div>
        <div className={styles.inputWrapper}>
          <input
            type={showKey ? 'text' : 'password'}
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            placeholder={`Enter your ${integration.name} API Key...`}
            className={styles.keyInput}
            disabled={loading}
            required
          />
          <button 
            type="button" 
            className={styles.keyToggle} 
            onClick={() => setShowKey(!showKey)}
          >
            {showKey ? <EyeOff size={16} /> : <Eye size={16} />}
          </button>
        </div>

        {error && (
          <div className={styles.errorAlert}>
            <AlertCircle size={16} />
            <span>{error}</span>
          </div>
        )}

        <div className={styles.modalActions}>
          <button type="button" className={styles.cancelBtn} onClick={onClose} disabled={loading}>
            Cancel
          </button>
          <button
            type="submit"
            className={`${styles.connectBtn} ${styles.btnPrimary}`}
            disabled={loading || !apiKey.trim()}
          >
            {loading ? <Loader2 size={16} className={styles.spinner} /> : 'Connect Integration'}
          </button>
        </div>
      </form>
    );
  };

  return (
    <div className={styles.modalOverlay}>
      <div className={styles.modalCard}>
        <button className={styles.closeBtn} onClick={onClose} disabled={loading}>
          <X size={18} />
        </button>
        
        <div className={styles.modalHeader}>
          <div 
            className={styles.logoWrapper}
            style={{ '--brand-bg': BRAND_COLORS[integration.id] || 'rgba(255,255,255,0.1)' }}
          >
            {BRAND_LOGOS[integration.id] || <Key size={24} />}
          </div>
          <div>
            <h2 className={styles.modalTitle}>Connect {integration.name}</h2>
            <span className={styles.categoryBadge}>{integration.category}</span>
          </div>
        </div>

        <div className={styles.modalBody}>
          {renderFormContent()}
        </div>
      </div>
    </div>
  );
}
