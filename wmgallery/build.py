"""Build the static gallery site: docs/index.html, docs/svg/{stack,mini}/*.svg, docs/data.json.

    python3 -m wmgallery.build                       # site into docs/
    python3 -m wmgallery.build --artifact page.html  # also a skeleton-free copy for publishing as an artifact

Page design: compact two-column cards (thumbnail diagram, name, one-line tagline); details collapsed behind
clicks, one fact at a time; the detailed diagram opens in a full-page viewer (zoom, previous/next, compare).
"""
import os
import re
import sys
import json
import html
import argparse
import datetime

from . import diagram as D
from . import registry as R
from . import stack as S
from . import audit as A

ROOT = R.ROOT
SITE_TITLE = "World Model Architecture Gallery"
DEFAULT_OUT = os.path.join(ROOT, "docs")

FAMILY_SHORT = {"rl": "RL world model", "token": "Token video", "dit": "Causal DiT", "driving": "Driving & robots",
                "jepa": "Embedding predictor", "wam": "World-action", "llm": "LLM & code", "object": "Object-centric",
                "ssm": "State-space"}
FAMILY_COLOUR = {"rl": "#1D3E72", "token": "#5E6B80", "dit": "#C46A12", "driving": "#007F7C", "jepa": "#9A7300",
                 "wam": "#8A8418", "llm": "#6B4FA0", "object": "#B4436C", "ssm": "#2F7D32"}
EVIDENCE_TEXT = {"read": "Architecture compared with the primary publication and available code; see Source check for limits",
                 "claim": "Facts from a developer page only"}


def h(s):
    return html.escape(str(s), quote=True)


def web_svg(svg, prefix):
    """Inline-ready SVG: no font import, page fonts with fallbacks, unique marker ids, scalable size."""
    svg = svg.replace(D.FONT_IMPORT, "")
    svg = svg.replace('font-family="Saira SemiCondensed"',
                      "font-family=\"'Saira Semi Condensed','Saira SemiCondensed',Arial Narrow,sans-serif\"")
    svg = svg.replace('font-family="IBM Plex Sans"', "font-family=\"'IBM Plex Sans',Helvetica,Arial,sans-serif\"")
    svg = svg.replace('font-family="IBM Plex Mono"', "font-family=\"'IBM Plex Mono',Menlo,Consolas,monospace\"")
    svg = svg.replace('id="ah_', 'id="%s_ah_' % prefix).replace("url(#ah_", "url(#%s_ah_" % prefix)
    svg = re.sub(r'<svg ([^>]*?)width="(\d+)" height="(\d+)"', r'<svg \1data-w="\2" data-h="\3"', svg, count=1)
    svg = svg.replace("<svg ", '<svg role="img" preserveAspectRatio="xMidYMid meet" ', 1)
    return svg


def read_changelog():
    p = os.path.join(ROOT, "CHANGELOG.md")
    if not os.path.exists(p):
        return ""
    out, in_list = [], False
    for line in open(p, encoding="utf-8"):
        line = line.rstrip()
        if line.startswith("## "):
            if in_list:
                out.append("</ul>"); in_list = False
            out.append("<h4>%s</h4>" % h(line[3:]))
        elif line.startswith("- "):
            if not in_list:
                out.append("<ul>"); in_list = True
            out.append("<li>%s</li>" % h(line[2:]))
    if in_list:
        out.append("</ul>")
    return "\n".join(out)


def audit_html(m):
    review = m["source_review"]
    limits = " ".join(review["limitations"])
    link = "architecture_audit.md#" + m["slug"].replace("_", "-")
    return ('<details class="fact source-review"><summary>Source check</summary>'
            '<p>Reviewed %s · %s. Figure: %s.</p><p>%s</p>'
            '<p><a href="%s" target="_blank" rel="noopener">Findings and pinned primary sources</a></p></details>'
            % (h(review["date"]), h(review["coverage"]), h(review["variant"]), h(limits), h(link)))


def card_html(m, mini_svg, artifact=False):
    slug = m["slug"]
    links = [('<a href="%s" target="_blank" rel="noopener">%s</a>' % (h(u), h(k))) for k, u in m.get("links", {}).items()]
    links.append('<a href="svg/stack/%s.svg" target="_blank" rel="noopener"%s>SVG</a>' % (h(slug), "" if artifact else " download"))
    facts = "".join('<details class="fact"><summary>%s</summary><p>%s</p></details>' % (h(k), h(v)) for k, v in m["facts"])
    ev = m["evidence"]
    fam = m["family"]
    org = str(m.get("org", "")).split(" (")[0]
    size = re.sub(r"\s*\[D[^\]]*\]", "", str(m.get("params", ""))).split(" (")[0].split(",")[0]
    return f'''<article class="card" id="{h(slug)}" data-slug="{h(slug)}" data-family="{h(fam)}" data-role="{h(m["role"])}"
 data-evidence="{h(ev)}" data-open="{h(m.get("open", ""))}" data-year="{m.get("year", 0)}" data-month="{m.get("month", 0)}"
 data-params="{m.get("params_num") or 0}" data-name="{h(m["name"])}">
  <button class="thumb" type="button" data-view="{h(slug)}" aria-label="Open the detailed diagram of {h(m["name"])}">{mini_svg}<span class="expand" aria-hidden="true">Expand</span></button>
  <div class="info">
    <div class="kicker"><span class="org">{h(org)} · {m.get("year", "")}</span><span class="size">{h(size)}</span></div>
    <h3><button class="name" type="button" data-view="{h(slug)}">{h(m["name"])}</button></h3>
    <p class="tag">{h(m.get("tagline", ""))}</p>
    <p class="tags"><span class="fam" style="--fc:{FAMILY_COLOUR[fam]}">{h(FAMILY_SHORT[fam])}</span><span class="ev ev-{h(ev)}" title="{h(EVIDENCE_TEXT[ev])}">{h(ev)}</span></p>
    <details class="more"><summary>Details</summary>
      <div class="facts">
        <details class="fact"><summary>Overview</summary><p>{h(m["summary"])}</p></details>
        {facts}
        <details class="fact"><summary>Status and sources</summary><p>{h(m["status"])}. Availability: {h(m.get("open", "n/a"))}. Sources: {h("; ".join(m.get("sources", [])))}.</p></details>
        {audit_html(m)}
      </div>
      <p class="links">{" · ".join(links)}</p>
    </details>
  </div>
</article>'''


