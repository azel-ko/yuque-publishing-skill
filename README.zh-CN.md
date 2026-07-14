# 语雀发布 Skill

[English](README.md) | 中文

这是一个兼容 Codex 和 Claude Code 的语雀发布 skill，负责整理文章、dry-run 预览、发布和更新语雀文档，并尽量保证 Token 不进入仓库、skill 文件或聊天记录。

## 功能

- 将草稿、笔记、技术文章整理成结构化语雀文档。
- 使用语雀开放 API，通过 `X-Auth-Token` 认证。
- 给不能生成 API Token 的用户提供浏览器会话和显式 Cookie/session fallback。
- 不在仓库或 skill 文件中保存真实凭证。
- 写入操作默认 dry-run。
- 只有显式传入 `--execute` 时才会创建或更新语雀文档。

## 快速开始

1. 按你使用的 agent 安装 skill：

```bash
# Codex
mkdir -p ~/.codex/skills/yuque-publishing
cp -a skills/yuque-publishing/. ~/.codex/skills/yuque-publishing/

# Claude Code
mkdir -p ~/.claude/skills/yuque-publishing
cp -a skills/yuque-publishing/. ~/.claude/skills/yuque-publishing/
```

2. 重启 Codex 或 Claude Code。

3. 在聊天里让 agent 使用这个 skill。Claude Code 可以直接调用：

```text
/yuque-publishing
```

4. 在聊天里提供文章内容或文件路径；如果不是默认语雀知识库，再说明目标空间。skill 会选择认证流程，先 dry-run，只有你确认创建或更新后才会写入。

## 安装

### Codex：从 GitHub 安装

使用 Codex 的 skill installer：

```bash
python3 ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo azel-ko/yuque-publishing-skill \
  --path skills/yuque-publishing
```

安装完成后重启 Codex，让新 skill 被发现。

### Codex：本地手动安装

如果已经克隆了这个仓库：

```bash
mkdir -p ~/.codex/skills/yuque-publishing
cp -a skills/yuque-publishing/. ~/.codex/skills/yuque-publishing/
```

然后重启 Codex。

### Claude Code CLI：个人安装

Claude Code 的个人 skill 路径是 `~/.claude/skills/<skill-name>/SKILL.md`。官方文档：https://code.claude.com/docs/en/skills

如果已经克隆了这个仓库：

```bash
mkdir -p ~/.claude/skills/yuque-publishing
cp -a skills/yuque-publishing/. ~/.claude/skills/yuque-publishing/
```

启动或重启 Claude Code，然后可以直接调用：

```text
/yuque-publishing
```

在 Claude Code 中，skill 可以通过 `${CLAUDE_SKILL_DIR}` 引用自身目录下的脚本。仓库里的 `yuque_auth.py select` 也会输出当前安装位置下的脚本路径，所以即使 Claude Code 从其他项目目录启动，生成的命令也能找到脚本。

下面的示例默认使用 Codex 安装路径。在 Claude Code 中，建议先运行选择器；或者在已调用的 skill 里把 `~/.codex/skills/yuque-publishing` 替换为 `${CLAUDE_SKILL_DIR}`。

也可以安装为项目级 skill：

```bash
mkdir -p .claude/skills/yuque-publishing
cp -a skills/yuque-publishing/. .claude/skills/yuque-publishing/
```

## 认证方式选择

发布前先选择一种认证方式：

| 模式 | 适合谁 | 权限范围 | 说明 |
|---|---|---:|---|
| 官方 OAuth / 应用授权 或 Open API Token | 能使用语雀官方开发者认证的用户，通常是付费或超级会员账号 | 如果语雀支持 scope，则可控 | 首选，最稳定。当前 helper 脚本实现的是 `X-Auth-Token` 的 Open API Token 路径。 |
| 浏览器会话自动化 | 不能生成 API Token、可以正常网页登录、并接受可视化引导式 UI 流程的非超级会员用户 | 等同当前网页登录态 | 使用隔离浏览器 profile，通过 UI 自动化操作语雀，不导出 cookie。不适合后台静默发布。 |
| Cookie/session 后台发布 | 明确接受风险、并希望登录后静默写入的非超级会员用户 | 最大，通常等同完整账号登录权限 | 最高风险。Session 通常就是完整登录凭证。只使用 skill 的隔离 profile，创建和预检默认 headless，真实写入必须传 `--i-understand-session-risk`。 |

