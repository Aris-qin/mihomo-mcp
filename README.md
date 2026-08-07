# mihomo-mcp

> Bridge [mihomo](https://github.com/metacubex/mihomo) (clash meta) RESTful API to [Model Context Protocol](https://modelcontextprotocol.io).
> Switch proxies, refresh subscriptions, monitor traffic — directly from your AI client.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](pyproject.toml)
[![MCP](https://img.shields.io/badge/badge-MCP_2026--07--28-green.svg)](https://modelcontextprotocol.io)

**Status: v0.1.0 (public)** — 9 tools, 17 tests, verified on mihomo v1.19.24

## What is mihomo-mcp?

mihomo exposes a powerful RESTful API on `127.0.0.1:9090` (`external-controller`). This package wraps that API as MCP tools, so an AI client (Claude Code, OpenClaw, Cursor, etc.) can:

- List and switch proxy groups
- Test proxy latency
- Refresh provider subscriptions
- **Update provider subscription URL** (without restart in many cases)
- Set operating mode (rule / global / direct)
- Inspect active connections

## Requirements

- Python 3.10+
- mihomo running with `external-controller` enabled
- An MCP-compatible client (OpenClaw, Claude Code, Claude Desktop, etc.)

> **Not affiliated with mihomo.** This is a community project.

## Installation

```bash
# Recommended (uv)
uv tool install mihomo-mcp

# Or pip
pip install mihomo-mcp

# Or from source
git clone https://github.com/Aris-qin/mihomo-mcp.git
cd mihomo-mcp
pip install -e .
```

## Configuration

```yaml
# ~/.config/mihomo-mcp/config.yaml
mihomo:
  host: 127.0.0.1
  port: 9090
  secret: ""            # if mihomo has external-controller-secret
  timeout: 10
```

Environment variables override file values:

| Var | Default |
|---|---|
| `MIHOMO_HOST` | `127.0.0.1` |
| `MIHOMO_PORT` | `9090` |
| `MIHOMO_SECRET` | (empty) |
| `MIHOMO_TIMEOUT` | `10` |

## Register with OpenClaw

In `openclaw.json`:

```json
{
  "mcp": {
    "servers": {
      "mihomo": {
        "type": "stdio",
        "command": "mihomo-mcp",
        "env": {
          "MIHOMO_HOST": "127.0.0.1",
          "MIHOMO_PORT": "9090"
        }
      }
    }
  }
}
```

## Register with Claude Desktop

Edit `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "mihomo": {
      "command": "mihomo-mcp",
      "env": {
        "MIHOMO_HOST": "127.0.0.1",
        "MIHOMO_PORT": "9090"
      }
    }
  }
}
```

## Tools

| Tool | Description |
|---|---|
| `proxy_list` | List all proxy groups and their current selection |
| `proxy_select` | Switch a selector group to a specific proxy |
| `proxy_test` | Test latency of a single proxy |
| `proxy_test_group` | Test all proxies in a group, sorted by latency |
| `provider_list` | List providers (subscriptions) and node counts |
| `provider_healthcheck` | Trigger health check on a provider |
| `provider_update_url` | **Update provider's subscription URL and refresh** |
| `mode_set` | Switch operating mode (rule / global / direct) |
| `connections_list` | List active connections |

## Security & Privacy

1. **No subscription URL is persisted.** The `provider_update_url` tool receives a URL via MCP, forwards it to mihomo, and discards it. Nothing is logged or written to disk.
2. **Default host is `127.0.0.1`.** Overriding host to a public IP is not recommended and may be rejected in future versions.
3. **No credentials stored.** If your mihomo has `external-controller-secret`, pass it via `MIHOMO_SECRET` env var — never in config files checked into version control.
4. **No traffic proxying.** This package only manages mihomo state — it does not forward your traffic.
5. **Not affiliated with mihomo.** Community project, MIT licensed.

## License

MIT — see [LICENSE](LICENSE).

## Contributing

PRs welcome after the initial public release. Please open an issue first for major changes.