CSS = r"""
/* Layout: centered title block with crop marks on a plain page; two-column catalogue of cards;
   diagrams on white tiles; labels and figures in mono. */
:root{
  --paper:#F5F7FA;--panel:#FFFFFF;--ink:#0F1B2D;--muted:#5B6779;--faint:#8792A5;
  --line:#E1E6EE;--line-strong:#C3CCDA;
  --navy:#1D3E72;--accent:#F58F2D;--accent-ink:#B4560A;
  --tile:#FFFFFF;--shade:rgba(8,15,28,.56);--shadow:rgba(15,27,45,.08);
  --ev-v:#0B6E6B;--ev-r:#1D3E72;--ev-c:#A4520E;--focus:#F58F2D;
  --display:"Saira Semi Condensed","Saira SemiCondensed","Arial Narrow",sans-serif;
  --body:"IBM Plex Sans",system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;
  --mono:"IBM Plex Mono",ui-monospace,Menlo,Consolas,monospace;
}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){
  --paper:#09111E;--panel:#0E1829;--ink:#E5ECF6;--muted:#9AA7BA;--faint:#6E7C91;
  --line:#1C2A40;--line-strong:#2C3D5B;
  --navy:#AFC8F4;--accent:#F58F2D;--accent-ink:#FFAD6A;
  --tile:#FFFFFF;--shade:rgba(2,6,14,.74);--shadow:rgba(0,0,0,.35);
  --ev-v:#6FD9D4;--ev-r:#AFC8F4;--ev-c:#FFB57A;color-scheme:dark}}
:root[data-theme="dark"]{
  --paper:#09111E;--panel:#0E1829;--ink:#E5ECF6;--muted:#9AA7BA;--faint:#6E7C91;
  --line:#1C2A40;--line-strong:#2C3D5B;
  --navy:#AFC8F4;--accent:#F58F2D;--accent-ink:#FFAD6A;
  --tile:#FFFFFF;--shade:rgba(2,6,14,.74);--shadow:rgba(0,0,0,.35);
  --ev-v:#6FD9D4;--ev-r:#AFC8F4;--ev-c:#FFB57A;color-scheme:dark}
*{box-sizing:border-box}
html,body{margin:0}
body{background:var(--paper);color:var(--ink);font-family:var(--body);font-size:15px;line-height:1.5}
body.noscroll{overflow:hidden}
a{color:var(--navy);text-underline-offset:2px}
button{font:inherit;color:inherit}
:focus-visible{outline:2px solid var(--focus);outline-offset:2px;border-radius:4px}
.page{max-width:1240px;margin:0 auto;padding-inline:20px;padding-block:0 56px}
/* top utility bar */
.util{display:flex;justify-content:flex-end;gap:6px;padding-top:14px}
.ubtn{font-family:var(--mono);font-size:11.5px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);
  background:transparent;border:1px solid var(--line);border-radius:6px;height:30px;padding:0 10px;cursor:pointer}
.ubtn:hover{color:var(--ink);border-color:var(--line-strong)}
/* title block */
.hero{position:relative;max-width:820px;margin:18px auto 30px;padding:40px 28px 32px;text-align:center}
.hero::before{content:"";position:absolute;inset:0;pointer-events:none;--c:var(--line-strong);
  background:linear-gradient(var(--c),var(--c)) 0 0/20px 1px no-repeat,linear-gradient(var(--c),var(--c)) 0 0/1px 20px no-repeat,
  linear-gradient(var(--c),var(--c)) 100% 0/20px 1px no-repeat,linear-gradient(var(--c),var(--c)) 100% 0/1px 20px no-repeat,
  linear-gradient(var(--c),var(--c)) 0 100%/20px 1px no-repeat,linear-gradient(var(--c),var(--c)) 0 100%/1px 20px no-repeat,
  linear-gradient(var(--c),var(--c)) 100% 100%/20px 1px no-repeat,linear-gradient(var(--c),var(--c)) 100% 100%/1px 20px no-repeat}
.eyebrow{margin:0 0 14px;font-family:var(--mono);font-size:12px;letter-spacing:.22em;text-transform:uppercase;color:var(--accent-ink)}
.hero h1{margin:0;font-family:var(--display);font-weight:600;font-size:clamp(34px,5.4vw,60px);line-height:1.02;letter-spacing:.005em;color:var(--ink);text-wrap:balance}
.hero h1 .thin{font-weight:500;color:var(--navy)}
.lede{margin:16px auto 0;max-width:560px;color:var(--muted);font-size:16px;text-wrap:balance}
.stats{margin:22px 0 0;display:flex;justify-content:center;flex-wrap:wrap;gap:0;font-family:var(--mono);font-size:12px;letter-spacing:.06em;color:var(--muted)}
.stats span{padding:0 14px;border-left:1px solid var(--line-strong)}
.stats span:first-child{border-left:none}
.stats b{color:var(--ink);font-weight:500}
/* sticky toolbar */
.toolbar{position:sticky;top:env(safe-area-inset-top,0px);z-index:5;margin:0 -20px 22px;padding:10px 20px 12px;
  display:flex;flex-direction:column;align-items:center;gap:10px;border-bottom:1px solid transparent;transition:background .2s,border-color .2s}
.toolbar.stuck{background:color-mix(in srgb,var(--paper) 88%,transparent);-webkit-backdrop-filter:blur(10px);backdrop-filter:blur(10px);border-bottom-color:var(--line)}
.controls{display:flex;flex-wrap:wrap;justify-content:center;gap:8px;width:100%;max-width:760px}
.search{flex:1 1 280px;min-width:0;display:flex;align-items:center;gap:8px;background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:0 12px;height:40px}
.search:focus-within{border-color:var(--navy)}
.search svg{flex:none;color:var(--faint)}
.search input{flex:1;min-width:0;border:none;outline:none;background:transparent;color:var(--ink);font:inherit;font-size:14.5px}
.ctl,.filters>summary{font-family:var(--mono);font-size:12px;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);
  background:var(--panel);border:1px solid var(--line);border-radius:8px;height:40px;padding:0 12px;cursor:pointer}
.ctl:hover,.filters>summary:hover{border-color:var(--line-strong);color:var(--ink)}
select.ctl{appearance:none;-webkit-appearance:none;padding-right:28px;background-image:linear-gradient(45deg,transparent 50%,var(--muted) 50%),linear-gradient(135deg,var(--muted) 50%,transparent 50%);
  background-position:calc(100% - 15px) 17px,calc(100% - 10px) 17px;background-size:5px 5px;background-repeat:no-repeat}
.filters{position:relative}
.filters>summary{list-style:none;display:flex;align-items:center}
.filters>summary::-webkit-details-marker{display:none}
.filters[open]>summary{border-color:var(--navy);color:var(--ink)}
.filters .menu{position:absolute;top:calc(100% + 6px);right:0;z-index:6;background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:12px;display:grid;gap:8px;min-width:240px;box-shadow:0 12px 32px var(--shadow)}
.menu select,.menu button{font:inherit;font-size:13.5px;color:var(--ink);background:var(--panel);border:1px solid var(--line);border-radius:6px;padding:7px 8px}
.menu button{cursor:pointer;font-family:var(--mono);font-size:11.5px;letter-spacing:.06em;text-transform:uppercase;color:var(--muted)}
.count{display:flex;align-items:center;font-family:var(--mono);font-size:12px;letter-spacing:.04em;color:var(--faint);padding:0 4px;font-variant-numeric:tabular-nums}
.chips{display:flex;flex-wrap:wrap;justify-content:center;gap:6px;max-width:100%}
.chip{display:inline-flex;align-items:center;gap:7px;font-size:12.5px;color:var(--muted);background:var(--panel);border:1px solid var(--line);border-radius:999px;padding:5px 11px;cursor:pointer;transition:border-color .15s,color .15s}
.chip i{width:7px;height:7px;border-radius:2px;background:var(--fc);display:block}
.chip:hover{color:var(--ink);border-color:var(--line-strong)}
.chip[aria-pressed="true"]{color:var(--ink);border-color:var(--fc);box-shadow:inset 0 0 0 1px var(--fc)}
@media (max-width:640px){.chips{flex-wrap:nowrap;overflow-x:auto;justify-content:flex-start;width:100%;scrollbar-width:none;padding-bottom:2px}.chips::-webkit-scrollbar{display:none}.chip{flex:none}}
/* catalogue */
.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px;align-items:start}
@media (max-width:900px){.grid{grid-template-columns:minmax(0,1fr)}}
.card{position:relative;display:grid;grid-template-columns:220px minmax(0,1fr);gap:18px;padding:14px;background:var(--panel);
  border:1px solid var(--line);border-radius:10px;scroll-margin-top:150px;transition:border-color .2s,box-shadow .2s,transform .2s}
.card:hover{border-color:var(--line-strong);box-shadow:0 10px 30px var(--shadow);transform:translateY(-1px)}
.card.hidden{display:none}
.thumb{position:relative;display:block;width:220px;height:228px;padding:8px;cursor:zoom-in;border:1px solid var(--line);border-radius:8px;background:var(--tile)}
.thumb svg{display:block;width:100%;height:100%}
.expand{position:absolute;top:8px;right:8px;font-family:var(--mono);font-size:10px;letter-spacing:.12em;text-transform:uppercase;color:#1D3E72;
  background:#fff;border:1px solid #C3CCDA;border-radius:4px;padding:2px 6px;opacity:0;transform:translateY(-2px);transition:opacity .15s,transform .15s}
.card:hover .expand,.thumb:focus-visible .expand{opacity:1;transform:none}
.info{min-width:0;display:flex;flex-direction:column;padding-top:4px}
.kicker{display:flex;justify-content:space-between;gap:10px;font-family:var(--mono);font-size:11px;letter-spacing:.09em;text-transform:uppercase;color:var(--faint)}
.kicker .size{color:var(--muted);white-space:nowrap}
.info h3{margin:6px 0 0;font-family:var(--display);font-weight:600;font-size:23px;line-height:1.1;letter-spacing:.005em}
.name{background:none;border:none;padding:0;cursor:pointer;text-align:left;color:var(--ink);font:inherit}
.name:hover{color:var(--navy)}
.tag{margin:8px 0 0;color:var(--muted);font-size:14.5px;line-height:1.45}
.tags{margin:12px 0 0;display:flex;flex-wrap:wrap;align-items:center;gap:8px}
.fam{display:inline-flex;align-items:center;gap:7px;font-size:12.5px;color:var(--ink)}
.fam::before{content:"";width:7px;height:7px;border-radius:2px;background:var(--fc)}
.ev{font-family:var(--mono);font-size:10px;letter-spacing:.12em;text-transform:uppercase;padding:2px 7px;border:1px solid currentColor;border-radius:4px;opacity:.9}
.ev-verified{color:var(--ev-v)}.ev-read{color:var(--ev-r)}.ev-claim{color:var(--ev-c)}
.more{margin-top:auto;padding-top:14px}
.more>summary,.fact>summary{list-style:none;cursor:pointer;user-select:none}
.more>summary::-webkit-details-marker,.fact>summary::-webkit-details-marker{display:none}
.more>summary{display:inline-flex;align-items:center;gap:8px;font-family:var(--mono);font-size:11.5px;letter-spacing:.12em;text-transform:uppercase;color:var(--navy)}
.more>summary::before{content:"+";display:inline-grid;place-items:center;width:16px;height:16px;border:1px solid currentColor;border-radius:4px;font-size:12px;line-height:1}
.more[open]>summary::before{content:"−"}
.facts{margin-top:10px;border-top:1px solid var(--line)}
.fact{border-bottom:1px solid var(--line)}
.fact>summary{display:flex;align-items:center;justify-content:space-between;padding:8px 2px;font-family:var(--mono);font-size:11px;letter-spacing:.1em;text-transform:uppercase;color:var(--muted)}
.fact>summary::after{content:"";width:6px;height:6px;border-right:1.5px solid currentColor;border-bottom:1.5px solid currentColor;transform:rotate(45deg);transition:transform .15s;margin-right:4px}
.fact[open]>summary{color:var(--ink)}
.fact[open]>summary::after{transform:rotate(-135deg)}
.fact p{margin:0 2px 10px;font-size:13.5px;line-height:1.55}
.links{margin:10px 0 0;font-family:var(--mono);font-size:11.5px;letter-spacing:.04em}
@media (max-width:560px){.card{grid-template-columns:minmax(0,1fr)}.thumb{width:100%;height:240px}.hero{padding:30px 16px 24px}}
/* footer */
footer{margin-top:44px;padding-top:18px;border-top:1px solid var(--line);text-align:center;color:var(--faint);font-size:13px}
footer .fl{display:flex;justify-content:center;gap:18px;font-family:var(--mono);font-size:11.5px;letter-spacing:.08em;text-transform:uppercase}
footer details{display:inline-block}
footer summary{cursor:pointer;list-style:none;color:var(--muted)}
footer summary::-webkit-details-marker{display:none}
footer summary:hover{color:var(--ink)}
footer .fold{max-width:720px;margin:12px auto 0;text-align:left;font-family:var(--body);font-size:13.5px;letter-spacing:0;text-transform:none;color:var(--muted)}
footer h4{margin:12px 0 2px;font-size:13px;color:var(--ink)}
footer ul{margin:0 0 6px 18px;padding:0}
footer .copy{margin:14px 0 0;font-family:var(--mono);font-size:11px;letter-spacing:.06em}
/* viewer */
.viewer{position:fixed;inset:0;z-index:20;display:flex;padding:max(14px,env(safe-area-inset-top,0px)) 14px max(14px,env(safe-area-inset-bottom,0px));
  background:var(--shade);-webkit-backdrop-filter:blur(6px);backdrop-filter:blur(6px)}
.viewer[hidden]{display:none!important}
.vpanel{flex:1;display:flex;flex-direction:column;min-width:0;min-height:0;overflow:hidden;background:var(--panel);border:1px solid var(--line);border-radius:12px;box-shadow:0 30px 80px rgba(0,0,0,.35)}
.vbar{display:flex;align-items:center;gap:12px;flex-wrap:wrap;padding:12px 16px;border-bottom:1px solid var(--line)}
.vtitle{min-width:0;flex:1 1 240px}
.vtitle h2{margin:0;font-family:var(--display);font-weight:600;font-size:24px;line-height:1.1;color:var(--ink)}
.vtitle span{display:block;margin-top:2px;font-family:var(--mono);font-size:11px;letter-spacing:.09em;text-transform:uppercase;color:var(--faint)}
.vtools{display:flex;align-items:center;gap:6px;flex-wrap:wrap}
.vtools .vl{display:flex;gap:10px;margin-right:6px;font-family:var(--mono);font-size:11.5px;letter-spacing:.06em;text-transform:uppercase}
.vtools select{font-family:var(--mono);font-size:11.5px;letter-spacing:.04em;color:var(--ink);background:var(--panel);border:1px solid var(--line);border-radius:6px;height:32px;padding:0 8px;max-width:210px}
.vb{font-family:var(--mono);font-size:11.5px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);background:var(--panel);border:1px solid var(--line);border-radius:6px;height:32px;min-width:32px;padding:0 10px;cursor:pointer}
.vb:hover{color:var(--ink);border-color:var(--line-strong)}
.vbody{flex:1;min-height:0;overflow:auto;display:flex;background:#fff}
.vbody .pane{flex:1;min-width:0;display:flex;flex-direction:column;align-items:center;padding:14px}
.vbody .pane+.pane{border-left:1px solid #DCE2EB}
.vbody .fig{flex:1;width:100%;min-height:0;display:flex;justify-content:center}
.vbody .source-review{flex:none;width:100%;max-width:760px;margin-top:12px;color:#0F1B2D}
.vbody .source-review>summary{color:#5B6779}
.vbody .source-review a{color:#1D3E72}
.vbody.fit .fig svg{width:100%;height:100%;max-height:100%}
.vbody.zoom{display:block}
.vbody.zoom .pane{display:inline-flex;vertical-align:top;min-width:max-content}
.vbody.zoom .fig svg{height:auto}
.vkeys{font-family:var(--mono);font-size:10.5px;letter-spacing:.08em;text-transform:uppercase;color:var(--faint);padding:8px 16px;border-top:1px solid var(--line);text-align:center}
.help{max-width:760px;margin:auto;width:100%;flex:0 1 auto}
.help .vbody{display:block;padding:20px 22px;background:var(--panel);color:var(--ink)}
.help h2{margin:0 0 6px;font-family:var(--display);font-weight:600;font-size:24px}
.help p{margin:0 0 12px;color:var(--muted)}
.legend-list{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:10px 18px;font-size:14px;margin:8px 0 14px;padding:0;list-style:none}
.legend-list li{display:flex;align-items:center;gap:10px}
.sw{display:inline-block;width:36px;height:18px;border-radius:5px;border:1px solid #1E2A3B;background:#fff;flex:none}
.sw.dark{background:#1D3E72;border-color:#1D3E72}.sw.teal{background:#DCF2F1;border-color:#00A8A4}.sw.orange{background:#FDE8D4;border-color:#F58F2D}
.sw.group{background:#E4EAF4;border-color:#1D3E72;border-radius:8px}.sw.inset{background:#EEF1F5;border-style:dashed;border-color:#5E6B80}
.sw.plus{border-radius:50%;width:18px;text-align:center;line-height:16px;font-weight:700;color:#1E2A3B}
.sw.acc{border:none;background:none;color:var(--accent-ink);font-weight:700;width:auto;font-family:var(--mono)}
.sw.loop{border:none;border-top:2px dashed #B95A08;height:0;border-radius:0}
.sw.soft{background:#EEF1F5;border-color:#5E6B80}
@media (prefers-reduced-motion: reduce){*{transition:none!important}.card:hover{transform:none}}
"""

