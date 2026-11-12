# Methodology

## 1. Scope
- **Question:** How are the leading IT services firms competing in generative and agentic AI?
- **Competitors:** Accenture, TCS, Infosys, Wipro, HCLTech, Cognizant, Capgemini, Tech Mahindra. These are the firms enterprise buyers and sourcing advisors most often benchmark against each other.
- **Window:** 1 Jun 2025 – 11 Nov 2026.
- **In scope:** AI-related acquisitions, investments, partnerships, platform launches, talent and CoE commitments, AI-led deals and GCC takeovers, AI revenue disclosures, and portfolio moves that shape the AI strategy.

## 2. Taxonomy
| Field | Values |
|---|---|
| Event type | Acquisition, Partnership, Launch, Investment, Deal / GCC, Talent / CoE, Financial disclosure, Client proof point, Divestiture |
| Counterparty type | Frontier model lab, Hyperscaler, Enterprise platform, Chip / compute, AI-native firm, Domain consultancy, Client, … |
| Strategic theme | 20 themes, e.g. Frontier-lab alliance, Forward-deployed talent, GCC / captive takeover, Sovereign / India AI |

The full lists live in `src/ci_tracker/config.py`, so the taxonomy is version-controlled.

## 3. Pipeline
1. **Collect.** GDELT DOC API query per competitor (company + AI terms, last 14 days), with Google News RSS as fallback, or a list of press-release URLs from the analyst. Only headlines that name the company and look like an event (acquire, partner, launch, deal…) are sent to the LLM, capped at 6 per competitor per run.
2. **Extract.** The prompt (`prompts/extract_event.md`) tells the LLM to use only facts stated in the article, to write the summary in its own words, and to return an exact `evidence_quote`. Temperature is 0 and output is JSON.
3. **Validate.** Hard rules reject an event; soft rules send it to review (see README). Duplicates are matched on company, type and counterparty within 30 days, headline similarity above 60%, the same source URL and type, or the same type within 14 days with closely matching summaries.
4. **Review.** The analyst opens the source for every event in `data/review_queue.csv` and then approves, corrects or rejects it.
5. **Analyse.** Findings and battle cards in `src/ci_tracker/insights.py` cite event IDs, so every claim can be traced to a source.

## 4. Source rules
- **Primary:** company newsroom, PR Newswire, Business Wire, GlobeNewswire, NSE/BSE/SEC filings, partner press rooms.
- **Secondary:** established business and trade media (Business Standard, Reuters syndication, TechCrunch, SiliconANGLE, IT Brief, etc.).
- **Not accepted alone:** forums, social media, personal blogs.
- If a deal value appears only in a secondary report (for example, Infosys deal values taken from a Crisil report), `value_note` says so.

## 5. Review protocol (seed database)
The 60 seed events were collected with LLM-assisted web research. For each one, the analyst checked the date, the counterparty and any value against the linked source. Two events are deliberately left as **Needs review**:
- `INF-008`: only the article update date is known, not the announcement date.
- `WIP-007`: the stake size is unconfirmed and the only source is an aggregator.

## 6. Pipeline additions
The first successful live run (11 Nov 2026) added 15 events; analyst review removed 2 duplicates and moved 1 non-AI item to review, leaving 12. See `outputs/run_log.md`.

## 7. Refresh cadence
Automated weekly in GitHub Actions (Mondays) using GitHub Models. The analyst clears `data/review_queue.csv` after each run and re-writes findings monthly.
