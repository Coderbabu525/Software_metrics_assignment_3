import git
import csv
import os
from datetime import datetime

def extract_code_churn(repo_path, output_csv="churn_data.csv"):
    """
    Extracts code churn metrics (added, deleted, modified lines per commit) from a Git repository.
    Saves the result as a CSV file for downstream IQ analysis.
    """

    if not os.path.exists(repo_path):
        raise FileNotFoundError(f"Repository path not found: {repo_path}")

    print(f"📂 Scanning repository at: {repo_path}")
    repo = git.Repo(repo_path)

    churn_records = []
    commits = list(repo.iter_commits())
    total_commits = len(commits)
    print(f"🔍 Found {total_commits} commits")

    for idx, commit in enumerate(commits, start=1):
        try:
            stats = commit.stats.files
            for file_path, file_stats in stats.items():
                loc_added = file_stats.get("insertions", 0)
                loc_deleted = file_stats.get("deletions", 0)
                loc_modified = loc_added + loc_deleted

                churn_records.append([
                    commit.hexsha[:8],
                    commit.author.name if commit.author else "Unknown",
                    commit.committed_datetime.strftime("%Y-%m-%d"),
                    file_path,
                    file_path.split("/")[0] if "/" in file_path else "root",
                    loc_added,
                    loc_deleted,
                    loc_modified
                ])
        except Exception as e:
            print(f"⚠️ Skipping commit {commit.hexsha[:8]} due to error: {e}")

        if idx % 50 == 0:
            print(f"Processed {idx}/{total_commits} commits...")

    print(f"✅ Extraction complete. Total records: {len(churn_records)}")

    # Write to CSV
    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "commit_hash", "author", "date", "file_path", "module",
            "loc_added", "loc_deleted", "loc_modified"
        ])
        writer.writerows(churn_records)

    print(f"📊 Churn data saved to: {output_csv}")
    return output_csv


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Extract code churn data from a Git repository.")
    parser.add_argument("--repo", required=True, help="Path to the local Git repository.")
    parser.add_argument("--out", default="churn_data.csv", help="Path to output CSV file.")
    args = parser.parse_args()

    extract_code_churn(args.repo, args.out)
