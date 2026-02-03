---
name: why-practice
description: Recursive "why?" questioning to deepen understanding before action. Expands the surface area of priorities and tasks to illuminate the dependency network of vision.
---

# The Why Practice

## Purpose

The Why Practice suspends Claude's tendency to jump in and solve problems. Instead, it deepens understanding through recursive questioning. Given a topic, ask "why?" After explaining why, ask "why?" to the explanation. Repeat recursively for approximately 5 minutes.

This practice:
- Expands the surface area of priorities and tasks
- Illuminates the dependency network of the full vision
- Reveals closed loops where tool serves vision and vision demands tool
- Grounds action in deep understanding

## Invocation

When the user requests the Why Practice (or `/why-practice`), follow this protocol:

### Step 1: Topic Selection

If no topic is provided, use the AskUserQuestion tool to offer options based on current context. Example categories:
- Current project or task
- Infrastructure decisions
- Methodology choices
- Conceptual foundations

### Step 2: Begin the Practice

Ask the first "why?" question:

```
**Why?**

Why [topic reframed as question]?

*Take your time. I'll follow your answer with another "why."*
```

### Step 3: Recursive Questioning

After each user response:
1. Acknowledge the essence of what they said (optionally)
2. Ask "why?" to their explanation
3. Continue for approximately 5-8 iterations or until a natural loop closes

Example transitions:
- "Why is that important?"
- "Why does that matter?"
- "Why [key phrase from their answer]?"

### Step 4: Recognize the Loop

When the questioning returns to the original topic or reveals a closed loop, acknowledge it:

```
---

*We've arrived back at the beginning.*

---

**The Loop:**

1. [First answer]
2. → [Second answer]
3. → [Third answer]
...
→ **[Original topic]**

---

[Synthesis statement about tool serving vision / vision demanding tool]
```

### Step 5: Logging

After completing the practice, ask if the user wants to log it:

```
*Should we log this and continue exploring another thread — or sit with what emerged?*
```

If yes, write a log file to `.claude/local/reports/YYYY/MM/DD/why-practice-{topic-slug}.md` containing:

1. **Header**: Date, participant, facilitator, duration
2. **Topic**: The chosen topic
3. **Full transcript**: Each question and answer verbatim
4. **The Loop**: The synthesized chain of reasoning
5. **Tags**: Relevant tags for the content
6. **Extracted questions**: Any questions that emerged for future exploration

## Example Session

See reference implementation: `.claude/local/reports/2026/01/30/why-practice-universal-task-networks.md`

## When to Use

- Before starting a new project or feature
- When feeling overwhelmed by complexity
- When unsure which direction to take
- When wanting to connect tactical work to larger vision
- When needing to suspend the urge to act
- At the beginning of a writing session

## The Insight

The Why Practice reveals that deep work and its infrastructure are not separate. The questions:
- "Why do we need X?" eventually arrives at deep values
- Those values eventually require X to manifest

**The tool serves the vision. The vision demands the tool.**

## Tags for This Skill

`#why-practice` `#dialectic` `#metacognition` `#understanding` `#vision` `#grounding`
