"""
Agent Registry
Central mapping of agent_type → agent class.
"""
from flozai.core.agents.email_writer import EmailWriterAgent
from flozai.core.agents.lead_qualifier import LeadQualifierAgent
from flozai.core.agents.text_summarizer import TextSummarizerAgent
from flozai.core.agents.data_extractor import DataExtractorAgent
from flozai.core.agents.decision_maker import DecisionMakerAgent


# Instantiate all agents
_AGENTS = {
    "email_writer": EmailWriterAgent(),
    "lead_qualifier": LeadQualifierAgent(),
    "text_summarizer": TextSummarizerAgent(),
    "data_extractor": DataExtractorAgent(),
    "decision_maker": DecisionMakerAgent(),
}


def get_agent(agent_type: str):
    """Get an agent instance by type."""
    agent = _AGENTS.get(agent_type)
    if not agent:
        raise ValueError(f"Unknown agent type: {agent_type}. Available: {list(_AGENTS.keys())}")
    return agent


def get_all_agents_metadata() -> list:
    """Return metadata for all agents (for frontend)."""
    return [agent.to_metadata() for agent in _AGENTS.values()]
