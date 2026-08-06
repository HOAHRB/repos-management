from __future__ import annotations

import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from repos_management.__main__ import build_parser, cmd_workflow_trigger


class CliTests(unittest.TestCase):
    def test_temporary_repository_list_commands_keep_their_interfaces(self) -> None:
        parser = build_parser()

        fetch = parser.parse_args(["repos", "fetch"])
        explicit_fetch = parser.parse_args(
            ["repos", "fetch", "--org", "HOAHRB-Courses", "--token", "x"]
        )
        trigger = parser.parse_args(
            ["workflow", "trigger", "--repos-file", "repos_list.txt", "--dry-run"]
        )
        default_trigger = parser.parse_args(["workflow", "trigger"])

        self.assertIsNone(fetch.org)
        self.assertEqual(explicit_fetch.org, "HOAHRB-Courses")
        self.assertEqual(explicit_fetch.token, "x")
        self.assertEqual(trigger.repos_file, "repos_list.txt")
        self.assertEqual(default_trigger.repos_file, "repos_list.txt")
        self.assertTrue(trigger.dry_run)

    def test_workflow_trigger_does_not_filter_repositories_by_name(self) -> None:
        parser = build_parser()
        with tempfile.TemporaryDirectory() as raw_dir:
            repos_file = Path(raw_dir) / "repos_list.txt"
            repos_file.write_text("course-template\nCS101\n", encoding="utf-8")
            args = parser.parse_args(
                [
                    "workflow",
                    "trigger",
                    "--repos-file",
                    str(repos_file),
                    "--dry-run",
                ]
            )

            output = io.StringIO()
            with patch(
                "repos_management.__main__._get_github_token", return_value="token"
            ):
                with contextlib.redirect_stdout(output):
                    self.assertEqual(cmd_workflow_trigger(args), 0)

        text = output.getvalue()
        self.assertIn("/course-template/actions/workflows/", text)
        self.assertIn("/CS101/actions/workflows/", text)
        self.assertIn("Total:   2", text)
        self.assertIn("Skipped: 0", text)

    def test_repos_list_command_does_not_exist(self) -> None:
        parser = build_parser()

        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                parser.parse_args(["repos", "list"])


if __name__ == "__main__":
    unittest.main()
