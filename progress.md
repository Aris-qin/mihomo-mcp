# mcp-mihomo 进度

## Now

v0.1.0-dev 已交付, OpenClaw mcp.servers.mihomo 已注册, 真实 mihomo v1.19.24 探针 9 tools 通了. 等 L 验收拍 public + tag.

## Done (今日 21:16-22:17)

- **调研** (21:16-21:33): stdio transport / Python mcp v2 (`MCPServer`) / httpx async 选型; 9 tool 设计取代 11 个; mihomo REST 端点实测 (24 endpoints, 157 fields).
- **建仓** (21:38): https://github.com/Aris-qin/mihomo-mcp (private, MIT).
- **订阅刷新** (21:44): 新 URL 已写入 /etc/mihomo/config.yaml; 28/38 节点活; openai API 401 通; URL 0 残留 git / log / history.
- **代码** (21:50): `src/mihomo_mcp/{config,client,server}.py` + `__main__.py`; 9 tool 全部实测过真 mihomo; stdout 干净 (logging→stderr).
- **测试** (21:53): 17/17 pass (3 unit + 7 client + 7 server); `pip install -e .` + `mihomo-mcp` console script + stdio JSON-RPC handshake OK.
- **OpenClaw 注册** (21:54): `openclaw mcp add mihomo --command /usr/local/bin/mihomo-mcp --env MIHOMO_HOST/PORT/TIMEOUT --exclude provider_update_url --timeout 15` 探针 9 tools.
- **TOOLS.md** (22:11): 表格 + 短段 (3 段合并成 1 句/段).

## Done (8-08 18:43 CI 修复)

L 问"项目写完没" → 答"v0.1.0 release/tag/README 都到位, 但 CI 5 次跑全 ❌". L 拍"去修". 三连击:

- **ruff 修复** (1b98cbc): 5 个 lint 错 (UP037/F401×2/I001×2) --fix 一键; ruff format 重排 server.py (75 行变化纯 cosmetic); 17/17 pytest 本地过.
- **mypy 修复** (3d0d7a8): mypy 缺 types-PyYAML stub; DEFAULTS 未标注 (默认 `dict[str, object]`); `_coerce_int(value: object, default: int)` 签名过严. 修法: dev deps 加 types-PyYAML, DEFAULTS 标 `dict[str, str | int]`, `_coerce_int` 改 `(value: Any, default: Any)` + `int(default)` 兜底. ruff/mypy/pytest 三连绿.
- **CI 策略修复** (5daff07): CI step 8 (pytest) 之前一直挂, 不是因为代码错, 是因为 `pytest -v` 收了 14 个 `pytest.mark.integration` 测试, 这些测要连本地 127.0.0.1:9090 的 mihomo, GitHub runner 根本跑不了. 而且 integration 路径含 `provider_update_url` 会暴露订阅 URL — 8-07 安全审计要隔离 URL, CI 跑 integration 等于自爆. CI step 改成 `pytest -v -m "not integration"`, 只跑 3 个 unit (smoke + import + config-load). 集成测留给 user 本地 `pytest -v` 验.

**CI #8 (5daff07)**: 4 jobs (Python 3.10/3.11/3.12/3.13) all success ✅.

## Next

- [x] CI 第一次跑通 (8-08 18:55, 4/4 jobs success on 5daff07)
- [ ] GitHub repo description 仍写 "Private during initial development..." (search_repositories API 可见); 需 gh CLI 或 web Settings 改, 待 L 拍板要不要动
- [ ] 备份 openclaw.json 已有 `pre-mihomo-mcp.20260807_215239`

## 安全审计 (重要 — 订阅 URL 隔离)

| 落点 | 命中 |
|---|---|
| 项目 tracked 代码 / README | 0 |
| git 2 commit 全文 | 0 |
| GitHub public/private 页面 | 0 |
| /tmp/mihomo.log | 0 |
| bash/zsh history | 0 |
| `/etc/mihomo/config.yaml` | 1 (必需, `.gitignore` 不挡属于 mihomo 自身的文件) |
| `~/.agents/inbox/mihomo_sub_20260807.txt` (chmod 600) | 1 (本地独立备份, 不入 GitHub) |
| OpenClaw `toolFilter.exclude = [provider_update_url]` | 已生效 |

## GitHub 公开链接

- 仓库: https://github.com/Aris-qin/mihomo-mcp (public)
- Release: https://github.com/Aris-qin/mihomo-mcp/releases/tag/v0.1.0
- 5 commits + 1 tag v0.1.0 (已 push, 0008ec0 HEAD)

## 项目完结 (2026-08-08 18:59 L 拍归档)

L 问"项目写完没"后验证发现 CI 5 次跑全, 补三道 fix 修到 CI 绿 (1b98cbc ruff / 3d0d7a8 mypy / 5daff07 ci 策略 / 0008ec0 progress)。L 拍"如果这个项目已经完成就写一下结尾然后归档吧"。状态归档。

**交付清单** (全部到位):

- ✅ 9 MCP tools 实现: `proxy_list`, `proxy_select`, `proxy_test`, `proxy_test_group`, `provider_list`, `provider_healthcheck`, `provider_update_url`, `mode_set`, `connections_list`, `version` (10 个, 含 version 检验)
- ✅ 17 测试 (3 unit + 14 integration), 实跱 mihomo v1.19.24 探针
- ✅ v0.1.0 GitHub release + tag: https://github.com/Aris-qin/mihomo-mcp/releases/tag/v0.1.0
- ✅ repo public, README 带 Status badge
- ✅ CI #8 31253687289 (5daff07) Python 3.10/3.11/3.12/3.13 4/4 success
- ✅ OpenClaw `mcp.servers.mihomo` 已注册, 10 tools 实跑探针
- ✅ 订阅 URL 隔离审计 0 命中 (git / GitHub / /tmp / bash history)
- ✅ OpenClaw `toolFilter.exclude = [provider_update_url]` 生效 (额外防御层)

**可改进/未来工作** (不阻塞归档, 留给后续独立 task):

- PyPI 发布: `mihomo-mcp` 包名可用, 但 v0.1.0 未推上 PyPI。推送需要 `uv publish` + PyPI token, 未在 L 验收范围。user 本地 `uv tool install mihomo-mcp` / `pip install mihomo-mcp` 当前会因没上 PyPI 报错, 需 `pip install git+https://github.com/Aris-qin/mihomo-mcp.git`。
- GitHub repo description 仍写 "Private during initial development..." (search_repositories API 可见); 需要 `gh repo edit --description` 改, L 未拍。
- 类型注解还可以再严 (e.g. mcp tool return type, ToolError 分类), 但 mypy 现在绿, 不是阻塞项。
- 集成测试本地 user 可跑 `pytest -v` 验; CI 策略 (跳过 integration) 是为了隔离订阅 URL 不是技术限制。

**保留位置**: 归档到 `projects/已完成归档/mcp-mihomo/` 后, 仓库路径不变 (本地仍可 `cd` / 改 / push), `git log` 保留全部 5 commits。fact.db projects.status 同步为 'done'。