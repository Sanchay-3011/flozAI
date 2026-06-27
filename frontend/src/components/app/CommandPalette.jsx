import React, { useState, useEffect, useRef } from 'react';
import { Search, Plus, GitBranch, Settings, Activity } from 'lucide-react';
import styles from './CommandPalette.module.css';

const COMMANDS = [
  { id: 'create_wf', title: 'Create Automation', icon: Plus, group: 'Actions' },
  { id: 'search_wf', title: 'Search Workflows', icon: Search, group: 'Navigation' },
  { id: 'view_integrations', title: 'Integrations', icon: GitBranch, group: 'Navigation' },
  { id: 'view_activity', title: 'Recent Activity', icon: Activity, group: 'Navigation' },
  { id: 'settings', title: 'Workspace Settings', icon: Settings, group: 'System' },
];

export default function CommandPalette() {
  const [isOpen, setIsOpen] = useState(false);
  const [query, setQuery] = useState('');
  const [selectedIndex, setSelectedIndex] = useState(0);
  const inputRef = useRef(null);

  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'k' && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        setIsOpen(true);
      }
      if (e.key === 'Escape') {
        setIsOpen(false);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  useEffect(() => {
    if (isOpen) {
      setQuery('');
      setSelectedIndex(0);
      setTimeout(() => inputRef.current?.focus(), 50);
    }
  }, [isOpen]);

  const filtered = COMMANDS.filter(cmd => 
    cmd.title.toLowerCase().includes(query.toLowerCase())
  );

  const handleListKeyDown = (e) => {
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setSelectedIndex(i => (i + 1) % filtered.length);
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setSelectedIndex(i => (i - 1 + filtered.length) % filtered.length);
    } else if (e.key === 'Enter') {
      e.preventDefault();
      if (filtered[selectedIndex]) {
        console.log('Execute:', filtered[selectedIndex].id);
        setIsOpen(false);
      }
    }
  };

  if (!isOpen) return null;

  return (
    <div className={styles.overlay} onClick={() => setIsOpen(false)}>
      <div 
        className={styles.palette} 
        onClick={e => e.stopPropagation()}
      >
        <div className={styles.inputArea}>
          <Search size={18} className={styles.searchIcon} />
          <input
            ref={inputRef}
            className={styles.input}
            placeholder="Type a command or search..."
            value={query}
            onChange={e => {
              setQuery(e.target.value);
              setSelectedIndex(0);
            }}
            onKeyDown={handleListKeyDown}
          />
        </div>

        <div className={styles.results}>
          {filtered.length > 0 ? (
            filtered.map((cmd, idx) => {
              const Icon = cmd.icon;
              return (
                <button
                  key={cmd.id}
                  className={`${styles.cmdItem} ${idx === selectedIndex ? styles.cmdActive : ''}`}
                  onMouseEnter={() => setSelectedIndex(idx)}
                  onClick={() => setIsOpen(false)}
                >
                  <Icon size={16} className={styles.cmdIcon} />
                  <span>{cmd.title}</span>
                </button>
              );
            })
          ) : (
            <div className={styles.noResults}>
              No commands found for "{query}"
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