仓库按模式提供了独立脚本：

- `yuque_auth.py`：选择认证模式，并打印对应的下一步命令。
- `yuque_publish.py`：Open API Token 模式。
- `yuque_browser.py`：浏览器会话 UI 模式，不导出 cookie。
- `yuque_session.py`：Cookie/session 后台/headless 发布模式。

发布前先运行选择器：

```bash
python3 ~/.codex/skills/yuque-publishing/scripts/yuque_auth.py select
```

非交互示例：

```bash
python3 ~/.codex/skills/yuque-publishing/scripts/yuque_auth.py select \
  --mode browser \
  --title "文章标题" \
  --file article.md
```

## 获取语雀 Token 或官方授权

语雀开放 API 需要 Token 认证，请求时通过 HTTP Header `X-Auth-Token` 传入。官方文档：

- https://www.yuque.com/yuque/developer/api
- https://www.yuque.com/yuque/developer/openapi

如果你的账号可以创建 Token：

1. 登录语雀。
2. 打开 Token 设置页：https://www.yuque.com/settings/tokens
3. 创建一个新的 Token。
4. 只授予目标知识库读写所需的最小权限。
5. 复制 Token，并保存到本地 shell 环境变量或密钥管理器。
6. 如果 Token 曾经出现在聊天、日志或仓库里，立即撤销并重新生成。

不要把 Token 提交到仓库，也不要把 Token 粘贴到 Codex 或 Claude Code 聊天里。

如果你的账号不能创建 Token，就从上面的认证方式里选择“浏览器会话自动化”或“Cookie/session 提取”。优先选浏览器会话自动化，因为它可以避免导出原始 session 凭证。

## 配置认证

在当前 shell 中设置：

```bash
export YUQUE_TOKEN="your-yuque-token"
```

可选配置：

```bash
export YUQUE_BASE_URL="https://www.yuque.com/api/v2"
export YUQUE_USER_AGENT="codex-yuque-publishing-skill/0.1"
```

## 浏览器依赖

浏览器相关模式需要 Playwright：

```bash
python3 -m pip install playwright
python3 -m playwright install chromium
```

如果系统已经安装 Chrome，helper 会优先尝试系统 Chrome，不一定必须下载 Playwright 自带 Chromium。也可以显式设置：

```bash
export YUQUE_BROWSER_EXECUTABLE="/usr/bin/google-chrome"
```

如果 Google Chrome 窗口打开后马上消失，通常是因为命令运行在非交互 stdin 环境里。现在登录 helper 在这种情况下默认会让浏览器保持打开 30 分钟。也可以用 `--keep-open-seconds 0` 一直保持打开，直到你停止命令：

```bash
python3 ~/.codex/skills/yuque-publishing/scripts/yuque_browser.py login \
  --space-url https://www.yuque.com/azel/zob9yu \
  --keep-open-seconds 0
```

## Open API Token 使用示例

先做认证和目标知识库检查：

```bash
python3 ~/.codex/skills/yuque-publishing/scripts/yuque_publish.py \
  preflight \
  --namespace azel/zob9yu
```

生成 dry-run payload，不会写入语雀：

```bash
python3 ~/.codex/skills/yuque-publishing/scripts/yuque_publish.py \
  create-doc \
  --namespace azel/zob9yu \
  --title "文章标题" \
  --slug article-title \
  --file article.md
```

确认 dry-run 内容无误后发布：

```bash
python3 ~/.codex/skills/yuque-publishing/scripts/yuque_publish.py \
  create-doc \
  --namespace azel/zob9yu \
  --title "文章标题" \
  --slug article-title \
  --file article.md \
  --execute
```

通过 Open API Token 模式更新已有文档：

```bash
python3 ~/.codex/skills/yuque-publishing/scripts/yuque_publish.py \
  update-doc \
  --namespace azel/zob9yu \
  --doc article-title \
  --title "文章标题" \
  --file article.md \
  --execute
```

