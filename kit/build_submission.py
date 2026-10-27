#!/usr/bin/env python3
"""Builds dist/report.html and dist/slides.html from REAL measured data.
Reads: eval/results_baseline.json, eval/results_optimized.json, eval/walkthrough.json,
       eval/attack_demo.json, eval/budget_demo.json, eval/pytest_summary.txt, shots/*.png
Optional: pilot.json {"who","quote","manual_minutes","app_minutes"} (a real user test).
Refuses to build if data is missing, not live, or any placeholder is left.
Usage: python kit/build_submission.py [--allow-mock]"""
import json, os, re, subprocess, base64, mimetypes, sys, html
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KIT = Path(__file__).resolve().parent
ALLOW_MOCK = "--allow-mock" in sys.argv

def die(msg):
    print("BUILD FAILED:", msg); sys.exit(1)

def read_env():
    env = {}
    for p in (ROOT.parent / ".env", ROOT / ".env"):
        if p.exists():
            for line in p.read_text().splitlines():
                if "=" in line and not line.strip().startswith("#"):
                    k, v = line.split("=", 1); env[k.strip()] = v.strip().strip('"').strip("'")
    for k, v in os.environ.items():
        if k.startswith(("PRICE_", "STUDENT_", "MEMOS_", "MANUAL_", "REVIEW_")): env[k] = v
    return env
ENV = read_env()

def sh(cmd):
    try: return subprocess.check_output(cmd, shell=True, cwd=ROOT, stderr=subprocess.DEVNULL).decode().strip()
    except Exception: return ""

name = ENV.get("STUDENT_NAME") or sh("git config user.name")
if not name or name == "MY_NAME_HERE": die("No student name. Put STUDENT_NAME=Your Name in .env")
repo = sh("git remote get-url origin") or "(repo link: add a git remote named origin, then rebuild)"
repo = re.sub(r"^git@github.com:", "https://github.com/", repo).removesuffix(".git")

PRICE_IN = float(ENV.get("PRICE_INPUT_PER_M", 0.15)); PRICE_C = float(ENV.get("PRICE_CACHED_PER_M", 0.075)); PRICE_OUT = float(ENV.get("PRICE_OUTPUT_PER_M", 0.60))
PRICE_SRC = "course pricing from .env" if "PRICE_INPUT_PER_M" in ENV else "assumed reference prices for a small model (the real course price was not available to the build)"
R = int(ENV.get("MEMOS_PER_MONTH", 40))
MANUAL_MIN = float(ENV.get("MANUAL_SCREEN_MIN", 180)); REVIEW_MIN = float(ENV.get("REVIEW_MIN", 20))

def load(p, required=True):
    f = ROOT / p
    if not f.exists():
        if required: die(f"missing {p}. Run the pipeline first (python scripts/run_all.py).")
        return None
    return json.loads(f.read_text())

base, opt = load("eval/results_baseline.json"), load("eval/results_optimized.json")
walk, attack, budget = load("eval/walkthrough.json"), load("eval/attack_demo.json"), load("eval/budget_demo.json")
ptxt = ROOT / "eval/pytest_summary.txt"
if not ptxt.exists(): die("missing eval/pytest_summary.txt")
pl = [l for l in ptxt.read_text().splitlines() if re.search(r"\d+ passed|\d+ failed|error", l)]
pytest_line = pl[-1].strip("= ").strip() if pl else "see eval/pytest_summary.txt"
pilot = load("pilot.json", required=False)

live = base.get("live") and opt.get("live")
if not live and not ALLOW_MOCK: die("Eval results are not from live model calls. Fix the API key and re-run, or pass --allow-mock for a clearly-labelled mock build.")
mock_banner = "" if live else '<div class="note"><strong>Mock build:</strong> the numbers below came from a mocked model, not live calls.</div>'

def cost(s):
    unc = s["input_tokens"] - s["cached_tokens"]
    return (unc * PRICE_IN + s["cached_tokens"] * PRICE_C + s["output_tokens"] * PRICE_OUT) / 1e6

def ratio(a, b): return (a / b) if b else 0.0

