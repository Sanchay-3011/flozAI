import React, { useState, useEffect } from 'react';
import { 
  Network, LayoutDashboard, GitBranch, PlusCircle, 
  Activity, Settings, Search, Bell, ChevronDown, 
  TerminalSquare, Sparkles, BookTemplate
} from 'lucide-react';
import CommandPalette from './CommandPalette';
import ParticleField from '../ui/ParticleField';
import styles from './AppLayout.module.css';

const NAV_ITEMS = [
  { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { id: 'workflows', label: 'Workflows', icon: GitBranch },
  { id: 'create', label: 'Create Automation', icon: PlusCircle },
  { id: 'integrations', label: 'Integrations', icon: Network },
  { id: 'activity', label: 'Activity Logs', icon: Activity },
  { id: 'templates', label: 'Templates', icon: BookTemplate },
  { id: 'ai', label: 'AI Assistant', icon: Sparkles },
  { id: 'settings', label: 'Settings', icon: Settings },
];

export default function AppLayout({ children, activeTab = 'dashboard', onNavigate, user, onLogout }) {
  const [isSidebarOpen, setSidebarOpen] = useState(true);
  const [isDropdownOpen, setDropdownOpen] = useState(false);

  useEffect(() => {
    if (activeTab === 'create' || activeTab === 'workspace') {
      setSidebarOpen(false);
    } else {
      setSidebarOpen(true);
    }
  }, [activeTab]);

  return (
    <div className={styles.appContainer}>
      <ParticleField />
      
      {/* Top Navigation */}
      <header className={styles.topNav}>
        <div className={styles.navLeft}>
          <div className={styles.logoArea} onClick={() => setSidebarOpen(!isSidebarOpen)}>
            <img src="/floz-logo.png" alt="FlozAI" className={styles.logoImage} />
            <span className={styles.logoText}>FlozAI</span>
          </div>
          <div className={styles.workspaceSelector}>
            <span className={styles.workspaceName}>Personal Workspace</span>
            <ChevronDown size={14} className={styles.chevron} />
          </div>
        </div>

        <div className={styles.navCenter}>
          <button className={styles.searchBtn} onClick={() => {/* trigger cmd+k */}}>
            <Search size={14} />
            <span>Search or jump to...</span>
            <kbd className={styles.shortcutKey}>⌘K</kbd>
          </button>
        </div>

        <div className={styles.navRight}>
          <button className={styles.iconBtn}>
            <TerminalSquare size={18} />
          </button>
          <button className={styles.iconBtn}>
            <Bell size={18} />
            <span className={styles.badgePulse}></span>
          </button>
          <div className={styles.profileMenu}>
            <button className={styles.avatarBtn} onClick={() => setDropdownOpen(!isDropdownOpen)}>
              <img src={`https://api.dicebear.com/7.x/notionists/svg?seed=${user?.email || 'Floz'}&backgroundColor=transparent`} alt="User" />
            </button>
            {isDropdownOpen && (
              <div className={styles.dropdown}>
                <div className={styles.dropdownHeader}>
                  <span className={styles.dropdownName}>{user?.email ? user.email.split('@')[0] : 'User'}</span>
                  <span className={styles.dropdownEmail}>{user?.email || 'user@example.com'}</span>
                </div>
                <div className={styles.dropdownDivider} />
                <button className={styles.dropdownItem}>Profile Settings</button>
                <button className={styles.dropdownItem}>Workspace Settings</button>
                <button className={styles.dropdownItem}>API Keys</button>
                <button className={styles.dropdownItem}>Billing</button>
                <div className={styles.dropdownDivider} />
                <button className={styles.dropdownItem} onClick={onLogout}>Log out</button>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <div className={styles.mainWrapper}>
        
        {/* Left Sidebar */}
        <aside className={`${styles.sidebar} ${isSidebarOpen ? styles.sidebarOpen : styles.sidebarClosed}`}>
          <div className={styles.sidebarNav}>
            {NAV_ITEMS.map(item => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button 
                  key={item.id}
                  className={`${styles.navItem} ${isActive ? styles.navActive : ''}`}
                  onClick={() => onNavigate && onNavigate(item.id)}
                  title={!isSidebarOpen ? item.label : ''}
                >
                  <Icon size={18} className={styles.navIcon} />
                  {isSidebarOpen && <span className={styles.navLabel}>{item.label}</span>}
                </button>
              );
            })}
          </div>
          {isSidebarOpen && (
            <div className={styles.sidebarFooter}>
              <div className={styles.usageCard}>
                <div className={styles.usageHeader}>
                  <span>Tasks this month</span>
                  <span>14.2k / 50k</span>
                </div>
                <div className={styles.progressBar}>
                  <div className={styles.progressFill} style={{ width: '28%' }} />
                </div>
              </div>
            </div>
          )}
        </aside>

        {/* Dynamic Inner Content */}
        <main className={styles.contentArea}>
          {children}
        </main>
      </div>

      <CommandPalette />
    </div>
  );
}