JS = r"""
(function(){
  const cards=[...document.querySelectorAll('.card')];
  const grid=document.getElementById('grid');
  const state={fam:new Set(),role:'',ev:'',open:'',q:'',sort:'date'};
  const famBtns=[...document.querySelectorAll('.chip[data-fam]')];
  famBtns.forEach(b=>b.addEventListener('click',()=>{const f=b.dataset.fam;if(state.fam.has(f)){state.fam.delete(f)}else{state.fam.add(f)}b.setAttribute('aria-pressed',state.fam.has(f));apply()}));
  [['role','role'],['ev','ev'],['open','open'],['sort','sort']].forEach(([id,k])=>{const e=document.getElementById(id);e.addEventListener('change',()=>{state[k]=e.value;apply()})});
  const q=document.getElementById('q');q.addEventListener('input',()=>{state.q=q.value.trim().toLowerCase();apply()});
  document.getElementById('clear').addEventListener('click',()=>{state.fam.clear();famBtns.forEach(b=>b.setAttribute('aria-pressed','false'));['role','ev','open'].forEach(k=>{state[k]='';document.getElementById(k).value=''});state.q='';q.value='';apply()});
  function visible(){return cards.filter(c=>!c.classList.contains('hidden'))}
  function apply(){
    cards.forEach(c=>{
      let ok=true;
      if(state.fam.size&&!state.fam.has(c.dataset.family))ok=false;
      if(state.role&&c.dataset.role!==state.role)ok=false;
      if(state.ev&&c.dataset.evidence!==state.ev)ok=false;
      if(state.open&&!c.dataset.open.includes(state.open))ok=false;
      if(state.q&&!c.textContent.toLowerCase().includes(state.q))ok=false;
      c.classList.toggle('hidden',!ok);
    });
    const key=c=>(+c.dataset.year)*12+(+c.dataset.month);
    const sorted=[...cards].sort((a,b)=>{
      if(state.sort==='name')return a.dataset.name.localeCompare(b.dataset.name);
      if(state.sort==='size')return (+b.dataset.params)-(+a.dataset.params);
      if(state.sort==='old')return key(a)-key(b);
      return key(b)-key(a);
    });
    sorted.forEach(c=>grid.appendChild(c));
    const n=visible().length;
    document.getElementById('count').textContent=n===cards.length?n+' models':n+' / '+cards.length;
  }
  // sticky toolbar gets a backdrop once the title block scrolls away
  const tb=document.querySelector('.toolbar'),sentinel=document.getElementById('sentinel');
  if('IntersectionObserver' in window){new IntersectionObserver(es=>{es.forEach(e=>tb.classList.toggle('stuck',!e.isIntersecting))}).observe(sentinel)}
  // ---------------- viewer
  const viewer=document.getElementById('viewer'),vbody=document.getElementById('vbody');
  const vtitle=document.getElementById('vtitle'),vmeta=document.getElementById('vmeta'),vlinks=document.getElementById('vlinks');
  const vcmp=document.getElementById('vcmp'),vzoom=document.getElementById('vzoom');
  let cur=null,cmp='',zoom=false,lastFocus=null;
  cards.forEach(c=>{const o=document.createElement('option');o.value=c.dataset.slug;o.textContent=c.dataset.name;vcmp.appendChild(o)});
  function figure(slug){
    const t=document.getElementById('full-'+slug);
    const wrap=document.createElement('div');wrap.className='fig';
    wrap.appendChild(t.content.cloneNode(true));
    const svg=wrap.querySelector('svg');
    if(svg&&zoom){const w=+svg.dataset.w;svg.style.width=Math.round(w*1.6)+'px'}
    return wrap;
  }
  function pane(slug){
    const p=document.createElement('div');p.className='pane';p.appendChild(figure(slug));
    const review=document.getElementById(slug).querySelector('.source-review').cloneNode(true);
    review.open=true;p.appendChild(review);return p;
  }
  function render(){
    const c=document.getElementById(cur);
    vtitle.textContent=c.dataset.name+(cmp?'  ·  '+document.getElementById(cmp).dataset.name:'');
    const meta=el=>{const k=el.querySelector('.kicker');return k.querySelector('.org').textContent+' · '+k.querySelector('.size').textContent};
    vmeta.textContent=cmp?meta(c)+'   |   '+meta(document.getElementById(cmp)):meta(c);
    vlinks.innerHTML='';
    if(!cmp)c.querySelectorAll('.links a').forEach(a=>vlinks.appendChild(a.cloneNode(true)));
    vbody.innerHTML='';vbody.className='vbody '+(zoom?'zoom':'fit');
    vbody.appendChild(pane(cur));
    if(cmp)vbody.appendChild(pane(cmp));
    vcmp.value=cmp;vzoom.setAttribute('aria-pressed',zoom);vzoom.textContent=zoom?'Fit':'Zoom';
  }
  function openView(slug){
    if(!document.getElementById('full-'+slug))return;
    if(viewer.hidden)lastFocus=document.activeElement;
    cur=slug;render();viewer.hidden=false;document.body.classList.add('noscroll');
    document.getElementById('vclose').focus();
    try{history.replaceState(null,'','#'+slug)}catch(e){}
  }
  function closeView(){
    viewer.hidden=true;document.body.classList.remove('noscroll');cmp='';
    try{history.replaceState(null,'',location.pathname+location.search)}catch(e){}
    const c=document.getElementById(cur);
    if(c&&c.getBoundingClientRect().top>innerHeight){c.scrollIntoView({block:'center'})}
    if(lastFocus)lastFocus.focus({preventScroll:true});
  }
  function step(d){const v=visible();if(!v.length)return;let i=v.findIndex(c=>c.dataset.slug===cur);i=(i+d+v.length)%v.length;cmp='';openView(v[i].dataset.slug)}
  document.addEventListener('click',e=>{const b=e.target.closest('[data-view]');if(b){openView(b.dataset.view)}});
  document.getElementById('vclose').addEventListener('click',closeView);
  document.getElementById('vprev').addEventListener('click',()=>step(-1));
  document.getElementById('vnext').addEventListener('click',()=>step(1));
  vzoom.addEventListener('click',()=>{zoom=!zoom;render()});
  vcmp.addEventListener('change',()=>{cmp=vcmp.value===cur?'':vcmp.value;render()});
  viewer.addEventListener('click',e=>{if(e.target===viewer)closeView()});
  // ---------------- guide
  const help=document.getElementById('helpview');
  document.getElementById('help').addEventListener('click',()=>{help.hidden=false;document.body.classList.add('noscroll');document.getElementById('hclose').focus()});
  function closeHelp(){help.hidden=true;document.body.classList.remove('noscroll');document.getElementById('help').focus()}
  document.getElementById('hclose').addEventListener('click',closeHelp);
  help.addEventListener('click',e=>{if(e.target===help)closeHelp()});
  document.addEventListener('keydown',e=>{
    if(!help.hidden&&e.key==='Escape'){closeHelp();return}
    if(viewer.hidden){if(e.key==='/'&&document.activeElement!==q){e.preventDefault();q.focus()}return}
    if(e.key==='Escape')closeView();
    else if(e.key==='ArrowRight')step(1);
    else if(e.key==='ArrowLeft')step(-1);
  });
  const fm=document.querySelector('.filters');
  document.addEventListener('click',e=>{if(fm.open&&!fm.contains(e.target))fm.open=false});
  // ---------------- theme
  const th=document.getElementById('theme');
  th.addEventListener('click',()=>{const r=document.documentElement;const c=r.getAttribute('data-theme');const dark=c?c==='dark':matchMedia('(prefers-color-scheme: dark)').matches;const n=dark?'light':'dark';r.setAttribute('data-theme',n);try{localStorage.setItem('wmg-theme',n)}catch(e){}});
  try{const t=localStorage.getItem('wmg-theme');if(t)document.documentElement.setAttribute('data-theme',t)}catch(e){}
  apply();
  if(location.hash){const s=location.hash.slice(1);const c=document.getElementById(s);if(c&&c.classList.contains('card')){lastFocus=c.querySelector('.thumb');openView(s)}}
})();
"""