def summ(d):
    s = d["scenarios"]; n = len(s)
    if n == 0: die("empty eval results")
    S = lambda k: sum(x[k] for x in s)
    inj = [x for x in s if x.get("injected")]
    num = [x for x in s if x.get("numeric_correct") is not None]
    return dict(n=n, recall=ratio(S("planted_found"), S("planted_total")), found=S("planted_found"), planted=S("planted_total"),
        cite=ratio(S("citations_valid"), S("citations_total")), cite_total=S("citations_total"), cite_valid=S("citations_valid"),
        decoy=S("decoys_flagged"), decoy_total=S("decoys_total"),
        numok=sum(1 for x in num if x["numeric_correct"]), numn=len(num),
        labok=sum(1 for x in s if x["label_correct"]),
        injok=sum(1 for x in inj if x["injection_resisted"]), injn=len(inj),
        tin=S("input_tokens") / n, tc=S("cached_tokens") / n, tout=S("output_tokens") / n,
        cost=sum(cost(x) for x in s) / n, sec=S("seconds") / n)
B, O = summ(base), summ(opt)

pct = lambda x: f"{x*100:.0f}%"
num_ = lambda x: f"{x:,.0f}"
usd = lambda x: f"${x:,.4f}" if x < 1 else f"${x:,.2f}"
tt = lambda m: m["tin"] + m["tout"]
tok_cut = 1 - ratio(tt(O), tt(B)); cost_cut = 1 - ratio(O["cost"], B["cost"])
same_or_better = O["recall"] >= B["recall"] - 0.05 and O["cite"] >= B["cite"] - 0.05
if same_or_better:
    verdict = (f"Cost cutting did not hurt quality in this test: optimized recall was {pct(O['recall'])} versus {pct(B['recall'])} for the baseline, "
               f"while using {pct(tok_cut)} fewer tokens and costing {pct(cost_cut)} less per memo.")
else:
    verdict = (f"Cost cutting had a trade-off: optimized recall was {pct(O['recall'])} versus {pct(B['recall'])} for the baseline, "
               f"in exchange for {pct(tok_cut)} fewer tokens ({pct(cost_cut)} lower cost per memo).")

run_min = O["sec"] / 60; app_min = REVIEW_MIN + run_min; saved = MANUAL_MIN - app_min
annual_hours = saved * R * 12 / 60
E = html.escape
walk_html = "<ol>" + "".join(f"<li><strong>{E(e['agent'])}:</strong> {E(e['detail'])}</li>" for e in walk["events"]) + "</ol>"
top_html = "<ul>" + "".join(f"<li><strong>{E(r['code'])} {E(r['title'])}</strong> (severity {E(str(r['severity']))}). Evidence: {E(r['citation'])}</li>" for r in walk["top_risks"]) + "</ul>"
if pilot:
    pilot_html = (f"<p><strong>Experienced-user check.</strong> {E(pilot['who'])} reviewed the tool. Manual first pass: {E(str(pilot['manual_minutes']))} min; "
                  f"with HardwareRisk: {E(str(pilot['app_minutes']))} min. Comment: &ldquo;{E(pilot['quote'])}&rdquo;</p>")
else:
    pilot_html = ("<p><strong>No external user pilot was run for this submission.</strong> The evidence comes from an automated evaluation on synthetic data rooms, "
                  "a measured end-to-end run, and a safety test suite. Putting real, anonymized past deals through the tool and comparing against an experienced investor's memo is the first next step and the largest gap in the evidence.</p>")
cost_rows = "".join(f"<tr><td>{l}</td><td>{num_(k)}</td><td>{usd(O['cost']*k)}</td></tr>" for l, k in
                    [("1 investor", R), ("100 investors", R*100), ("10,000 investors", R*10000)])
