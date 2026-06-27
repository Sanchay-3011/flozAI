import { useState, useEffect } from 'react'
import styles from './Navbar.module.css'

export default function Navbar() {
  const [scrolled, setScrolled] = useState(false)

  useEffect(() => {
    const fn = () => setScrolled(window.scrollY > 20)
    window.addEventListener('scroll', fn)
    return () => window.removeEventListener('scroll', fn)
  }, [])

  return (
    <nav className={`${styles.nav} ${scrolled ? styles.scrolled : ''}`}>
      <div className={styles.inner}>
        <a href="/" className={styles.logo}>
          <svg width="22" height="22" viewBox="0 0 22 22" fill="none">
            <path d="M4 4L11 2L18 4V11C18 15.4 14.5 18.8 11 20C7.5 18.8 4 15.4 4 11V4Z"
              stroke="url(#lg)" strokeWidth="1.5" fill="none"/>
            <circle cx="11" cy="11" r="2.5" fill="url(#lg)"/>
            <defs>
              <linearGradient id="lg" x1="4" y1="2" x2="18" y2="20" gradientUnits="userSpaceOnUse">
                <stop offset="0%"   stopColor="#4fa8d5"/>
                <stop offset="100%" stopColor="#8b6fcb"/>
              </linearGradient>
            </defs>
          </svg>
          FlozAI
        </a>

        <div className={styles.links}>
          <a href="#product">Product</a>
          <a href="#about">About</a>
          <a href="#faq">FAQ</a>
        </div>

        <div className={styles.actions}>
          <button className="btn-ghost" style={{ padding: '8px 18px', fontSize: '13px' }}>Login</button>
          <button className="btn-primary" style={{ padding: '8px 18px', fontSize: '13px' }}>Sign up</button>
        </div>
      </div>
    </nav>
  )
}