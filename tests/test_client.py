"""Integration tests for MihomoClient.

These tests require a live mihomo instance on 127.0.0.1:9090. They are
marked with `pytest.mark.integration` and can be skipped with
`pytest -m 'not integration'`.
"""

from __future__ import annotations

import pytest

from mihomo_mcp.client import MihomoClient, MihomoError

pytestmark = pytest.mark.integration


async def _client() -> MihomoClient:
    return MihomoClient(host="127.0.0.1", port=9090, timeout=5.0)


def test_version() -> None:
    import asyncio

    async def run():
        async with await _client() as c:
            r = await c.version()
            assert "version" in r
            assert r["version"].startswith("v")

    asyncio.run(run())


def test_list_proxies() -> None:
    import asyncio

    async def run():
        async with await _client() as c:
            r = await c.list_proxies()
            assert "proxies" in r
            assert len(r["proxies"]) > 0

    asyncio.run(run())


def test_list_providers() -> None:
    import asyncio

    async def run():
        async with await _client() as c:
            r = await c.list_providers()
            assert "providers" in r
            assert len(r["providers"]) > 0

    asyncio.run(run())


def test_get_proxy() -> None:
    import asyncio

    async def run():
        async with await _client() as c:
            r = await c.get_proxy("DIRECT")
            assert r["type"] == "Direct"

    asyncio.run(run())


def test_select_proxy_invalid() -> None:
    """Selecting a non-existent proxy should raise MihomoError with helpful hint."""
    import asyncio

    async def run():
        async with await _client() as c:
            with pytest.raises(MihomoError) as exc:
                await c.select_proxy("nonexistent_node", "GLOBAL")
            assert "not exist" in str(exc.value) or exc.value.status_code == 400
            assert exc.value.hint  # the friendly hint is set

    asyncio.run(run())


def test_get_configs() -> None:
    import asyncio

    async def run():
        async with await _client() as c:
            r = await c.get_configs()
            assert "mode" in r

    asyncio.run(run())


def test_connections_idle() -> None:
    """connection list should return None / empty when idle."""
    import asyncio

    async def run():
        async with await _client() as c:
            r = await c.list_connections()
            assert "connections" in r

    asyncio.run(run())
