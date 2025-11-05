import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import datetime as dt

# -----------------------------
# IQ Attribute 1: Free-of-error
# -----------------------------

def free_of_error_checks(df):
    """
    Performs 10 data quality checks on churn_data.csv.
    Returns a dictionary with results for each check.
    """

    checks = {}

    # 1. Missing values
    checks["missing_values"] = df.isnull().sum().sum() == 0

    # 2. Invalid dates (future dates or non-date)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    checks["valid_dates"] = df["date"].notna().all() and (df["date"] <= dt.datetime.today()).all()

    # 3. Duplicated records
    checks["no_duplicates"] = not df.duplicated().any()

    # 4. Non-negative LOC values
    checks["non_negative_LOC"] = (
        (df["loc_added"] >= 0).all() and
        (df["loc_deleted"] >= 0).all() and
        (df["loc_modified"] >= 0).all()
    )

    # 5. LOC consistency check (modified = added + deleted)
    checks["LOC_consistency"] = (df["loc_modified"] == df["loc_added"] + df["loc_deleted"]).all()

    # 6. Reasonable LOC bounds (less than 10k lines per commit)
    checks["reasonable_LOC_bounds"] = (df["loc_modified"] < 10000).all()

    # 7. Commit hash length (should be 8 chars)
    checks["valid_commit_hash"] = df["commit_hash"].apply(lambda x: len(str(x)) == 8).all()

    # 8. Author field validity
    checks["author_validity"] = df["author"].apply(lambda x: isinstance(x, str) and len(x) > 1).all()

    # 9. Module field presence
    checks["module_field_presence"] = df["module"].notna().all()

    # 10. Temporal consistency (dates should not go backwards)
    checks["chronological_order"] = df["date"].is_monotonic_increasing or df["date"].is_monotonic_decreasing

    return checks


# -----------------------------
# IQ Attribute 2: Timeliness
# -----------------------------

def compute_timeliness(df):
    """
    Timeliness = fraction of records updated within the last 90 days
    """
    latest_date = df["date"].max()
    cutoff_date = latest_date - pd.Timedelta(days=90)
    recent_records = df[df["date"] >= cutoff_date]
    timeliness_score = len(recent_records) / len(df)
    return timeliness_score


# -----------------------------
# Visualization & Reporting
# -----------------------------

def visualize_iq_results(check_results, timeliness_score):
    """
    Visualizes results of the IQ checks.
    """
    plt.figure(figsize=(10, 5))
    sns.barplot(x=list(check_results.keys()), y=[1 if v else 0 for v in check_results.values()], palette="coolwarm")
    plt.xticks(rotation=60, ha="right")
    plt.title("Free-of-error Quality Checks (1 = Passed, 0 = Failed)")
    plt.ylabel("Result")
    plt.tight_layout()
    plt.savefig("iq_check_results.png", dpi=200)
    plt.show()

    print("\n🧮 Timeliness Score:", round(timeliness_score * 100, 2), "%")

    if timeliness_score < 0.5:
        print("⚠️ Warning: Most churn data are older than 90 days.")
    else:
        print("✅ Timeliness is satisfactory.")


def summarize_check_results(results):
    """
    Prints a readable summary of all checks.
    """
    print("\n=== Information Quality Summary ===")
    for check, passed in results.items():
        print(f"{check:30s}: {'✅ Pass' if passed else '❌ Fail'}")

    passed_count = sum(results.values())
    total_checks = len(results)
    print(f"\nOverall Free-of-error Score: {passed_count}/{total_checks} checks passed.")


# -----------------------------
# Manual Quality Attribute
# -----------------------------

def manual_check_reputability():
    """
    Example of a manual IQ attribute (cannot be automated).
    Checks the reputability of commit authors.
    """
    print("\n🔍 Manual Check: Reputability")
    print("This attribute evaluates whether commit authors belong to known, trusted organizations.")
    print("To verify:")
    print(" - Cross-check author emails/names with known contributor lists.")
    print(" - Use GitHub API or organization membership data (manual review).")
    print("Visualization idea:")
    print(" - Pie chart of commits per known organization vs unknown authors.")


# -----------------------------
# Main Entry
# -----------------------------

def main():
    csv_path = "churn_data.csv"

    if not os.path.exists(csv_path):
        print("❌ churn_data.csv not found! Please run code_churn_extractor.py first.")
        return

    df = pd.read_csv(csv_path)
    print(f"✅ Loaded churn data: {len(df)} records")

    # Perform Free-of-error checks
    results = free_of_error_checks(df)
    summarize_check_results(results)

    # Compute Timeliness
    timeliness = compute_timeliness(df)

    # Visualize results
    visualize_iq_results(results, timeliness)

    # Manual check
    manual_check_reputability()


if __name__ == "__main__":
    main()
