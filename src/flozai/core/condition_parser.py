"""
Condition Parser
Converts natural language condition descriptions into structured condition objects.
Uses regex-based heuristics for common patterns.
"""
import re
from typing import Dict, Any, Optional
from flozai.utils.logger import get_logger

logger = get_logger(__name__)

# Common field aliases — maps natural language terms to field paths
FIELD_ALIASES = {
    "lead status": "lead.status",
    "lead": "lead.status",
    "status": "status",
    "email": "email",
    "amount": "amount",
    "total": "total",
    "price": "price",
    "name": "name",
    "score": "score",
    "priority": "priority",
    "type": "type",
    "category": "category",
    "country": "country",
    "city": "city",
    "phone": "phone",
    "company": "company",
    "source": "source",
    "stage": "stage",
    "deal value": "deal.value",
    "deal stage": "deal.stage",
    "customer name": "customer.name",
    "customer email": "customer.email",
    "order status": "order.status",
    "order total": "order.total",
    "payment status": "payment.status",
}

# Operator keyword mappings
OPERATOR_KEYWORDS = {
    "equals": [
        r"\bis\b(?!\s+not\b)(?!\s+greater\b)(?!\s+more\b)(?!\s+less\b)(?!\s+above\b)(?!\s+below\b)",
        r"\bequals?\b",
        r"\b==\b",
        r"\bmatches\b",
    ],
    "not_equals": [
        r"\bis\s+not\b",
        r"\bisn'?t\b",
        r"\bdoes\s*n'?t\s+equal\b",
        r"\b!=\b",
        r"\bnot\s+equal\b",
    ],
    "contains": [
        r"\bcontains?\b",
        r"\bincludes?\b",
        r"\bhas\b",
    ],
    "greater_than": [
        r"\bgreater\s+than\b",
        r"\bmore\s+than\b",
        r"\babove\b",
        r"\bover\b",
        r"\bexceeds?\b",
        r"\b>\b",
        r"\bis\s+greater\b",
        r"\bis\s+more\b",
        r"\bis\s+above\b",
    ],
    "exists": [
        r"\bexists?\b",
        r"\bis\s+present\b",
        r"\bis\s+set\b",
        r"\bis\s+provided\b",
        r"\bhas\s+a\b",
    ],
    "not_exists": [
        r"\bdoes\s*n'?t\s+exist\b",
        r"\bnot\s+exist\b",
        r"\bis\s+missing\b",
        r"\bis\s+not\s+set\b",
        r"\bis\s+empty\b",
        r"\bis\s+blank\b",
    ],
}


def _find_field(text: str) -> Optional[str]:
    """Try to extract a field name from text using alias matching."""
    text_lower = text.lower()

    # Try longest aliases first for best match
    sorted_aliases = sorted(FIELD_ALIASES.keys(), key=len, reverse=True)
    for alias in sorted_aliases:
        if alias in text_lower:
            return FIELD_ALIASES[alias]

    # Fallback: try to extract a single-word field-like token
    # Look for patterns like "if <word> is/equals/contains ..."
    match = re.search(r'\b(?:if|when|only\s+if)\s+(?:the\s+)?(\w+)', text_lower)
    if match:
        candidate = match.group(1)
        if candidate not in {"the", "a", "an", "this", "that", "it", "is", "are"}:
            return candidate

    return None


def _find_operator(text: str) -> Optional[str]:
    """Detect which operator the text describes."""
    text_lower = text.lower()

    # Check not_equals and not_exists before equals and exists (more specific first)
    priority_order = ["not_equals", "not_exists", "greater_than", "contains", "exists", "equals"]

    for operator in priority_order:
        patterns = OPERATOR_KEYWORDS.get(operator, [])
        for pattern in patterns:
            if re.search(pattern, text_lower):
                return operator

    return None


