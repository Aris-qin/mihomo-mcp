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
- 3 commits + 1 tag v0.1.0 (已 push)