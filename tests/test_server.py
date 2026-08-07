"""Server-tool integration tests. These hit real mihomo through the tool layer."""
from __future__ import annotations

import asyncio

import pytest


pytestmark = pytest.mark.integration


def test_proxy_list() -> None:
    from mihomo_mcp.server import proxy_list
    r = asyncio.run(proxy_list())
    assert r["ok"] is True
    assert len(r["data"]) > 0


def test_proxy_test_direct() -> None:
    from mihomo_mcp.server import proxy_test
    r = asyncio.run(proxy_test("DIRECT", timeout_ms=3000))
    assert r["ok"] is True
    assert "delay" in r["data"]


def test_provider_list() -> None:
    from mihomo_mcp.server import provider_list
    r = asyncio.run(provider_list())
    assert r["ok"] is True
    assert len(r["data"]) > 0


def test_mode_set_valid() -> None:
    from mihomo_mcp.server import mode_set
    r = asyncio.run(mode_set("rule"))
    assert r["ok"] is True
    assert r["data"]["mode"] == "rule"


def test_mode_set_invalid() -> None:
    from mihomo_mcp.server import mode_set
    r = asyncio.run(mode_set("bogus"))
    assert "ok" not in r
    assert "error" in r
    assert "hint" in r
    assert "invalid" in r["error"].lower()


def test_version_tool() -> None:
    from mihomo_mcp.server import version
    r = asyncio.run(version())
    assert "package" in r
    assert "mihomo" in r


def test_proxy_select_invalid_group() -> None:
    from mihomo_mcp.server import proxy_select
    r = asyncio.run(proxy_select("NONEXISTENT", "whatever"))
    assert "ok" not in r
    assert "error" in r
