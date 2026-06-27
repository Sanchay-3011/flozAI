"""
Condition Evaluator
Safe evaluation of step conditions against workflow execution context.
No eval() — uses explicit field resolution and comparison only.
"""
from typing import Any, Dict, Optional, Tuple
from flozai.utils.logger import get_logger

logger = get_logger(__name__)


def resolve_field(field_path: str, context: Dict[str, Any]) -> Tuple[bool, Any]:
    """
    Resolve a dot-notation field path against a context dictionary.
    Returns (found: bool, value: Any).
    
    Example:
        resolve_field("lead.status", {"lead": {"status": "new"}})
        → (True, "new")
    """
    if not field_path or not context:
        return False, None

    parts = field_path.strip().split(".")
    current = context

    for part in parts:
        if isinstance(current, dict):
            if part in current:
                current = current[part]
            else:
                # Try case-insensitive match
                lower_part = part.lower()
                matched = False
                for key in current:
                    if key.lower() == lower_part:
                        current = current[key]
                        matched = True
                        break
                if not matched:
                    return False, None
        else:
            return False, None

    return True, current


def evaluate_condition(condition: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluate a step condition against the execution context.
    
    Args:
        condition: {
            "enabled": true,
            "field": "lead.status",
            "operator": "equals",
            "value": "new",
            "natural_language": "Only if the lead is new"
        }
        context: The accumulated execution context dict.
    
    Returns:
        {
            "passed": bool,
            "field_value": <actual value found>,
            "reason": "Human-readable explanation"
        }
    """
    if not condition:
        return {"passed": True, "field_value": None, "reason": "No condition defined"}

    if not condition.get("enabled", True):
        return {"passed": True, "field_value": None, "reason": "Condition is disabled"}

    field = condition.get("field", "")
    operator = condition.get("operator", "")
    compare_value = condition.get("value")

    VALID_OPERATORS = {"equals", "not_equals", "contains", "greater_than", "exists", "not_exists"}
    if operator not in VALID_OPERATORS:
        return {
            "passed": False,
            "field_value": None,
            "reason": f"Invalid operator: '{operator}'. Must be one of: {', '.join(sorted(VALID_OPERATORS))}"
        }

    # Resolve the field from context
    found, field_value = resolve_field(field, context)

    # ── EXISTS / NOT_EXISTS ──
    if operator == "exists":
        passed = found and field_value is not None
        return {
            "passed": passed,
            "field_value": field_value,
            "reason": f"'{field}' {'exists' if passed else 'does not exist'}"
        }

    if operator == "not_exists":
        passed = not found or field_value is None
        return {
            "passed": passed,
            "field_value": field_value,
            "reason": f"'{field}' {'does not exist' if passed else 'exists'}"
        }

    # For the remaining operators, if the field wasn't found, condition fails
    if not found:
        return {
            "passed": False,
            "field_value": None,
            "reason": f"Field '{field}' not found in context"
        }

    # Normalize both sides for comparison
    field_str = str(field_value).strip().lower() if field_value is not None else ""
    compare_str = str(compare_value).strip().lower() if compare_value is not None else ""

    # ── EQUALS ──
    if operator == "equals":
        passed = field_str == compare_str
        return {
            "passed": passed,
            "field_value": field_value,
            "reason": f"'{field}' is {'equal to' if passed else 'not equal to'} '{compare_value}'"
        }

    # ── NOT_EQUALS ──
    if operator == "not_equals":
        passed = field_str != compare_str
        return {
            "passed": passed,
            "field_value": field_value,
            "reason": f"'{field}' is {'not equal to' if passed else 'equal to'} '{compare_value}'"
        }

    # ── CONTAINS ──
    if operator == "contains":
        passed = compare_str in field_str
        return {
            "passed": passed,
            "field_value": field_value,
            "reason": f"'{field}' {'contains' if passed else 'does not contain'} '{compare_value}'"
        }

    # ── GREATER_THAN (numbers only) ──
    if operator == "greater_than":
        try:
            num_field = float(str(field_value))
            num_compare = float(str(compare_value))
            passed = num_field > num_compare
            return {
                "passed": passed,
                "field_value": field_value,
                "reason": f"'{field}' ({num_field}) is {'greater than' if passed else 'not greater than'} {num_compare}"
            }
        except (ValueError, TypeError):
            return {
                "passed": False,
                "field_value": field_value,
                "reason": f"Cannot compare '{field}' numerically — value '{field_value}' or '{compare_value}' is not a number"
            }

    # Fallback (should never reach here)
    return {"passed": False, "field_value": field_value, "reason": "Unknown evaluation error"}
