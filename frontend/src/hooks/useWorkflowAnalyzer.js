import { useMemo } from 'react';

/**
 * Analyzes a workflow to detect missing integrations or credentials.
 * Uses the same auth-type and description data as the backend integration registry.
 * 
 * @param {Object} workflow - The workflow object containing steps
 * @param {Object} userIntegrations - Object of connected integrations from useAppData
 * @returns {Array} List of missing integration requirements
 */
export function useWorkflowAnalyzer(workflow, userIntegrations = {}) {
  return useMemo(() => {
    if (!workflow || !workflow.steps || workflow.steps.length === 0) return [];

    const requirements = new Set();
    
    // Built-in integrations that don't require external credentials
    const noAuthIntegrations = new Set(['scheduler', 'webhook']);
    
    // Scan steps for integration types
    workflow.steps.forEach(step => {
      const integrationId = step.integration;
      
      // Filter out internal/core types and no-auth integrations
      if (integrationId && integrationId !== 'trigger' && integrationId !== 'action' && !noAuthIntegrations.has(integrationId.toLowerCase())) {
        requirements.add(integrationId.toLowerCase());
      }
    });

    const missing = Array.from(requirements).filter(id => {
      const integration = userIntegrations[id];
      return !integration || integration.status !== 'connected';
    }).map(id => {
      const reg = INTEGRATION_REGISTRY[id] || {};
      return {
        id,
        name: reg.name || id.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase()),
        type: reg.authType || 'apikey',
        description: reg.description || `Enables connectivity with ${id}.`,
      };
    });

    return missing;
  }, [workflow, userIntegrations]);
}

/**
 * Frontend mirror of the backend integration registry.
 * Auth types and descriptions stay in sync with integration_registry.py.
 */
const INTEGRATION_REGISTRY = {
  // Communication
  gmail:           { name: 'Gmail',           authType: 'oauth',  description: 'Send and receive emails via Gmail.' },
  slack:           { name: 'Slack',           authType: 'oauth',  description: 'Send messages and notifications to Slack channels.' },
  whatsapp:        { name: 'WhatsApp',        authType: 'apikey', description: 'Send messages via WhatsApp Business Cloud API.' },
  linkedin:        { name: 'LinkedIn',        authType: 'oauth',  description: 'Publish posts to your LinkedIn profile.' },
  // CRM
  hubspot:         { name: 'HubSpot',         authType: 'oauth',  description: 'Manage contacts, leads, and deals in HubSpot CRM.' },
  salesforce:      { name: 'Salesforce',      authType: 'oauth',  description: 'Manage enterprise CRM records in Salesforce.' },
  // Data & Storage
  google_sheets:   { name: 'Google Sheets',   authType: 'oauth',  description: 'Read and write rows in Google Sheets.' },
  notion:          { name: 'Notion',          authType: 'apikey', description: 'Create pages and database entries in Notion.' },
  airtable:        { name: 'Airtable',        authType: 'apikey', description: 'Create and read records in Airtable bases.' },
  // AI
  openai:          { name: 'OpenAI',          authType: 'apikey', description: 'Generate AI content via OpenAI GPT models.' },
  perplexity:      { name: 'Perplexity',      authType: 'apikey', description: 'Search the web and get AI-summarized answers.' },
  // Payments
  stripe:          { name: 'Stripe',          authType: 'apikey', description: 'Handle payments, invoices, and subscription events.' },
  // Scheduling
  google_calendar: { name: 'Google Calendar', authType: 'oauth',  description: 'Create and monitor Google Calendar events.' },
};
