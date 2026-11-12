"""Analyst layer: key findings and battle cards.

Written by the analyst from the verified events in data/ci_events.csv (event IDs
cited in brackets). The LLM helps collect and structure the data; the "so what"
is human judgement. Update after each refresh.
"""

AS_OF = "12 Nov 2026"

KEY_FINDINGS = [
    {
        "title": "Access to frontier models is now table stakes, so the race has moved to delivery capacity",
        "evidence": "In the window, 5 of 8 firms announced an OpenAI tie-up and 3 an Anthropic one. "
                    "TCS has the widest model bench: OpenAI, Anthropic, Mistral, Google Cloud and AMD [TCS-001..006].",
        "so_what": "Saying 'we partner with OpenAI' no longer sets a firm apart. Buyers should ask who has "
                   "certified people and live production references on each model.",
    },
    {
        "title": "Talent has become the product: 'forward-deployed' and 'frontier' squads",
        "evidence": "Cognizant: 25,000+ for OpenAI and 18,000+ for Gemini [CTS-009, CTS-008]. "
                    "Wipro: 1,500 forward-deployed engineers [WIP-008]. Capgemini: Outcome Deployed Engineer "
                    "pods [CAP-004]. Accenture: Anthropic Business Group [ACN-002].",
        "so_what": "Expect AI work to be sold as named, certified pods priced on outcomes, not on headcount. "
                   "The people-model of IT services is being repackaged rather than replaced.",
    },
    {
        "title": "Two M&A playbooks: global majors buy scale, Indian majors buy vertical depth",
        "evidence": "Capgemini–WNS $3.3B [CAP-001]. Accenture: $4.9B across 17 deals in FY26 [ACN-005]. "
                    "Cognizant–Astreya ~$600M [CTS-004]. Indian peers made tuck-ins: Infosys in healthcare "
                    "($465M) and insurance ($95M); Tech Mahindra in payments; Wipro bought contracts.",
        "so_what": "WNS on its own is worth more than all disclosed acquisitions by the four Indian firms "
                   "in the tracker put together. Indian majors are trading scale for domain credibility.",
    },
    {
        "title": "Buying a client's captive centre (GCC) has become a way to win deals",
        "evidence": "Wipro–Mindsprint plus a $1B+ Olam contract [WIP-004]. HCLTech bought Guardian's India GCC "
                    "for $10.5M with a 7-year deal [HCL-008]. TCS is taking over Best Buy's India GCC "
                    "[TCS-008]. Infosys is building Truist's GCC [INF-009].",
        "so_what": "4 of 8 firms used GCC transfers in 2026. Clients' GCC leaders now face providers offering "
                   "to absorb their centres. This is a key watch area for GCC-focused intelligence teams.",
    },
    {
        "title": "Firms are racing to disclose AI revenue, but the numbers can't be compared directly",
        "evidence": "TCS: $3.1B annualised, more than 10% of revenue [TCS-007]. HCLTech: $620M of "
                    "'Advanced AI' [HCL-003]. Infosys: 5.5% of quarterly revenue (Dec-25) [INF-002]. "
                    "Capgemini: more than 10% of Q4 bookings [CAP-003].",
        "so_what": "Each firm defines 'AI revenue' differently: run-rate, bookings or a share of the "
                   "quarter. Normalise the definitions before benchmarking, or the league table misleads.",
    },
    {
        "title": "Sovereign and India-built AI is a new axis of competition",
        "evidence": "HCLTech: $150M in Sarvam AI plus 50MW of AI data centres [HCL-004, HCL-007]. "
                    "TCS HyperVault: 100MW with OpenAI [TCS-002]. Tech Mahindra: BharatGPT combined with "
                    "Project Indus [TEM-004].",
        "so_what": "Public-sector and regulated buyers in India, the Middle East and Europe will weigh where "
                   "models and data sit. Firms without a sovereignty story risk being left out of those deals.",
    },
]

