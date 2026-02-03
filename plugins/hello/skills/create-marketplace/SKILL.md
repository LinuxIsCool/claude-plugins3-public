---
name: create-marketplace
description: |
  This skill should be used when the user asks to "create a marketplace",
  "scaffold a plugin marketplace", "start a new plugin ecosystem",
  "initialize a plugin distribution repository", or mentions creating
  Claude Code marketplaces. Accepts marketplace name as argument.
  Example: /hello:create-marketplace symbiocene-publishing
allowed-tools: AskUserQuestion, Write, Bash, Glob, Read
---

# Create Marketplace Skill

Scaffold a complete Claude Code plugin marketplace with a working hello plugin example, comprehensive CLAUDE.md with worktree enforcement, and proper directory structure.

## Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `$ARGUMENTS` | No | Marketplace name (kebab-case). If omitted, prompt user. |

## Usage

```
/hello:create-marketplace my-marketplace
/hello:create-marketplace symbiocene-publishing
```

## Seed Directory Support

**Convention**: If a directory named `{marketplace-name}-seed/` exists in the current working directory, automatically load all files from it to customize the generated marketplace.

### Seed Directory Discovery

Before starting the interview, check:
```bash
ls -la ./{marketplace-name}-seed/ 2>/dev/null
```

If the seed directory exists:
1. **Read the INDEX.md** (if present) to understand the seed structure
2. **Read ALL files** in the seed directory using the Read tool
3. **Use seed content** to:
   - Replace CLAUDE.md with seed's CLAUDE.md (if present)
   - Replace README.md with seed's README.md (if present)
   - Use seed's SKILL.md as the first skill template (if present)
   - Copy any .jsonl files as data seeds
4. **Skip redundant interview questions** if seed files provide the answers

### Seed File Mapping

| Seed File | Maps To | Purpose |
|-----------|---------|---------|
| `CLAUDE.md` | `{marketplace}/CLAUDE.md` | Constitutional framework |
| `README.md` | `{marketplace}/README.md` | Project documentation |
| `SKILL.md` | `plugins/{plugin}/skills/{skill}/SKILL.md` | First skill template |
| `*.jsonl` | `{marketplace}/data/*.jsonl` | Seed data files |
| `INDEX.md` | (not copied) | Instructions for loading |

### Example with Seed

```bash
# Directory structure before running skill:
marketplaces/
├── symbiocene-publishing-seed/
│   ├── INDEX.md
│   ├── CLAUDE.md
│   ├── README.md
│   ├── SKILL.md
│   ├── cards.jsonl
│   ├── skills.jsonl
│   └── tasks.jsonl
└── (current directory)

# Run skill:
/hello:create-marketplace symbiocene-publishing

# Skill detects seed directory and uses its content
```

## Interview Flow

Conduct a progressive interview using AskUserQuestion. If `$ARGUMENTS` provides a marketplace name, skip question 1.

### Question 1: Marketplace Name (if not in $ARGUMENTS)

Ask for the marketplace name. Suggest kebab-case format (e.g., `my-plugins`, `team-tools`).

### Question 2: First Plugin Name

Ask what the first plugin should be called. Provide suggestions based on marketplace name. Must be kebab-case.

### Question 3: Plugin Description

Ask for a 1-2 sentence description of what this plugin will do. This helps generate appropriate skill content.

### Question 4: Owner Information

Ask for owner name and optionally GitHub URL for attribution in marketplace.json.

### Question 5: Initial Skill Name

Ask what the first skill in the plugin should be called. Suggest based on plugin purpose from Question 3.

## Generation Process

After gathering all information, generate the marketplace structure.

### Step 0: Check for Seed Directory

**CRITICAL**: Before the interview, check if `{marketplace-name}-seed/` exists:

```bash
ls ./{marketplace-name}-seed/ 2>/dev/null
```

If it exists:
1. Read `INDEX.md` first (if present) to understand what files to load
2. Read ALL files in the seed directory using the Read tool
3. Store the seed content for use during generation
4. Inform the user: "Found seed directory with N files. Using seed content for generation."

### Step 1: Confirm Target Directory

Display the planned structure and confirm with the user before creating files. The marketplace will be created in the current working directory as `./{marketplace-name}/`.

