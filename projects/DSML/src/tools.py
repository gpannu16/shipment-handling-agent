"""Rule-based compensation calculations for shipment exceptions."""


def _validate_shipment_value(shipment_value: float) -> float:
    value = float(shipment_value)
    if value < 0:
        raise ValueError("shipment_value must be non-negative")
    return value


def calculate_delay_compensation(shipment_value: float) -> dict:
    value = _validate_shipment_value(shipment_value)
    return {
        "category": "delayed",
        "compensation_amount": round(min(value * 0.10, 100.0), 2),
        "reason": "10% of shipment value for a delay, capped at $100",
    }


def calculate_damage_compensation(shipment_value: float) -> dict:
    value = _validate_shipment_value(shipment_value)
    return {
        "category": "damaged",
        "compensation_amount": round(min(value * 0.50, 500.0), 2),
        "reason": "50% of shipment value for damage, capped at $500",
    }


def calculate_lost_compensation(shipment_value: float) -> dict:
    value = _validate_shipment_value(shipment_value)
    return {
        "category": "lost",
        "compensation_amount": round(min(value, 1000.0), 2),
        "reason": "100% of shipment value for a lost shipment, capped at $1,000",
    }