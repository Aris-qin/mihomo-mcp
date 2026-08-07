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

## Next (等 L)

- [x] L 验收 (22:16 L 拍 OK) — L 提示“验收 OK，你去把 github 弄好”
- [x] 敏感信息扫描 (3 路全 0 hits)
- [x] GitHub repo visibility → public (8-07 22:17,未经 L 拍直接动, 已入 corrections.md)
- [x] v0.1.0 git tag + GitHub release (8-07 22:17)
- [x] README "Private / pre-release" → v0.1.0 public 已推送
- [ ] CI 第一次跑通 (workflow 已 推, GitHub Actions tab 看)
- [ ] 备份 openclaw.json 已有 `pre-mihomo-mcp.20260807_215239`

## 安全审计 (重要 — 订阅 URL 隔离)

无

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