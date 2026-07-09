import json
from pathlib import Path

import git


def get_git_history(repo_path: Path, limit: int = 5) -> list[dict]:
    """Retrieves recent git commit log information using GitPython."""
    try:
        repo = git.Repo(repo_path, search_parent_directories=True)
        commits_data = []

        # Iterate over the last N commits of the active branch
        for commit in list(repo.iter_commits(max_count=limit)):
            commits_data.append(
                {
                    "hash": commit.hexsha[:7],
                    "author": commit.author.name,
                    "date": commit.authored_datetime.strftime("%Y-%m-%d"),
                    "message": commit.message.strip(),
                }
            )
        return commits_data
    except (git.InvalidGitRepositoryError, git.NoSuchPathError) as e:
        print(f"Error accessing git repository: {e}")
        return []


def main():
    print("Initializing Git History CV Extractor (using GitPython)...")

    # Define output paths
    project_dir = Path(__file__).resolve().parent
    output_dir = project_dir / "output"
    output_dir.mkdir(exist_ok=True)

    # Fetch history
    commits = get_git_history(project_dir)

    print("\n--- Recent Git Commits ---")
    for c in commits:
        print(f"{c['hash']} | {c['author']} | {c['date']} | {c['message']}")
    print("--------------------------\n")

    # Structure data for AI
    summary_data = {
        "project": "git-history-cv-extractor",
        "description": "Dumping git metadata for CV construction",
        "recent_commits": commits,
    }

    # Save outputs
    output_file = output_dir / "summary.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(summary_data, f, indent=2)

    rel_path = output_file.relative_to(project_dir)
    print(f"Extraction complete! Context dumped to: {rel_path}")


if __name__ == "__main__":
    main()
# end of file
