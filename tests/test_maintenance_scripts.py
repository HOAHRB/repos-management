import importlib
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import add_licenses

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = REPO_ROOT / "scripts"


class FakeOrgResponse:
    status_code = 200
    text = ""

    def __init__(
        self,
        payload: list[dict[str, object]],
        *,
        next_url: str | None = None,
    ) -> None:
        self._payload = payload
        self.links = {} if next_url is None else {"next": {"url": next_url}}

    def raise_for_status(self) -> None:
        pass

    def json(self) -> list[dict[str, object]]:
        return self._payload


class MaintenanceScriptTests(unittest.TestCase):
    def test_pull_or_clone_can_be_imported_as_a_scripts_module(self) -> None:
        module = importlib.import_module("scripts.pull_or_clone")

        self.assertTrue(callable(module.main))

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
        )

        for path in changed_files:
            content = path.read_text(encoding="utf-8")
            self.assertIn("HOAHRB-Courses", content, path.name)

        self.assertIn(
            "https://raw.githubusercontent.com/HOAHRB/repos-management/",
            (SCRIPTS / "add_workflow.sh").read_text(encoding="utf-8"),
        )
        self.assertIn(
            'os.getenv("ORG_NAME", "HOAHRB-Courses")',
            (SCRIPTS / "fetch_repos.py").read_text(encoding="utf-8"),
        )

    def test_manual_python_scripts_keep_their_existing_entry_points(self) -> None:
        add_licenses = (SCRIPTS / "add_licenses.py").read_text(encoding="utf-8")
        pull_or_clone = (SCRIPTS / "pull_or_clone.py").read_text(encoding="utf-8")

        self.assertIn("def get_org_repos()", add_licenses)
        self.assertIn(
            "from fetch_repos import ORG_NAME, PERSONAL_ACCESS_TOKEN, get_repos",
            pull_or_clone,
        )
        self.assertIn("for repo_name in get_repos(ORG_NAME, PERSONAL_ACCESS_TOKEN):", pull_or_clone)
        self.assertNotIn("bypass_list", pull_or_clone)
        self.assertNotIn("HITSZ-OpenAuto", pull_or_clone)

    def test_add_licenses_uses_the_shared_course_repository_selection(self) -> None:
        responses = iter(
            [
                FakeOrgResponse(
                    [
                        {"name": "CS101", "archived": False, "is_template": False},
                        {"name": ".github", "archived": False, "is_template": False},
                        {"name": "OLD", "archived": True, "is_template": False},
                        {"name": "template", "archived": False, "is_template": True},
                    ],
                    next_url="page-2",
                ),
                FakeOrgResponse(
                    [{"name": "hoa-moe", "archived": False, "is_template": False}]
                ),
            ]
        )

        with patch.object(
            add_licenses.requests,
            "get",
            side_effect=lambda *_a, **_k: next(responses),
        ):
            with patch.object(add_licenses, "org_name", "HOAHRB-Courses"):
                with patch.object(add_licenses, "token", "token"):
                    self.assertEqual(add_licenses.get_org_repos(), ["CS101", "hoa-moe"])

    def test_batch_trigger_does_not_filter_repositories_by_name(self) -> None:
        bash = shutil.which("bash")
        if bash is None:
            git_bash = Path(r"C:\Program Files\Git\bin\bash.exe")
            if git_bash.is_file():
                bash = str(git_bash)
        if bash is None:
            self.skipTest("bash is not available")

        with tempfile.TemporaryDirectory() as raw_dir:
            root = Path(raw_dir)
            scripts_dir = root / "scripts"
            scripts_dir.mkdir()
            script = scripts_dir / "batch_trigger_workflows.sh"
            shutil.copy2(SCRIPTS / script.name, script)
            (root / "repos_list.txt").write_bytes(b"course-template\nCS101\n")
            env = os.environ.copy()
            env["GITHUB_TOKEN"] = "token"

            result = subprocess.run(
                [bash, str(script), "--dry-run", "--delay", "0"],
                cwd=root,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("/course-template/actions/workflows/", result.stdout)
        self.assertIn("/CS101/actions/workflows/", result.stdout)
        self.assertIn("Total:   2", result.stdout)
        self.assertIn("Skipped: 0", result.stdout)


if __name__ == "__main__":
    unittest.main()
