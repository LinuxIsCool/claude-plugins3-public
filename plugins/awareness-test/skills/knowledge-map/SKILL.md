---
name: knowledge-map
description: Navigate and explore the Claude Code documentation knowledge graph. Use when users need to find related documentation, understand topic connections, or get an overview of documentation structure.
argument-hint: [action] (overview|find|related|hubs|path)
disable-model-invocation: true
user-invocable: true
allowed-tools: Read, Glob, Grep, Bash
---

# Knowledge Map Skill

Navigate the Claude Code documentation knowledge graph.

## Usage

```
/knowledge-map overview         - Documentation structure overview
/knowledge-map find TOPIC       - Find pages related to a topic
/knowledge-map related PAGE     - Show pages related to a specific page
/knowledge-map hubs             - Show central hub pages
/knowledge-map path FROM TO     - Find path between two topics
```

## Action: Overview

Provide a hierarchical overview of documentation structure:

```
## Claude Code Documentation Overview

### Categories
| Category | Pages | Key Topics |
|----------|-------|------------|
| Core | 5 | overview, quickstart, setup, how-it-works |
| Configuration | 4 | settings, model-config, network-config |
| Extension | 7 | hooks, skills, plugins, mcp, sub-agents |
| Integration | 7 | vs-code, jetbrains, github-actions, etc. |
| Enterprise | 6 | iam, security, costs, monitoring |
| Deployment | 6 | bedrock, vertex-ai, headless |
| Reference | 5 | cli-reference, best-practices, changelog |

### Total Pages: 51
### Total Links: 733
### Total Code Examples: 375
```

## Action: Find TOPIC

Search for documentation related to a specific topic:

1. Query the knowledge graph for matching pages
2. Include both title matches and content matches
3. Show relevance ranking

Response format:
```
## Results for "{topic}"

### Exact Matches
- {page}: {description}

### Related Pages
- {page}: {why relevant}

### Code Examples
- Found {n} code examples in matched pages
```

## Action: Related PAGE

Show pages linked to/from a specific page:

1. Look up the page in the knowledge graph
2. Get incoming links (pages that link TO this page)
3. Get outgoing links (pages this page links TO)

Response format:
```
## Related to {page}

### Linked FROM This Page (Outgoing)
- {target}: {link context}

### Linking TO This Page (Incoming)
- {source}: {link context}

### Also See
- {related pages by topic}
```

## Action: Hubs

Show the most connected documentation pages:

```
## Documentation Hubs

### Most Linked To (Entry Points)
| Page | Incoming Links | Description |
|------|----------------|-------------|
| settings.md | 15 | Central configuration reference |
| mcp.md | 9 | MCP server integration |
| skills.md | 7 | Custom skill development |

### Most Outgoing (Comprehensive Guides)
| Page | Outgoing Links | Description |
|------|----------------|-------------|
| settings.md | 69 | Links to all config topics |
| claude-code-on-the-web.md | 49 | Web features overview |
| sub-agents.md | 43 | Agent ecosystem guide |
```

## Action: Path FROM TO

Find connection path between two topics:

1. Locate both pages in the graph
2. Find shortest path through links
3. Show intermediate pages

Response format:
```
## Path: {from} → {to}

### Direct Path
{from} → {intermediate} → {to}

### Via Topics
1. {from}: {topic}
2. {intermediate}: {connecting topic}
3. {to}: {topic}

### Alternative Paths
- {from} → {alt1} → {to}
```

## Knowledge Graph Data

The knowledge graph contains:
- **51 documentation pages** across 8 categories
- **733 edges** (links between pages)
- **375 code examples**
- **219 internal links** + **239 section anchors** + **195 external links**

### Category Reference

| Category | Description | Key Pages |
|----------|-------------|-----------|
| Core | Getting started, fundamentals | overview, quickstart, setup |
| Configuration | Settings and customization | settings, model-config |
| Extension | Extending Claude Code | hooks, skills, plugins, mcp |
| Integration | IDE and tool integration | vs-code, github-actions |
| Enterprise | Security, compliance, costs | iam, security, costs |
| Deployment | Cloud and headless deployment | bedrock, vertex-ai, headless |
| Reference | CLI, best practices, changelog | cli-reference, best-practices |

## Data Sources

Query these files for knowledge graph data:
- `research/implementation/knowledge_maps/documentation_index.md` - Categorized index
- `research/storage/experiments/awareness_prototype.db` - Full graph database
- `research/implementation/knowledge_mapper.py` - Query tool

## Response Guidelines

1. Be specific about link counts and relationships
2. Include relevant code example counts
3. Suggest related topics for exploration
4. Note when information might be outdated
5. Provide clickable links where possible
