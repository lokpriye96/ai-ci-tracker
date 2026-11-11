# Pipeline run log

Every automated or manual run is recorded here.

> **11 Nov 2026 – setup note:** four test runs in GitHub Actions failed at the LLM step because they targeted GitHub Models, which GitHub retired on 30 Jul 2026. News collection worked (42–48 event-like articles per run). The pipeline was switched to the Gemini API, with the key held as an encrypted GitHub secret.

## Run 2026-11-11 14:46 UTC
- Trigger: GitHub Actions · run 43038980496
- LLM: gemini / gemini-3.5-flash-lite · look-back 14 days
- Articles sent to LLM: 32 · LLM errors: 0
- Candidate events: 27 → verified 15, needs review 2, rejected 9, duplicates skipped 1
  - Collected: Accenture: 9 event-like via Bing News, 4 kept, 3 with article text
  - Collected: TCS: 11 event-like via Bing News, 4 kept, 4 with article text
  - Collected: Infosys: 10 event-like via Bing News, 4 kept, 4 with article text
  - Collected: Wipro: 11 event-like via Bing News, 4 kept, 3 with article text
  - Collected: HCLTech: 12 event-like via Bing News, 4 kept, 2 with article text
  - Collected: Cognizant: 7 event-like via Bing News, 4 kept, 2 with article text
  - Collected: Capgemini: 12 event-like via Bing News, 4 kept, 4 with article text
  - Collected: Tech Mahindra: 9 event-like via Bing News, 4 kept, 4 with article text
  - [Verified] ACN-008 Accenture:  (https://finance.yahoo.com/technology/ai/articles/accenture-accused-publishing-research-full-122237861.html)
  - [Verified] TCS-009 TCS:  (https://www.moneycontrol.com/news/business/information-technology/tcs-salesforce-consulting-bets-gives-it-an-edge-over-rivals-in-agentic-ai-say-analysts-13721696.html)
  - [Verified] TCS-010 TCS:  (https://www.moneycontrol.com/news/business/information-technology/tcs-salesforce-consulting-bets-gives-it-an-edge-over-rivals-in-agentic-ai-say-analysts-13721696.html)
  - [Verified] INF-010 Infosys:  (https://www.prnewswire.com/in/news-releases/infosys-unveils-ai-first-value-framework-uniquely-positioned-to-capture-new-ai-services-opportunity-of-over-300-billion-302689496.html)
  - [Verified] WIP-009 Wipro:  (https://finance.yahoo.com/technology/ai/articles/labelbox-partners-wipro-scale-adoption-170000136.html)
  - [Verified] WIP-010 Wipro:  (https://finance.yahoo.com/technology/ai/articles/labelbox-partners-wipro-scale-adoption-170000136.html)
  - [Verified] WIP-011 Wipro:  (https://www.adgully.com/post/22390/wipro-acquires-20-stake-in-agentic-ai-start-up-flarreai)
  - [Verified] WIP-012 Wipro:  (https://www.adgully.com/post/22390/wipro-acquires-20-stake-in-agentic-ai-start-up-flarreai)
  - [Verified] HCL-010 HCLTech:  (https://cio.economictimes.indiatimes.com/news/artificial-intelligence/hcltech-launches-ai-agents-to-automate-enterprise-mainframe-operations/135452621)
  - [Verified] CAP-007 Capgemini:  (https://www.engineering.com/capgemini-to-lead-eu-consortium-assessing-advanced-ai-risks/)
  - [Verified] CAP-008 Capgemini:  (https://www.ad-hoc-news.de/boerse/news/corporate-news/capgemini-stock-gains-telia-sweden-ai-transformation-mandate/70485106)
  - [Verified] CAP-009 Capgemini:  (https://finance.yahoo.com/technology/ai/articles/capgemini-selected-lead-european-commission-073000347.html)
  - [Verified] TEM-006 Tech Mahindra:  (https://www.zawya.com/en/press-release/companies-news/tech-mahindra-expands-agentic-ai-readiness-with-google-cloud-gemini-enterprise-1517787)
  - [Verified] TEM-007 Tech Mahindra:  (https://www.zawya.com/en/press-release/companies-news/tech-mahindra-expands-agentic-ai-readiness-with-google-cloud-gemini-enterprise-1517787)
  - [Verified] TEM-008 Tech Mahindra:  (https://finance.yahoo.com/technology/ai/articles/tech-mahindra-launches-aws-agentic-130000684.html)
  - [Needs review] CTS-010 Cognizant:  (https://www.msn.com/en-us/technology/artificial-intelligence/cognizant-establishes-25-000-person-claude-ai-group-and-introduces-enterprise-managed-services/ar-AA2h9wtf)
  - [Needs review] TEM-005 Tech Mahindra:  (https://www.msn.com/en-us/money/general/uniphore-and-tech-mahindra-launch-agentic-ai-factory-partnership/ar-AA2b7Mgk)
  - [Rejected] :  - company not in tracked list
  - [Rejected] :  - company not in tracked list
  - [Rejected] :  - company not in tracked list
  - [Rejected] :  - company not in tracked list
  - [Rejected] :  - company not in tracked list; event before tracking window
  - [Rejected] :  - company not in tracked list
  - [Rejected] HCLTech:  - event before tracking window; article text unavailable (headline only)
  - [Rejected] :  - company not in tracked list
  - [Rejected] Capgemini:  - event before tracking window
