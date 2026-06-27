import React, { useState, useEffect } from 'react';
import { useAppData } from '../../hooks/useAppData';
import { Search, Plus, Network, Check, ExternalLink, Loader2 } from 'lucide-react';
import { BRAND_LOGOS, BRAND_COLORS } from './brandLogos';
import { flozApi } from '../../services/api';
import IntegrationConnectModal from './IntegrationConnectModal';
import styles from './IntegrationsView.module.css';

export default function IntegrationsView() {
  const appData = useAppData();
  const [query, setQuery] = useState('');
  const [filter, setFilter] = useState('all'); // all, connected, available
  const [registry, setRegistry] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [selectedIntegration, setSelectedIntegration] = useState(null);
  const [modalOpen, setModalOpen] = useState(false);

  useEffect(() => {
    let active = true;
    async function fetchRegistry() {
      try {
        const data = await flozApi.getIntegrationRegistry();
        if (active) {
          setRegistry(data);
          setLoading(false);
        }
      } catch (err) {
        console.error('Failed to load integrations registry:', err);
        if (active) {
          setError('Failed to load integrations registry. Please try again.');
          setLoading(false);
        }
      }
    }
    fetchRegistry();
    return () => {
      active = false;
    };
  }, []);

  const filtered = registry.filter(item => {
    const isConnected = !!appData.integrations[item.id];
    const nameMatch = item.name?.toLowerCase().includes(query.toLowerCase());
    const descMatch = (item.description || item.desc || '').toLowerCase().includes(query.toLowerCase());
    const matchesQuery = nameMatch || descMatch;
    
    if (!matchesQuery) return false;
    
    if (filter === 'connected') return isConnected;
    if (filter === 'available') return !isConnected;
    return true;
  });

  if (loading) {
    return (
      <div className={styles.viewContainer}>
        <header className={styles.header}>
          <div>
            <h1 className={styles.title}>Integrations</h1>
            <p className={styles.subtitle}>Connect FlozAI with your favorite apps</p>
          </div>
        </header>
        <div className={styles.loadingContainer}>
          <Loader2 size={36} className={styles.spinner} />
          <p>Loading integration registry...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.viewContainer}>
        <header className={styles.header}>
          <div>
            <h1 className={styles.title}>Integrations</h1>
            <p className={styles.subtitle}>Connect FlozAI with your favorite apps</p>
          </div>
        </header>
        <div className={styles.emptyState}>
          <Network size={32} />
          <h3>Something went wrong</h3>
          <p>{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.viewContainer}>
      <header className={styles.header}>
        <div>
          <h1 className={styles.title}>Integrations</h1>
          <p className={styles.subtitle}>Connect FlozAI with your favorite apps</p>
        </div>
        <button className={styles.requestBtn}>
          <Plus size={16} /> Request App
        </button>
      </header>

      <div className={styles.controls}>
        <div className={styles.searchBar}>
          <Search size={16} className={styles.searchIcon} />
          <input 
            type="text" 
            placeholder="Search integrations..." 
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className={styles.searchInput}
          />
        </div>
        <div className={styles.filters}>
          <button 
            className={`${styles.filterBtn} ${filter === 'all' ? styles.active : ''}`}
            onClick={() => setFilter('all')}
          >All</button>
          <button 
            className={`${styles.filterBtn} ${filter === 'connected' ? styles.active : ''}`}
            onClick={() => setFilter('connected')}
          >Connected</button>
          <button 
            className={`${styles.filterBtn} ${filter === 'available' ? styles.active : ''}`}
            onClick={() => setFilter('available')}
          >Available</button>
        </div>
      </div>

      <div className={styles.grid}>
        {filtered.map(app => (
          <div key={app.id} className={styles.appCard}>
            <div className={styles.cardHeader}>
              <div 
                className={styles.logoWrapper}
                style={{ '--brand-bg': BRAND_COLORS[app.id] || 'rgba(255,255,255,0.1)' }}
              >
                {BRAND_LOGOS[app.id] || <Network size={20} />}
              </div>
              {appData.integrations[app.id] ? (
                <div className={styles.statusConnected}>
                  <Check size={12} /> Connected
                </div>
              ) : (
                <div className={styles.statusDisconnected}>Not connected</div>
              )}
            </div>
            
            <div className={styles.cardBody}>
              <h3 className={styles.appName}>{app.name}</h3>
              <p className={styles.appDesc}>{app.description || app.desc}</p>
            </div>

            <div className={styles.cardFooter}>
              {appData.integrations[app.id] ? (
                <button 
                  className={`${styles.actionBtn} ${styles.btnSecondary}`}
                  onClick={() => appData.removeIntegration(app.id)}
                >
                  Disconnect
                </button>
              ) : (
                <button 
                  className={`${styles.actionBtn} ${styles.btnPrimary}`}
                  onClick={() => {
                    setSelectedIntegration(app);
                    setModalOpen(true);
                  }}
                >
                  Connect
                </button>
              )}
            </div>
          </div>
        ))}
      </div>
      
      {filtered.length === 0 && (
        <div className={styles.emptyState}>
          <Network size={32} />
          <h3>No integrations found</h3>
          <p>Try adjusting your search or filters.</p>
        </div>
      )}

      <IntegrationConnectModal 
        isOpen={modalOpen} 
        onClose={() => {
          setModalOpen(false);
          setSelectedIntegration(null);
        }}
        integration={selectedIntegration}
        appData={appData}
        onConnectSuccess={() => {
          console.log('Connected integration successfully');
        }}
      />
    </div>
  );
}

