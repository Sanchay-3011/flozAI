import React, { useState } from 'react';
import { signUp, login } from '../../services/authService';
import { Eye, EyeOff, Lock, Mail, Loader2, Sparkles } from 'lucide-react';
import styles from './AuthModal.module.css';

export default function AuthModal({ onAuthSuccess }) {
  const [isSignUp, setIsSignUp] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [successMsg, setSuccessMsg] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccessMsg(null);

    if (password.length < 8) {
      setError('Password must be at least 8 characters long');
      setLoading(false);
      return;
    }

    try {
      if (isSignUp) {
        const { user, session, error: signUpErr } = await signUp(email, password);
        if (signUpErr) throw new Error(signUpErr);
        
        // Supabase sends confirmation email by default unless configured otherwise
        setSuccessMsg('Verification email sent! Please check your inbox.');
        if (session) {
          setTimeout(() => onAuthSuccess && onAuthSuccess(session), 2000);
        }
      } else {
        const { session, error: loginErr } = await login(email, password);
        if (loginErr) throw new Error(loginErr);
        if (onAuthSuccess) {
          onAuthSuccess(session);
        }
      }
    } catch (err) {
      setError(err.message || 'An error occurred during authentication');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.overlay}>
      <div className={styles.modal}>
        {/* Glow effects */}
        <div className={styles.glow1} />
        <div className={styles.glow2} />

        <div className={styles.header}>
          <div className={styles.logo}>
            <svg width="28" height="28" viewBox="0 0 22 22" fill="none">
              <path d="M4 4L11 2L18 4V11C18 15.4 14.5 18.8 11 20C7.5 18.8 4 15.4 4 11V4Z"
                stroke="url(#auth-lg)" strokeWidth="1.8" fill="none"/>
              <circle cx="11" cy="11" r="2.5" fill="url(#auth-lg)"/>
              <defs>
                <linearGradient id="auth-lg" x1="4" y1="2" x2="18" y2="20" gradientUnits="userSpaceOnUse">
                  <stop offset="0%" stopColor="#4fa8d5"/>
                  <stop offset="100%" stopColor="#8b6fcb"/>
                </linearGradient>
              </defs>
            </svg>
            <span className={styles.logoText}>FlozAI</span>
          </div>
          <h2 className={styles.title}>
            {isSignUp ? 'Create your account' : 'Welcome back'}
          </h2>
          <p className={styles.subtitle}>
            {isSignUp 
              ? 'Start building intelligent automated workflows' 
              : 'Sign in to access your automated workspace'}
          </p>
        </div>

        {/* Tab Selection */}
        <div className={styles.tabs}>
          <button 
            type="button"
            className={`${styles.tab} ${!isSignUp ? styles.tabActive : ''}`}
            onClick={() => { setIsSignUp(false); setError(null); setSuccessMsg(null); }}
          >
            Login
          </button>
          <button 
            type="button"
            className={`${styles.tab} ${isSignUp ? styles.tabActive : ''}`}
            onClick={() => { setIsSignUp(true); setError(null); setSuccessMsg(null); }}
          >
            Sign Up
          </button>
        </div>

        <form onSubmit={handleSubmit} className={styles.form}>
          {error && <div className={styles.errorAlert}>{error}</div>}
          {successMsg && <div className={styles.successAlert}>{successMsg}</div>}

          <div className={styles.inputGroup}>
            <label className={styles.label}>Email Address</label>
            <div className={styles.inputWrapper}>
              <Mail size={16} className={styles.inputIcon} />
              <input 
                type="email" 
                required 
                placeholder="you@example.com" 
                value={email}
                onChange={e => setEmail(e.target.value)}
                className={styles.input}
                disabled={loading}
              />
            </div>
          </div>

          <div className={styles.inputGroup}>
            <label className={styles.label}>Password</label>
            <div className={styles.inputWrapper}>
              <Lock size={16} className={styles.inputIcon} />
              <input 
                type={showPassword ? 'text' : 'password'} 
                required 
                placeholder="••••••••" 
                value={password}
                onChange={e => setPassword(e.target.value)}
                className={styles.input}
                disabled={loading}
              />
              <button 
                type="button"
                className={styles.passwordToggle}
                onClick={() => setShowPassword(!showPassword)}
              >
                {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
          </div>

          <button 
            type="submit" 
            className={styles.submitBtn}
            disabled={loading}
          >
            {loading ? (
              <>
                <Loader2 size={16} className={styles.spin} />
                <span>Processing...</span>
              </>
            ) : (
              <>
                <Sparkles size={16} />
                <span>{isSignUp ? 'Sign Up' : 'Sign In'}</span>
              </>
            )}
          </button>
        </form>
      </div>
    </div>
  );
}
