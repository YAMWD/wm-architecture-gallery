"""Build the static gallery site: docs/index.html, docs/svg/*.svg, docs/data.json (+ PNGs with --png).

    python3 -m wmgallery.build            # site into docs/
    python3 -m wmgallery.build --png      # also PNGs (slow; used for slides)
"""
import os
import sys
import json
import html
import argparse
import datetime

from . import diagram as D
from . import registry as R

ROOT = R.ROOT
SITE_TITLE = "World Model Architecture Gallery"
DEFAULT_OUT = os.path.join(ROOT, "docs")


def h(s):
    return html.escape(str(s), quote=True)


def read_changelog():
    p = os.path.join(ROOT, "CHANGELOG.md")
    if not os.path.exists(p):
        return ""
    items = []
    for line in open(p, encoding="utf-8"):
        line = line.rstrip()
        if line.startswith("## "):
            items.append("<h4>%s</h4>" % h(line[3:]))
        elif line.startswith("- "):
            items.append("<li>%s</li>" % h(line[2:]))
    out, in_list = [], False
    for it in items:
        if it.startswith("<li>") and not in_list:
            out.append("<ul>"); in_list = True
        if it.startswith("<h4>") and in_list:
            out.append("</ul>"); in_list = False
        out.append(it)
    if in_list:
        out.append("</ul>")
    return "\n".join(out)


def card_html(m, svg, artifact=False):
    links = " · ".join('<a href="%s" target="_blank" rel="noopener">%s</a>' % (h(u), h(k)) for k, u in m.get("links", {}).items())
    facts = "".join("<tr><th>%s</th><td>%s</td></tr>" % (h(k), h(v)) for k, v in m["facts"])
    sources = "; ".join(h(s) for s in m.get("sources", []))
    ev = m["evidence"]
    fam = R.FAMILIES[m["family"]]
    return f'''
<article class="card" id="{h(m["slug"])}" data-slug="{h(m["slug"])}" data-family="{h(m["family"])}" data-role="{h(m["role"])}"
         data-evidence="{h(ev)}" data-open="{h(m.get("open", ""))}" data-year="{m.get("year", 0)}" data-month="{m.get("month", 0)}"
         data-params="{m.get("params_num") or 0}" data-name="{h(m["name"])}">
  <header class="card-head">
    <div>
      <h3><a href="#{h(m["slug"])}">{h(m["name"])}</a></h3>
      <div class="meta">{m.get("year", "")} · {h(m["org"])} · {h(m["params"])}</div>
    </div>
    <div class="badges">
      <span class="badge fam">{h(fam)}</span>
      <span class="badge role">{h(m["role"])}</span>
      <span class="badge ev ev-{h(ev)}" title="{h(R.EVIDENCE[ev])}">{h(ev)}</span>
      <span class="badge open">{h(m.get("open", ""))}</span>
    </div>
  </header>
  <div class="card-body">
    <div class="fig">{svg}</div>
    <div class="text">
      <p class="status"><b>{h(m["status"])}</b>{(" · " + links) if links else ""}</p>
      <p class="summary">{h(m["summary"])}</p>
      <table class="facts">{facts}</table>
      <p class="sources"><b>Sources:</b> {sources}</p>
      <p class="tools"><a href="svg/{h(m["slug"])}.svg"{"" if artifact else " download"} target="_blank" rel="noopener">{"Open" if artifact else "Download"} SVG</a> · <button class="cmp" data-slug="{h(m["slug"])}">Compare</button></p>
    </div>
  </div>
</article>'''


