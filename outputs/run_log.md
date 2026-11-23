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

> **12 Nov 2026 – analyst review of run 43038980496:** removed 2 duplicates (INF-010, CAP-009), moved WIP-012 (general results, no AI angle) to review, re-typed WIP-011 as an Investment, and wrote missing headlines. Pipeline fixed so blank headlines and these duplicates are caught automatically.

## Run 2026-11-16 11:31 UTC
- Trigger: GitHub Actions · run 43857574263
- LLM: gemini / gemini-3.5-flash-lite · look-back 14 days
- Articles sent to LLM: 32 · LLM errors: 0
- Candidate events: 19 → verified 7, needs review 3, rejected 5, duplicates skipped 4
  - Collected: Accenture: 10 event-like via Bing News, 4 kept, 1 with article text
  - Collected: TCS: 10 event-like via Bing News, 4 kept, 3 with article text
  - Collected: Infosys: 9 event-like via Bing News, 4 kept, 3 with article text
  - Collected: Wipro: 10 event-like via Bing News, 4 kept, 3 with article text
  - Collected: HCLTech: 11 event-like via Bing News, 4 kept, 3 with article text
  - Collected: Cognizant: 12 event-like via Bing News, 4 kept, 3 with article text
  - Collected: Capgemini: 7 event-like via Bing News, 4 kept, 4 with article text
  - Collected: Tech Mahindra: 8 event-like via Bing News, 4 kept, 3 with article text
  - [Verified] TCS-011 TCS: TCS hosts large-scale AI hackathon for non-engineering students (https://www.businesstoday.in/technology/story/building-ai-ready-workforce-tcs-hosts-ai-hackathon-for-10000-non-engineering-students-515941-2026-02-12)
  - [Verified] WIP-012 Wipro: Capco recognized by OpenAI for AI innovation (https://finance.yahoo.com/technology/ai/articles/wipro-builds-ai-momentum-capco-002816032.html)
  - [Verified] WIP-013 Wipro: Wipro completes data center migration for METRO (https://finance.yahoo.com/technology/ai/articles/wipro-builds-ai-momentum-capco-002816032.html)
  - [Verified] HCL-012 HCLTech: HCLTech Secures $1.14 Billion Mega AI Deal From Mercedes-Benz (https://www.moneycontrol.com/news/business/information-technology/hcltech-reports-876-million-in-annualised-advanced-ai-revenue-up-72-yoy-14050421.html)
  - [Verified] CAP-009 Capgemini: Capgemini and AWS build TELme conversational AI platform (https://www.crn.com/news/ai/2026/capgemini-vp-on-3-huge-aws-opportunities-and-ai-customer-wins)
  - [Verified] CAP-010 Capgemini: Capgemini acquires WNS for agentic AI operations (https://www.crn.com/news/ai/2026/capgemini-vp-on-3-huge-aws-opportunities-and-ai-customer-wins)
  - [Verified] CAP-011 Capgemini: Capgemini promotes AI Yield metric for value measurement (https://www.ad-hoc-news.de/boerse/news/corporate-news/capgemini-stock-gains-as-ai-costs-drive-multi-model-shift/70500055)
  - [Needs review] INF-010 Infosys: Infosys to hire 20,000 freshers (https://www.msn.com/en-in/money/topstories/infosys-is-hiring-20000-freshers-in-the-ai-era-but-will-their-jobs-look-the-same/ar-AA2ei5wR)
  - [Needs review] HCL-011 HCLTech: HCLTech reports $219 million in advanced AI revenue (https://www.businessworld.in/article/hcltech-flags-early-ai-led-deflation-as-advanced-ai-revenue-hits-219-mn-628175)
  - [Needs review] TEM-009 Tech Mahindra: Tech Mahindra and Uniphore launch Agentic AI Factory partnership (https://www.msn.com/en-us/money/general/uniphore-and-tech-mahindra-launch-agentic-ai-factory-partnership/ar-AA2b7Mgk)
  - [Rejected] : Accenture secures 850-role IT and AI outsourcing mandate from Qantas - company not in tracked list
  - [Rejected] Infosys: Infosys Launches Topaz for SAP S/4HANA Cloud - event before tracking window
  - [Rejected] : Wipro launches Google Gemini Experience Zone for AI adoption - company not in tracked list; event before tracking window
  - [Rejected] : HCLTech partners with OpenAI for enterprise AI transformation - company not in tracked list
  - [Rejected] : Cognizant acquires Wizeline for digital engineering expansion - company not in tracked list

> **22 Nov 2026 – analyst review:** all 79 events reviewed; those with deal values, dates in question or weak sources re-checked against their sources (the rest were validated at the seed review). Added 7 in total. Removed 5 (CAP-010 and HCL-012 repeated old deals; WIP-012 was an award, not a partnership; CAP-009 was a 2024-25 case study; ACN-008 was a report about AI-fabricated citations, not a partnership). Merged 2 split announcements (TEM-007 into TEM-006, WIP-010 into WIP-009). Corrected dates and sources, mostly to the original announcement. Added ACN-009 (Qantas) and CTS-011 (Wizeline), which the 16 Nov run had wrongly rejected because the LLM left the company blank, and cleared the review queue. Pipeline changed: from now on every new event waits in `data/review_queue.csv` until an analyst approves it. Details in `data/retired_ids.csv`.

## Run 2026-11-23 12:30 UTC
- Trigger: GitHub Actions · run 45173968286
- LLM: gemini / gemini-3.5-flash-lite · look-back 14 days
- Articles sent to LLM: 32 · LLM errors: 0
- Candidate events: 21 → verified 16, needs review 1, rejected 1, duplicates skipped 3
  - Collected: Accenture: 12 event-like via Bing News, 4 kept, 3 with article text
  - Collected: TCS: 11 event-like via Bing News, 4 kept, 4 with article text
  - Collected: Infosys: 10 event-like via Bing News, 4 kept, 3 with article text
  - Collected: Wipro: 11 event-like via Bing News, 4 kept, 4 with article text
  - Collected: HCLTech: 11 event-like via Bing News, 4 kept, 3 with article text
  - Collected: Cognizant: 12 event-like via Bing News, 4 kept, 4 with article text
  - Collected: Capgemini: 10 event-like via Bing News, 4 kept, 4 with article text
  - Collected: Tech Mahindra: 7 event-like via Bing News, 4 kept, 3 with article text
  - [Verified] ACN-010 Accenture: Accenture and Mondelēz partner for agentic AI Order-to-Cash (https://finance.yahoo.com/technology/ai/articles/accenture-acn-expands-ai-major-181048770.html)
  - [Verified] TCS-012 TCS: HCLTech Reports $219 Million in Q2 Advanced AI Revenue (https://www.businesstoday.in/markets/stocks/story/tcs-vs-hcl-tech-how-2-it-giants-stack-up-in-the-ai-race-after-q2-results-561285-2026-10-13)
  - [Verified] TCS-013 TCS: HCLTech and Anthropic Form Global Premier Partnership (https://www.businesstoday.in/markets/stocks/story/tcs-vs-hcl-tech-how-2-it-giants-stack-up-in-the-ai-race-after-q2-results-561285-2026-10-13)
  - [Verified] TCS-014 TCS: TCS expands AI partnership with ABB (https://yourstory.com/ai-story/tcs-abb-ai-deal-hiring-acquisitions)
  - [Verified] TCS-015 TCS: TCS plans to deploy 8,900 forward-deployed engineers (https://yourstory.com/ai-story/tcs-abb-ai-deal-hiring-acquisitions)
  - [Verified] WIP-014 Wipro: Wipro launches AI-Native Business and Platforms Unit (https://tech.yahoo.com/ai/articles/internet-agents-next-shift-wipro-130000362.html)
  - [Verified] WIP-015 Wipro: Wipro selected for life sciences supply chain AI platform (https://supplychaindigital.com/news/how-wipro-deploys-wega-ai-agents-for-supply-chain-intelligen)
  - [Verified] WIP-016 Wipro: Wipro closes US$2.6bn in total contract value (https://supplychaindigital.com/news/how-wipro-deploys-wega-ai-agents-for-supply-chain-intelligen)
  - [Verified] HCL-015 HCLTech: HCLTech and NetApp partner for STaaS (https://telecom.economictimes.indiatimes.com/news/enterprise-services/hcltech-netapp-partner-on-staas-to-drive-enterprise-ai-adoption/133209645)
  - [Verified] HCL-016 HCLTech: HCLTech partners with Cohere for sovereign AI solutions (https://cio.economictimes.indiatimes.com/news/business-analytics/hcltech-cohere-partner-to-build-sovereign-ai-solutions-for-enterprises-and-governments/135946935)
  - [Verified] CTS-012 Cognizant: Cognizant launches Patient Hub Operations built with NVIDIA (https://finance.yahoo.com/technology/ai/articles/cognizant-technology-solutions-ctsh-puts-190639419.html)
  - [Verified] CTS-013 Cognizant: Cognizant expands AI cybersecurity partnership with Qualys (https://finance.yahoo.com/technology/ai/articles/cognizant-technology-solutions-ctsh-puts-190639419.html)
  - [Verified] CTS-014 Cognizant: Cognizant opens AI training centre in Chennai (https://www.moneycontrol.com/artificial-intelligence/cognizant-opens-chennai-training-centre-targets-15-000-ai-certified-employees-article-14085042.html)
  - [Verified] CAP-012 Capgemini: Capgemini to lead European Commission AI safety consortium (https://finance.yahoo.com/technology/ai/articles/capgemini-selected-lead-european-commission-073000347.html)
  - [Verified] TEM-010 Tech Mahindra: Tech Mahindra and Rezolve Ai form global agentic commerce alliance (https://finance.yahoo.com/technology/ai/articles/rezolve-ai-tech-mahindra-forge-120000727.html)
  - [Verified] TEM-011 Tech Mahindra: Tech Mahindra Partners With SpaceXSI For AI-Assisted Software Engineering (https://www.rediff.com/business/report/tech-mahindra-and-spacexsi-partner-for-ai-software-engineering/20261022.htm)
  - [Needs review] HCL-014 HCLTech: HCLTech Reports $219 Million in Advanced AI Revenue (https://www.businessworld.in/article/hcltech-flags-early-ai-led-deflation-as-advanced-ai-revenue-hits-219-mn-628175)
  - [Rejected] Infosys: Infosys Launches Topaz for SAP S/4HANA Cloud - event before tracking window
