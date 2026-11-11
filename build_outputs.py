"""Build analyst outputs from data/ci_events.csv:

  outputs/CI_Tracker.xlsx    competitor database + live summary formulas + battle cards
  outputs/battle_cards.md    battle cards (GitHub-readable)
  outputs/key_findings.md    findings and watch list
  docs/index.html            interactive dashboard (GitHub Pages ready)
"""
from __future__ import annotations

import csv
import json
import sys
from datetime import datetime
from pathlib import Path

from openpyxl import Workbook
from openpyxl.chart import BarChart, Reference
from openpyxl.comments import Comment
from openpyxl.formatting.rule import ColorScaleRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import Table, TableStyleInfo

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT / "src"))
from ci_tracker.config import COMPANIES, EVENT_TYPES  # noqa: E402
from ci_tracker.insights import AS_OF, BATTLE_CARDS, KEY_FINDINGS, WATCH_LIST  # noqa: E402

NAVY, TEAL, GREY = "1F3A5F", "2A9D8F", "F2F4F7"
F = "Arial"
H_FONT = Font(name=F, bold=True, color="FFFFFF", size=10)
H_FILL = PatternFill("solid", fgColor=NAVY)
BODY = Font(name=F, size=10)
BOLD = Font(name=F, size=10, bold=True)
TITLE = Font(name=F, size=16, bold=True, color=NAVY)
SUB = Font(name=F, size=10, italic=True, color="555555")
LINK = Font(name=F, size=10, color="0563C1", underline="single")
THIN = Border(bottom=Side(style="thin", color="D0D5DD"))
WRAP = Alignment(wrap_text=True, vertical="top")
PARTNERS = ["OpenAI", "Anthropic", "Mistral", "Google Cloud", "Microsoft", "ServiceNow", "AMD"]
MAXROW = 1000  # formulas cover rows 2..1000 so new pipeline rows are picked up


def load() -> list[dict]:
    with (ROOT / "data/ci_events.csv").open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def header(ws, row, values, widths=None):
    for i, v in enumerate(values, 1):
        c = ws.cell(row=row, column=i, value=v)
        c.font, c.fill = H_FONT, H_FILL
        c.alignment = Alignment(wrap_text=True, vertical="center", horizontal="center")
    if widths:
        for i, w in enumerate(widths, 1):
            ws.column_dimensions[get_column_letter(i)].width = w


