"""
03_analysis_stats.py
Reads data/results.csv and produces:
  1) data/top_3.txt         – top 3 highest & bottom 3 lowest per numeric stat
  2) data/results2.csv      – median/mean/std overall and per-Team
  3) data/plots/*.png       – histograms per stat (league-wide + per-Team)
"""

import os
import re
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ── Configuration ──────────────────────────────────────────────────────────
INPUT_CSV   = os.path.join("data", "results.csv")
TOP3_TXT    = os.path.join("data", "top_3.txt")
RESULT2_CSV = os.path.join("data", "results2.csv")
PLOTS_DIR   = os.path.join("data", "plots")

ID_COLS = ["Player", "Nation", "Team", "Position", "Age"]


def safe_filename(name: str) -> str:
    """Convert a column name into a filesystem-safe string."""
    return re.sub(r'[^\w\-]', '_', name)


def load_and_clean(path: str) -> pd.DataFrame:
    """Load CSV, replace 'N/a' with NaN, strip '%' from percentage values,
    and coerce every non-identifier column to numeric."""
    df = pd.read_csv(path, encoding="utf-8-sig")
    df.replace("N/a", pd.NA, inplace=True)

    stat_cols = [c for c in df.columns if c not in ID_COLS]
    for col in stat_cols:
        # strip trailing '%' if present (e.g. "33.3%")
        df[col] = df[col].astype(str).str.rstrip("%")
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


# ── 1) Top 3 / Bottom 3 ──────────────────────────────────────────────────
def write_top3(df: pd.DataFrame, path: str):
    stat_cols = [c for c in df.columns if c not in ID_COLS]
    lines = []
    for col in stat_cols:
        valid = df.dropna(subset=[col])
        if valid.empty:
            continue
        top3 = valid.nlargest(3, col)
        bot3 = valid.nsmallest(3, col)

        lines.append(f"{'='*60}")
        lines.append(f"  {col}")
        lines.append(f"{'='*60}")
        lines.append("  TOP 3 (highest):")
        for _, row in top3.iterrows():
            lines.append(f"    {row['Player']:30s}  {row['Team']:25s}  {row[col]}")
        lines.append("  BOTTOM 3 (lowest):")
        for _, row in bot3.iterrows():
            lines.append(f"    {row['Player']:30s}  {row['Team']:25s}  {row[col]}")
        lines.append("")

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"[1] Wrote {path}  ({len(stat_cols)} statistics)")


# ── 2) Summary statistics ────────────────────────────────────────────────
def write_summary(df: pd.DataFrame, path: str):
    stat_cols = [c for c in df.columns if c not in ID_COLS]
    records = []

    # League-wide
    for col in stat_cols:
        s = df[col].dropna()
        records.append({
            "Team": "ALL (League)",
            "Statistic": col,
            "Median": s.median() if len(s) else None,
            "Mean":   s.mean()   if len(s) else None,
            "Std":    s.std()    if len(s) else None,
        })

    # Per-Team
    for team, grp in df.groupby("Team"):
        for col in stat_cols:
            s = grp[col].dropna()
            records.append({
                "Team": team,
                "Statistic": col,
                "Median": s.median() if len(s) else None,
                "Mean":   s.mean()   if len(s) else None,
                "Std":    s.std()    if len(s) else None,
            })

    out = pd.DataFrame(records)
    out.to_csv(path, index=False, encoding="utf-8-sig")
    print(f"[2] Wrote {path}  ({len(out)} rows)")


# ── 3) Histograms ────────────────────────────────────────────────────────
def draw_histograms(df: pd.DataFrame, plots_dir: str):
    os.makedirs(plots_dir, exist_ok=True)
    stat_cols = [c for c in df.columns if c not in ID_COLS]
    teams = sorted(df["Team"].dropna().unique())
    count = 0

    for col in stat_cols:
        series = df[col].dropna()
        if series.empty:
            continue

        # --- league-wide histogram ---
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.hist(series, bins=30, edgecolor="black", alpha=0.75)
        ax.set_title(f"{col} – All Teams", fontsize=12)
        ax.set_xlabel(col)
        ax.set_ylabel("Count")
        fig.tight_layout()
        fname = os.path.join(plots_dir, f"{safe_filename(col)}_all.png")
        fig.savefig(fname, dpi=100)
        plt.close(fig)
        count += 1

        # --- per-team histograms ---
        for team in teams:
            team_series = df.loc[df["Team"] == team, col].dropna()
            if team_series.empty:
                continue
            fig, ax = plt.subplots(figsize=(8, 4))
            ax.hist(team_series, bins=20, edgecolor="black", alpha=0.75)
            ax.set_title(f"{col} – {team}", fontsize=11)
            ax.set_xlabel(col)
            ax.set_ylabel("Count")
            fig.tight_layout()
            fname = os.path.join(
                plots_dir,
                f"{safe_filename(col)}_{safe_filename(team)}.png"
            )
            fig.savefig(fname, dpi=100)
            plt.close(fig)
            count += 1

    print(f"[3] Saved {count} histogram images to {plots_dir}/")


# ── Main ──────────────────────────────────────────────────────────────────
def main():
    df = load_and_clean(INPUT_CSV)
    print(f"Loaded {len(df)} rows, {len(df.columns)} columns from {INPUT_CSV}")

    write_top3(df, TOP3_TXT)
    write_summary(df, RESULT2_CSV)
    draw_histograms(df, PLOTS_DIR)

    print("Done.")


if __name__ == "__main__":
    main()
