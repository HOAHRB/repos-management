import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = REPO_ROOT / "scripts"


class MaintenanceScriptTests(unittest.TestCase):
    def test_list_consuming_shell_scripts_keep_the_temporary_file_interface(self) -> None:
        for name in (
            "add_workflow.sh",
            "add_secrets.sh",
            "approve_pr.sh",
            "close_pr.sh",
            "batch_delete.sh",
            "batch_trigger_workflows.sh",
        ):
            content = (SCRIPTS / name).read_text(encoding="utf-8")
            self.assertIn("repos_list.txt", content, name)
            self.assertNotIn("repos_management repos list", content, name)

    def test_course_maintenance_endpoints_use_the_local_course_organization(self) -> None:
        changed_files = (
            REPO_ROOT / ".env.example",
            SCRIPTS / "add_workflow.sh",
            SCRIPTS / "add_secrets.sh",
            SCRIPTS / "approve_pr.sh",
            SCRIPTS / "close_pr.sh",
            SCRIPTS / "batch_delete.sh",
            SCRIPTS / "batch_trigger_workflows.sh",
            SCRIPTS / "pull_or_clone.py",
        )

        for path in changed_files:
            content = path.read_text(encoding="utf-8")
            self.assertIn("HOAHRB-Courses", content, path.name)

        self.assertIn(
            "https://raw.githubusercontent.com/HOAHRB/repos-management/",
            (SCRIPTS / "add_workflow.sh").read_text(encoding="utf-8"),
        )

    def test_manual_python_scripts_keep_their_existing_entry_points(self) -> None:
        add_licenses = (SCRIPTS / "add_licenses.py").read_text(encoding="utf-8")
        pull_or_clone = (SCRIPTS / "pull_or_clone.py").read_text(encoding="utf-8")

        self.assertIn("def get_org_repos()", add_licenses)
        self.assertIn("from github import Github", pull_or_clone)


if __name__ == "__main__":
    unittest.main()
