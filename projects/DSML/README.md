# Shipment Exception Desk

A LangChain-based workflow for triaging shipment exceptions, calculating compensation, escalating edge cases, and presenting results through a simple Gradio interface.

## Project overview

Northwind Logistics receives shipment exception reports for delayed, damaged, or lost items. Manual triage is slow and inconsistent because analysts must:

- classify each report,
- calculate a compensation amount based on policy,
- decide whether the case should be escalated,
- draft either a customer response or a manager note,
- summarize daily operations and identify the most expensive category.

This project automates that process using a lightweight LLM-driven pipeline with deterministic business rules around compensation and escalation.

## What this project does

- Classifies incoming exception reports as delayed, damaged, lost, or unknown
- Calculates compensation using business rules for each category
- Escalates high-value cases or unclassifiable reports to a manager
- Drafts either a customer email or an internal escalation note
- Tracks processed exceptions in a daily session log
- Aggregates total compensation, escalation rate, and costliest category
- Exposes the workflow through a small Gradio app

## Tech stack

- Python
- LangChain
- OpenAI chat model
- Gradio
- dotenv

## Project architecture

- `llm.py` — shared LLM setup using the configured OpenAI model
- `chains.py` — LLM chains for classification, escalation drafting, and customer email drafting
- `tools.py` — compensation calculators for delay, damage, and loss cases
- `pipeline.py` — orchestration logic that connects classification, compensation, escalation, and drafting
- `session.py` — daily triage log and aggregation logic
- `app.py` — Gradio interface for end-user interaction
- `triage_check.py` — smoke tests for the four required routing scenarios
- `main.py` — CLI runner for single-report testing

## Setup

1. Create and activate a virtual environment:

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Configure your environment variables:

```bash
cp .env.example .env
```

Then update `.env` with your OpenAI key:

```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
```

## Run the app

```bash
python app.py
```

This launches the Gradio interface where you can submit a shipment exception report and view the outcome plus the daily summary.

## Run the smoke test

```bash
python triage_check.py
```

This validates the four required scenarios:

- mild delay → not escalated
- high-value loss → escalated
- minor damage → not escalated
- unclassifiable report → escalated

## CLI runner

```bash
python main.py
```

This lets you test the processing flow interactively from the terminal for a single exception.

## Business logic highlights

The compensation rules in this project are intentionally deterministic:

- delayed shipments: 10% of shipment value, capped at $100
- damaged shipments: 50% of shipment value, capped at $500
- lost shipments: 100% of shipment value, capped at $1,000

Escalation logic:

- unknown categories automatically escalate
- premium customers use a lower escalation threshold than standard customers
- any case above the threshold is escalated to a manager

## Daily summary output

The session layer calculates:

- total exceptions processed,
- total compensation paid,
- escalation rate,
- compensation by category,
- the costliest category for the day.

## Project files

- `Problem_Statement_and_Milestones.md` — original assignment and milestone breakdown
- `Getting_Started_With_VSCode.md` — editor setup notes
- `.env.example` — environment template
- `.gitignore` — excludes venv and sensitive environment files
- `requirements.txt` — Python dependencies

## Why this project is relevant for interviews

This project demonstrates practical AI application design with a clear workflow:

- LLM-powered classification with structured business rules
- deterministic control flow for operational decisions
- reusable prompt chains and orchestration logic
- a user-facing interface for business operations
- session-level reporting and summary metrics

It is a good example of combining AI reasoning with rule-based operational logic in a real-world business process.

## Future extensions

Potential enhancements include:

- additional exception types such as wrong-item shipment,
- persistent log storage,
- customer repeat-incident detection,
- configurable escalation thresholds,
- alerting and dashboard improvements.

## License

This project is intended for learning and portfolio use. Add a license if you plan to publish it publicly on GitHub.

## Notes

This repository is best suited for portfolio visibility and project demos. Before publishing to GitHub, consider adding a short architecture diagram, screenshots of the Gradio app, and a demo video or GIF if you want to make the repository more compelling to interviewers.
