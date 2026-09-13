"""Simple command-line runner for one shipment exception."""

from pipeline import process_exception
from session import TriageSession


def main() -> None:
    """Read one report, process it, and print its result and daily summary."""
    report = input("Exception report: ").strip()
    shipment_value = float(input("Shipment value: "))
    customer_tier = input("Customer tier (standard/premium): ").strip() or "standard"

    result = process_exception(report, shipment_value, customer_tier)
    session = TriageSession()
    session.record(result)

    print(f"Category: {result['category']}")
    print(f"Compensation: ${result['compensation_amount']:.2f}")
    print(f"Escalated: {'yes' if result['escalated'] else 'no'}")
    print(f"Steps: {' -> '.join(result['steps'])}")
    print(f"Daily summary: {session.generate_daily_summary()}")


if __name__ == "__main__":
    main()
