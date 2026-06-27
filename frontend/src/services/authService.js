/**
 * Authentication Service
 * Frontend JavaScript service for handling auth operations
 * 
 * This service communicates with Supabase Auth and the backend API
 * for creating user profiles in the database
 */

import { supabase } from './supabaseClient'

/**
 * Sign up a new user
 * @param {string} email - Email address
 * @param {string} password - Password (min 8 characters)
 * @returns {Promise<{user, session, error}>}
 */
export const signUp = async (email, password) => {
  try {
    const { data, error } = await supabase.auth.signUp({
      email,
      password
    })

    if (error) throw error

    return {
      user: data.user,
      session: data.session,
      error: null
    }
  } catch (error) {
    console.error('Sign up error:', error)
    return {
      user: null,
      session: null,
      error: error.message
    }
  }
}

/**
 * Log in an existing user
 * @param {string} email - Email address
 * @param {string} password - Password
 * @returns {Promise<{user, session, error}>}
 */
export const login = async (email, password) => {
  try {
    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password
    })

    if (error) throw error

    return {
      user: data.user,
      session: data.session,
      error: null
    }
  } catch (error) {
    console.error('Login error:', error)
    return {
      user: null,
      session: null,
      error: error.message
    }
  }
}

/**
 * Log out the current user
 * @returns {Promise<{error}>}
 */
export const logout = async () => {
  try {
    const { error } = await supabase.auth.signOut()

    if (error) throw error

    return { error: null }
  } catch (error) {
    console.error('Logout error:', error)
    return { error: error.message }
  }
}

/**
 * Get the current authenticated user
 * @returns {Promise<{user, error}>}
 */
export const getCurrentUser = async () => {
  try {
    const { data, error } = await supabase.auth.getUser()

    if (error) throw error

    return {
      user: data.user,
      error: null
    }
  } catch (error) {
    console.error('Get current user error:', error)
    return {
      user: null,
      error: error.message
    }
  }
}

/**
 * Get the current session
 * @returns {Promise<{session, error}>}
 */
export const getSession = async () => {
  try {
    const { data, error } = await supabase.auth.getSession()

    if (error) throw error

    return {
      session: data.session,
      error: null
    }
  } catch (error) {
    console.error('Get session error:', error)
    return {
      session: null,
      error: error.message
    }
  }
}

/**
 * Subscribe to auth state changes
 * @param {Function} callback - Callback function that receives {event, session}
 * @returns {Function} Unsubscribe function
 */
export const onAuthStateChange = (callback) => {
  const { data } = supabase.auth.onAuthStateChange((event, session) => {
    callback({ event, session })
  })

  // Return unsubscribe function
  return data?.subscription?.unsubscribe || (() => {})
}

/**
 * Refresh the access token
 * @returns {Promise<{session, error}>}
 */
export const refreshToken = async () => {
  try {
    const { data, error } = await supabase.auth.refreshSession()

    if (error) throw error

    return {
      session: data.session,
      error: null
    }
  } catch (error) {
    console.error('Token refresh error:', error)
    return {
      session: null,
      error: error.message
    }
  }
}

/**
 * Send password reset email
 * @param {string} email - Email address
 * @returns {Promise<{error}>}
 */
export const sendPasswordResetEmail = async (email) => {
  try {
    const { error } = await supabase.auth.resetPasswordForEmail(email, {
      redirectTo: `${window.location.origin}/auth/reset-password`
    })

    if (error) throw error

    return { error: null }
  } catch (error) {
    console.error('Password reset email error:', error)
    return { error: error.message }
  }
}

/**
 * Update user password
 * @param {string} newPassword - New password
 * @returns {Promise<{user, error}>}
 */
export const updatePassword = async (newPassword) => {
  try {
    const { data, error } = await supabase.auth.updateUser({
      password: newPassword
    })

    if (error) throw error

    return {
      user: data.user,
      error: null
    }
  } catch (error) {
    console.error('Update password error:', error)
    return {
      user: null,
      error: error.message
    }
  }
}

/**
 * Update user email
 * @param {string} newEmail - New email address
 * @returns {Promise<{user, error}>}
 */
export const updateEmail = async (newEmail) => {
  try {
    const { data, error } = await supabase.auth.updateUser({
      email: newEmail
    })

    if (error) throw error

    return {
      user: data.user,
      error: null
    }
  } catch (error) {
    console.error('Update email error:', error)
    return {
      user: null,
      error: error.message
    }
  }
}
