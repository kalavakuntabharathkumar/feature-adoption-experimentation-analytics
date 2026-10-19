from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency, norm
from statsmodels.stats.proportion import proportions_ztest, proportion_confint
from statsmodels.stats.multitest import multipletests

EXPERIMENTS = [
    ("EXP-001", "Onboarding checklist", 0.31, 0.43),
    ("EXP-002", "Daily learning reminder", 0.31, 0.39),
    ("EXP-003", "Progress streaks", 0.31, 0.41),
    ("EXP-004", "Personalized course cards", 0.31, 0.44),
    ("EXP-005", "One-tap lesson resume", 0.31, 0.40),
    ("EXP-006", "Weekly progress summary", 0.31, 0.37),
]

def make_users(n, seed):
    rng = np.random.default_rng(seed)
    return pd.DataFrame({
        "user_id": np.arange(1, n + 1),
        "signup_date": pd.Timestamp("2025-01-01") + pd.to_timedelta(rng.integers(0, 365, n), unit="D"),
        "platform": rng.choice(["Android", "iOS"], n, p=[0.58, 0.42]),
        "country_group": rng.choice(["India", "North America", "Europe", "Other"], n, p=[0.56, 0.18, 0.14, 0.12]),
        "tenure_days": rng.integers(0, 730, n),
    })

def make_assignments(users, seed):
    rng = np.random.default_rng(seed + 11)
    frames = []
    for exp_id, feature, _, _ in EXPERIMENTS:
        arm = rng.choice(["control", "treatment"], len(users))
        frames.append(pd.DataFrame({
            "experiment_id": exp_id,
            "experiment_name": feature,
            "user_id": users.user_id.to_numpy(),
            "variant": arm,
            "assigned_at": pd.Timestamp("2026-01-01") + pd.to_timedelta(rng.integers(0, 28, len(users)), unit="D")
        }))
    return pd.concat(frames, ignore_index=True)

def make_events(users, n_events, seed):
    rng = np.random.default_rng(seed + 22)
    n_events = max(n_events, len(users))
    user_ids = np.concatenate([users.user_id.to_numpy(), rng.integers(1, len(users)+1, n_events-len(users))])
    rng.shuffle(user_ids)
    event_types = rng.choice(
        ["app_open", "lesson_view", "lesson_start", "lesson_complete", "course_search", "feature_adopted"],
        n_events, p=[.25, .25, .18, .15, .10, .07]
    )
    start = pd.Timestamp("2026-01-01")
    timestamps = start + pd.to_timedelta(rng.integers(0, 90*24*60, n_events), unit="m")
    return pd.DataFrame({"event_id": np.arange(1, n_events+1), "user_id": user_ids,
                         "event_timestamp": timestamps, "event_name": event_types,
                         "session_id": rng.integers(1, max(2, n_events//3), n_events)})

def analyse(assignments, seed):
    rng = np.random.default_rng(seed + 33)
    results = []
    for idx, (exp_id, name, control_rate, treatment_rate) in enumerate(EXPERIMENTS):
        a = assignments[assignments.experiment_id == exp_id].copy()
        # A fixed, seeded outcome draw creates a reproducible synthetic experiment.
        control_mask = a.variant.eq("control").to_numpy()
        rates = np.where(control_mask, control_rate, treatment_rate)
        # Small variation per experiment, not an assertion about real outcomes.
        rates = np.clip(rates + rng.normal(0, 0.002, len(a)), 0.01, 0.99)
        a["adopted"] = rng.binomial(1, rates)
        c = a[a.variant == "control"].adopted
        t = a[a.variant == "treatment"].adopted
        count = np.array([int(t.sum()), int(c.sum())])
        nobs = np.array([len(t), len(c)])
        stat, pvalue = proportions_ztest(count, nobs)
        cr, tr = c.mean(), t.mean()
        ci_low, ci_high = proportion_confint(int(t.sum()), len(t), method="wilson")
        results.append({
            "experiment_id": exp_id, "experiment_name": name,
            "control_users": len(c), "treatment_users": len(t),
            "control_adoption_rate": cr, "treatment_adoption_rate": tr,
            "absolute_lift_pp": (tr-cr)*100,
            "relative_lift_pct": ((tr-cr)/cr*100) if cr else np.nan,
            "treatment_ci_low": ci_low, "treatment_ci_high": ci_high,
            "z_statistic": stat, "p_value": pvalue,
            "significant_005": bool(pvalue < 0.05)
        })
    out = pd.DataFrame(results)
    out["p_value_fdr"] = multipletests(out.p_value, method="fdr_bh")[1]
    out["significant_fdr_005"] = out.p_value_fdr < 0.05
    return out

def make_dashboard_data(results, users):
    trend = results[["experiment_id","experiment_name","control_adoption_rate","treatment_adoption_rate","absolute_lift_pp"]].melt(
        id_vars=["experiment_id","experiment_name"], var_name="series", value_name="adoption_rate")
    trend["adoption_rate_pct"] = trend["adoption_rate"] * 100
    metric = pd.DataFrame([
        {"metric":"Experiments run","value":len(results),"definition":"Number of simulated A/B tests"},
        {"metric":"Users in cohort","value":len(users),"definition":"Synthetic user population"},
        {"metric":"Significant at p < 0.05","value":int(results.significant_005.sum()),"definition":"Unadjusted two-sided proportion z-test"},
        {"metric":"Significant after FDR","value":int(results.significant_fdr_005.sum()),"definition":"Benjamini-Hochberg adjusted p-value < 0.05"},
        {"metric":"Mean absolute lift (pp)","value":results.absolute_lift_pp.mean(),"definition":"Average treatment minus control adoption, percentage points"},
    ])
    comparison = results[["experiment_id","experiment_name","control_adoption_rate","treatment_adoption_rate",
                          "absolute_lift_pp","relative_lift_pct","p_value","p_value_fdr","significant_005","significant_fdr_005"]]
    return trend, metric, comparison

def run(n_users=48000, n_events=2400000, seed=42, output="outputs"):
    outdir = Path(output); outdir.mkdir(parents=True, exist_ok=True)
    users = make_users(n_users, seed)
    assignments = make_assignments(users, seed)
    events = make_events(users, n_events, seed)
    results = analyse(assignments, seed)
    trend, metrics, comparison = make_dashboard_data(results, users)
    events.to_csv(outdir/"events.csv", index=False)
    assignments.to_csv(outdir/"experiment_assignments.csv", index=False)
    results.to_csv(outdir/"experiment_results.csv", index=False)
    trend.to_csv(outdir/"dashboard_adoption_trends.csv", index=False)
    metrics.to_csv(outdir/"dashboard_metric_summary.csv", index=False)
    comparison.to_csv(outdir/"dashboard_experiment_comparison.csv", index=False)
    with pd.ExcelWriter(outdir/"analytics_report.xlsx", engine="openpyxl") as writer:
        results.to_excel(writer, sheet_name="Experiment Results", index=False)
        metrics.to_excel(writer, sheet_name="Metric Summary", index=False)
        comparison.to_excel(writer, sheet_name="Dashboard Data", index=False)
        users.head(1000).to_excel(writer, sheet_name="User Sample", index=False)
    print(f"Pipeline complete: {outdir.resolve()}")
    print(results[["experiment_id","experiment_name","absolute_lift_pp","p_value","p_value_fdr"]].to_string(index=False))
    print("Synthetic event rows:", len(events))