WATCH_LIST = [
    "Robotiq.ai deal closing (HCLTech, expected Nov 2026) [HCL-009]",
    "Whether Wipro or Tech Mahindra announce a frontier-lab alliance (no OpenAI or Anthropic tie-up tracked for either)",
    "Accenture's ~$5B FY27 acquisition budget: which AI and industry targets [ACN-005]",
    "Cognizant's first deployment-ready Frontier cohort (Q4 2026) and named client results [CTS-005]",
    "Q3 FY27 results (Jan 2027): AI revenue disclosures from TCS, Infosys and HCLTech",
]

# How to compete is written for a hypothetical mid-tier IT services challenger.
BATTLE_CARDS = {
    "Accenture": {
        "positioning": "'Reinvention partner of choice': the most client-focused, AI-enabled firm",
        "ai_assets": "Accenture Anthropic Business Group; OpenAI flagship programme; Faculty Frontier; ~110k AI & data staff",
        "key_moves": "Anthropic and OpenAI alliances (Dec-25); Faculty acquisition, whose CEO became CTO (Jan-26); 17 deals worth $4.9B in FY26; Sagacity and Avicado (Oct-26)",
        "strengths": "Largest M&A firepower; C-suite access; allied with both leading model labs; pre-built industry assets (telecom, construction, customer)",
        "gaps": "FY27 growth guidance of only 3-6% in local currency; premium pricing; many acquisitions to integrate at once",
        "how_to_win": "Compete where price and outcome certainty matter (run-heavy deals, mid-market). Offer fixed-outcome pilots and faster time-to-value than a large Accenture programme",
    },
    "TCS": {
        "positioning": "Aims to be 'the world's largest AI-led technology services company'",
        "ai_assets": "HyperVault AI infrastructure (100MW with OpenAI); Claude business unit; ADD AgentHub; Gemini Enterprise across its portfolio",
        "key_moves": "ListEngage $72.8M (Oct-25) and Coastal Cloud (Dec-25, largest TCS deal); AMD (Jan); OpenAI and HyperVault (Feb); ServiceNow (Feb); Google Cloud (Apr); Mistral Forge (May); Anthropic Global Premier Partner (Jun); Best Buy GCC (Q2 FY27)",
        "strengths": "Broadest bench of model partners; AI revenue of $3.1B, more than 10% of the total; huge delivery scale; strong BFSI franchise",
        "gaps": "Headline growth is slow (~2.8% YoY in constant currency in Q2 FY27); India revenue dipped; so many partners risks diluting focus",
        "how_to_win": "Present breadth as complexity. Lead with one deep, certified platform partnership and a named team the client can meet",
    },
    "Infosys": {
        "positioning": "AI-first services firm targeting a $300B+ AI services opportunity",
        "ai_assets": "Infosys Topaz and Topaz Fabric; AI First Value Framework (6 value pools); Anthropic CoE (telecom); Columbia Enterprise AI Center",
        "key_moves": "Anthropic (Feb); Optimum Healthcare ($465M) and Stratus ($95M) (Mar); Google Cloud (Apr); Columbia centre, OpenAI Codex and Truist GCC (Oct)",
        "strengths": "Clear AI service taxonomy that buyers can follow; new depth in healthcare and P&C insurance; Finacle as a ready channel for banking AI",
        "gaps": "Disclosed AI revenue share (5.5%, Dec-25) is below the share TCS claims; two healthcare and insurance acquisitions still to integrate",
        "how_to_win": "In healthcare and insurance, expect Optimum and Stratus references. Counter with outcome-priced pilots and platform-neutral delivery",
    },
    "Wipro": {
        "positioning": "Consulting-led, AI-powered firm with a separate AI-native platforms business",
        "ai_assets": "Wipro Intelligence (WINGS, WEGA, NetOxygen, CROAMIS); LIFT framework; 1,500 forward-deployed engineers on Gemini",
        "key_moves": "HARMAN DTS ($375M, closed Dec-25); AI-Native Platforms Unit (Apr); Mindsprint with $1B+ Olam deal (Apr); Alpha Net contracts; ServiceNow (May); Google Cloud and LIFT (Aug)",
        "strengths": "Creative deal structures (captive plus contract); IP separated from services; engineering depth from DTS",
        "gaps": "No frontier-lab alliance tracked; shares down ~35% YTD by Aug-26; one low-confidence event (Aggne) still unverified",
        "how_to_win": "Probe for model-neutral depth beyond Google. Lead with multi-model options and production references in the client's industry",
    },
    "HCLTech": {
        "positioning": "Services plus software: AI Force across engineering, operations and applications",
        "ai_assets": "AI Force 2.0; AI Foundry; HCLSoftware (UnO Agentic, Actian, Jaspersoft); OpenAI Advanced Partner",
        "key_moves": "AI Force 2.0 (Apr); $1.14B AI deal, Sarvam $150M and Jaspersoft (Jul); ₹3,500 cr AI data centres (Jul); Guardian GCC (Jul); Robotiq.ai (Sep)",
        "strengths": "Owns software IP and is now building its own AI infrastructure; won a $1B+ AI-led deal; sovereign-AI stake",
        "gaps": "'Advanced AI' revenue ($620M) is defined narrowly and differently from peers; several software acquisitions to integrate",
        "how_to_win": "In infrastructure and run deals they bundle software. Position on openness and freedom from lock-in, and ask about exit costs",
    },
    "Cognizant": {
        "positioning": "'AI Builder': bridging AI investment and enterprise value",
        "ai_assets": "Neuro AI and Neuro AI Trust; Flowsource; OpenAI (25k) and Gemini (18k) Frontier Capability Groups; Astreya AI OpsHub",
        "key_moves": "3Cloud (Jan); Microsoft (Jan); Cognition (Jan); Astreya ~$600M (Apr); Frontier talent pledge (Sep); Activate unit, Google and OpenAI groups (Oct)",
        "strengths": "Most aggressive public talent commitments; a measured proof point (37% net saving with Cognition); stack running from AI infrastructure to software engineering",
        "gaps": "Announcements lean on headcount and badges, with few named client results; four big acquisitions in 18 months",
        "how_to_win": "Ask for production references, not certification numbers. Lead with measured case studies and accountable delivery leads",
    },
    "Capgemini": {
        "positioning": "Catalyst for enterprise-wide AI adoption, led by agentic 'Intelligent Operations'",
        "ai_assets": "WNS Intelligent Operations; Google Cloud AI Enterprise Hub; Outcome Deployed Engineer pods",
        "key_moves": "WNS $3.3B (Jul-25, closed Oct-25); Cloud4C (Nov-25); GenAI over 10% of Q4 bookings (Feb); Google Hub (Apr); sale of US federal unit (Sep); Q3 +11.7% (Oct)",
        "strengths": "Largest AI-motivated acquisition tracked; strong in operations and BPO; European sovereignty credentials",
        "gaps": "About 5 points of 2026 growth is acquired, not organic; ~€700M restructuring; leaving the US federal market",
        "how_to_win": "Capgemini plus WNS is strong in operations deals. Compete on transition risk, US-specific references and price",
    },
    "Tech Mahindra": {
        "positioning": "Telecom-first AI and India-built ('sovereign') AI platforms",
        "ai_assets": "Project Indus; TechM Orion; ontology-driven agentic platform with Microsoft; ServiceNow AI & Innovation CoE",
        "key_moves": "Microsoft agentic platform for telecom (Mar); Avant acquisition (May); ServiceNow Client Zero and CoE (Aug); AWS Agentic Process Transformation Center and CoRover BharatGPT (Sep); Google Cloud expansion, 12,500+ staff on Gemini (Oct)",
        "strengths": "Deep telecom domain; sovereign-AI story; credibility from using the ServiceNow platform itself first ('Client Zero')",
        "gaps": "Fewest AI events tracked (7); no frontier-lab alliance tracked; small-ticket M&A",
        "how_to_win": "Outside telecom their AI story is thinner. Compete in BFSI and manufacturing with stronger model partnerships",
    },
}
