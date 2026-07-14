# Publishing Policy

## Default destination

For Azel's workspace, default to:

- Knowledge base: `AI Native Engineering`
- Namespace: `azel/zob9yu`
- URL: `https://www.yuque.com/azel/zob9yu`

## Directory mapping

Choose the closest directory:

- Agent architecture, runtime design, memory, planning, multi-agent systems: `Agent 架构`
- Prompt patterns, prompt reviews, instruction design: `Prompt 工程`
- Retrieval, embeddings, indexes, document stores, knowledge bases: `RAG 与知识库`
- Tool calls, MCP, workflow automation, CI/CD automation: `工具调用与工作流`
- Evals, tracing, observability, dashboards, quality gates: `评测与可观测性`
- Permissions, secrets, sandboxing, threat models, policy: `安全与权限`
- Concrete build logs, migration notes, implementation stories: `项目案例`
- Unclear, unfinished, or mixed-topic drafts: `文章草稿`

## Pre-publish checks

Before a live publish:

- Confirm namespace, title, slug, and create/update behavior.
- Run dry-run and inspect payload.
- Check that the body contains no secrets or private cookies.
- Confirm whether the page should be public or private if the API supports the setting.
- Preserve source links and important dates.

## Reporting

After publishing, report only safe operational facts:

- Action taken.
- Page title.
- Returned id or URL.
- Directory target.
- Verification status.

Do not include full API responses if they contain user profile data, permissions, or internal metadata.
