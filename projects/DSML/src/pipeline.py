"""Orchestration for classifying and resolving shipment exceptions."""

from tools import (
    calculate_damage_compensation,
    calculate_delay_compensation,
    calculate_lost_compensation,
)

try:
    from chains import classify_chain, draft_email_chain, escalate_chain
except ImportError:
    classify_chain = None
    draft_email_chain = None
    escalate_chain = None


STANDARD_ESCALATION_THRESHOLD = 500.0
PREMIUM_ESCALATION_THRESHOLD = 250.0


def _chain_result(chain, inputs: dict):
    """Invoke a configured LangChain chain and fail clearly if it is unavailable."""
    if chain is None:
        raise RuntimeError("chains.py is required to process an exception")
    return chain.invoke(inputs)


def _normalize_category(result) -> str:
    """Convert a chain response into one supported category or ``unknown``."""
    if isinstance(result, dict):
        result = result.get("category", result.get("text", ""))
    category = str(result).strip().lower()
    return category if category in {"delayed", "damaged", "lost"} else "unknown"


def process_exception(
    report: str,
    shipment_value: float,
    customer_tier: str = "standard",
) -> dict:
    """Process one shipment exception from classification through final drafting.

    The LLM classifies the report, while compensation and escalation remain
    deterministic business rules. Unknown categories always go to a manager.
    """
    # Validate the numeric input before passing it to a compensation calculator.
    value = float(shipment_value)
    if value < 0:
        raise ValueError("shipment_value must be non-negative")

    # Ask the classification chain to identify the exception type.
    tier = str(customer_tier).strip().lower()
    category = _normalize_category(_chain_result(classify_chain, {"report": report}))

    # Select the policy calculator for known categories; unknown reports receive no payout.
    calculators = {
        "delayed": calculate_delay_compensation,
        "damaged": calculate_damage_compensation,
        "lost": calculate_lost_compensation,
    }
    compensation = (
        calculators[category](value)
        if category in calculators
        else {
            "category": "unknown",
            "compensation_amount": 0.0,
            "reason": "The exception could not be classified",
        }
    )
    amount = compensation["compensation_amount"]

    # Premium customers use the lower escalation threshold. Unknown reports escalate automatically.
    threshold = (
        PREMIUM_ESCALATION_THRESHOLD
        if tier == "premium"
        else STANDARD_ESCALATION_THRESHOLD
    )
    escalated = category == "unknown" or amount > threshold

    # Both drafting chains receive the same structured context for their response.
    draft_inputs = {
        "report": report,
        "category": category,
        "shipment_value": value,
        "customer_tier": tier,
        "compensation": compensation,
    }

    # Escalated cases get an internal manager note; other cases get a customer email.
    if escalated:
        draft = _chain_result(escalate_chain, draft_inputs)
        steps = ["classified", "compensated", "escalated", "manager_note_drafted"]
    else:
        draft = _chain_result(draft_email_chain, draft_inputs)
        steps = ["classified", "compensated", "auto_resolved", "customer_email_drafted"]

    return {
        "category": category,
        "compensation": compensation,
        "compensation_amount": amount,
        "customer_tier": tier,
        "escalated": escalated,
        "escalation_threshold": threshold,
        "draft": draft,
        "steps": steps,
    }