# Power BI dashboard build guide

Import these generated files from `outputs/`:
- `dashboard_adoption_trends.csv`
- `dashboard_metric_summary.csv`
- `dashboard_experiment_comparison.csv`

## Suggested model
Use `experiment_id` as the experiment key. Keep experiment results at one row per experiment. The trend export is long-format to support a clustered column chart.

## Page 1 — Experiment overview
- KPI cards: experiment count, significant tests, FDR-significant tests, mean absolute lift.
- Clustered column chart: experiment name on axis, `adoption_rate_pct` as value, `series` as legend.
- Table: experiment, control rate, treatment rate, absolute lift, p-value, adjusted p-value.
- Slicer: experiment name.

## Page 2 — Statistical quality
- Scatter plot: sample size vs. absolute lift.
- Table: p-value, FDR-adjusted p-value, significance flags.
- Tooltip note: use adjusted p-values when interpreting six simultaneous experiments.

## Page 3 — Adoption by segment
For a real project, add platform, country, and tenure to the experiment outcome table, then compare treatment effects by segment. Avoid interpreting small subgroups without confidence intervals.

## Example DAX measures
```DAX
Experiment Count = DISTINCTCOUNT(dashboard_experiment_comparison[experiment_id])
Significant Tests = CALCULATE(COUNTROWS(dashboard_experiment_comparison),
    dashboard_experiment_comparison[significant_005] = TRUE())
Average Lift (pp) = AVERAGE(dashboard_experiment_comparison[absolute_lift_pp])
```

This repository provides Power BI-ready datasets and instructions, not a native PBIX file.
