"""
Regression tests for PyPI packaging metadata in setup.py.

Ensures `url` and `project_urls` point at the real GitHub org
(AINative-Studio) instead of the nonexistent `ainative` org/repo.
Refs #7177.
"""

import ast
import os

SETUP_PY_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "setup.py"
)


def _load_setup_kwargs():
    """Parse setup.py and return the keyword arguments passed to setup()
    without executing the file (setuptools' setup() would try to build)."""
    with open(SETUP_PY_PATH, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=SETUP_PY_PATH)

    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "setup"
        ):
            kwargs = {}
            for kw in node.keywords:
                try:
                    kwargs[kw.arg] = ast.literal_eval(kw.value)
                except ValueError:
                    # Non-literal value (e.g. a function call like
                    # read_readme()) - not needed for these assertions.
                    kwargs[kw.arg] = None
            return kwargs
    raise AssertionError("No setup() call found in setup.py")


class TestSetupPyGitHubMetadata:
    """Verify setup.py metadata references the real AINative-Studio org."""

    def test_url_points_to_real_org(self):
        kwargs = _load_setup_kwargs()
        assert kwargs["url"] == "https://github.com/AINative-Studio/core"

    def test_source_project_url_points_to_real_org(self):
        kwargs = _load_setup_kwargs()
        assert (
            kwargs["project_urls"]["Source"]
            == "https://github.com/AINative-Studio/core"
        )

    def test_bug_reports_project_url_points_to_real_org(self):
        kwargs = _load_setup_kwargs()
        assert (
            kwargs["project_urls"]["Bug Reports"]
            == "https://github.com/AINative-Studio/core/issues"
        )

    def test_homepage_project_url_present(self):
        kwargs = _load_setup_kwargs()
        assert kwargs["project_urls"]["Homepage"] == "https://ainative.studio"

    def test_no_nonexistent_ainative_org_reference_remains(self):
        with open(SETUP_PY_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        assert "github.com/ainative/" not in content
        assert "github.com/ainative/studio" not in content
