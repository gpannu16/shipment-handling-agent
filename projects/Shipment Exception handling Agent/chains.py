"""LangChain chains used by the shipment exception pipeline."""

import json
from typing import Any

from llm import get_model


class _LazyChain:
    """Invoke a prompt against the shared model only when a report is submitted."""

    def __init__(self, prompt_builder):
        self._prompt_builder = prompt_builder

    def invoke(self, inputs: dict[str, Any]) -> str:
        """Build the prompt, call the model, and return its text content."""
        response = get_model().invoke(self._prompt_builder(inputs))
        content = response.content
        if isinstance(content, str):
            return content.strip()
        return str(content).strip()


def _classification_prompt(inputs: dict[str, Any]) -> str:
    return (
        "Classify this shipment exception into exactly one label: delayed, damaged, "
        "lost, or unknown. Return only the lowercase label and no explanation.\n\n"
        f"Report: {inputs.get('report', '')}"
    )


def _manager_prompt(inputs: dict[str, Any]) -> str:
    return (
        "Write a concise internal note for a logistics manager reviewing this shipment "
        "exception. Include the category, shipment value, compensation decision, and "
        "why escalation is needed. Do not invent facts.\n\n"
        f"Context:\n{json.dumps(inputs, indent=2, default=str)}"
    )


def _customer_email_prompt(inputs: dict[str, Any]) -> str:
    return (
        "Write a concise, empathetic customer-facing email about this shipment exception. "
        "State what happened, the compensation amount, and the next step. Do not invent "
        "facts or mention internal escalation rules.\n\n"
        f"Context:\n{json.dumps(inputs, indent=2, default=str)}"
    )


classify_chain = _LazyChain(_classification_prompt)
escalate_chain = _LazyChain(_manager_prompt)
draft_email_chain = _LazyChain(_customer_email_prompt)
