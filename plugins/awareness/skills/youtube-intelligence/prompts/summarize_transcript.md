# Transcript Summary Prompt

## Context

You are analyzing a YouTube video transcript about Claude Code or AI development tools.

## Video Information

<fill_in_video_info_here>
```yaml
title: <video title>
channel: <channel name>
duration: <video duration>
url: <video url>
```
</fill_in_video_info_here>

## Transcript

<fill_in_transcript_here>
```
<paste the full transcript here>
```
</fill_in_transcript_here>

## Analysis Task

Analyze this transcript and provide:

### 1. Main Topic Summary (2-3 sentences)
What is this video primarily about? Who is the target audience?

### 2. Key Technical Points (3-5 bullet points)
What specific Claude Code features, techniques, or concepts are discussed?

### 3. Code/Configuration Examples
List any code snippets, commands, or configuration examples mentioned.

### 4. Actionable Takeaways (3-5 bullet points)
What can the viewer immediately apply to their own workflow?

### 5. Related Documentation
Based on the content, which Claude Code documentation pages would be most relevant?

### 6. Notable Quotes
Extract 1-2 memorable or insightful quotes from the transcript.

## Output Format

```yaml
summary:
  main_topic: "<2-3 sentence summary>"
  target_audience: "<who this is for>"

technical_points:
  - "<point 1>"
  - "<point 2>"
  - "<point 3>"

code_examples:
  - type: "<bash|json|python|etc>"
    description: "<what it does>"
    snippet: "<the code if mentioned verbatim>"

actionable_takeaways:
  - "<takeaway 1>"
  - "<takeaway 2>"
  - "<takeaway 3>"

related_docs:
  - "<doc1.md>"
  - "<doc2.md>"

notable_quotes:
  - "<quote 1>"
  - "<quote 2>"

quality_assessment:
  depth: "<shallow|moderate|deep>"
  accuracy: "<verified|unverified|outdated>"
  recommendation: "<highly recommend|worth watching|skip>"
```
