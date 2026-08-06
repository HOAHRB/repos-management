import os
import subprocess
from pathlib import Path

if __package__:
    from .fetch_repos import ORG_NAME, PERSONAL_ACCESS_TOKEN, get_repos
else:
    from fetch_repos import ORG_NAME, PERSONAL_ACCESS_TOKEN, get_repos

TARGET_FOLDER = Path("./")

if http_proxy := os.getenv("HTTP_PROXY"):
    os.environ["HTTP_PROXY"] = http_proxy
if https_proxy := os.getenv("HTTPS_PROXY"):
    os.environ["HTTPS_PROXY"] = https_proxy

def clone_or_update_repo(repo_url: str, target_path: Path):
    """克隆或更新仓库"""
    if target_path.exists():
        if (target_path / ".git").is_dir():
            print(f"Switching to main branch and updating repository: {repo_url}")
            try:
                subprocess.run(
                    ["git", "-C", str(target_path), "checkout", "main"], check=True
                )
            except subprocess.CalledProcessError:
                print(
                    f"Failed to switch to main branch in {target_path}. Skipping update."
                )
                raise
            subprocess.run(["git", "-C", str(target_path), "pull"], check=True)
        else:
            raise Exception(f"Invalid Git directory: {target_path}")
    else:
        print(f"Cloning repository: {repo_url}")
        subprocess.run(["git", "clone", repo_url, str(target_path)], check=True)


def main():
    TARGET_FOLDER.mkdir(parents=True, exist_ok=True)

    for repo_name in get_repos(ORG_NAME, PERSONAL_ACCESS_TOKEN):
        repo_url = f"git@github.com:{ORG_NAME}/{repo_name}.git"
        target_path = TARGET_FOLDER / repo_name

        try:
            clone_or_update_repo(repo_url, target_path)
        except subprocess.CalledProcessError as e:
            print(f"Failed to process repository {repo_name}: {e}")
            raise
        except Exception as e:
            print(f"Error: {e}")
            raise


if __name__ == "__main__":
    main()
