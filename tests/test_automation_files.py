import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


class AutomationFileTests(unittest.TestCase):
    def test_worktree_automation_has_no_repository_list_refresh(self) -> None:
        reusable = (
            REPO_ROOT / ".github" / "workflows" / "reusable_worktree_generate.yml"
        ).read_text(encoding="utf-8")
        caller = (REPO_ROOT / "call_worktree_update.yml").read_text(encoding="utf-8")

        self.assertNotIn("update_repos_list", reusable)
        self.assertNotIn("Trigger Update Repositories List", reusable)
        self.assertIn(
            "https://raw.githubusercontent.com/HOAHRB/repos-management/main/scripts",
            reusable,
        )
        self.assertIn(
            "HOAHRB/repos-management/.github/workflows/"
            "reusable_worktree_generate.yml@main",
            caller,
        )
        self.assertNotIn("HITSZ-OpenAuto/hoa-moe", reusable)
        self.assertNotIn("token: ${{ secrets.PAT }}", reusable)
        self.assertIn("required: false", reusable)
        self.assertNotIn("PERSONAL_ACCESS_TOKEN", caller)
        self.assertNotIn("pull-requests: write", caller)
        self.assertNotIn("trigger_page_build:", caller)


if __name__ == "__main__":
    unittest.main()
