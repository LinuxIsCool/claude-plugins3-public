---
name: load-symbiocene-seed
description: |
  Example seed loader skill. Demonstrates how to use deterministic file
  injection with !`cat` commands. Customize the paths below to point to
  your own seed directory. Use /hello:create-seed-loader to generate these
  automatically.
---

# Symbiocene Publishing Seed Context

This is an **example** seed loader. To use it:

1. Create your seed directory with the files listed below
2. Update the paths to match your local filesystem
3. The `!`cat path`` syntax will inject file contents at skill load time

---

## File 1/6: CLAUDE.md (Constitutional Framework)

!`cat ./seeds/symbiocene-publishing/CLAUDE.md`

---

## File 2/6: README.md (System Documentation)

!`cat ./seeds/symbiocene-publishing/README.md`

---

## File 3/6: SKILL.md (Resources Skill Template)

!`cat ./seeds/symbiocene-publishing/SKILL.md`

---

## File 4/6: cards.jsonl (Seed Cards)

!`cat ./seeds/symbiocene-publishing/cards.jsonl`

---

## File 5/6: skills.jsonl (Skill Definitions)

!`cat ./seeds/symbiocene-publishing/skills.jsonl`

---

## File 6/6: tasks.jsonl (Task Definitions)

!`cat ./seeds/symbiocene-publishing/tasks.jsonl`

---

## How This Works

The `!`command`` syntax in SKILL.md files runs the shell command BEFORE the skill content is sent to Claude, substituting the output directly into the markdown. This guarantees deterministic content loading.

## Creating Your Own Seed Loader

Use the create-seed-loader skill:
```
/hello:create-seed-loader /path/to/your/seed-directory
```
