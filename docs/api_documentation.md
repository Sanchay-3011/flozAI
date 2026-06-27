# FlozAI Supported Integrations and Actions

This document outlines all currently supported integrations, their actions, and triggers within the FlozAI ecosystem. This is derived directly from the `capabilities.yaml` configuration.

## Triggers

- **Form Submission** (`form_submission`): Triggered when a form is submitted (requires `form_id`).
- **New Record** (`new_record`): Triggered when a new record is created (requires `table_name`).
- **Scheduled Time** (`scheduled_time`): Triggered at a specific time or recurring interval.
- **New Email Received** (`new_email`): Triggered when a new email arrives matching criteria.
- **New Lead** (`new_lead`): Triggered when a new lead is created in a CRM.
- **Lead Score Change** (`lead_score_change`): Triggered when a lead score crosses a threshold.
- **New Payment** (`new_payment`): Triggered when a payment is received.
- **Failed Payment** (`failed_payment`): Triggered when a payment fails.
- **New Support Ticket** (`new_ticket`): Triggered when a new support ticket is created.
- **Webhook** (`webhook`): Triggered by an incoming HTTP webhook.
- **New Spreadsheet Row** (`new_row`): Triggered when a new row is added to a spreadsheet.
- **New Social Mention** (`new_mention`): Triggered when a keyword or brand is mentioned.
- **Manual Run** (`manual`): Triggered manually by the user.

## Supported Integrations and their Actions

### Generic CRM (`generic_crm`)
- **Actions:** Create Record, Update Record, Assign Owner, Enrich Contact, Add to Email Sequence, Sync Record
- **Triggers:** New Lead, New Record, Form Submission, Lead Score Change

### HubSpot (`hubspot`)
- **Actions:** Create Record, Update Record, Assign Owner, Add to Email Sequence, Enrich Contact
- **Triggers:** New Lead, Lead Score Change, New Record

### Salesforce (`salesforce`)
- **Actions:** Create Record, Update Record, Assign Owner, Enrich Contact, Sync Record
- **Triggers:** New Lead, New Record, Lead Score Change

### Notion (`notion`)
- **Actions:** Create Record, Create Page, Add to Database, Update Record, Add Spreadsheet Row
- **Triggers:** New Record

### Airtable (`airtable`)
- **Actions:** Create Record, List Records, Update Record, Add Spreadsheet Row
- **Triggers:** New Record, New Spreadsheet Row

### Slack (`slack`)
- **Actions:** Send Slack Message, Send Message, Post Message, Send Notification
- **Triggers:** None

### Gmail (`gmail`)
- **Actions:** Send Email
- **Triggers:** New Email Received

### Stripe (`stripe`)
- **Actions:** Log Event, Create Invoice
- **Triggers:** New Payment, Failed Payment

### QuickBooks (`quickbooks`)
- **Actions:** Create Record, Sync Record
- **Triggers:** None

### Google Sheets (`google_sheets`)
- **Actions:** Add Spreadsheet Row, Add Row, Read Range, Create Record, Update Record
- **Triggers:** New Spreadsheet Row

### Google Forms (`google_forms`)
- **Actions:** None
- **Triggers:** Form Submission

### WhatsApp (`whatsapp`)
- **Actions:** Send WhatsApp Message, Send Message, Send Notification
- **Triggers:** None

### LinkedIn (`linkedin`), Twitter / X (`twitter`), Instagram (`instagram`)
- **Actions:** Create Social Post (Instagram also supports Send Notification)
- **Triggers:** New Social Mention

### Mailchimp (`mailchimp`)
- **Actions:** Add to Email Sequence, Send Email
- **Triggers:** None

### OpenAI / AI (`openai`)
- **Actions:** Generate AI Content, AI Summarize, AI Analyze
- **Triggers:** None

### Perplexity / Web Search (`perplexity`)
- **Actions:** Search Web / News, Web Search, AI Web Search, Generate AI Content
- **Triggers:** None

### Asana (`asana`), Trello (`trello`), Jira (`jira`)
- **Actions:** Create Task, Update Record
- **Triggers:** New Record (Jira also supports New Support Ticket)

### Zendesk (`zendesk`), Intercom (`intercom`)
- **Actions:** Create Record, Update Record (Zendesk), Send Notification (Both)
- **Triggers:** New Support Ticket (Zendesk), New Lead/New Ticket (Intercom)

### Google Calendar (`google_calendar`)
- **Actions:** Check Availability, Create Appointment, Create Calendar Event, List Calendar Events, Create Record
- **Triggers:** New Record, Scheduled Time
