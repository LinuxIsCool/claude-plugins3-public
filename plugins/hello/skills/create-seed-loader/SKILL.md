---
name: create-seed-loader
description: |
  This skill should be used when the user asks to "create a seed loader",
  "make a loader skill for seed files", or wants to deterministically
  load all files from a directory. Creates a SKILL.md with !`cat` commands.
allowed-tools: Bash, Glob, Write, Read, AskUserQuestion
---

# Create Seed Loader Skill

Generate a deterministic loader skill that uses `!`cat`` commands to inject all files from a seed directory.

## Parameters

| Parameter | Description |
|-----------|-------------|
| `$ARGUMENTS` | Path to seed directory |

## Process

### Step 1: Validate Seed Directory

Check that the directory exists and list all files:
```bash
ls -la {seed-directory}/
```

### Step 2: Generate Skill Name

Derive skill name from directory name:
- `symbiocene-publishing-seed/` → `load-symbiocene-seed`
- `my-project-seed/` → `load-my-project-seed`

### Step 3: Generate SKILL.md

Create a new skill in the hello plugin's skills/ directory with this structure:

```markdown
---
name: load-{name}-seed
description: |
  Deterministically loads all files from {seed-directory}.
---

# {Name} Seed Context

## File 1/N: filename.ext

!`cat {full-path-to-file}`

---

## File 2/N: filename2.ext

!`cat {full-path-to-file2}`

[... repeat for all files ...]
```

### Step 4: Confirm Creation

Report:
- Skill location: `plugins/hello/skills/load-{name}-seed/SKILL.md`
- Number of files that will be deterministically loaded
- How to invoke: `/hello:load-{name}-seed`

## Example

```
User: /hello:create-seed-loader /home/user/my-project-seed
Claude: Created deterministic loader skill at plugins/hello/skills/load-my-project-seed/SKILL.md
        Will load 4 files via !`cat`:
        - CLAUDE.md
        - README.md
        - config.json
        - data.jsonl

        Invoke with: /hello:load-my-project-seed
```

## Why This Works

The `!`command`` syntax in SKILL.md files:
1. Runs the shell command BEFORE the skill content is sent to Claude
2. Substitutes the command output directly into the markdown
3. Guarantees the content is loaded - it's not an instruction, it's literal injection

This is equivalent to @ tagging every file, but works within the skill system.