CSS = r"""
:root{--bg:#f6f8fb;--card:#ffffff;--ink:#1E2A3B;--muted:#5E6B80;--navy:#1D3E72;--orange:#F58F2D;--teal:#00A8A4;--gold:#F0B225;
--line:#d7dde7;--soft:#EEF1F5;--link:#1D3E72;--badge:#e4eaf4;}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#0f1b2d;--card:#162642;--ink:#eef2f7;--muted:#aab6c8;--navy:#8fb0e6;--line:#2b3b57;--soft:#1d2f4e;--link:#9cc0ff;--badge:#22365a;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#0f1b2d;--card:#162642;--ink:#eef2f7;--muted:#aab6c8;--navy:#8fb0e6;--line:#2b3b57;--soft:#1d2f4e;--link:#9cc0ff;--badge:#22365a;color-scheme:dark}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font-family:"IBM Plex Sans",system-ui,-apple-system,Segoe UI,Roboto,sans-serif;font-size:15px;line-height:1.45}
a{color:var(--link)}
h1,h2,h3,h4{font-family:"Saira Semi Condensed","Saira SemiCondensed","IBM Plex Sans",sans-serif;font-weight:600;color:var(--navy);margin:0}
.wrap{max-width:1280px;margin:0 auto;padding-inline:16px;padding-block:16px}
.scroll{overflow-x:auto;max-width:100%}
header.top{display:flex;flex-wrap:wrap;gap:12px;align-items:flex-end;justify-content:space-between;border-bottom:3px solid var(--orange);padding-bottom:12px;margin-bottom:16px}
header.top h1{font-size:34px;line-height:1.1}
header.top .sub{color:var(--muted);margin-top:4px}
.topbtns{display:flex;gap:8px;align-items:center}
button,select,input[type=search]{font:inherit;color:var(--ink);background:var(--card);border:1px solid var(--line);border-radius:6px;padding:6px 10px}
button{cursor:pointer}
button.primary{background:var(--navy);color:#fff;border-color:var(--navy)}
.intro{display:grid;grid-template-columns:1.3fr 1fr;gap:16px;margin-bottom:16px}
@media (max-width:900px){.intro{grid-template-columns:1fr}}
.panel{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px 16px}
.panel h2{font-size:20px;margin-bottom:6px}
.legend svg{width:100%;height:auto;background:#fff;border-radius:6px}
.controls{position:sticky;top:0;z-index:5;background:var(--bg);padding:8px 0 10px;border-bottom:1px solid var(--line);margin-bottom:14px;display:flex;flex-wrap:wrap;gap:8px;align-items:center}
.chips{display:flex;flex-wrap:wrap;gap:6px}
.chip{border:1px solid var(--line);background:var(--card);border-radius:999px;padding:4px 10px;font-size:13px;cursor:pointer;user-select:none}
.chip.on{background:var(--navy);color:#fff;border-color:var(--navy)}
.count{color:var(--muted);font-size:13px;margin-left:auto}
.grid{display:grid;grid-template-columns:1fr;gap:16px}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;overflow:hidden;scroll-margin-top:70px}
.card-head{display:flex;flex-wrap:wrap;justify-content:space-between;gap:8px;padding:12px 16px;border-bottom:1px solid var(--line)}
.card-head h3{font-size:22px}
.card-head h3 a{text-decoration:none;color:inherit}
.meta{color:var(--muted);font-size:13px}
.badges{display:flex;flex-wrap:wrap;gap:6px;align-items:center}
.badge{font-size:12px;padding:2px 8px;border-radius:999px;background:var(--badge);color:var(--ink);white-space:nowrap}
.badge.ev-verified{background:#dcf2f1;color:#055e5c}.badge.ev-read{background:#e4eaf4;color:#1D3E72}.badge.ev-claim{background:#fde8d4;color:#8a4a07}
.card-body{display:grid;grid-template-columns:320px minmax(0,1fr);gap:16px;padding:14px 16px}
.text{min-width:0}
@media (max-width:760px){.card-body{grid-template-columns:1fr}}
.fig{background:#fff;border:1px solid var(--line);border-radius:8px;padding:6px;align-self:start}
.fig svg{width:100%;height:auto;display:block}
.summary{margin:6px 0 10px}
.status{margin:0;color:var(--muted);font-size:13px}
.facts{border-collapse:collapse;width:100%;font-size:13.5px;margin-bottom:8px}
.facts th{text-align:left;color:var(--muted);font-weight:600;padding:4px 10px 4px 0;vertical-align:top;white-space:nowrap;width:120px}
.facts td{padding:4px 0;border-top:1px solid var(--line);vertical-align:top}
.facts tr:first-child td{border-top:none}
.sources,.tools{font-size:12.5px;color:var(--muted);margin:6px 0 0}
.cmpbar{position:sticky;top:52px;z-index:4;background:var(--card);border:1px solid var(--line);border-radius:10px;padding:8px 12px;margin-bottom:14px;display:none;gap:10px;align-items:center;flex-wrap:wrap}
.cmpbar.on{display:flex}
.cmpview{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:16px}
@media (max-width:900px){.cmpview{grid-template-columns:1fr}}
.cmptable{width:100%;border-collapse:collapse;font-size:13.5px;margin-bottom:16px}
.cmptable th,.cmptable td{border-top:1px solid var(--line);padding:6px 8px;vertical-align:top;text-align:left}
.cmptable th{color:var(--muted);width:120px}
.cmptable thead th{color:var(--navy);font-size:16px}
footer{color:var(--muted);font-size:13px;margin:30px 0 10px;border-top:1px solid var(--line);padding-top:12px}
.hidden{display:none !important}
details summary{cursor:pointer;color:var(--navy);font-weight:600}
.changelog ul{margin:4px 0 10px 18px}
code{font-family:"IBM Plex Mono",ui-monospace,monospace;font-size:13px;background:var(--soft);padding:1px 4px;border-radius:4px}
"""

