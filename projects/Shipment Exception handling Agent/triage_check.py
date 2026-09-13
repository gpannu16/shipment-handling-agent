"""Smoke-test the four required exception-routing scenarios."""

import pipeline


class _FakeChain:
    """Small deterministic substitute for a LangChain runnable in this check."""

    def __init__(self, result):
        self.result = result

    def invoke(self, inputs):
        return self.result


def run_checks() -> None:
    """Run the required delay, loss, damage, and unknown routing checks."""
    pipeline.draft_email_chain = _FakeChain("customer email")
    pipeline.escalate_chain = _FakeChain("manager note")

    scenarios = [
        {
            "name": "mild delay",
            "report": "The shipment arrived two days late.",
            "category": "delayed",
            "shipment_value": 500,
            "customer_tier": "standard",
            "expected_escalated": False,
        },
        {
            "name": "high-value loss",
            "report": "The high-value shipment was lost in transit.",
            "category": "lost",
            "shipment_value": 1200,
            "customer_tier": "standard",
            "expected_escalated": True,
        },
        {
            "name": "minor damage claim",
            "report": "The box has minor visible damage.",
            "category": "damaged",
            "shipment_value": 100,
            "customer_tier": "standard",
            "expected_escalated": False,
        },
        {
            "name": "garbled report",
            "report": "xj4 ??? qqq",
            "category": "unknown",
            "shipment_value": 1,
            "customer_tier": "standard",
            "expected_escalated": True,
        },
    ]

    for scenario in scenarios:
        pipeline.classify_chain = _FakeChain(scenario["category"])
        result = pipeline.process_exception(
            scenario["report"],
            scenario["shipment_value"],
            scenario["customer_tier"],
        )
        assert result["category"] == scenario["category"]
        assert result["escalated"] is scenario["expected_escalated"]
        print(
            f"PASS: {scenario['name']} -> "
            f"{result['category']}, escalated={result['escalated']}"
        )

    print("All four triage scenarios passed.")


if __name__ == "__main__":
    run_checks()
