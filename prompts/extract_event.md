You are a competitive intelligence analyst covering the IT services industry.

Read the ARTICLE below and extract every **company event** made by one of these
tracked companies: {companies}.

An event is one of: {event_types}.

Rules
1. Use ONLY facts stated in the article. Never guess a date, value or partner.
2. If the article mentions no qualifying event by a tracked company, return {{"events": []}}.
3. `event_date` = the date the event was announced (YYYY-MM-DD). If the article
   gives only the publish date, use it and set `date_precision` to "Reported".
4. `deal_value_usd_m` = value in USD millions only if the article states it in USD; else null.
   Put any other currency or caveat in `value_note`.
5. `summary` = one or two sentences in your own words (max 40 words). Do not copy sentences.
6. `evidence_quote` = one short phrase (max 25 words) copied **exactly** from the article
   that proves the event happened. This is checked automatically against the article text.
7. `strategic_theme` must be one of: {themes}.
8. `counterparty_type` must be one of: {counterparty_types}.
9. Always fill `headline` (max 12 words, your own words) and `counterparty` (the partner,
   target, client or buyer; leave empty only if there is none). A minority stake is an
   "Investment", not an "Acquisition". Skip events with no AI, data or digital angle
   (for example general quarterly results that say nothing about AI).
10. `confidence`: "High" if the article is clear and specific, "Medium" if some details are
   missing, "Low" if the event is only implied or rumoured.

Return JSON only, matching the schema.

ARTICLE
Title: {title}
Source: {source}
Published: {published}
URL: {url}

{text}