### Step 2: Create Directory Structure

```
{marketplace-name}/
├── .claude-plugin/
│   └── marketplace.json
├── plugins/
│   └── {first-plugin}/
│       ├── .claude-plugin/
│       │   └── plugin.json
│       ├── skills/
│       │   └── {skill-name}/
│       │       └── SKILL.md
│       ├── commands/
│       │   └── hello.md
│       ├── hooks/
│       ├── agents/
│       └── output-styles/
├── CLAUDE.md
└── README.md
```

### Step 3: Generate Files

**If seed directory exists**, use seed files instead of templates:

1. **`.claude-plugin/marketplace.json`** - Generate from template with seed-informed values
2. **`CLAUDE.md`** - Use seed's CLAUDE.md directly (copy verbatim if it exists)
3. **`README.md`** - Use seed's README.md directly (copy verbatim if it exists)
4. **`data/`** - Copy all .jsonl files from seed directory
5. **Plugin files:**
   - `plugins/{plugin}/.claude-plugin/plugin.json` - From template
   - `plugins/{plugin}/skills/{skill}/SKILL.md` - Use seed's SKILL.md if present
   - `plugins/{plugin}/commands/hello.md` - From template

**If no seed directory**, read templates from `examples/` directory:

1. **`.claude-plugin/marketplace.json`** - From `examples/marketplace.json.template`
2. **`CLAUDE.md`** - From `examples/CLAUDE.md.template` (includes worktree enforcement, plugin caching)
3. **`README.md`** - From `examples/README.md.template`
4. **Plugin files:**
   - `plugins/{plugin}/.claude-plugin/plugin.json` - From `examples/plugin.json.template`
   - `plugins/{plugin}/skills/{skill}/SKILL.md` - From `examples/SKILL.md.template`
   - `plugins/{plugin}/commands/hello.md` - From `examples/command.md.template`

Replace all placeholders with gathered values:
- `{{MARKETPLACE_NAME}}` - Marketplace name
- `{{PLUGIN_NAME}}` - First plugin name
- `{{PLUGIN_DESCRIPTION}}` - Plugin description
- `{{SKILL_NAME}}` - Initial skill name
- `{{OWNER_NAME}}` - Owner name
- `{{OWNER_URL}}` - Owner GitHub URL (or empty)

### Step 4: Initialize Git (Optional)

If the user wants version control, run:
```bash
cd {marketplace-name} && git init
```

### Step 5: Verify Structure

Run the verification script:
```bash
bash ${CLAUDE_PLUGIN_ROOT}/scripts/verify-marketplace.sh {marketplace-path}
```

### Step 6: Report Success

Display:
- Summary of created files
- Next steps for development
- How to add more plugins
- How to install locally for testing

## Template Reference

### examples/marketplace.json.template
Marketplace configuration with plugins array.

### examples/plugin.json.template
Plugin manifest declaring skills, commands, hooks.

### examples/CLAUDE.md.template
Comprehensive project instructions including:
- Worktree enforcement (critical for multi-Claude development)
- Plugin caching documentation
- Agent output strategy
- Git worktree quick reference

### examples/SKILL.md.template
Example skill structure with frontmatter.

### examples/command.md.template
Example command with argument handling.

### examples/README.md.template
Project documentation template.

## Error Handling

| Error | Resolution |
|-------|------------|
| Directory exists | Ask to overwrite or choose new name |
| Invalid name format | Suggest corrected kebab-case format |
| Write permission denied | Report error, suggest different location |
| Missing $ARGUMENTS | Fall back to interview Question 1 |

## Post-Creation Next Steps

After marketplace creation, inform the user:

1. **Add to Claude Code:**
   ```bash
   cd {marketplace-name}
   claude --plugin-dir ./plugins/{plugin-name}
   ```

2. **Create more plugins:**
   - Copy plugin template directory
   - Add entry to `.claude-plugin/marketplace.json`

3. **Develop skills:**
   - Add SKILL.md files to `plugins/{name}/skills/{skill}/`
   - Follow progressive disclosure pattern

4. **Test changes:**
   - Plugin caching means changes need cache update
   - See CLAUDE.md for cache update instructions