def _find_value(text: str, field: str, operator: str) -> Optional[str]:
    """Extract the comparison value from the text."""
    if operator in ("exists", "not_exists"):
        return None

    text_lower = text.lower()

    # Try quoted values first: "new", 'new'
    quoted = re.search(r"""['"]([^'"]+)['"]""", text)
    if quoted:
        return quoted.group(1)

    # Try numeric values for greater_than
    if operator == "greater_than":
        numbers = re.findall(r'\b(\d+(?:\.\d+)?)\b', text)
        if numbers:
            return numbers[-1]  # use the last number found

    # Try to get value after the operator keyword
    # Pattern: "field is/equals VALUE" or "field contains VALUE"
    operator_patterns = {
        "equals": [r'\bis\s+(.+?)(?:\s*$)', r'\bequals?\s+(.+?)(?:\s*$)'],
        "not_equals": [r'\bis\s+not\s+(.+?)(?:\s*$)', r'\bisn\'?t\s+(.+?)(?:\s*$)'],
        "contains": [r'\bcontains?\s+(.+?)(?:\s*$)', r'\bincludes?\s+(.+?)(?:\s*$)'],
        "greater_than": [r'\bgreater\s+than\s+(.+?)(?:\s*$)', r'\bmore\s+than\s+(.+?)(?:\s*$)', r'\babove\s+(.+?)(?:\s*$)', r'\bover\s+(.+?)(?:\s*$)'],
    }

    patterns = operator_patterns.get(operator, [])
    for pattern in patterns:
        match = re.search(pattern, text_lower)
        if match:
            value = match.group(1).strip().strip("'\".,!?")
            # Clean up common trailing words
            value = re.sub(r'\s+(then|and|or|so|to)$', '', value)
            if value and value not in {"the", "a", "an"}:
                return value

    # Last resort: take the last word if it looks like a value
    words = text_lower.split()
    if len(words) >= 2:
        last_word = words[-1].strip("'\".,!?")
        if last_word not in {"if", "is", "the", "a", "an", "when", "only", "not", "exists", "exist"}:
            return last_word

    return None


def _generate_natural_language(field: str, operator: str, value: Optional[str]) -> str:
    """Generate a human-readable summary of the condition."""
    # Pretty-print the field name
    field_display = field.replace(".", " ").replace("_", " ").title()

    operator_phrases = {
        "equals": f"is {value}",
        "not_equals": f"is not {value}",
        "contains": f"contains {value}",
        "greater_than": f"is greater than {value}",
        "exists": "exists",
        "not_exists": "does not exist",
    }

    phrase = operator_phrases.get(operator, f"{operator} {value}")
    return f"Only run if {field_display} {phrase}"


def parse_condition(text: str) -> Dict[str, Any]:
    """
    Parse a natural language condition description into a structured condition.
    
    Args:
        text: Natural language like "only if lead is new" or "if amount > 1000"
    
    Returns:
        {
            "field": "lead.status",
            "operator": "equals",
            "value": "new",
            "natural_language": "Only run if Lead Status is new",
            "needs_clarification": false
        }
        
        OR if unclear:
        {
            "needs_clarification": true,
            "suggestion": "Could you specify..."
        }
    """
    if not text or not text.strip():
        return {
            "needs_clarification": True,
            "suggestion": "Please describe the condition, for example: 'Only if lead status is new'"
        }

    text = text.strip()

    # Detect field
    field = _find_field(text)
    if not field:
        return {
            "needs_clarification": True,
            "suggestion": f"I couldn't identify which field to check. Try something like 'if lead status is new' or 'if amount > 1000'."
        }

    # Detect operator
    operator = _find_operator(text)
    if not operator:
        # Default to "equals" if it seems like a simple statement
        operator = "equals"

    # Detect value
    value = _find_value(text, field, operator)
    if operator not in ("exists", "not_exists") and not value:
        return {
            "needs_clarification": True,
            "suggestion": f"I found the field '{field}' and operator '{operator}', but couldn't determine the value to compare. What value should '{field}' be compared to?"
        }

    # Generate natural language summary
    natural_language = _generate_natural_language(field, operator, value)

    return {
        "field": field,
        "operator": operator,
        "value": value,
        "natural_language": natural_language,
        "enabled": True,
        "needs_clarification": False,
    }
