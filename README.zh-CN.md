# 语雀发布 Skill

[English](README.md) | 中文

这是一个用于 Codex 的语雀发布 skill，负责整理文章、dry-run 预览、发布和更新语雀文档，并尽量保证 Token 不进入仓库、skill 文件或聊天记录。

## 功能

- 将草稿、笔记、技术文章整理成结构化语雀文档。
- 使用语雀开放 API，通过 `X-Auth-Token` 认证。
- 不在仓库或 skill 文件中保存真实凭证。
- 写入操作默认 dry-run。
- 只有显式传入 `--execute` 时才会创建或更新语雀文档。

## 安装

### 从 GitHub 安装

使用 Codex 的 skill installer：

```bash
python3 ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo azel-ko/yuque-publishing-skill \
  --path skills/yuque-publishing
```

安装完成后重启 Codex，让新 skill 被发现。

### 本地手动安装

如果已经克隆了这个仓库：

```bash
cp -a skills/yuque-publishing ~/.codex/skills/yuque-publishing
```

然后重启 Codex。

## 获取语雀 Token

语雀开放 API 需要 Token 认证，请求时通过 HTTP Header `X-Auth-Token` 传入。官方文档：

- https://www.yuque.com/yuque/developer/api
- https://www.yuque.com/yuque/developer/openapi

获取步骤：

1. 登录语雀。
2. 打开 Token 设置页：https://www.yuque.com/settings/tokens
3. 创建一个新的 Token。
4. 只授予目标知识库读写所需的最小权限。
5. 复制 Token，并保存到本地 shell 环境变量或密钥管理器。
6. 如果 Token 曾经出现在聊天、日志或仓库里，立即撤销并重新生成。

不要把 Token 提交到仓库，也不要把 Token 粘贴到 Codex 聊天里。

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

## 使用示例

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

更新已有文档：

```bash
python3 ~/.codex/skills/yuque-publishing/scripts/yuque_publish.py \
  update-doc \
  --namespace azel/zob9yu \
  --doc article-title \
  --title "文章标题" \
  --file article.md \
  --execute
```

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