## 浏览器会话使用示例

当你不能创建语雀 API Token、但可以正常网页登录时，优先使用这个模式。
它拥有当前登录语雀账号的完整权限。专用 profile 只限制本机暴露范围，不降低语雀侧权限。
这个模式是可视化 UI 自动化，适合你愿意看到并操作语雀浏览器窗口的场景。

用隔离 profile 登录：

```bash
python3 ~/.codex/skills/yuque-publishing/scripts/yuque_browser.py login \
  --space-url https://www.yuque.com/azel/zob9yu
```

如果新 profile 中语雀验证失败，可以在同一个浏览器窗口里切换为微信、钉钉等官方 App 扫码登录。登录态仍保存在专用 profile 中，skill 不需要读取账号密码、cookie 或 session 值。

dry-run，不会写入：

```bash
python3 ~/.codex/skills/yuque-publishing/scripts/yuque_browser.py create-doc \
  --space-url https://www.yuque.com/azel/zob9yu \
  --title "文章标题" \
  --file article.md
```

执行引导式 UI 发布：

```bash
python3 ~/.codex/skills/yuque-publishing/scripts/yuque_browser.py create-doc \
  --space-url https://www.yuque.com/azel/zob9yu \
  --title "文章标题" \
  --file article.md \
  --execute
```

脚本会打开语雀，让你创建或打开空白编辑器，然后填入标题和正文。最终仍由你在浏览器里检查并保存/发布。

## Cookie/session 使用示例

当隔离 profile 已经登录、并且你希望后台静默发布文档时，使用这个模式；前提是你明确接受 session 具有完整账号权限。
专用 profile 只能降低本机横向泄露范围，不能降低语雀账号权限。
文档创建默认 headless 运行，不会打开 Google Chrome 窗口。只有调试时才传 `--no-headless`。

用同一个隔离 profile 登录：

```bash
python3 ~/.codex/skills/yuque-publishing/scripts/yuque_session.py login \
  --space-url https://www.yuque.com/azel/zob9yu
```

检查登录状态，不打印 cookie：

```bash
python3 ~/.codex/skills/yuque-publishing/scripts/yuque_session.py preflight \
  --space-url https://www.yuque.com/azel/zob9yu \
  --headless
```

dry-run web-session 创建请求：

```bash
python3 ~/.codex/skills/yuque-publishing/scripts/yuque_session.py create-doc \
  --space-url https://www.yuque.com/azel/zob9yu \
  --title "文章标题" \
  --slug article-title \
  --file article.md
```

真实执行必须显式确认风险：

```bash
python3 ~/.codex/skills/yuque-publishing/scripts/yuque_session.py create-doc \
  --space-url https://www.yuque.com/azel/zob9yu \
  --title "文章标题" \
  --slug article-title \
  --file article.md \
  --headless \
  --execute \
  --i-understand-session-risk
```

默认 session endpoint 是 `/api/docs`。这是语雀网页端接口，可能随前端变化；必要时用 `--endpoint` 和 `--book-id` 覆盖。

## 默认发布目标

skill 内置了 Azel 的默认语雀发布偏好：

- 知识库：`AI Native Engineering`
- Namespace：`azel/zob9yu`
- URL：https://www.yuque.com/azel/zob9yu

目录归类规则见 `skills/yuque-publishing/references/publishing-policy.md`。

## 安全说明

- `YUQUE_TOKEN` 只从运行时环境变量读取。
- 写入命令默认 dry-run。
- 必须显式传 `--execute` 才会真实写入。
- helper 脚本会在错误输出里遮蔽 Token。
- 仓库默认忽略 `.env` 文件。
- CI 中应使用受保护的 Secret 注入 `YUQUE_TOKEN`。
- Cookie/session 模式权限最大，不能作为默认模式。
- 专用浏览器 profile 不降低语雀账号权限，只是相比读取主浏览器 profile 降低本机暴露范围。
- 浏览器会话自动化应使用隔离浏览器 profile；除非用户明确接受风险，否则不要导出 cookie。
- 默认隔离浏览器 profile 是 `~/.local/share/yuque-publishing/browser-profile`。
