"""Tracker scope: who we track, what counts as an event, how we grade sources."""
from datetime import date

TRACKING_START = date(2025, 6, 1)

# Company -> names the LLM or a headline might use for it
COMPANIES = {
    "Accenture": ["Accenture", "ACN"],
    "TCS": ["TCS", "Tata Consultancy Services"],
    "Infosys": ["Infosys", "INFY"],
    "Wipro": ["Wipro"],
    "HCLTech": ["HCLTech", "HCL Technologies", "HCLSoftware", "HCL Software"],
    "Cognizant": ["Cognizant", "CTSH"],
    "Capgemini": ["Capgemini"],
    "Tech Mahindra": ["Tech Mahindra", "TechM"],
}

# News queries run for every company (Google News RSS search syntax)
QUERY_TEMPLATES = [
    '"{name}" acquisition AI',
    '"{name}" partnership AI',
    '"{name}" launches agentic AI',
]

EVENT_TYPES = [
    "Acquisition", "Partnership", "Launch", "Investment", "Deal / GCC",
    "Talent / CoE", "Financial disclosure", "Client proof point", "Divestiture",
]

COUNTERPARTY_TYPES = [
    "Frontier model lab", "Hyperscaler", "Enterprise platform", "Chip / compute",
    "AI-native firm", "Domain consultancy", "Data & analytics firm", "Software product",
    "Cloud services firm", "Managed services firm", "Engineering services firm",
    "BPM / operations firm", "Captive / GCC", "Contract / book of business",
    "Client", "Academic", "Infrastructure", "Buyer", "",
]

STRATEGIC_THEMES = [
    "Frontier-lab alliance", "Hyperscaler alliance", "Platform ecosystem",
    "Agentic AI offering", "Forward-deployed talent", "AI talent & IP acquisition",
    "Vertical / domain depth", "GCC / captive takeover", "Intelligent operations",
    "AI infrastructure", "Sovereign / India AI", "Data & analytics",
    "AI in software engineering", "Engineering & physical AI", "Large AI-led deal",
    "AI revenue & scale", "Platform / IP-led model", "Thought leadership / R&D",
    "New segment / GTM", "Portfolio reshaping",
]

# Domains treated as primary sources (company newsrooms, wire services, filings)
PRIMARY_DOMAINS = [
    "accenture.com", "tcs.com", "tata.com", "infosys.com", "wipro.com", "hcltech.com",
    "hcl-software.com", "cognizant.com", "capgemini.com", "techmahindra.com",
    "mahindra.com", "businesswire.com", "prnewswire.com", "globenewswire.com",
    "nseindia.com", "bseindia.com", "sec.gov", "googlecloudpresscorner.com",
]

# Domains we never accept as the only source
BLOCKED_DOMAINS = ["reddit.com", "quora.com", "medium.com", "x.com", "twitter.com"]
