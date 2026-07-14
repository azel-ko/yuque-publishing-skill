# Yuque Publishing Skill

Codex skill for preparing, dry-running, publishing, and updating Yuque articles with safe token handling.

Install with the Codex skill installer from this repository path:

```bash
python3 ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo azel-ko/yuque-publishing-skill \
  --path skills/yuque-publishing
```

Authentication is runtime-only:

```bash
export YUQUE_TOKEN="..."
```

The skill and helper scripts never require storing Yuque credentials in the repository.