HELP = """
<h2>How to read a diagram</h2>
<p>Data flows from the bottom up: input, encoder, the transformer block, the sampling loop, output heads, decoder.
Click a card's diagram to open the detailed version; open <i>Details</i> for the facts behind it.</p>
<ul class="legend-list">
  <li><span class="sw"></span> one operation</li>
  <li><span class="sw dark"></span> attention (the label names the mask)</li>
  <li><span class="sw teal"></span> encoder, tokenizer or decoder</li>
  <li><span class="sw orange"></span> action or conditioning module</li>
  <li><span class="sw group"></span> repeated block, with its N × marker</li>
  <li><span class="sw plus">+</span> residual add</li>
  <li><span class="sw inset"></span> zoom-in on one box</li>
  <li><span class="sw loop"></span> rollout loop: the label names what carries to the next step (tokens, latents)</li>
  <li><span class="sw acc">12</span> numbers sit beside the model</li>
  <li><span class="sw soft"></span> "Rest of block not stated": layers the source does not describe</li>
</ul>
<p style="margin:0;font-size:13.5px">Evidence: <b>read</b> means the primary publication and available code were read;
<b>claim</b> means an official developer page only. Each Source check names the figure's configuration,
paper/code differences and missing evidence. Undisclosed details are not inferred from other models.
Keys: <b>/</b> search, <b>← →</b> previous and next, <b>Esc</b> close.</p>
"""


