"""Daily triage logging and aggregation for shipment exceptions."""

from collections import defaultdict
from typing import Any


class TriageSession:
    """Keep processed exceptions and generate an aggregated daily summary."""

    def __init__(self) -> None:
        self.log: list[dict[str, Any]] = []

    def record(self, result: dict[str, Any]) -> dict[str, Any]:
        """Add one pipeline result to the session and return it unchanged."""
        self.log.append(result)
        return result

    def clear(self) -> None:
        """Remove all records from the current triage session."""
        self.log.clear()

    def generate_daily_summary(self) -> dict[str, Any]:
        """Aggregate payouts, escalation rate, and the costliest category."""
        total_exceptions = len(self.log)
        total_compensation = sum(
            float(result.get("compensation_amount", 0.0)) for result in self.log
        )
        escalated_count = sum(1 for result in self.log if result.get("escalated", False))

        compensation_by_category: dict[str, float] = defaultdict(float)
        for result in self.log:
            category = str(result.get("category", "unknown"))
            compensation_by_category[category] += float(
                result.get("compensation_amount", 0.0)
            )

        costliest_category = None
        if compensation_by_category:
            costliest_category = max(
                compensation_by_category,
                key=compensation_by_category.get,
            )

        return {
            "total_exceptions": total_exceptions,
            "total_compensation": round(total_compensation, 2),
            "escalated_count": escalated_count,
            "escalation_rate": round(
                escalated_count / total_exceptions if total_exceptions else 0.0,
                4,
            ),
            "compensation_by_category": {
                category: round(amount, 2)
                for category, amount in compensation_by_category.items()
            },
            "costliest_category": costliest_category,
        }


_default_session = TriageSession()
triage_log = _default_session.log


def record_exception(result: dict[str, Any]) -> dict[str, Any]:
    """Record a pipeline result in the module's default daily session."""
    return _default_session.record(result)


def generate_daily_summary() -> dict[str, Any]:
    """Return the aggregate summary for the module's default daily session."""
    return _default_session.generate_daily_summary()
