"""Smoke test: import and version."""

from mihomo_mcp import __version__


def test_version_semver() -> None:
    parts = __version__.split(".")
    assert len(parts) >= 2
    assert parts[0].isdigit()