JS = r"""
(function(){
  const cards=[...document.querySelectorAll('.card')];
  const state={fam:new Set(),role:'',ev:'',open:'',q:'',sort:'date'};
  const chips=document.querySelectorAll('.chip[data-fam]');
  chips.forEach(c=>c.addEventListener('click',()=>{const f=c.dataset.fam;if(state.fam.has(f)){state.fam.delete(f);c.classList.remove('on')}else{state.fam.add(f);c.classList.add('on')}apply()}));
  const sel=(id,key)=>{const e=document.getElementById(id);e.addEventListener('change',()=>{state[key]=e.value;apply()})};
  sel('role','role');sel('ev','ev');sel('open','open');sel('sort','sort');
  const q=document.getElementById('q');q.addEventListener('input',()=>{state.q=q.value.toLowerCase();apply()});
  document.getElementById('clear').addEventListener('click',()=>{state.fam.clear();chips.forEach(c=>c.classList.remove('on'));['role','ev','open'].forEach(k=>{state[k]='';document.getElementById(k).value=''});state.q='';q.value='';apply()});
  function apply(){
    let n=0;
    cards.forEach(c=>{
      let ok=true;
      if(state.fam.size&&!state.fam.has(c.dataset.family))ok=false;
      if(state.role&&c.dataset.role!==state.role)ok=false;
      if(state.ev&&c.dataset.evidence!==state.ev)ok=false;
      if(state.open&&!c.dataset.open.includes(state.open))ok=false;
      if(state.q&&!c.textContent.toLowerCase().includes(state.q))ok=false;
      c.classList.toggle('hidden',!ok);if(ok)n++;
    });
    const grid=document.getElementById('grid');
    const sorted=[...cards].sort((a,b)=>{
      if(state.sort==='name')return a.dataset.name.localeCompare(b.dataset.name);
      if(state.sort==='size')return (+b.dataset.params)-(+a.dataset.params);
      if(state.sort==='old')return (a.dataset.year*12+ +a.dataset.month)-(b.dataset.year*12+ +b.dataset.month);
      return (b.dataset.year*12+ +b.dataset.month)-(a.dataset.year*12+ +a.dataset.month);
    });
    sorted.forEach(c=>grid.appendChild(c));
    document.getElementById('count').textContent=n+' of '+cards.length+' models';
  }
  // compare
  const cmp={a:null,b:null};
  const bar=document.getElementById('cmpbar'),view=document.getElementById('cmpview'),tbl=document.getElementById('cmptable');
  const selA=document.getElementById('cmpA'),selB=document.getElementById('cmpB');
  cards.forEach(c=>{[selA,selB].forEach(s=>{const o=document.createElement('option');o.value=c.dataset.slug;o.textContent=c.dataset.name;s.appendChild(o)})});
  function setCmp(slot,slug){cmp[slot]=slug;(slot==='a'?selA:selB).value=slug||'';renderCmp()}
  selA.addEventListener('change',()=>setCmp('a',selA.value));selB.addEventListener('change',()=>setCmp('b',selB.value));
  document.querySelectorAll('button.cmp').forEach(b=>b.addEventListener('click',()=>{const s=b.dataset.slug;if(!cmp.a||cmp.a===s)setCmp('a',s);else setCmp('b',s);bar.classList.add('on');window.scrollTo({top:0,behavior:'smooth'})}));
  document.getElementById('cmpswap').addEventListener('click',()=>{const t=cmp.a;setCmp('a',cmp.b);setCmp('b',t)});
  document.getElementById('cmpclear').addEventListener('click',()=>{setCmp('a',null);setCmp('b',null);bar.classList.remove('on')});
  function renderCmp(){
    view.innerHTML='';tbl.innerHTML='';
    const picks=[cmp.a,cmp.b].filter(Boolean).map(s=>document.getElementById(s));
    if(!picks.length){view.classList.add('hidden');tbl.classList.add('hidden');return}
    bar.classList.add('on');view.classList.remove('hidden');
    picks.forEach(c=>{const d=document.createElement('div');d.className='fig';d.innerHTML='<h3 style="padding:6px 8px">'+c.dataset.name+'</h3>'+c.querySelector('.fig').innerHTML;view.appendChild(d)});
    if(picks.length===2){
      tbl.classList.remove('hidden');
      const rows=[...picks[0].querySelectorAll('.facts tr')].map(r=>r.children[0].textContent);
      let html='<thead><tr><th></th><th>'+picks[0].dataset.name+'</th><th>'+picks[1].dataset.name+'</th></tr></thead><tbody>';
      rows.forEach(label=>{const v=picks.map(c=>{const r=[...c.querySelectorAll('.facts tr')].find(r=>r.children[0].textContent===label);return r?r.children[1].textContent:'—'});html+='<tr><th>'+label+'</th><td>'+v[0]+'</td><td>'+v[1]+'</td></tr>'});
      tbl.innerHTML=html+'</tbody>';
    }else{tbl.classList.add('hidden')}
  }
  // theme
  const tb=document.getElementById('theme');
  tb.addEventListener('click',()=>{const r=document.documentElement;const cur=r.getAttribute('data-theme');const dark=cur?cur==='dark':matchMedia('(prefers-color-scheme: dark)').matches;r.setAttribute('data-theme',dark?'light':'dark');try{localStorage.setItem('wmg-theme',dark?'light':'dark')}catch(e){}});
  try{const t=localStorage.getItem('wmg-theme');if(t)document.documentElement.setAttribute('data-theme',t)}catch(e){}
  // deep link to a card
  if(location.hash){const c=document.getElementById(location.hash.slice(1));if(c)setTimeout(()=>c.scrollIntoView(),50)}
  apply();
})();
"""


