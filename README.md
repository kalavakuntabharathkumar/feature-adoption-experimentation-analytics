# Feature Adoption Experimentation & Analytics

A reproducible analytics portfolio project for a fictional mobile-learning product. It generates synthetic event data, builds an experiment analysis dataset, runs statistical tests, exports Power BI-ready CSVs and an Excel workbook, and includes PostgreSQL schema/query examples.

> **Data note:** All records and outcomes are synthetic. The adoption uplift in this demo is generated data, not evidence of a real product experiment.

## What it does
- Creates a configurable synthetic event log (default: 2.4M events across 48,000 users).
- Models six A/B experiments with user-level assignment and adoption outcomes.
- Uses PostgreSQL-compatible SQL for event aggregation and experiment cohorts.
- Uses pandas, SciPy and statsmodels for proportions tests, confidence intervals, and multiple-testing correction.
- Exports four dashboard-ready datasets and an Excel workbook with summary sheets.
- Includes Power BI dashboard specifications and a manual Excel workflow.

## Quick start
Python 3.10+ recommended.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python run_pipeline.py --users 48000 --events 2400000 --seed 42
```

For a quick smoke test:
```bash
python run_pipeline.py --users 3000 --events 30000 --seed 42
```

Outputs are written to `outputs/`:
- `events.csv`
- `experiment_assignments.csv`
- `experiment_results.csv`
- `dashboard_adoption_trends.csv`
- `dashboard_metric_summary.csv`
- `dashboard_experiment_comparison.csv`
- `analytics_report.xlsx`

## PostgreSQL
Create a database, then run `sql/01_schema.sql`. `sql/02_analysis_queries.sql` includes reusable queries. The Python pipeline runs locally without requiring PostgreSQL so the project is easy to reproduce; its output columns align with the SQL schema.

## Power BI
Use **Get Data → Text/CSV** to import the dashboard CSV files. Follow `powerbi/DASHBOARD_GUIDE.md` for relationships, measures, visuals, and recommended layout. A native `.pbix` file is not included because it must be authored in Power BI Desktop.

## Project structure
```text
feature_adoption_experimentation_analytics/
├── data/                 # generated data is not committed
├── outputs/              # generated files
├── sql/
├── src/
├── powerbi/
├── tests/
└── run_pipeline.py
```

## Important interpretation notes
- Statistical significance does not by itself establish product value or causality beyond the experiment design.
- This demo uses independent user-level assignment per experiment and binary adoption outcomes.
- The generated dataset is intentionally synthetic; never present its metrics as results from an actual employer or client.