def build(out_dir=DEFAULT_OUT, artifact=None):
    specs = R.load_models()
    bad = False
    for m in specs:
        errs = R.validate(m)
        if errs:
            bad = True
            print("INVALID %s: %s" % (m["slug"], "; ".join(errs)))
        if "flow" not in m:
            bad = True
            print("INVALID %s: no flow diagram" % m["slug"])
    if bad:
        sys.exit(1)
    ledger = A.load_reviews(specs)
    for m in specs:
        m["source_review"] = dict(ledger["models"][m["slug"]], date=ledger["date"])
    specs.sort(key=R.sort_key, reverse=True)
    for sub in ("stack", "mini"):
        os.makedirs(os.path.join(out_dir, "svg", sub), exist_ok=True)
    cards_site, cards_art, templates, data = [], [], [], []
    for m in specs:
        slug = m["slug"]
        full, w1, _ = S.render_stack_svg(m)
        mini, w2, _ = S.render_stack_svg(m, mini=True)
        for w in w1 + w2:
            print("WARN", w)
        with open(os.path.join(out_dir, "svg", "stack", slug + ".svg"), "w", encoding="utf-8") as f:
            f.write(full)
        with open(os.path.join(out_dir, "svg", "mini", slug + ".svg"), "w", encoding="utf-8") as f:
            f.write(mini)
        mini_web = web_svg(S.render_stack_svg(m, mini=True, background=False)[0], slug + "_m")
        full_web = web_svg(S.render_stack_svg(m, background=False, title=False)[0], slug + "_f")
        cards_site.append(card_html(m, mini_web, artifact=False))
        cards_art.append(card_html(m, mini_web, artifact=True))
        templates.append('<template id="full-%s">%s</template>' % (h(slug), full_web))
        d = {k: v for k, v in m.items() if not k.startswith("_")}
        d["facts"] = [list(f) for f in m["facts"]]
        data.append(d)
    with open(os.path.join(out_dir, "data.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=1, ensure_ascii=False)
    A.write_report(ledger, os.path.join(out_dir, "architecture_audit.md"))
    with open(os.path.join(out_dir, "architecture_audit.json"), "w", encoding="utf-8") as f:
        json.dump(ledger, f, indent=2, ensure_ascii=False)
        f.write("\n")

    fams = [k for k in R.FAMILIES if any(m["family"] == k for m in specs)]
    fam_chips = "".join('<button type="button" class="chip" data-fam="%s" aria-pressed="false" style="--fc:%s">'
                        '<i></i>%s</button>' % (k, FAMILY_COLOUR[k], h(FAMILY_SHORT[k])) for k in fams)
    years = sorted({m["year"] for m in specs})
    role_opts = "".join('<option value="%s">%s</option>' % (h(r), h(r)) for r in R.ROLES if any(m["role"] == r for m in specs))
    today = datetime.date.today().isoformat()
    n = len(specs)

    def body(cards):
        return f'''<div class="page">
<div class="util"><button class="ubtn" id="help" type="button" aria-label="How to read the diagrams">Guide</button><button class="ubtn" id="theme" type="button" aria-label="Switch light or dark theme">Theme</button></div>
<header class="hero">
  <p class="eyebrow">Transformer-core world models</p>
  <h1>World Model <span class="thin">Architecture</span> Gallery</h1>
  <p class="lede">Every model drawn in one visual language, from input to decoder. Click a diagram to open it.</p>
  <p class="stats"><span><b>{n}</b> models</span><span><b>{len(fams)}</b> families</span><span><b>{years[0]}–{years[-1]}</b></span><span>updated <b>{today}</b></span></p>
</header>
<div id="sentinel" aria-hidden="true"></div>
<div class="toolbar" role="search">
  <div class="controls">
    <label class="search"><svg width="15" height="15" viewBox="0 0 16 16" aria-hidden="true"><circle cx="7" cy="7" r="5.2" fill="none" stroke="currentColor" stroke-width="1.6"/><path d="M11 11l3.6 3.6" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg><input type="search" id="q" placeholder="Search {n} models" aria-label="Search models"></label>
    <details class="filters"><summary>Filters</summary><div class="menu">
      <select id="role" aria-label="Role"><option value="">Any role</option>{role_opts}</select>
      <select id="ev" aria-label="Evidence"><option value="">Any evidence</option><option value="read">read</option><option value="claim">claim</option></select>
      <select id="open" aria-label="Availability"><option value="">Any availability</option><option value="weights">open weights</option><option value="code">code</option><option value="closed">closed</option></select>
      <button type="button" id="clear">Clear filters</button>
    </div></details>
    <select class="ctl" id="sort" aria-label="Sort"><option value="date">Newest</option><option value="old">Oldest</option><option value="name">A–Z</option><option value="size">Largest</option></select>
    <span class="count" id="count"></span>
  </div>
  <div class="chips" aria-label="Families">{fam_chips}</div>
</div>
<main class="grid" id="grid">
{"".join(cards)}
</main>
<footer>
  <div class="fl">
    <details><summary>About</summary><div class="fold">
      <p>Architecture diagrams for world models whose dynamics model or generative backbone is a transformer, drawn in one visual language after the <a href="https://sebastianraschka.com/llm-architecture-gallery/" target="_blank" rel="noopener">LLM Architecture Gallery</a>. Numbers marked [D] in the details are our own arithmetic; speeds are the developers' own figures on their own hardware.</p>
      <p>Source review: all 49 original publications or official technical pages; matching released code for 42 models. Seven have no matching official implementation in the consulted sources. See the <a href="architecture_audit.md">per-model findings</a> for configurations, differences and pinned sources.</p>
      <p>Corrections and new models are welcome as issues or pull requests.</p>
    </div></details>
    <details><summary>Changelog</summary><div class="fold">{read_changelog()}</div></details>
  </div>
  <p class="copy">Cards and diagrams CC BY 4.0 · IBM Plex and Saira, OFL</p>
</footer>
</div>
<div class="viewer" id="viewer" hidden role="dialog" aria-modal="true" aria-labelledby="vtitle">
  <div class="vpanel">
    <div class="vbar">
      <div class="vtitle"><h2 id="vtitle"></h2><span id="vmeta"></span></div>
      <div class="vtools">
        <span class="vl" id="vlinks"></span>
        <select id="vcmp" aria-label="Compare with"><option value="">Compare with…</option></select>
        <button class="vb" id="vzoom" type="button" aria-pressed="false">Zoom</button>
        <button class="vb" id="vprev" type="button" aria-label="Previous model">←</button>
        <button class="vb" id="vnext" type="button" aria-label="Next model">→</button>
        <button class="vb" id="vclose" type="button" aria-label="Close">✕</button>
      </div>
    </div>
    <div class="vbody fit" id="vbody"></div>
    <div class="vkeys">← → browse · Esc close</div>
  </div>
</div>
<div class="viewer" id="helpview" hidden role="dialog" aria-modal="true" aria-label="How to read the diagrams">
  <div class="vpanel help">
    <div class="vbar"><div class="vtitle"><span>Guide</span></div><div class="vtools"><button class="vb" id="hclose" type="button" aria-label="Close">✕</button></div></div>
    <div class="vbody">{HELP}</div>
  </div>
</div>
{"".join(templates)}
<script>{JS}</script>
'''
    fonts = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n'
             '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
             '<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500'
             '&family=Saira+Semi+Condensed:wght@500;600&display=swap" rel="stylesheet">\n')
    desc = ("Architecture diagrams for %d world models whose core is a transformer, drawn in one visual language." % n)
    page = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n<title>%s</title>\n'
            '<meta name="description" content="%s">\n%s<style>%s</style>\n</head>\n<body>\n%s</body>\n</html>\n'
            % (SITE_TITLE, h(desc), fonts, CSS, body(cards_site)))
    with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(page)
    print("built %s with %d cards -> %s" % (SITE_TITLE, n, os.path.join(out_dir, "index.html")))
    if artifact:
        frag = "<title>%s</title>\n%s<style>%s</style>\n%s" % (SITE_TITLE, fonts, CSS, body(cards_art))
        os.makedirs(os.path.dirname(os.path.abspath(artifact)), exist_ok=True)
        with open(artifact, "w", encoding="utf-8") as f:
            f.write(frag)
        print("artifact fragment -> %s" % artifact)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=DEFAULT_OUT)
    ap.add_argument("--artifact", default=None, help="also write a skeleton-free copy for publishing as an artifact")
    a = ap.parse_args(argv)
    build(a.out, a.artifact)


if __name__ == "__main__":
    main()