V = dict(name=E(name), repo=E(repo), mock_banner=mock_banner, model=E(str(opt.get("model", "gpt-6-luna"))), n=O["n"],
    price_in=f"${PRICE_IN}", price_c=f"${PRICE_C}", price_out=f"${PRICE_OUT}", price_src=PRICE_SRC, R=R,
    o_in=num_(O["tin"]), o_c=num_(O["tc"]), o_out=num_(O["tout"]), o_cost=usd(O["cost"]), o_cost2=usd(O["cost"]), o_user_month=usd(O["cost"] * R),
    o_10k=usd(O["cost"] * R * 10000), cost_rows=cost_rows,
    b_recall=f"{B['found']}/{B['planted']} ({pct(B['recall'])})", o_recall=f"{O['found']}/{O['planted']} ({pct(O['recall'])})",
    b_cite=f"{B['cite_valid']}/{B['cite_total']} ({pct(B['cite'])})", o_cite=f"{O['cite_valid']}/{O['cite_total']} ({pct(O['cite'])})",
    b_decoy=f"{B['decoy']}/{B['decoy_total']}", o_decoy=f"{O['decoy']}/{O['decoy_total']}",
    b_num=f"{B['numok']}/{B['numn']}", o_num=f"{O['numok']}/{O['numn']}", b_label=f"{B['labok']}/{B['n']}", o_label=f"{O['labok']}/{O['n']}",
    b_tok=num_(tt(B)), o_tok=num_(tt(O)), b_cost=usd(B["cost"]), verdict=verdict,
    o_inj=f"{O['injok']}/{O['injn']}", cite_total=O["cite_total"], cite_valid=O["cite_valid"], cite_dropped=O["cite_total"] - O["cite_valid"],
    pytest=E(pytest_line),
    w_name=E(walk["startup_name"]), w_cat=E(walk["category"]), w_docs=walk["docs_count"], w_chunks=walk["chunks"], w_html=walk_html, w_top=top_html,
    w_findings=walk["findings_count"], w_verified=walk["verified_findings"], w_dropped=walk["dropped_findings"], w_score=walk["overall_score"], w_rec=E(walk["recommendation"]),
    w_calls=walk["model_calls"], w_in=num_(walk["input_tokens"]), w_c=num_(walk["cached_tokens"]), w_out=num_(walk["output_tokens"]), w_sec=f"{walk['seconds']:.1f}",
    a_startup=E(attack["startup"]), a_text=E(attack["injected_text"]), a_detected="yes" if attack["guard_detected"] else "NO (defense failed)", a_by=E(str(attack["blocked_by"])),
    a_rec_inj=E(attack["recommendation_with_injection"]), a_rec_clean=E(attack["recommendation_clean"]), a_found=attack["planted_found_with_injection"], a_total=attack["planted_total"], a_reason=E(attack["log_reason"]),
    bud_cap=num_(budget["cap_tokens"]), bud_status=E(budget["status"]), bud_stop="stopped before finishing" if budget["stopped_before_completion"] else "did not stop (see logs)",
    manual_min=f"{MANUAL_MIN:.0f}", app_min=f"{app_min:.0f}", saved_min=f"{saved:.0f}", annual_hours=f"{annual_hours:.0f}", review_min=f"{REVIEW_MIN:.0f}",
    run_min=f"{run_min:.1f}", sec_per_memo=f"{O['sec']:.0f}", pilot_html=pilot_html)

def embed(h):
    pat = re.compile(r'<span class="shot" data-file="([^"]+)" data-alt="([^"]*)">.*?</span>', re.S)
    def sub(m):
        f = ROOT / m.group(1)
        if not f.exists(): die(f"missing screenshot {m.group(1)}")
        mime = mimetypes.guess_type(f.name)[0] or "image/png"
        return f'<img src="data:{mime};base64,{base64.b64encode(f.read_bytes()).decode()}" alt="{m.group(2)}">'
    return pat.sub(sub, h)

out = ROOT / "dist"; out.mkdir(exist_ok=True)
svg = (KIT / "templates/diagram.svg").read_text()
for t in ("report", "slides"):
    h = (KIT / f"templates/{t}_template.html").read_text().replace("<!--DIAGRAM-->", svg)
    h = re.sub(r"\{\{(\w+)\}\}", lambda m: str(V[m.group(1)]) if m.group(1) in V else die(f"{t}: unknown variable {m.group(1)}"), h)
    h = embed(h)
    left = re.findall(r"\{\{|\[FILL|class=\"shot\"", h)
    if left: die(f"{t}: leftover placeholders {left}")
    (out / f"{t}.html").write_text(h, encoding="utf-8")
    print(f"wrote dist/{t}.html ({len(h)//1024} KB)")
print("OK: no placeholders left. Open dist/report.html and dist/slides.html to check.")
