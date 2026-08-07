"""Smoke test: import and version."""

from mihomo_mcp import __version__


def test_version_semver() -> None:
    parts = __version__.split(".")
    assert len(parts) >= 2
    assert parts[0].isdigit()


def test_server_imports() -> None:
    """All 9 tools should be importable + registered with the MCPServer."""
    from mihomo_mcp import server
    funcs = [
        "proxy_list",
        "proxy_select",
        "proxy_test",
        "proxy_test_group",
        "provider_list",
        "provider_healthcheck",
        "provider_update_url",
        "mode_set",
        "connections_list",
        "version",
    ]
    for name in funcs:
        assert hasattr(server, name), f"missing tool: {name}"
        assert callable(getattr(server, name)), f"not callable: {name}"


def test_config_loads() -> None:
    """Config loader should return defaults when no env / file is set."""
    from mihomo_mcp.config import load_config
    cfg = load_config()
    assert cfg["host"] == "127.0.0.1"
    assert cfg["port"] == 9090
    assert cfg["timeout"] == 10
