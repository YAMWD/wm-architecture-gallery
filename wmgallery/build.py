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

ROOT = R.ROOT
SITE_TITLE = "World Model Architecture Gallery"
DEFAULT_OUT = os.path.join(ROOT, "docs")

FAMILY_SHORT = {"rl": "RL world model", "token": "Token video", "dit": "Causal DiT", "driving": "Driving & robots",
                "jepa": "Embedding predictor", "wam": "World-action", "llm": "LLM & code", "object": "Object-centric",
                "ssm": "State-space"}
FAMILY_COLOUR = {"rl": "#1D3E72", "token": "#5E6B80", "dit": "#C46A12", "driving": "#007F7C", "jepa": "#9A7300",
                 "wam": "#8A8418", "llm": "#6B4FA0", "object": "#B4436C", "ssm": "#2F7D32"}
EVIDENCE_TEXT = {"verified": "Facts passed a 3-vote adversarial check",
                 "read": "Facts read from the paper or code",
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


def card_html(m, mini_svg, artifact=False):
    slug = m["slug"]
    links = [('<a href="%s" target="_blank" rel="noopener">%s</a>' % (h(u), h(k))) for k, u in m.get("links", {}).items()]
    links.append('<a href="svg/stack/%s.svg" target="_blank" rel="noopener"%s>SVG</a>' % (h(slug), "" if artifact else " download"))
    facts = "".join('<details class="fact"><summary>%s</summary><p>%s</p></details>' % (h(k), h(v)) for k, v in m["facts"])
    ev = m["evidence"]
    fam = m["family"]
    org = str(m.get("org", "")).split(" (")[0]
    size = re.sub(r"\s*\[D[^\]]*\]", "", str(m.get("params", ""))).split(" (")[0].split(",")[0]
    meta = " · ".join(str(v) for v in (org, m.get("year"), size) if v)
    return f'''<article class="card" id="{h(slug)}" data-slug="{h(slug)}" data-family="{h(fam)}" data-role="{h(m["role"])}"
 data-evidence="{h(ev)}" data-open="{h(m.get("open", ""))}" data-year="{m.get("year", 0)}" data-month="{m.get("month", 0)}"
 data-params="{m.get("params_num") or 0}" data-name="{h(m["name"])}">
  <button class="thumb" type="button" data-view="{h(slug)}" aria-label="Open the detailed diagram of {h(m["name"])}">{mini_svg}<span class="zoomhint" aria-hidden="true">⤢</span></button>
  <div class="info">
    <h3><button class="name" type="button" data-view="{h(slug)}">{h(m["name"])}</button></h3>
    <p class="meta">{h(meta)}</p>
    <p class="tag">{h(m.get("tagline", ""))}</p>
    <p class="chips"><span class="fam" style="--fc:{FAMILY_COLOUR[fam]}">{h(FAMILY_SHORT[fam])}</span><span class="ev ev-{h(ev)}" title="{h(EVIDENCE_TEXT[ev])}">{h(ev)}</span></p>
    <details class="more"><summary>Details</summary>
      <div class="facts">
        <details class="fact"><summary>Overview</summary><p>{h(m["summary"])}</p></details>
        {facts}
        <details class="fact"><summary>Status and sources</summary><p>{h(m["status"])}. Availability: {h(m.get("open", "n/a"))}. Sources: {h("; ".join(m.get("sources", [])))}.</p></details>
      </div>
      <p class="links">{" · ".join(links)}</p>
    </details>
  </div>
</article>'''


CSS = r"""
:root{--bg:#f5f7fa;--panel:#ffffff;--ink:#1E2A3B;--muted:#5E6B80;--navy:#1D3E72;--accent:#B95A08;--line:#dfe4ec;
--soft:#EEF1F5;--chip:#eef1f6;--link:#1D3E72;--shade:rgba(19,40,74,.55);--ev-v:#055e5c;--ev-vb:#dcf2f1;--ev-r:#1D3E72;
--ev-rb:#e4eaf4;--ev-c:#8a4a07;--ev-cb:#fde8d4;--focus:#F58F2D;--head:"Saira Semi Condensed","Saira SemiCondensed",Arial Narrow,sans-serif;
--body:"IBM Plex Sans",system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#0e1a2c;--panel:#152540;--ink:#e9eef5;--muted:#a6b3c6;--navy:#9cbcf0;--accent:#f5a05a;--line:#2a3a56;--soft:#1b2d4c;--chip:#1e3253;--link:#a9c8ff;--shade:rgba(3,8,18,.72);--ev-v:#7fe0dc;--ev-vb:#123e3d;--ev-r:#b8cdf3;--ev-rb:#1f3459;--ev-c:#ffc48f;--ev-cb:#4a2e12;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#0e1a2c;--panel:#152540;--ink:#e9eef5;--muted:#a6b3c6;--navy:#9cbcf0;--accent:#f5a05a;--line:#2a3a56;--soft:#1b2d4c;--chip:#1e3253;--link:#a9c8ff;--shade:rgba(3,8,18,.72);--ev-v:#7fe0dc;--ev-vb:#123e3d;--ev-r:#b8cdf3;--ev-rb:#1f3459;--ev-c:#ffc48f;--ev-cb:#4a2e12;color-scheme:dark}
*{box-sizing:border-box}
html,body{margin:0}
body{background:var(--bg);color:var(--ink);font-family:var(--body);font-size:15px;line-height:1.45}
body.noscroll{overflow:hidden}
a{color:var(--link)}
button{font:inherit;color:inherit}
:focus-visible{outline:2px solid var(--focus);outline-offset:2px}
.wrap{max-width:1240px;margin:0 auto;padding-inline:16px;padding-block:18px 40px}
.top{display:flex;align-items:flex-end;justify-content:space-between;gap:12px;flex-wrap:wrap;margin-bottom:12px}
.top h1{font-family:var(--head);font-weight:600;font-size:clamp(26px,4vw,36px);line-height:1.05;margin:0;color:var(--navy);text-wrap:balance}
.top .sub{margin:4px 0 0;color:var(--muted);font-size:14px}
.iconbtn{border:1px solid var(--line);background:var(--panel);border-radius:999px;min-width:36px;height:36px;padding:0 12px;cursor:pointer}
.iconbtn:hover{border-color:var(--navy)}
.toolbar{position:sticky;top:env(safe-area-inset-top,0px);z-index:5;background:var(--bg);display:flex;flex-direction:column;gap:8px;padding:10px 0;border-bottom:1px solid var(--line);margin-bottom:16px}
.toolbar .row{display:flex;flex-wrap:wrap;gap:8px;align-items:center}
.toolbar input[type=search],.toolbar select{font:inherit;font-size:14px;color:var(--ink);background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:7px 10px}
.toolbar input[type=search]{flex:1 1 200px;min-width:0;max-width:320px}
.chips-row{display:flex;flex-wrap:wrap;gap:6px}
.chip{border:1px solid var(--line);background:var(--panel);border-radius:999px;padding:4px 10px;font-size:13px;cursor:pointer;display:inline-flex;align-items:center;gap:6px}
.chip .dot{width:8px;height:8px;border-radius:50%;background:var(--fc)}
.chip[aria-pressed="true"]{background:var(--navy);border-color:var(--navy);color:var(--panel)}
.chip[aria-pressed="true"] .dot{background:var(--panel)}
.filters{position:relative}
.filters>summary{list-style:none;cursor:pointer;border:1px solid var(--line);background:var(--panel);border-radius:8px;padding:7px 10px;font-size:14px}
.filters>summary::-webkit-details-marker{display:none}
.filters[open]>summary{border-color:var(--navy)}
.filters .menu{position:absolute;top:calc(100% + 6px);left:0;z-index:6;background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:10px;display:grid;gap:8px;min-width:230px;box-shadow:0 8px 24px rgba(0,0,0,.12)}
.count{margin-left:auto;color:var(--muted);font-size:13px;font-variant-numeric:tabular-nums}
.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px;align-items:start}
@media (max-width:880px){.grid{grid-template-columns:minmax(0,1fr)}}
.card{background:var(--panel);border:1px solid var(--line);border-radius:12px;display:grid;grid-template-columns:230px minmax(0,1fr);gap:14px;padding:12px;scroll-margin-top:72px}
.card.hidden{display:none}
.thumb{position:relative;display:block;width:230px;height:236px;padding:6px;border:1px solid var(--line);border-radius:9px;background:#fff;cursor:zoom-in}
.thumb svg{display:block;width:100%;height:100%}
.thumb:hover{border-color:var(--navy)}
.zoomhint{position:absolute;right:6px;top:6px;font-size:14px;line-height:1;color:#5E6B80;background:#fff;border-radius:6px;padding:3px 5px;opacity:0;transition:opacity .15s}
.thumb:hover .zoomhint,.thumb:focus-visible .zoomhint{opacity:1}
@media (max-width:520px){.card{grid-template-columns:minmax(0,1fr)}.thumb{width:100%;height:240px}}
.info{min-width:0;display:flex;flex-direction:column;gap:4px}
.info h3{margin:0;font-family:var(--head);font-weight:600;font-size:21px;line-height:1.15;color:var(--navy)}
.name{background:none;border:none;padding:0;cursor:pointer;text-align:left;color:inherit;font:inherit}
.name:hover{text-decoration:underline}
.meta{margin:0;color:var(--muted);font-size:13px}
.tag{margin:2px 0 0;font-size:14.5px}
.chips{margin:4px 0 0;display:flex;flex-wrap:wrap;gap:6px}
.fam{font-size:12px;padding:2px 8px;border-radius:999px;background:var(--chip);display:inline-flex;align-items:center;gap:6px}
.fam::before{content:"";width:8px;height:8px;border-radius:50%;background:var(--fc)}
.ev{font-size:12px;padding:2px 8px;border-radius:999px}
.ev-verified{color:var(--ev-v);background:var(--ev-vb)}.ev-read{color:var(--ev-r);background:var(--ev-rb)}.ev-claim{color:var(--ev-c);background:var(--ev-cb)}
.more{margin-top:auto;padding-top:6px}
.more>summary,.fact>summary{cursor:pointer;list-style:none;display:flex;align-items:center;gap:6px;user-select:none}
.more>summary::-webkit-details-marker,.fact>summary::-webkit-details-marker{display:none}
.more>summary{font-size:13.5px;color:var(--link);width:max-content}
.more>summary::before,.fact>summary::before{content:"";width:6px;height:6px;border-right:1.6px solid currentColor;border-bottom:1.6px solid currentColor;transform:rotate(-45deg);transition:transform .15s;margin-right:2px}
.more[open]>summary::before,.fact[open]>summary::before{transform:rotate(45deg)}
.facts{margin-top:6px;border-top:1px solid var(--line)}
.fact{border-bottom:1px solid var(--line)}
.fact>summary{font-size:13.5px;font-weight:600;color:var(--muted);padding:6px 0}
.fact p{margin:0 0 8px 14px;font-size:13.5px}
.links{margin:8px 0 0;font-size:13px}
footer{margin-top:28px;border-top:1px solid var(--line);padding-top:12px;color:var(--muted);font-size:13.5px}
footer details{margin:6px 0}
footer summary{cursor:pointer;color:var(--link)}
footer h4{margin:10px 0 2px;font-size:13.5px;color:var(--ink)}
footer ul{margin:0 0 6px 18px;padding:0}
.viewer{position:fixed;inset:0;z-index:20;background:var(--shade);display:flex;padding:max(12px,env(safe-area-inset-top,0px)) 12px max(12px,env(safe-area-inset-bottom,0px))}
.viewer[hidden]{display:none!important}
.vpanel{background:var(--panel);border-radius:14px;flex:1;display:flex;flex-direction:column;min-width:0;min-height:0;overflow:hidden;box-shadow:0 20px 60px rgba(0,0,0,.35)}
.vbar{display:flex;align-items:center;gap:10px;flex-wrap:wrap;padding:10px 14px;border-bottom:1px solid var(--line)}
.vtitle{min-width:0;flex:1 1 220px}
.vtitle h2{margin:0;font-family:var(--head);font-weight:600;font-size:22px;color:var(--navy);line-height:1.1}
.vtitle span{color:var(--muted);font-size:13px}
.vtools{display:flex;align-items:center;gap:6px;flex-wrap:wrap}
.vtools select{font:inherit;font-size:13.5px;color:var(--ink);background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:6px 8px;max-width:200px}
.vtools a{font-size:13.5px}
.vbody{flex:1;min-height:0;overflow:auto;background:#fff;display:flex}
.vbody .pane{flex:1;min-width:0;display:flex;flex-direction:column;align-items:center;padding:10px}
.vbody .pane+.pane{border-left:1px solid #dfe4ec}
.vbody .pane h3{margin:0 0 4px;font-family:var(--head);font-weight:600;color:#1D3E72;font-size:16px}
.vbody .fig{flex:1;width:100%;min-height:0;display:flex;justify-content:center}
.vbody.fit .fig svg{width:100%;height:100%;max-height:100%}
.vbody.zoom{display:block}
.vbody.zoom .pane{display:inline-flex;vertical-align:top;min-width:max-content}
.vbody.zoom .fig svg{height:auto}
.help{max-width:760px;margin:auto;width:100%}
.help .vbody{display:block;padding:16px 18px;background:var(--panel);color:var(--ink)}
.legend-list{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:8px 16px;font-size:14px;margin:6px 0 12px;padding:0;list-style:none}
.legend-list li{display:flex;align-items:center;gap:10px}
.sw{display:inline-block;width:36px;height:18px;border-radius:5px;border:1px solid #1E2A3B;background:#fff;flex:none}
.sw.dark{background:#1D3E72;border-color:#1D3E72}.sw.teal{background:#DCF2F1;border-color:#00A8A4}.sw.orange{background:#FDE8D4;border-color:#F58F2D}
.sw.group{background:#E4EAF4;border-color:#1D3E72;border-radius:8px}.sw.inset{background:#EEF1F5;border-style:dashed;border-color:#5E6B80}
.sw.plus{border-radius:50%;width:18px;text-align:center;line-height:16px;font-weight:700;color:#1E2A3B}
.sw.acc{border:none;background:none;color:var(--accent);font-weight:700;width:auto}
.sw.loop{border:none;border-top:2px dashed #B95A08;height:0;border-radius:0}
@media (prefers-reduced-motion: reduce){*{transition:none!important}}
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
    document.getElementById('count').textContent=n===cards.length?n+' models':n+' of '+cards.length+' models';
  }
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
  function pane(slug,title){
    const p=document.createElement('div');p.className='pane';
    if(title){const h=document.createElement('h3');h.textContent=document.getElementById(slug).dataset.name;p.appendChild(h)}
    p.appendChild(figure(slug));return p;
  }
  function render(){
    const c=document.getElementById(cur);
    vtitle.textContent=c.dataset.name+(cmp?' vs '+document.getElementById(cmp).dataset.name:'');
    vmeta.textContent=c.querySelector('.meta').textContent;
    vlinks.innerHTML='';
    c.querySelectorAll('.links a').forEach(a=>{const x=a.cloneNode(true);vlinks.appendChild(x);vlinks.appendChild(document.createTextNode(' '))});
    vbody.innerHTML='';vbody.className='vbody '+(zoom?'zoom':'fit');
    vbody.appendChild(pane(cur,false));
    if(cmp)vbody.appendChild(pane(cmp,false));
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
  // ---------------- help
  const help=document.getElementById('helpview');
  document.getElementById('help').addEventListener('click',()=>{help.hidden=false;document.body.classList.add('noscroll');document.getElementById('hclose').focus()});
  function closeHelp(){help.hidden=true;document.body.classList.remove('noscroll');document.getElementById('help').focus()}
  document.getElementById('hclose').addEventListener('click',closeHelp);
  help.addEventListener('click',e=>{if(e.target===help)closeHelp()});
  document.addEventListener('keydown',e=>{
    if(!help.hidden&&e.key==='Escape'){closeHelp();return}
    if(viewer.hidden)return;
    if(e.key==='Escape')closeView();
    else if(e.key==='ArrowRight')step(1);
    else if(e.key==='ArrowLeft')step(-1);
  });
  // close the filter menu when clicking elsewhere
  const fm=document.querySelector('.filters');
  document.addEventListener('click',e=>{if(fm.open&&!fm.contains(e.target))fm.open=false});
  // ---------------- theme
  const tb=document.getElementById('theme');
  tb.addEventListener('click',()=>{const r=document.documentElement;const c=r.getAttribute('data-theme');const dark=c?c==='dark':matchMedia('(prefers-color-scheme: dark)').matches;const n=dark?'light':'dark';r.setAttribute('data-theme',n);try{localStorage.setItem('wmg-theme',n)}catch(e){}});
  try{const t=localStorage.getItem('wmg-theme');if(t)document.documentElement.setAttribute('data-theme',t)}catch(e){}
  apply();
  if(location.hash){const s=location.hash.slice(1);const c=document.getElementById(s);if(c&&c.classList.contains('card')){lastFocus=c.querySelector('.thumb');openView(s)}}
})();
"""

HELP = """
<h2 style="margin:0 0 6px;font-family:var(--head);font-weight:600;color:var(--navy)">How to read a diagram</h2>
<p style="margin:0 0 10px">Data flows from the bottom up: input, encoder, the transformer block, the sampling loop, output heads,
decoder. Click a card's diagram to open the detailed version; click <i>Details</i> for the facts.</p>
<ul class="legend-list">
  <li><span class="sw"></span> one operation</li>
  <li><span class="sw dark"></span> attention (the label names the mask)</li>
  <li><span class="sw teal"></span> encoder, tokenizer or decoder</li>
  <li><span class="sw orange"></span> action or conditioning module</li>
  <li><span class="sw group"></span> repeated block, with its N × marker</li>
  <li><span class="sw plus">+</span> residual add</li>
  <li><span class="sw inset"></span> zoom-in on one box</li>
  <li><span class="sw loop"></span> sampling or rollout loop</li>
  <li><span class="sw acc">12</span> numbers sit beside the model</li>
</ul>
<p style="margin:0;color:var(--muted);font-size:13.5px">Evidence: <b>verified</b> facts passed a 3-vote adversarial check;
<b>read</b> facts come from the paper or code; <b>claim</b> facts come from a developer page only.</p>
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
        mini_web = web_svg(mini, slug + "_m")
        cards_site.append(card_html(m, mini_web, artifact=False))
        cards_art.append(card_html(m, mini_web, artifact=True))
        templates.append('<template id="full-%s">%s</template>' % (h(slug), web_svg(full, slug + "_f")))
        d = {k: v for k, v in m.items() if not k.startswith("_")}
        d["facts"] = [list(f) for f in m["facts"]]
        data.append(d)
    with open(os.path.join(out_dir, "data.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=1, ensure_ascii=False)

    fam_chips = "".join('<button type="button" class="chip" data-fam="%s" aria-pressed="false" style="--fc:%s">'
                        '<span class="dot"></span>%s</button>' % (k, FAMILY_COLOUR[k], h(FAMILY_SHORT[k]))
                        for k in R.FAMILIES if any(m["family"] == k for m in specs))
    role_opts = "".join('<option value="%s">%s</option>' % (h(r), h(r)) for r in R.ROLES if any(m["role"] == r for m in specs))
    today = datetime.date.today().isoformat()
    n = len(specs)

    def body(cards):
        return f'''<div class="wrap">
<header class="top">
  <div><h1>{SITE_TITLE}</h1><p class="sub">{n} transformer-core world models · updated {today}</p></div>
  <div style="display:flex;gap:8px"><button class="iconbtn" id="help" type="button" aria-label="How to read the diagrams">?</button><button class="iconbtn" id="theme" type="button" aria-label="Switch light or dark theme">◐</button></div>
</header>
<div class="toolbar" role="search">
  <div class="row">
  <input type="search" id="q" placeholder="Search models" aria-label="Search models">
  <details class="filters"><summary>Filters</summary><div class="menu">
    <select id="role" aria-label="Role"><option value="">Any role</option>{role_opts}</select>
    <select id="ev" aria-label="Evidence"><option value="">Any evidence</option><option value="verified">verified</option><option value="read">read</option><option value="claim">claim</option></select>
    <select id="open" aria-label="Availability"><option value="">Any availability</option><option value="weights">open weights</option><option value="code">code</option><option value="closed">closed</option></select>
    <button type="button" class="iconbtn" id="clear">Clear filters</button>
  </div></details>
  <select id="sort" aria-label="Sort"><option value="date">Newest first</option><option value="old">Oldest first</option><option value="name">Name</option><option value="size">Largest first</option></select>
  <span class="count" id="count"></span>
  </div>
  <div class="chips-row" aria-label="Families">{fam_chips}</div>
</div>
<main class="grid" id="grid">
{"".join(cards)}
</main>
<footer>
  <details><summary>About this gallery</summary>
    <p>Architecture diagrams for world models whose dynamics model or generative backbone is a transformer, drawn in one visual language after the <a href="https://sebastianraschka.com/llm-architecture-gallery/" target="_blank" rel="noopener">LLM Architecture Gallery</a>. Numbers marked [D] in the details are our own arithmetic; speeds are the developers' own figures on their own hardware.</p>
    <p>Corrections and new models are welcome as issues or pull requests. Cards and diagrams: CC BY 4.0. Fonts: IBM Plex and Saira (OFL).</p>
  </details>
  <details><summary>Changelog</summary>{read_changelog()}</details>
</footer>
</div>
<div class="viewer" id="viewer" hidden role="dialog" aria-modal="true" aria-labelledby="vtitle">
  <div class="vpanel">
    <div class="vbar">
      <div class="vtitle"><h2 id="vtitle"></h2><span id="vmeta"></span></div>
      <div class="vtools">
        <span id="vlinks"></span>
        <select id="vcmp" aria-label="Compare with"><option value="">Compare with…</option></select>
        <button class="iconbtn" id="vzoom" type="button" aria-pressed="false">Zoom</button>
        <button class="iconbtn" id="vprev" type="button" aria-label="Previous model">‹</button>
        <button class="iconbtn" id="vnext" type="button" aria-label="Next model">›</button>
        <button class="iconbtn" id="vclose" type="button" aria-label="Close">✕</button>
      </div>
    </div>
    <div class="vbody fit" id="vbody"></div>
  </div>
</div>
<div class="viewer" id="helpview" hidden role="dialog" aria-modal="true" aria-label="How to read the diagrams">
  <div class="vpanel help">
    <div class="vbar"><div class="vtitle"></div><div class="vtools"><button class="iconbtn" id="hclose" type="button" aria-label="Close">✕</button></div></div>
    <div class="vbody">{HELP}</div>
  </div>
</div>
{"".join(templates)}
<script>{JS}</script>
'''
    fonts = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n'
             '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
             '<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;600;700&family=IBM+Plex+Mono'
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
