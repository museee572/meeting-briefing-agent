#!/usr/bin/env python3
"""Meeting Briefing Agent — a minimal Tavily Research Agent.

Given a company or person and a meeting time, research the subject's recent
developments (default: last 30 days) via the Tavily Search API and produce a
concise one-page Markdown briefing: source-backed findings, discussion points
and open questions.

Usage:
    export TAVILY_API_KEY="tvly-..."
    python briefing_agent.py --subject "Acme Corp" --meeting "2026-11-25 10:00"

Demo mode (no API key needed, canned results):
    python briefing_agent.py --subject "Acme Corp" --meeting "2026-11-25 10:00" --mock

Built for the Geek Room Global AI Hackathon 2026 (Tavily Research Agent theme).
Standard library only — no third-party dependencies.
"""

import argparse
import datetime
import json
import os
import sys
import urllib.error
import urllib.request

TAVILY_API_URL = "https://api.tavily.com/search"
DEFAULT_DAYS = 30
MAX_RESULTS_PER_QUERY = 5
MAX_FINDINGS = 8

# Canned results for --mock mode so the full pipeline can be demonstrated
# and tested without an API key. Clearly labelled as demo data.
MOCK_RESULTS = [
    {
        "title": "Acme Corp launches Acme Cloud 2.0 with edge inference",
        "url": "https://example.com/news/acme-cloud-2",
        "content": "Acme Corp announced Acme Cloud 2.0, adding edge inference "
                   "nodes in 12 new regions and cutting p99 latency by 40%. "
                   "The release targets AI workloads that need low-latency "
                   "inference close to end users.",
        "published_date": "2026-11-12",
    },
    {
        "title": "Acme Corp appoints new CTO to lead AI platform push",
        "url": "https://example.com/news/acme-new-cto",
        "content": "Acme Corp named a new chief technology officer to lead its "
                   "AI platform strategy, signalling heavier investment in "
                   "agent infrastructure and developer tooling.",
        "published_date": "2026-11-08",
    },
    {
        "title": "Acme Corp reports Q3 revenue up 22% on AI products",
        "url": "https://example.com/news/acme-q3",
        "content": "Acme Corp reported third-quarter revenue up 22% year over "
                   "year, driven by growth in its AI product line and new "
                   "enterprise contracts.",
        "published_date": "2026-11-03",
    },
]


def build_queries(subject):
    """Three focused queries covering news, launches and people moves."""
    return [
        f"{subject} news",
        f"{subject} product launch announcement",
        f"{subject} leadership hiring executive",
    ]


def tavily_search(api_key, query, max_results=MAX_RESULTS_PER_QUERY):
    """Call the Tavily Search API. Returns a list of result dicts."""
    payload = json.dumps({
        "api_key": api_key,
        "query": query,
        "search_depth": "basic",
        "max_results": max_results,
        "time_range": "month",
        "include_answer": False,
    }).encode("utf-8")
    req = urllib.request.Request(
        TAVILY_API_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"Tavily API HTTP {exc.code}: {exc.read().decode('utf-8', 'replace')[:200]}")
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Tavily API request failed: {exc.reason}")
    return data.get("results", [])


def dedupe(results):
    """Drop duplicate results by URL, preserving order."""
    seen = set()
    out = []
    for r in results:
        url = r.get("url", "")
        if url and url not in seen:
            seen.add(url)
            out.append(r)
    return out


def first_sentence(text, limit=180):
    """Trim content to a readable one-sentence summary."""
    text = " ".join((text or "").split())
    if not text:
        return ""
    for sep in (". ", "。", "!\n", "?\n"):
        if sep in text:
            text = text.split(sep, 1)[0]
            break
    text = text.rstrip(".。")
    if len(text) > limit:
        text = text[:limit].rsplit(" ", 1)[0] + "…"
    return text


def render_briefing(subject, meeting, findings, days, mock=False):
    """Render the one-page Markdown briefing."""
    today = datetime.date.today().isoformat()
    lines = []
    lines.append(f"# Meeting Briefing: {subject}")
    lines.append("")
    lines.append(f"- **Meeting:** {meeting}")
    lines.append(f"- **Prepared:** {today} (developments from the last {days} days)")
    if mock:
        lines.append("- **Note:** demo mode — findings below are canned sample data, not live search results.")
    lines.append("")
    lines.append("## Key developments")
    lines.append("")
    if not findings:
        lines.append("No recent developments found in the search window.")
    for f in findings:
        summary = first_sentence(f.get("content", ""))
        title = f.get("title", "Untitled")
        url = f.get("url", "")
        date = f.get("published_date", "")
        date_part = f" ({date})" if date else ""
        lines.append(f"- **{title}**{date_part} — {summary} ([source]({url}))")
    lines.append("")
    lines.append("## Discussion points")
    lines.append("")
    if findings:
        for f in findings[:3]:
            lines.append(f"- How does \"{f.get('title', '')}\" change what we should ask for in this meeting?")
    else:
        lines.append("- No recent news to anchor on — open with the subject's current priorities.")
    lines.append("- What has changed since our last conversation with them?")
    lines.append("")
    lines.append("## Open questions")
    lines.append("")
    lines.append(f"- What is {subject}'s roadmap for the next quarter?")
    lines.append(f"- Which risks or blockers is {subject} facing right now?")
    lines.append(f"- Is there a partnership or integration angle worth exploring?")
    lines.append("")
    lines.append("## Sources")
    lines.append("")
    for f in findings:
        lines.append(f"- {f.get('title', '')} — {f.get('url', '')}")
    lines.append("")
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Meeting Briefing Agent (Tavily Research Agent)")
    parser.add_argument("--subject", required=True, help="Company or person to research")
    parser.add_argument("--meeting", required=True, help="Meeting date/time, e.g. '2026-11-25 10:00'")
    parser.add_argument("--days", type=int, default=DEFAULT_DAYS, help="Lookback window in days (default 30)")
    parser.add_argument("--output", default="briefing.md", help="Output Markdown file (default briefing.md)")
    parser.add_argument("--mock", action="store_true", help="Demo mode: use canned results, no API key needed")
    args = parser.parse_args(argv)

    api_key = os.environ.get("TAVILY_API_KEY", "")
    if not args.mock and not api_key:
        print("error: TAVILY_API_KEY is not set (or run with --mock for demo mode).",
              file=sys.stderr)
        return 2

    all_results = []
    if args.mock:
        all_results = list(MOCK_RESULTS)
    else:
        for query in build_queries(args.subject):
            print(f"Searching Tavily: {query}", file=sys.stderr)
            try:
                all_results.extend(tavily_search(api_key, query))
            except RuntimeError as exc:
                print(f"error: {exc}", file=sys.stderr)
                return 1

    findings = dedupe(all_results)[:MAX_FINDINGS]
    briefing = render_briefing(args.subject, args.meeting, findings, args.days, mock=args.mock)

    with open(args.output, "w", encoding="utf-8") as fh:
        fh.write(briefing)
    print(briefing)
    print(f"\nSaved to {args.output}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
