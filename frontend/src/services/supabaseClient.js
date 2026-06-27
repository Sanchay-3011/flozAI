/**
 * Supabase Client Configuration
 * Frontend JavaScript client for React
 * 
 * Usage:
 * import { supabase } from '@/services/supabaseClient'
 * const { data, error } = await supabase.auth.getUser()
 */

import { createClient } from '@supabase/supabase-js'

// Get environment variables
const SUPABASE_URL = import.meta.env.VITE_SUPABASE_URL
const SUPABASE_ANON_KEY = import.meta.env.VITE_SUPABASE_ANON_KEY

if (!SUPABASE_URL || !SUPABASE_ANON_KEY) {
  console.error(
    'Missing VITE_SUPABASE_URL or VITE_SUPABASE_ANON_KEY environment variables'
  )
}

/**
 * Supabase client instance
 * This is used for all database and auth operations
 */
export const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY, {
  auth: {
    autoRefreshToken: true,
    persistSession: true,
    storage: localStorage,
    storageKey: 'flozai-auth-token',
    detectSessionInUrl: true
  }
})

export default supabase
