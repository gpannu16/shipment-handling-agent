"""Gradio interface for the Shipment Exception Desk."""

import json

import gradio as gr

from pipeline import process_exception
from session import TriageSession


session = TriageSession()


def _format_result(result: dict) -> str:
    """Format one pipeline result for the outcome panel."""
    route = "Escalated to manager" if result["escalated"] else "Auto-resolved"
    draft = result["draft"]
    if not isinstance(draft, str):
        draft = json.dumps(draft, indent=2, default=str)
    return (
        f"### {route}\n"
        f"**Category:** {result['category']}  \n"
        f"**Compensation:** ${result['compensation_amount']:.2f}  \n"
        f"**Steps:** {' -> '.join(result['steps'])}\n\n"
        f"**Draft**\n\n{draft}"
    )


def _log_rows() -> list[list[str | float]]:
    """Return the session log in a compact table-friendly format."""
    return [
        [
            result.get("category", "unknown"),
            result.get("compensation_amount", 0.0),
            "Yes" if result.get("escalated") else "No",
            " -> ".join(result.get("steps", [])),
        ]
        for result in session.log
    ]


def submit_report(
    report: str,
    shipment_value: float,
    customer_tier: str,
) -> tuple[str, list[list[str | float]]]:
    """Process a submitted report and update the running triage log."""
    if not report or not report.strip():
        return "**Enter an exception report before submitting.**", _log_rows()
    if shipment_value is None:
        return "**Enter a shipment value before submitting.**", _log_rows()

    try:
        result = process_exception(report, shipment_value, customer_tier)
    except Exception as error:
        return f"**Unable to process report:** `{error}`", _log_rows()

    session.record(result)
    return _format_result(result), _log_rows()


def daily_summary() -> str:
    """Render the current session's aggregated daily summary."""
    summary = session.generate_daily_summary()
    return (
        f"### Daily Triage Summary\n"
        f"- **Exceptions processed:** {summary['total_exceptions']}\n"
        f"- **Total compensation:** ${summary['total_compensation']:.2f}\n"
        f"- **Escalation rate:** {summary['escalation_rate']:.1%}\n"
        f"- **Costliest category:** {summary['costliest_category'] or 'None'}\n"
        f"- **Compensation by category:** `{summary['compensation_by_category']}`"
    )


def build_app() -> gr.Blocks:
    """Create and return the Gradio application."""
    with gr.Blocks(title="Northwind Shipment Exception Desk") as app:
        gr.Markdown("# Shipment Exception Desk")
        gr.Markdown("Submit an exception report for automated triage.")

        with gr.Row():
            with gr.Column(scale=1):
                report = gr.Textbox(
                    label="Exception report",
                    placeholder="Describe what happened to the shipment...",
                    lines=7,
                )
                shipment_value = gr.Number(
                    label="Shipment value ($)", minimum=0, precision=2
                )
                customer_tier = gr.Dropdown(
                    ["standard", "premium"],
                    value="standard",
                    label="Customer tier",
                )
                submit = gr.Button("Process exception", variant="primary")
            with gr.Column(scale=2):
                outcome = gr.Markdown(label="Outcome")

        gr.Markdown("## Daily Triage Log")
        log = gr.Dataframe(
            headers=["Category", "Compensation", "Escalated", "Steps"],
            datatype=["str", "number", "str", "str"],
            value=[],
            interactive=False,
        )
        summary_button = gr.Button("Show daily summary")
        summary = gr.Markdown()

        submit.click(
            submit_report,
            inputs=[report, shipment_value, customer_tier],
            outputs=[outcome, log],
        )
        summary_button.click(daily_summary, outputs=summary)

    return app


app = build_app()


if __name__ == "__main__":
    app.launch()
