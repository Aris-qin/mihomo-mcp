"""MCP server: 9 tools wrapping mihomo RESTful API.

Tools:
- proxy_list              list groups + current selection
- proxy_select            switch a selector group; refuses unsafe target
- proxy_test              delay test for a single proxy
- proxy_test_group        delay test for an entire selector group, sorted
- provider_list           list providers + node counts
- provider_healthcheck    trigger health check on a provider
- provider_update_url     update provider's subscription URL (forwarded, not cached)
- mode_set                switch operating mode (rule / global / direct)
- connections_list        list active connections
- version                 mihomo-mcp package version (for sanity check)
"""

from __future__ import annotations

import asyncio
import logging
import sys
from contextlib import asynccontextmanager
from typing import Any

from mcp.server import MCPServer

from mihomo_mcp import __version__
from mihomo_mcp.client import MihomoClient, MihomoError
from mihomo_mcp.config import get_endpoint

# CRITICAL: stdio MCP — stdout is reserved for JSON-RPC. All logs go to stderr.
logging.basicConfig(
    level=logging.WARNING,
    stream=sys.stderr,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
# Silence httpx — its default INFO logging floods every request.
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

mcp = MCPServer("mihomo-mcp")


@asynccontextmanager
async def client_ctx():
    host, port, secret, timeout = get_endpoint()
    client = MihomoClient(host=host, port=port, secret=secret, timeout=timeout)
    try:
        yield client
    finally:
        await client.close()


def _err(e: MihomoError) -> dict:
    return e.to_dict()


def _ok(data: Any) -> dict:
    return {"ok": True, "data": data}


# ---- tools ----


@mcp.tool()
async def version() -> dict:
    """Return mihomo-mcp package version and connected mihomo version."""
    async with client_ctx() as c:
        try:
            mihomo_v = await c.version()
        except MihomoError as e:
            return {"package": __version__, "mihomo": _err(e)}
    return {"package": __version__, "mihomo": mihomo_v}


@mcp.tool()
async def proxy_list() -> dict:
    """List all proxy groups with their current selection and node count.

    Returns a list of groups, each with: name, type, current (the active
    proxy), and the number of available nodes. Selector/URLTest groups
    show all options; Direct/Reject/Compatible show a single fixed value.
    """
    async with client_ctx() as c:
        try:
            data = await c.list_proxies()
        except MihomoError as e:
            return _err(e)
    groups = []
    for name, p in data.get("proxies", {}).items():
        groups.append(
            {
                "name": name,
                "type": p.get("type"),
                "current": p.get("now"),
                "node_count": len(p.get("all", [])),
                "alive": p.get("alive"),
            }
        )
    return _ok(groups)


@mcp.tool()
async def proxy_select(group: str, proxy: str) -> dict:
    """Switch a Selector/URLTest group to a specific proxy.

    Args:
        group: the group name (e.g. "GLOBAL", "Manual")
        proxy: the proxy name to select (e.g. "🇭🇰香港01 [1×] - Lv.4")

    Returns the new selection. Mihomo returns 400 if the proxy is not
    in the group's all-list (case-sensitive).
    """
    async with client_ctx() as c:
        try:
            await c.select_proxy(proxy, group)
            updated = await c.get_proxy(group)
        except MihomoError as e:
            return _err(e)
    return _ok({"group": group, "selected": updated.get("now")})


@mcp.tool()
async def proxy_test(
    proxy: str,
    url: str = "http://www.gstatic.com/generate_204",
    timeout_ms: int = 5000,
) -> dict:
    """Test latency (ms) for a single proxy.

    Args:
        proxy: proxy name (must match an entry in a group's all-list)
        url: target URL, default is gstatic.com/generate_204 (used by mihomo itself)
        timeout_ms: per-test timeout in milliseconds (default 5000)

    Returns the delay in ms, or {"delay": -1} if the test failed.
    """
    async with client_ctx() as c:
        try:
            r = await c.test_proxy_delay(proxy, url, timeout_ms)
        except MihomoError as e:
            return _err(e)
    return _ok(r)


@mcp.tool()
async def proxy_test_group(
    group: str,
    url: str = "http://www.gstatic.com/generate_204",
    timeout_ms: int = 5000,
    concurrency: int = 8,
) -> dict:
    """Test latency of every proxy in a group, sorted by delay (fastest first).

    Args:
        group: the selector group to test
        url: target URL
        timeout_ms: per-proxy timeout
        concurrency: max parallel probes (default 8)

    Returns a list of {name, delay_ms, ok} sorted by delay. Failed probes
    show delay=-1 and are placed at the end.
    """
    async with client_ctx() as c:
        try:
            detail = await c.get_proxy(group)
        except MihomoError as e:
            return _err(e)

        if detail.get("type") not in ("Selector", "URLTest"):
            return _err(
                MihomoError(
                    f"group '{group}' is type '{detail.get('type')}', not Selector/URLTest",
                    hint="proxy_test_group only works on groups with multiple options",
                )
            )

        names = detail.get("all", [])
        sem = asyncio.Semaphore(max(1, concurrency))

        async def probe(name: str) -> dict:
            async with sem:
                try:
                    r = await c.test_proxy_delay(name, url, timeout_ms)
                    return {"name": name, "delay_ms": r.get("delay", -1), "ok": True}
                except MihomoError:
                    return {"name": name, "delay_ms": -1, "ok": False}

        results = await asyncio.gather(*(probe(n) for n in names))

    results.sort(key=lambda r: (r["delay_ms"] == -1, r["delay_ms"]))
    return _ok(results)


@mcp.tool()
async def provider_list() -> dict:
    """List all proxy providers with node counts and last update info.

    Returns: list of {name, type, vehicle_type, node_count, updated_at}.
    """
    async with client_ctx() as c:
        try:
            data = await c.list_providers()
        except MihomoError as e:
            return _err(e)
    out = []
    for name, p in data.get("providers", {}).items():
        out.append(
            {
                "name": name,
                "type": p.get("type"),
                "vehicle_type": p.get("vehicleType"),
                "node_count": len(p.get("proxies", [])),
            }
        )
    return _ok(out)


@mcp.tool()
async def provider_healthcheck(provider: str) -> dict:
    """Trigger health check on a provider (force-refresh + delay measurement).

    Args:
        provider: provider name (e.g. "MyVPN")

    Returns a no-content confirmation (mihomo returns 204). The actual
    health state is observable via provider_list.
    """
    async with client_ctx() as c:
        try:
            await c.healthcheck_provider(provider)
        except MihomoError as e:
            return _err(e)
    return _ok({"provider": provider, "triggered": True})


@mcp.tool()
async def provider_update_url(provider: str, url: str) -> dict:
    """Update a provider's subscription URL and trigger a refresh.

    Args:
        provider: provider name
        url: new subscription URL (forwarded to mihomo, never persisted)

    The URL is sent to mihomo via PUT and used immediately. It is not
    cached, logged, or written to disk by this server.
    """
    async with client_ctx() as c:
        try:
            await c.update_provider_url(provider, url)
        except MihomoError as e:
            return _err(e)
    return _ok({"provider": provider, "updated": True})


@mcp.tool()
async def mode_set(mode: str) -> dict:
    """Switch operating mode: rule (default), global, or direct.

    Args:
        mode: one of "rule", "global", "direct"

    - rule: use rules to decide what goes through proxy
    - global: all traffic through proxy
    - direct: all traffic bypasses proxy
    """
    if mode not in ("rule", "global", "direct"):
        return _err(
            MihomoError(
                f"invalid mode '{mode}'",
                hint="must be 'rule', 'global', or 'direct'",
            )
        )
    async with client_ctx() as c:
        try:
            await c.patch_configs({"mode": mode})
            cfg = await c.get_configs()
        except MihomoError as e:
            return _err(e)
    return _ok({"mode": cfg.get("mode")})


@mcp.tool()
async def connections_list() -> dict:
    """List active connections (source ip, host, rule, chains, upload, download).

    Returns a list of connection objects. An empty list means no active
    connections (mihomo returns {connections: null} on idle).
    """
    async with client_ctx() as c:
        try:
            data = await c.list_connections()
        except MihomoError as e:
            return _err(e)
    conns = data.get("connections") or []
    summary = []
    for c in conns:
        summary.append(
            {
                "id": c.get("id"),
                "host": c.get("host"),
                "rule": c.get("rule"),
                "chains": c.get("chains"),
                "upload": c.get("upload"),
                "download": c.get("download"),
                "start": c.get("start"),
                "matched": c.get("matched"),
            }
        )
    return _ok(summary)


def main() -> None:
    """Run the MCP server over stdio."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
