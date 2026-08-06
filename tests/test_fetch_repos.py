from __future__ import annotations

import unittest

from scripts.fetch_repos import get_repos


class FakeResponse:
    def __init__(
        self,
        payload: list[dict[str, object]],
        *,
        next_url: str | None = None,
        error: Exception | None = None,
    ) -> None:
        self._payload = payload
        self._error = error
        self.links = {} if next_url is None else {"next": {"url": next_url}}

    def raise_for_status(self) -> None:
        if self._error is not None:
            raise self._error

    def json(self) -> list[dict[str, object]]:
        return self._payload


class FakeSession:
    def __init__(self, responses: list[FakeResponse]) -> None:
        self._responses = iter(responses)
        self.urls: list[str] = []

    def get(self, url: str, **_: object) -> FakeResponse:
        self.urls.append(url)
        return next(self._responses)


class FetchReposTests(unittest.TestCase):
    def test_filters_and_paginates(self) -> None:
        session = FakeSession(
            [
                FakeResponse(
                    [
                        {"name": "CS101", "archived": False, "is_template": False},
                        {"name": ".github", "archived": False, "is_template": False},
                        {"name": ".private", "archived": False, "is_template": False},
                        {"name": "OLD", "archived": True, "is_template": False},
                        {"name": "template", "archived": False, "is_template": True},
                        {"name": "hoa-moe", "archived": False, "is_template": False},
                        {"name": "repos-helper", "archived": False, "is_template": False},
                        {"name": "dev-tool", "archived": False, "is_template": False},
                        {"name": "aextra", "archived": False, "is_template": False},
                    ],
                    next_url="page-2",
                ),
                FakeResponse(
                    [{"name": "MATH101", "archived": False, "is_template": False}]
                ),
            ]
        )

        self.assertEqual(
            get_repos("HOAHRB-Courses", "token", session=session),
            ["CS101", "MATH101", "aextra", "dev-tool", "hoa-moe", "repos-helper"],
        )
        self.assertEqual(session.urls, [
            "https://api.github.com/orgs/HOAHRB-Courses/repos",
            "page-2",
        ])

    def test_page_two_error_propagates_without_a_partial_result(self) -> None:
        session = FakeSession(
            [
                FakeResponse(
                    [{"name": "CS101", "archived": False, "is_template": False}],
                    next_url="page-2",
                ),
                FakeResponse([], error=RuntimeError("second page failed")),
            ]
        )

        with self.assertRaisesRegex(RuntimeError, "second page failed"):
            get_repos("HOAHRB-Courses", "token", session=session)


if __name__ == "__main__":
    unittest.main()
