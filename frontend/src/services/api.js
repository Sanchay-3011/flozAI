import { supabase } from './supabaseClient'

const BASE_URL = import.meta.env.VITE_API_URL || '/api'

async function request(path, options = {}) {
  let res
  const headers = { 'Content-Type': 'application/json' }

  try {
    const sessionRes = await supabase.auth.getSession()
    const token = sessionRes?.data?.session?.access_token
    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }
  } catch (err) {
    console.warn('Failed to retrieve session token:', err)
  }

  try {
    res = await fetch(`${BASE_URL}${path}`, {
      headers,
      ...options,
    })
  } catch (networkErr) {
    // Fetch itself failed — server is down or unreachable
    throw new Error('Cannot reach the backend. Is the FastAPI server running on port 8000?')
  }

  if (!res.ok) {
    let message = `Request failed (${res.status})`
    try {
      const body = await res.json()
      // FastAPI returns validation/app errors as { detail: "..." }
      if (typeof body.detail === 'string') {
        message = body.detail
      } else if (typeof body.detail === 'object') {
        // FastAPI validation errors are arrays of objects
        message = JSON.stringify(body.detail)
      } else if (body.message) {
        message = body.message
      } else if (body.error) {
        message = body.error
      } else {
        message = JSON.stringify(body)
      }
    } catch (_) {
      // Response body wasn't JSON
      message = res.statusText || message
    }
    throw new Error(message)
  }

  try {
    return await res.json()
  } catch (_) {
    throw new Error('Backend returned a non-JSON response.')
  }
}

export const flozApi = {
  // POST /parse  →  intent_parser.py
  parseIntent: (prompt) =>
    request('/parse', {
      method: 'POST',
      body: JSON.stringify({ user_input: prompt }),
    }),

  // POST /validate  →  validator.py
  validateWorkflow: (intent) =>
    request('/validate', {
      method: 'POST',
      body: JSON.stringify(intent),
    }),

  // POST /build  →  workflow_builder.py
  buildWorkflow: (intent) =>
    request('/build', {
      method: 'POST',
      body: JSON.stringify(intent),
    }),

  // GET /workflows
  listWorkflows: () => request('/workflows'),

  // POST /workflows/:id/activate
  activateWorkflow: (id) =>
    request(`/workflows/${id}/activate`, { method: 'POST' }),

  // GET /health
  healthCheck: () => request('/health'),

  // GET /integrations
  getIntegrations: () => request('/integrations'),

  // GET /integrations/registry
  getIntegrationRegistry: () => request('/integrations/registry'),

  // POST /integrations/:type
  saveIntegration: (type, data) =>
    request(`/integrations/${type}`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // DELETE /integrations/:type
  deleteIntegration: (type) =>
    request(`/integrations/${type}`, {
      method: 'DELETE',
    }),

  // GET /ai/providers
  getAiProviders: () => request('/ai/providers'),

  // POST /ai/providers/connect
  connectAiProvider: (provider, apiKey) =>
    request('/ai/providers/connect', {
      method: 'POST',
      body: JSON.stringify({ provider, api_key: apiKey }),
    }),

  // DELETE /ai/providers/:provider
  disconnectAiProvider: (provider) =>
    request(`/ai/providers/${provider}`, {
      method: 'DELETE',
    }),

  // GET /agents
  getAgents: () => request('/agents'),

  // POST /agents/test
  testAgent: (agentType, inputs, provider = null, tier = 'fast') =>
    request('/agents/test', {
      method: 'POST',
      body: JSON.stringify({ agent_type: agentType, inputs, provider, tier }),
    }),

  // POST /execute
  executeWorkflow: (workflow) =>
    request('/execute', {
      method: 'POST',
      body: JSON.stringify(workflow),
    }),

  // POST /conditions/parse
  parseCondition: (text) =>
    request('/conditions/parse', {
      method: 'POST',
      body: JSON.stringify({ text }),
    }),

  // GET /oauth/:provider/authorize
  getOAuthAuthorizeUrl: (provider) =>
    request(`/oauth/${provider}/authorize`),

  // GET /capabilities
  getCapabilities: () =>
    request('/capabilities'),
}