def build_excel(rows: list[dict]) -> Path:
    wb = Workbook()
    cols = list(rows[0].keys())
    col = {c: get_column_letter(i + 1) for i, c in enumerate(cols)}
    rng = lambda c: f"Events!${col[c]}$2:${col[c]}${MAXROW}"  # noqa: E731

    # ---------------- Overview ----------------
    ov = wb.active
    ov.title = "Overview"
    ov.sheet_view.showGridLines = False
    ov["A1"] = "AI-Powered Competitive Intelligence Tracker"
    ov["A1"].font = TITLE
    ov["A2"] = (f"The GenAI race in IT services: 8 competitors, Jun 2025 – Nov 2026 | "
                f"Data as of {AS_OF} | Public sources only")
    ov["A2"].font = SUB
    ov["A4"], ov["A4"].font = "Headline metrics (live formulas on the Events sheet)", BOLD
    kpis = [
        ("Events tracked", f"=COUNTA({rng('event_id')})"),
        ("Verified events", f'=COUNTIF({rng("validation_status")},"Verified")'),
        ("Events awaiting human review", f'=COUNTIF({rng("validation_status")},"Needs review")'),
        ("Primary-source share", f'=IFERROR(COUNTIF({rng("source_tier")},"Primary")/B5,0)'),
        ("Acquisitions", f'=COUNTIF({rng("event_type")},"Acquisition")'),
        ("Partnerships", f'=COUNTIF({rng("event_type")},"Partnership")'),
        ("Disclosed acquisition value ($M)",
         f'=SUMIFS({rng("deal_value_usd_m")},{rng("event_type")},"Acquisition")'),
        ("Firms with an OpenAI tie-up", "=COUNTIF('Partner Map'!B3:B10,\">0\")"),
    ]
    for i, (k, f) in enumerate(kpis, start=5):
        ov.cell(row=i, column=1, value=k).font = BODY
        c = ov.cell(row=i, column=2, value=f)
        c.font = BOLD
        c.number_format = "0%" if "share" in k else "#,##0"
        ov.cell(row=i, column=1).border = ov.cell(row=i, column=2).border = THIN
    ov["B11"].comment = Comment("Only deals with a disclosed USD value. Many deals are undisclosed, "
                                "so this is a floor, not a total.", "Analyst")
    r = 15
    ov.cell(row=r, column=1, value="How this tracker works").font = BOLD
    steps = [
        "1. Collect: Google News RSS queries per competitor, or a pasted list of press-release URLs.",
        "2. Extract: an LLM (Gemini / Claude / GPT) turns each article into structured events against a fixed taxonomy.",
        "3. Validate: rule checks (tracked company, valid date, accepted source, evidence quote found in article, de-duplication).",
        "4. Review: anything that fails a soft check goes to a human review queue; nothing is auto-published unchecked.",
        "5. Analyse: the analyst writes findings and battle cards; this workbook and the dashboard update from the same CSV.",
    ]
    for i, s in enumerate(steps, start=r + 1):
        ov.cell(row=i, column=1, value=s).font = BODY
    r = r + len(steps) + 2
    ov.cell(row=r, column=1, value="Sheets").font = BOLD
    for i, (n, d) in enumerate([
        ("Events", "Full competitor event database with source links (filterable)."),
        ("Company x Type", "Event counts by competitor and event type, plus chart."),
        ("Partner Map", "Which competitors announced ties with which AI/platform partners."),
        ("Themes", "Strategic theme heat map by competitor."),
        ("Key Findings", "So-what analysis and 90-day watch list."),
        ("Battle Cards", "One card per competitor: positioning, strengths, gaps, how to win."),
        ("Data Dictionary", "Field definitions and validation rules."),
    ], start=r + 1):
        ov.cell(row=i, column=1, value=n).font = BOLD
        ov.cell(row=i, column=2, value=d).font = BODY
    r = i + 2
    ov.cell(row=r, column=1, value=("Disclaimer: independent portfolio project built on public "
                                    "information; not affiliated with any company named. Not investment advice.")).font = SUB
    ov.column_dimensions["A"].width = 38
    ov.column_dimensions["B"].width = 70

    # ---------------- Events ----------------
    ev = wb.create_sheet("Events")
    widths = {"event_id": 10, "company": 14, "event_date": 11, "date_precision": 14, "event_type": 15,
              "counterparty": 22, "counterparty_type": 18, "headline": 48, "summary": 60,
              "strategic_theme": 22, "industry_focus": 20, "deal_value_usd_m": 12, "value_note": 22,
              "source_name": 22, "source_url": 14, "source_tier": 10, "validation_status": 13,
              "confidence": 11}
    header(ev, 1, cols, [widths.get(c, 14) for c in cols])
    for ri, rec in enumerate(rows, start=2):
        for ci, c in enumerate(cols, start=1):
            v = rec[c]
            cell = ev.cell(row=ri, column=ci)
            if c == "event_date":
                cell.value = datetime.strptime(v, "%Y-%m-%d").date()
                cell.number_format = "dd-mmm-yyyy"
            elif c == "deal_value_usd_m":
                cell.value = float(v) if v else None
                cell.number_format = "#,##0.0"
            elif c == "source_url":
                cell.value = "Open source"
                cell.hyperlink = v
            else:
                cell.value = v
            cell.font = LINK if c == "source_url" else BODY
            cell.alignment = WRAP
    last = len(rows) + 1
    tab = Table(displayName="Events", ref=f"A1:{get_column_letter(len(cols))}{last}")
    tab.tableStyleInfo = TableStyleInfo(name="TableStyleLight9", showRowStripes=True)
    ev.add_table(tab)
    ev.freeze_panes = "C2"
    ev["L1"].comment = Comment("USD millions; blank = not disclosed in USD. See value_note.", "Analyst")

    # ---------------- Company x Type ----------------
    ct = wb.create_sheet("Company x Type")
    types = [t for t in EVENT_TYPES]
    header(ct, 2, ["Company"] + types + ["Total"], [16] + [12] * len(types) + [9])
    ct["A1"], ct["A1"].font = "Event count by competitor and type (formulas)", BOLD
    for i, co in enumerate(COMPANIES, start=3):
        ct.cell(row=i, column=1, value=co).font = BOLD
        for j, t in enumerate(types, start=2):
            ct.cell(row=i, column=j, value=(f'=COUNTIFS({rng("company")},$A{i},'
                                            f'{rng("event_type")},{get_column_letter(j)}$2)')).font = BODY
        tc = len(types) + 2
        ct.cell(row=i, column=tc,
                value=f"=SUM(B{i}:{get_column_letter(tc - 1)}{i})").font = BOLD
    tr = 3 + len(COMPANIES)
    ct.cell(row=tr, column=1, value="Total").font = BOLD
    for j in range(2, len(types) + 3):
        L = get_column_letter(j)
        ct.cell(row=tr, column=j, value=f"=SUM({L}3:{L}{tr - 1})").font = BOLD
    ct.conditional_formatting.add(f"B3:{get_column_letter(len(types) + 1)}{tr - 1}",
                                  ColorScaleRule(start_type="num", start_value=0, start_color="FFFFFF",
                                                 end_type="max", end_color="7FB3D5"))
    # disclosed M&A value
    vr = tr + 3
    ct.cell(row=vr - 1, column=1, value="Disclosed acquisition value, $M (floor - many deals undisclosed)").font = BOLD
    header(ct, vr, ["Company", "Acq. value $M", "Acq. count"])
    for i, co in enumerate(COMPANIES, start=vr + 1):
        ct.cell(row=i, column=1, value=co).font = BODY
        c = ct.cell(row=i, column=2, value=(f'=SUMIFS({rng("deal_value_usd_m")},{rng("company")},$A{i},'
                                            f'{rng("event_type")},"Acquisition")'))
        c.number_format, c.font = "#,##0", BODY
        ct.cell(row=i, column=3, value=(f'=COUNTIFS({rng("company")},$A{i},'
                                        f'{rng("event_type")},"Acquisition")')).font = BODY
    chart = BarChart()
    chart.type, chart.style = "bar", 10
    chart.title = "Total AI-related events tracked, by competitor"
    chart.y_axis.title = "Events"
    tc = len(types) + 2
    chart.add_data(Reference(ct, min_col=tc, min_row=2, max_row=tr - 1), titles_from_data=True)
    chart.set_categories(Reference(ct, min_col=1, min_row=3, max_row=tr - 1))
    chart.legend = None
    chart.height, chart.width = 8, 16
    ct.add_chart(chart, f"E{vr}")

    # ---------------- Partner Map ----------------
    pm = wb.create_sheet("Partner Map")
    pm["A1"], pm["A1"].font = ("Announced ties with major AI / platform partners in the window "
                               "(1 = at least one event; counts from Events)"), BOLD
    header(pm, 2, ["Company"] + PARTNERS + ["Distinct partners"], [16] + [13] * len(PARTNERS) + [16])
    for i, co in enumerate(COMPANIES, start=3):
        pm.cell(row=i, column=1, value=co).font = BOLD
        for j, p in enumerate(PARTNERS, start=2):
            pm.cell(row=i, column=j, value=(f'=COUNTIFS({rng("company")},$A{i},'
                                            f'{rng("counterparty")},"*"&{get_column_letter(j)}$2&"*")')).font = BODY
        last_p = get_column_letter(len(PARTNERS) + 1)
        pm.cell(row=i, column=len(PARTNERS) + 2,
                value=f'=COUNTIF(B{i}:{last_p}{i},">0")').font = BOLD
    pm.conditional_formatting.add(f"B3:{get_column_letter(len(PARTNERS) + 1)}10",
                                  ColorScaleRule(start_type="num", start_value=0, start_color="FFFFFF",
                                                 end_type="num", end_value=1, end_color="2A9D8F"))
    pm["A12"] = ("Note: reflects events captured in this tracker's window, not every relationship "
                 "a firm has ever announced. Microsoft count for Cognizant excludes the 3Cloud (Azure) acquisition.")
    pm["A12"].font = SUB

    # ---------------- Themes ----------------
    th = wb.create_sheet("Themes")
    themes = sorted({r["strategic_theme"] for r in rows})
    th["A1"], th["A1"].font = "Strategic theme heat map (event counts)", BOLD
    header(th, 2, ["Theme"] + list(COMPANIES) + ["Total"], [28] + [12] * len(COMPANIES) + [8])
    for i, t in enumerate(themes, start=3):
        th.cell(row=i, column=1, value=t).font = BOLD
        for j, co in enumerate(COMPANIES, start=2):
            th.cell(row=i, column=j, value=(f'=COUNTIFS({rng("strategic_theme")},$A{i},'
                                            f'{rng("company")},{get_column_letter(j)}$2)')).font = BODY
        tcol = len(COMPANIES) + 2
        th.cell(row=i, column=tcol, value=f"=SUM(B{i}:{get_column_letter(tcol - 1)}{i})").font = BOLD
    th.conditional_formatting.add(f"B3:{get_column_letter(len(COMPANIES) + 1)}{2 + len(themes)}",
                                  ColorScaleRule(start_type="num", start_value=0, start_color="FFFFFF",
                                                 end_type="max", end_color="E76F51"))

    # ---------------- Key Findings ----------------
    kf = wb.create_sheet("Key Findings")
    kf.sheet_view.showGridLines = False
    kf["A1"], kf["A1"].font = f"Key findings (analyst view, as of {AS_OF})", TITLE
    header(kf, 3, ["#", "Finding", "Evidence (event IDs)", "So what"], [5, 42, 60, 60])
    for i, k in enumerate(KEY_FINDINGS, start=4):
        for j, v in enumerate([i - 3, k["title"], k["evidence"], k["so_what"]], start=1):
            c = kf.cell(row=i, column=j, value=v)
            c.font, c.alignment = (BOLD if j == 2 else BODY), WRAP
        kf.row_dimensions[i].height = 75
    w0 = 4 + len(KEY_FINDINGS) + 1
    kf.cell(row=w0, column=2, value="90-day watch list").font = BOLD
    for i, w in enumerate(WATCH_LIST, start=w0 + 1):
        kf.cell(row=i, column=2, value=f"• {w}").font = BODY

    # ---------------- Battle Cards ----------------
    bc = wb.create_sheet("Battle Cards")
    bc.sheet_view.showGridLines = False
    bc["A1"], bc["A1"].font = "Competitor battle cards", TITLE
    bc["A2"] = ("'How to win' is written for a hypothetical mid-tier IT services challenger. "
                "Strengths and gaps are analyst judgements from the tracked public events.")
    bc["A2"].font = SUB
    fields = [("positioning", "Positioning (own words)"), ("ai_assets", "Flagship AI assets"),
              ("key_moves", "Key moves"), ("strengths", "Strengths"), ("gaps", "Gaps / watch-outs"),
              ("how_to_win", "How to compete")]
    header(bc, 4, ["Competitor"] + [f[1] for f in fields], [14, 30, 34, 40, 34, 34, 36])
    for i, (co, card) in enumerate(BATTLE_CARDS.items(), start=5):
        bc.cell(row=i, column=1, value=co).font = BOLD
        for j, (key, _) in enumerate(fields, start=2):
            c = bc.cell(row=i, column=j, value=card[key])
            c.font, c.alignment = BODY, WRAP
        bc.cell(row=i, column=1).alignment = WRAP
        bc.row_dimensions[i].height = 120
    bc.freeze_panes = "B5"

    # ---------------- Data Dictionary ----------------
    dd = wb.create_sheet("Data Dictionary")
    header(dd, 1, ["Field", "Meaning"], [20, 110])
    defs = {
        "event_id": "Unique ID: company prefix + sequence (e.g. TCS-006).",
        "company": "Tracked competitor (8): Accenture, TCS, Infosys, Wipro, HCLTech, Cognizant, Capgemini, Tech Mahindra.",
        "event_date": "Announcement date. See date_precision when only a publish/reporting date was available.",
        "date_precision": "Day = exact announcement date; Reported = article/publish date; Month/Approx = derived.",
        "event_type": "One of: " + ", ".join(EVENT_TYPES) + ".",
        "counterparty": "Partner, target, client or buyer named in the event.",
        "counterparty_type": "Category of counterparty (frontier model lab, hyperscaler, client, etc.).",
        "headline / summary": "Analyst-written in own words (no copied text).",
        "strategic_theme": "Fixed taxonomy used for the heat map (see Themes sheet).",
        "deal_value_usd_m": "USD millions only when disclosed in USD; other currencies in value_note.",
        "source_tier": "Primary = company newsroom, wire service or exchange filing; Secondary = business/trade media.",
        "validation_status": "Verified = passed all checks and source opened by analyst; Needs review = open question.",
        "confidence": "High / Medium / Low: clarity and specificity of the source.",
        "Validation rules": ("Reject: untracked company, invalid/future date, no or blocked source. Review: evidence quote "
                             "not found in article text, USD value without USD in text, low confidence, headline-only."),
    }
    for i, (k, v) in enumerate(defs.items(), start=2):
        dd.cell(row=i, column=1, value=k).font = BOLD
        c = dd.cell(row=i, column=2, value=v)
        c.font, c.alignment = BODY, WRAP

    out = ROOT / "outputs/CI_Tracker.xlsx"
    out.parent.mkdir(exist_ok=True)
    wb.save(out)
    return out


