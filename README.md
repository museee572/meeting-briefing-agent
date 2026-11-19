# Meeting Briefing Agent

A minimal **Tavily Research Agent**: given a company or person and a meeting
time, it researches the subject's recent developments (last 30 days) via the
Tavily Search API and produces a concise **one-page meeting briefing** —
source-backed findings, discussion points and open questions.

Built for the **Geek Room Global AI Hackathon 2026** (Tavily Research Agent
theme). Standard library only — no third-party dependencies.

## Problem

Before a meeting with a company or person, you need to know what changed
recently: news, launches, hires, results. Manually searching and skimming
takes 20–30 minutes and still misses things. This agent does the research
pass in seconds and hands you a one-page brief you can read in two minutes.

## Solution

A small command-line agent:

1. Builds three focused Tavily queries (news, launches, leadership/people).
2. Searches the last 30 days via the Tavily Search API.
3. Deduplicates results and keeps the top findings.
4. Renders a one-page Markdown briefing: key developments with source links,
   discussion points anchored on the findings, open questions, and a source list.

## How AI is used

- **Tavily AI search** is the retrieval layer: an AI-powered search API that
  returns relevant, recent, source-backed results for each query.
- The briefing is assembled from those retrieved results — every finding in
  the brief links back to its source, so nothing is invented.
- No separate LLM call is made in this minimal version; the synthesis step is
  deterministic extraction + templating over Tavily results, which keeps the
  output grounded and the prototype dependency-free.

## Installation

Requires Python 3.10+ (standard library only).

```bash
git clone https://github.com/museee572/meeting-briefing-agent.git
cd meeting-briefing-agent
export TAVILY_API_KEY="tvly-..."   # get one at https://tavily.com (free tier: 1,000 credits/month)
```

## Usage

```bash
python briefing_agent.py --subject "Acme Corp" --meeting "2026-11-25 10:00"
```

Options:

- `--days N` — lookback window in days (default 30)
- `--output FILE` — output Markdown file (default `briefing.md`)
- `--mock` — demo mode with canned results, no API key needed

Example output: see [`example_briefing.md`](example_briefing.md) (generated
with `--mock`, sample data labelled as such).

## Architecture

```
CLI args ──> query builder ──> Tavily Search API (3 queries, last 30 days)
                                        │
                                        ▼
                              dedupe + top-8 findings
                                        │
                                        ▼
                              briefing renderer ──> briefing.md (Markdown)
```

Single file, ~200 lines. The only external call is `POST
https://api.tavily.com/search`.

## Technologies

- Python 3 (standard library: `argparse`, `urllib`, `json`)
- Tavily Search API (REST)
- Markdown output — readable anywhere, pasteable into notes/docs

## Project structure

| File | What it is |
| --- | --- |
| `briefing_agent.py` | The agent: search + briefing generation |
| `example_briefing.md` | Sample briefing output (mock data) |
| `PITCH.md` | Pitch deck: problem, solution, architecture, demo |
| `README.md` | This file |

## Future work

- Optional LLM pass to rewrite findings into tighter prose (with source
  citations preserved).
- Tavily Extract for full-article detail on the top 2–3 findings.
- Calendar integration: auto-generate a brief for every meeting on tomorrow's
  calendar.

## License

MIT.