def build(out_dir=DEFAULT_OUT, png=False, width=300, artifact=None):
    specs = R.load_models()
    bad = False
    for m in specs:
        errs = R.validate(m)
        if errs:
            bad = True
            print("INVALID %s: %s" % (m["slug"], "; ".join(errs)))
    if bad:
        sys.exit(1)
    specs.sort(key=R.sort_key)
    os.makedirs(os.path.join(out_dir, "svg"), exist_ok=True)
    cards = []
    acards = []
    data = []
    for m in specs:
        svg, warns, size = D.render_svg(m, width)
        for w in warns:
            print("WARN", w)
        with open(os.path.join(out_dir, "svg", m["slug"] + ".svg"), "w", encoding="utf-8") as f:
            f.write(svg)
        if png:
            D.svg_to_png(svg, os.path.join(out_dir, "png", m["slug"] + ".png")) if os.makedirs(os.path.join(out_dir, "png"), exist_ok=True) is None else None
        inline = svg.replace(D.FONT_IMPORT, "")  # the page loads the fonts once
        cards.append(card_html(m, inline, artifact=False))
        if artifact:
            acards.append(card_html(m, inline, artifact=True))
        d = {k: v for k, v in m.items() if not k.startswith("_")}
        d["facts"] = [list(f) for f in m["facts"]]
        data.append(d)
    legend = D.legend_svg(560).replace(D.FONT_IMPORT, "")
    with open(os.path.join(out_dir, "data.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=1, ensure_ascii=False)
    with open(os.path.join(out_dir, "legend.svg"), "w", encoding="utf-8") as f:
        f.write(D.legend_svg(560))

    fam_chips = "".join('<span class="chip" data-fam="%s">%s <span class="n">(%d)</span></span>'
                        % (k, h(v), sum(1 for m in specs if m["family"] == k)) for k, v in R.FAMILIES.items()
                        if any(m["family"] == k for m in specs))
    role_opts = "".join('<option value="%s">%s</option>' % (h(r), h(r)) for r in R.ROLES if any(m["role"] == r for m in specs))
    today = datetime.date.today().isoformat()
    n_models = len(specs)
    years = sorted({m["year"] for m in specs})
    def body(cards_html):
        return f'''<div class="wrap">
<header class="top">
  <div>
    <h1>{SITE_TITLE}</h1>
    <div class="sub">{n_models} transformer-core world models, {years[0]}–{years[-1]}, drawn in one visual language. Updated {today}.</div>
  </div>
  <div class="topbtns"><a href="data.json">data.json</a> <button id="theme" title="Toggle light/dark">Theme</button></div>
</header>

<section class="intro">
  <div class="panel">
    <h2>How to read a card</h2>
    <p>Each card is read from the bottom up: the <b>encoder</b> turns observations into the sequence, the <b>token row</b> shows what one step of the sequence contains, the <b>transformer box</b> lists its blocks (attention masks, where actions enter), the <b>sampling box</b> says how the next state is produced and how many passes that costs, and the <b>decoder</b> turns the prediction back into observations. The dashed orange arrow is the autoregressive or planning loop.</p>
    <p>Scope: models whose dynamics model or generative backbone is a transformer. U-Net diffusion models, RNN world models and MLP latent models are out of scope. Cards mark their evidence level: <span class="badge ev-verified">verified</span> facts survived a 3-vote adversarial check, <span class="badge ev-read">read</span> facts were read from the paper or code, <span class="badge ev-claim">claim</span> facts come from a developer page only. Numbers marked [D] are our own arithmetic.</p>
    <p>Maintained in the open: send corrections and new cards as issues or pull requests (see <code>CONTRIBUTING</code> in the repository). Every card has a permalink and a downloadable SVG.</p>
  </div>
  <div class="panel legend"><h2>Legend</h2>{legend}</div>
</section>

<div class="controls">
  <input type="search" id="q" placeholder="Search name, org, facts…" style="min-width:220px">
  <div class="chips">{fam_chips}</div>
  <select id="role"><option value="">All roles</option>{role_opts}</select>
  <select id="ev"><option value="">All evidence</option><option value="verified">verified</option><option value="read">read</option><option value="claim">claim</option></select>
  <select id="open"><option value="">Any availability</option><option value="weights">open weights</option><option value="code">code</option><option value="closed">closed</option></select>
  <select id="sort"><option value="date">Newest first</option><option value="old">Oldest first</option><option value="name">Name</option><option value="size">Largest first</option></select>
  <button id="clear">Clear</button>
  <span class="count" id="count"></span>
</div>

<div class="cmpbar" id="cmpbar">
  <b>Compare</b> <select id="cmpA"><option value="">Pick a model</option></select> <select id="cmpB"><option value="">Pick a model</option></select>
  <button id="cmpswap">Swap</button> <button id="cmpclear">Clear</button>
</div>
<div class="cmpview hidden" id="cmpview"></div>
<div class="scroll"><table class="cmptable hidden" id="cmptable"></table></div>

<div class="grid" id="grid">
{"".join(cards_html)}
</div>

<section class="panel changelog" style="margin-top:20px"><h2>Changelog</h2>{read_changelog()}</section>

<footer>Cards © the gallery authors, CC BY 4.0. Diagrams are drawn from the cited papers, code and reports; figures that come from a developer's own report are marked as such. Fonts: IBM Plex and Saira (OFL).</footer>
</div>
<script>{JS}</script>
'''
    fonts = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n'
             '<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;600;700&family=IBM+Plex+Mono'
             '&family=Saira+Semi+Condensed:wght@500;600&display=swap" rel="stylesheet">\n')
    desc = ("Architecture cards for %d world models whose core is a transformer, drawn in one visual language: "
            "tokenizer, token layout, transformer blocks, sampling, decoder." % n_models)
    page = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1">\n<title>%s</title>\n'
            '<meta name="description" content="%s">\n%s<style>%s</style>\n</head>\n<body>\n%s</body>\n</html>\n'
            % (SITE_TITLE, h(desc), fonts, CSS, body(cards)))
    with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(page)
    print("built %s with %d cards -> %s" % (SITE_TITLE, n_models, os.path.join(out_dir, "index.html")))
    if artifact:
        # fragment for publishing as a claude.ai artifact: the host adds the document skeleton
        frag = "<title>%s</title>\n%s<style>%s</style>\n%s" % (SITE_TITLE, fonts, CSS, body(acards))
        os.makedirs(os.path.dirname(os.path.abspath(artifact)), exist_ok=True)
        with open(artifact, "w", encoding="utf-8") as f:
            f.write(frag)
        print("artifact fragment -> %s" % artifact)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=DEFAULT_OUT)
    ap.add_argument("--png", action="store_true")
    ap.add_argument("--width", type=int, default=300)
    ap.add_argument("--artifact", default=None, help="also write a skeleton-free copy for publishing as an artifact")
    a = ap.parse_args(argv)
    build(a.out, a.png, a.width, a.artifact)


if __name__ == "__main__":
    main()
