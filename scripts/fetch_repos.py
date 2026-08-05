import os
from pathlib import Path

import requests
from dotenv import load_dotenv

# Load the personal access token from the .env file
load_dotenv()
PERSONAL_ACCESS_TOKEN = os.getenv("PERSONAL_ACCESS_TOKEN")
ORG_NAME = os.getenv("ORG_NAME", "HOAHRB-Courses")


def get_repos(org_name, access_token, *, session=requests):
    url = f"https://api.github.com/orgs/{org_name}/repos"
    headers = {"Authorization": f"token {access_token}"}
    repos = []

    while url:
        response = session.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        # Keep only active course repositories; dot-prefixed repositories are metadata.
        data = [
            repo
            for repo in data
            if not repo["name"].startswith(".")
            and not repo["archived"]
            and not repo["is_template"]
            and repo["name"] != "HITSZ-OpenAuto"
            and not repo["name"].startswith("hoa-")
            and repo["name"] != "aextra"
            and not repo["name"].startswith("repos-")
            and not repo["name"].startswith("dev-")
        ]
        repos.extend(repo["name"] for repo in data)
        url = response.links.get("next", {}).get("url")

    return sorted(repos)


def main():
    repos = get_repos(ORG_NAME, PERSONAL_ACCESS_TOKEN)
    with Path("repos_list.txt").open("w") as f:
        f.write("\n".join(repos) + "\n")


if __name__ == "__main__":
    main()
