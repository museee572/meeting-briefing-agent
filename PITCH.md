# Meeting Briefing Agent — Pitch Deck

**Geek Room Global AI Hackathon 2026 · Tavily Research Agent theme**

---

## 1. Problem

Before any meeting, you need to know what changed: news, launches, hires,
results. Doing that research by hand takes 20–30 minutes of searching and
skimming — and you still miss things. Busy people walk into meetings
under-prepared.

## 2. Solution

A minimal research agent: give it a company or person and a meeting time, and
it returns a **one-page briefing in seconds** — key developments from the last
30 days, discussion points, open questions, every finding linked to its source.

## 3. How it works

```
CLI args → 3 focused Tavily queries → dedupe + top-8 → Markdown briefing
```

- Queries cover news, product launches, and leadership/people moves.
- Tavily Search API (`time_range: month`) is the retrieval layer.
- The briefing is assembled deterministically from retrieved results — every
  claim has a source link, nothing is invented.

## 4. Working prototype

```bash
export TAVILY_API_KEY="tvly-..."
python briefing_agent.py --subject "Acme Corp" --meeting "2026-11-25 10:00"
# → prints the briefing and saves briefing.md
```

No API key? `python briefing_agent.py --subject "Acme Corp" --meeting
"2026-11-25 10:00" --mock` runs the full pipeline on labelled sample data.

Sample output: [`example_briefing.md`](example_briefing.md).

## 5. Tech stack

- Python 3, standard library only (zero dependencies)
- Tavily Search API (REST)
- Markdown output

## 6. What makes it useful

- **Fast:** seconds, not 30 minutes.
- **Grounded:** every finding links to a source.
- **Portable:** one file, no services to run, output pastes anywhere.

## 7. What's next

- Optional LLM rewrite pass (citations preserved).
- Tavily Extract for full detail on top findings.
- Calendar integration: auto-brief every meeting tomorrow.
