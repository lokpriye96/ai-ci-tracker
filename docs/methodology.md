# Methodology

## 1. Scope
- **Question:** How are the leading IT services firms competing in generative and agentic AI?
- **Competitors:** Accenture, TCS, Infosys, Wipro, HCLTech, Cognizant, Capgemini, Tech Mahindra. These are the firms enterprise buyers and sourcing advisors most often benchmark against each other.
- **Window:** 1 Jun 2025 – Nov 2026 (updated weekly).
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
3. **Validate.** Hard rules reject an event; soft rules send it to review (see README). Duplicates are matched on company, type and counterparty within 30 days, headline similarity above 60%, the same source URL and type, or the same type within 14 days with closely matching summaries. Two rules ignore dates: an acquisition, investment or divestiture with the same counterparty is one deal, and one source article with the same counterparty is one announcement. If the LLM leaves the company blank, the competitor whose news query found the article is used.
4. **Review.** Every new event lands in `data/review_queue.csv`: rule-passed events as *Awaiting approval*, the rest as *Needs review*. The analyst opens each source and approves, corrects or rejects it. Only approved events enter `data/ci_events.csv`. Removed or merged IDs go to `data/retired_ids.csv` with the reason and are never reused.
5. **Analyse.** Findings and battle cards in `src/ci_tracker/insights.py` cite event IDs, so every claim can be traced to a source.

## 4. Source rules
- **Primary:** company newsroom, PR Newswire, Business Wire, GlobeNewswire, NSE/BSE/SEC filings, partner press rooms.
- **Secondary:** established business and trade media (Business Standard, Reuters syndication, TechCrunch, SiliconANGLE, IT Brief, etc.).
- **Not accepted alone:** forums, social media, personal blogs.
- If a deal value appears only in a secondary report (for example, Infosys deal values taken from a Crisil report), `value_note` says so.

## 5. Review protocol
The 60 seed events were collected with LLM-assisted web research. For each one, the analyst checked the date, the counterparty and any value against the linked source.

The first live runs (11 and 16 Nov 2026) published rule-passed events straight to the database. The analyst review on 22 Nov 2026 found that this let errors through, so the design changed:
- **Removed (5):** two repeat mentions of old deals (WNS, the $1.14B HCLTech deal), an award logged as a partnership, a 2024-25 case study outside the window, and a report about an AI-citation controversy logged as a partnership.
- **Merged (2):** two announcements the LLM had split into two events each (Tech Mahindra–Google Cloud, Wipro–Labelbox).
- **Corrected:** dates and sources moved to the original announcement (for example HCLTech FY26 results, Sarvam AI, Infosys–OpenAI, Wipro–Aggne), with primary sources where available.
- **Added:** real events the pipeline had rejected because the LLM left the company blank (Accenture–Qantas, Cognizant–Wizeline), cleared review-queue items (Cognizant Claude group, Tech Mahindra–Uniphore, HCLTech $876M AI run-rate), and gaps found in checking (HCLTech–Anthropic, Infosys Q2 FY27 AI revenue).
- **Pipeline fixes:** rule-passed events now wait for approval; the duplicate check covers the review queue and repeat mentions of old deals; IDs are never reused. Each fix has a regression test.

Result: 79 events, all verified against their source. Every change is listed in `data/retired_ids.csv`.

## 7. Refresh cadence
Automated weekly in GitHub Actions (Mondays) using the Gemini API. The analyst clears `data/review_queue.csv` after each run by typing Approve or Reject in each row's `decision` column and committing; the *Apply analyst review* workflow (`apply_review.py`) publishes the decisions and rebuilds all outputs. Findings are re-written monthly.