def build_markdown() -> None:
    md = [f"# Competitor battle cards: GenAI in IT services\n",
          f"_As of {AS_OF}. 'How to compete' is written for a hypothetical mid-tier challenger. "
          f"Strengths and gaps are analyst judgements based on the tracked public events "
          f"([data](../data/ci_events.csv))._\n"]
    labels = [("positioning", "Positioning"), ("ai_assets", "Flagship AI assets"),
              ("key_moves", "Key moves"), ("strengths", "Strengths"),
              ("gaps", "Gaps / watch-outs"), ("how_to_win", "How to compete")]
    for co, card in BATTLE_CARDS.items():
        md.append(f"\n## {co}\n")
        md.append("| | |\n|---|---|")
        for k, lab in labels:
            md.append(f"| **{lab}** | {card[k]} |")
    (ROOT / "outputs/battle_cards.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    kf = [f"# Key findings: the GenAI race in IT services\n", f"_As of {AS_OF}._\n"]
    for i, k in enumerate(KEY_FINDINGS, 1):
        kf.append(f"\n### {i}. {k['title']}\n")
        kf.append(f"- **Evidence:** {k['evidence']}")
        kf.append(f"- **So what:** {k['so_what']}")
    kf.append("\n## 90-day watch list\n")
    kf += [f"- {w}" for w in WATCH_LIST]
    (ROOT / "outputs/key_findings.md").write_text("\n".join(kf) + "\n", encoding="utf-8")


def build_dashboard_data(rows: list[dict]) -> None:
    payload = {"as_of": AS_OF, "companies": list(COMPANIES), "partners": PARTNERS,
               "events": rows, "findings": KEY_FINDINGS, "watch": WATCH_LIST,
               "cards": BATTLE_CARDS}
    (ROOT / "docs").mkdir(exist_ok=True)
    data_js = "window.CI_DATA = " + json.dumps(payload, ensure_ascii=False).replace("</", "<\\/") + ";"
    template = (ROOT / "src/dashboard_template.html").read_text(encoding="utf-8")
    (ROOT / "docs/index.html").write_text(template.replace("/*__DATA__*/", data_js), encoding="utf-8")


if __name__ == "__main__":
    data = load()
    print("Excel:", build_excel(data))
    build_markdown()
    build_dashboard_data(data)
    print("Markdown + dashboard data written.")
