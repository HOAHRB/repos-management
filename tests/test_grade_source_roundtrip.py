import sys
import tempfile
import tomllib
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import convert_toml_to_readme as forward
from scripts import readme_to_toml as reverse


def _badge_line(*, alt: str, label: str, message: str | None, color: str) -> str:
    return forward._render_shields_badge(
        alt=alt,
        label=label,
        message=message,
        color=color,
    )


def _replace_badge(readme: str, *, alt: str, replacement: str) -> str:
    lines = readme.splitlines()
    for index, line in enumerate(lines):
        if line.startswith(f"![{alt}]"):
            lines[index] = replacement
            return "\n".join(lines) + "\n"
    raise AssertionError(f"badge {alt!r} not found")


def _reverse_over_existing(readme: str, existing_toml: str) -> dict[str, object]:
    with tempfile.TemporaryDirectory() as raw_dir:
        directory = Path(raw_dir)
        readme_path = directory / "README.md"
        toml_path = directory / "readme.toml"
        readme_path.write_text(readme, encoding="utf-8")
        toml_path.write_text(existing_toml, encoding="utf-8")

        with patch.object(
            sys,
            "argv",
            [
                "readme_to_toml.py",
                "--input",
                str(readme_path),
                "--output",
                str(toml_path),
                "--overwrite",
            ],
        ):
            assert reverse.main() == 0

        return tomllib.loads(toml_path.read_text(encoding="utf-8"))


class GradeSourceRoundTripTests(unittest.TestCase):
    def test_normal_course_separates_badge_groups_and_preserves_automatic_grade(self) -> None:
        existing_toml = """\
course_name = "Course"
course_code = "C001"

[[sections]]
title = "基本信息"

[[sections.items]]
content = "【学分】: 2"

[[sections.items]]
source = "grades_summary"
content = "【成绩构成】: 作业 40% | 考试 60%"

[[sections]]
title = "教材"

[[sections.items]]
content = "Manual material"
"""
        data = tomllib.loads(existing_toml)
        readme = forward.render_readme(data)

        self.assertEqual(
            readme.count('<!-- TOML-BADGES: source="basic_info" -->'), 1
        )
        self.assertEqual(
            readme.count('<!-- TOML-BADGES: source="grades_summary" -->'), 1
        )
        self.assertLess(
            readme.index('<!-- TOML-BADGES: source="basic_info" -->'),
            readme.index('<!-- TOML-BADGES: source="grades_summary" -->'),
        )

        edited_readme = _replace_badge(
            readme,
            alt="学分",
            replacement=_badge_line(alt="学分", label="学分", message="3", color="moccasin"),
        )
        edited_readme = _replace_badge(
            edited_readme,
            alt="作业40%",
            replacement=_badge_line(
                alt="作业50%", label="作业", message="50%", color="wheat"
            ),
        )
        output = _reverse_over_existing(edited_readme, existing_toml)

        basic_info = next(
            section for section in output["sections"] if section["title"] == "基本信息"
        )
        self.assertIn("【学分】: 3", basic_info["items"][0]["content"])
        automatic_items = [
            item
            for item in basic_info["items"]
            if item.get("source") == "grades_summary"
        ]
        self.assertEqual(
            automatic_items,
            [
                {
                    "source": "grades_summary",
                    "content": "【成绩构成】: 作业 40% | 考试 60%",
                }
            ],
        )
        self.assertEqual(output["sections"][1]["items"][0]["content"], "Manual material")

    def test_multi_project_separates_badge_groups_and_preserves_automatic_grade(self) -> None:
        existing_toml = """\
repo_type = "multi-project"

[[courses]]
name = "Course"
code = "C002"

[[courses.sections]]
title = "基本信息"

[[courses.sections.items]]
content = "【学时构成】: 理论 32"

[[courses.sections.items]]
source = "grades_summary"
content = "【成绩构成】: 平时 30% | 考试 70%"

[[courses.sections]]
title = "说明"

[[courses.sections.items]]
content = "Manual note"
"""
        data = tomllib.loads(existing_toml)
        readme = forward.render_readme(data)

        self.assertEqual(
            readme.count('<!-- TOML-BADGES: source="basic_info" -->'), 1
        )
        self.assertEqual(
            readme.count('<!-- TOML-BADGES: source="grades_summary" -->'), 1
        )

        edited_readme = _replace_badge(
            readme,
            alt="理论32",
            replacement=_badge_line(
                alt="理论40", label="理论", message="40", color="wheat"
            ),
        )
        edited_readme = _replace_badge(
            edited_readme,
            alt="平时30%",
            replacement=_badge_line(
                alt="平时20%", label="平时", message="20%", color="wheat"
            ),
        )
        output = _reverse_over_existing(edited_readme, existing_toml)

        basic_info = next(
            section
            for section in output["courses"][0]["sections"]
            if section["title"] == "基本信息"
        )
        self.assertIn("【学时构成】: 理论 40", basic_info["items"][0]["content"])
        automatic_items = [
            item
            for item in basic_info["items"]
            if item.get("source") == "grades_summary"
        ]
        self.assertEqual(
            automatic_items,
            [
                {
                    "source": "grades_summary",
                    "content": "【成绩构成】: 平时 30% | 考试 70%",
                }
            ],
        )
        self.assertEqual(
            output["courses"][0]["sections"][1]["items"][0]["content"],
            "Manual note",
        )

    def test_multiple_automatic_items_in_one_scope_are_rejected(self) -> None:
        existing_toml = """\
[[sections]]
title = "基本信息"

[[sections.items]]
source = "grades_summary"
content = "【成绩构成】: 作业 40%"

[[sections.items]]
source = "grades_summary"
content = "【成绩构成】: 考试 60%"
"""

        with self.assertRaisesRegex(ValueError, "multiple automatic grade items"):
            reverse.preserve_automatic_grade_items(reverse.Document(), existing_toml)

    def test_forward_converter_has_no_central_grade_loader(self) -> None:
        self.assertFalse(hasattr(forward, "_load_grades_summary"))
        self.assertFalse(hasattr(forward, "_pick_grade_string"))


if __name__ == "__main__":
    unittest.main()
