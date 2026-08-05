from __future__ import annotations

import contextlib
import io
import unittest

from repos_management.__main__ import build_parser


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

        self.assertEqual(fetch.org, "HOAHRB-Courses")
        self.assertEqual(explicit_fetch.org, "HOAHRB-Courses")
        self.assertEqual(explicit_fetch.token, "x")
        self.assertEqual(trigger.repos_file, "repos_list.txt")
        self.assertTrue(trigger.dry_run)

    def test_repos_list_command_does_not_exist(self) -> None:
        parser = build_parser()

        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                parser.parse_args(["repos", "list"])


if __name__ == "__main__":
    unittest.main()
