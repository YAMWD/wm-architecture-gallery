"""World-model architecture diagrams: a small declarative spec -> SVG (and PNG via cairosvg).

Every diagram is a vertical stack read from the bottom up, like a transformer architecture card:

    header       model name, year, organisation, size
    decoder      what turns the prediction back into observations (or 'no pixel decoder')
    heads        optional reward / value / policy / action heads
    sampling     how the next state is produced and how many passes it costs
    core         the transformer: title bar + inner rows (attention, MLP, action injection, ...)
    tokens       what one step of the sequence contains (token squares, coloured by type)
    encoder      what turns observations into the core's input

Spec keys (plain text; use \\n for a forced line break). Every box may carry a "short" variant used in
compact mode (slides), where only the main text, the token squares and the core rows are drawn:

    diagram = {
      "encoder":  {"text": "Frame 64x64 -> VQ-VAE (CNN)", "sub": "16 codes per frame", "tag": "frozen",
                   "short": "VQ-VAE, 16 codes per frame"},
      "tokens":   {"groups": [("frame", 16, "16 frame codes"), ("action", 1, "action")],
                   "note": "context 20 steps = 340 tokens"},
      "core":     {"title": "GPT x10 - d 256 - 4 heads",
                   "rows": [("attn", "Causal self-attention over tokens"), ("mlp", "MLP")],
                   "notes": ["KV cache reset at 340 tokens"]},
      "sampling": {"kind": "ar", "text": "Next-token softmax, 512 codes", "sub": "17 serial passes per frame",
                   "short": "Next token, 17 serial passes per frame"},
      "heads":    ["reward", "done"],                      # optional
      "decoder":  {"text": "VQ decoder (CNN) -> frame", "sub": "...", "tag": "frozen"},  # or {"none": "reason"}
      "loop":     "AR rollout",                             # optional: dashed feedback arrow
    }

Token kinds: frame (discrete codes, filled navy), latent (continuous, hollow navy), action (orange),
reward (gold), state (teal), text (gold, hollow), register (slate), slot (navy, rounded), noise, audio.
Core row kinds: attn, xattn, mlp, action, ssm, moe, note.
Sampling kinds: ar (serial loop), parallel (MaskGIT-style), diffusion (denoising loop), regress (single pass), search.
"""
import os
import math
from PIL import ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(os.path.dirname(HERE), "fonts")
FONT_FILES = {"head": "SairaSemiCondensed-SemiBold.ttf", "headm": "SairaSemiCondensed-Medium.ttf",
              "body": "IBMPlexSans-Regular.ttf", "bold": "IBMPlexSans-Bold.ttf", "mono": "IBMPlexMono-Regular.ttf"}
FONT_CSS = {"head": ("Saira SemiCondensed", 600), "headm": ("Saira SemiCondensed", 500),
            "body": ("IBM Plex Sans", 400), "bold": ("IBM Plex Sans", 700), "mono": ("IBM Plex Mono", 400)}

# ACCL palette (template theme) plus tints for fills
C = {"navy": "#1D3E72", "orange": "#F58F2D", "teal": "#00A8A4", "gold": "#F0B225", "lime": "#D3C72A",
     "slate": "#5E6B80", "ink": "#13284A", "text": "#1E2A3B", "soft": "#EEF1F5", "white": "#FFFFFF",
     "grey": "#5E6B80", "line": "#C9D1DD",
     "navy_t": "#E4EAF4", "orange_t": "#FDE8D4", "teal_t": "#DCF2F1", "gold_t": "#FCF0CB", "lime_t": "#F4F2D4",
     "slate_t": "#E7EAEF", "goldd": "#B07D00"}

TOKEN_STYLE = {  # kind: (fill, stroke, shape)
    "frame": (C["navy"], C["navy"], "rect"), "latent": (C["white"], C["navy"], "rect"),
    "action": (C["orange"], C["orange"], "rect"), "reward": (C["gold"], C["gold"], "rect"),
    "state": (C["teal"], C["teal"], "rect"), "text": (C["white"], C["goldd"], "rect"),
    "register": (C["slate"], C["slate"], "rect"), "slot": (C["navy"], C["navy"], "round"),
    "noise": (C["soft"], C["slate"], "rect"), "audio": (C["lime"], C["lime"], "rect"),
}
TOKEN_LEGEND = [("frame", "discrete codes"), ("latent", "continuous latents / features"), ("action", "action"),
                ("state", "proprioception / state"), ("reward", "reward"), ("text", "text"),
                ("register", "register / special"), ("slot", "object slot"), ("noise", "noise placeholder")]
ROW_STYLE = {  # core inner rows: (fill, stroke)
    "attn": (C["navy_t"], None), "xattn": (C["gold_t"], None), "mlp": (C["soft"], None),
    "action": (C["orange_t"], C["orange"]), "ssm": (C["lime_t"], None), "moe": (C["teal_t"], None),
    "note": (None, None),
}
ROW_LEGEND = [("attn", "self-attention"), ("xattn", "cross-attention"), ("mlp", "MLP / FFN"),
              ("action", "action injection"), ("ssm", "SSM / linear attention"), ("moe", "expert or second stream")]
SAMPLING_ICON = {"ar": "loop", "parallel": "parallel", "diffusion": "loop", "regress": None, "search": "tree"}

# ------------------------------------------------------------------ text measurement
_fonts = {}


def _font(kind, size):
    key = (kind, round(size * 4))
    if key not in _fonts:
        try:
            _fonts[key] = ImageFont.truetype(os.path.join(FONT_DIR, FONT_FILES[kind]), max(1, int(round(size * 4))))
        except OSError:
            _fonts[key] = None
    return _fonts[key]


def text_width(s, kind="body", size=13):
    f = _font(kind, size)
    if f is None:
        return 0.55 * size * len(s)
    return f.getlength(s) / 4.0


def wrap(s, kind, size, maxw):
    """Wrap text to maxw (units). Honour explicit newlines. Never returns an empty list."""
    out = []
    for para in str(s).split("\n"):
        words = para.split()
        if not words:
            out.append("")
            continue
        cur = ""
        for w in words:
            t = (cur + " " + w).strip()
            if not cur or text_width(t, kind, size) <= maxw:
                cur = t
            else:
                out.append(cur)
                cur = w
        out.append(cur)
    return out


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


# ------------------------------------------------------------------ svg primitives
class Canvas:
    def __init__(self):
        self.parts = []
        self.warnings = []
        self.markers = set()

    def rect(self, x, y, w, h, fill=None, stroke=None, sw=1.0, rx=5, dash=None, opacity=None):
        a = ['<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="%.1f"' % (x, y, w, h, rx)]
        a.append(' fill="%s"' % (fill or "none"))
        if stroke:
            a.append(' stroke="%s" stroke-width="%.1f"' % (stroke, sw))
        if dash:
            a.append(' stroke-dasharray="%s"' % dash)
        if opacity is not None:
            a.append(' opacity="%.2f"' % opacity)
        a.append("/>")
        self.parts.append("".join(a))

    def text(self, x, y, s, kind="body", size=13, fill=None, anchor="middle", rotate=None):
        fam, weight = FONT_CSS[kind]
        t = ('<text x="%.1f" y="%.1f" font-family="%s" font-weight="%d" font-size="%.1f" fill="%s" text-anchor="%s"'
             % (x, y, fam, weight, size, fill or C["text"], anchor))
        if rotate:
            t += ' transform="rotate(%.1f %.1f %.1f)"' % (rotate, x, y)
        self.parts.append(t + ">" + esc(s) + "</text>")

    def lines(self, x, y_top, lines, kind, size, fill=None, anchor="middle", lh=None):
        lh = lh or size * 1.25
        y = y_top + size * 0.95
        for ln in lines:
            if ln:
                self.text(x, y, ln, kind, size, fill, anchor)
            y += lh
        return y_top + len(lines) * lh

    def line(self, x1, y1, x2, y2, stroke=None, sw=1.2, dash=None):
        d = (' stroke-dasharray="%s"' % dash) if dash else ""
        self.parts.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="%.1f"%s/>'
                          % (x1, y1, x2, y2, stroke or C["slate"], sw, d))

    def path(self, d, stroke=None, sw=1.2, dash=None, marker=False, fill="none"):
        col = stroke or C["slate"]
        a = ['<path d="%s" fill="%s" stroke="%s" stroke-width="%.1f"' % (d, fill, col, sw)]
        if dash:
            a.append(' stroke-dasharray="%s"' % dash)
        if marker:
            self.markers.add(col)
            a.append(' marker-end="url(#ah_%s)"' % col.lstrip("#"))
        a.append("/>")
        self.parts.append("".join(a))

    def arrow(self, x1, y1, x2, y2, stroke=None, sw=1.4, dash=None):
        self.path("M %.1f %.1f L %.1f %.1f" % (x1, y1, x2, y2), stroke=stroke, sw=sw, dash=dash, marker=True)

    def token(self, x, y, s, kind):
        fill, stroke, shape = TOKEN_STYLE.get(kind, TOKEN_STYLE["frame"])
        self.rect(x, y, s, s, fill=fill, stroke=stroke, sw=1.0, rx=(s / 2 if shape == "round" else 1.5))

    def loop_icon(self, cx, cy, r, color):
        a0, a1 = math.radians(40), math.radians(320)
        x0, y0 = cx + r * math.cos(a0), cy + r * math.sin(a0)
        x1, y1 = cx + r * math.cos(a1), cy + r * math.sin(a1)
        self.path("M %.1f %.1f A %.1f %.1f 0 1 1 %.1f %.1f" % (x0, y0, r, r, x1, y1), stroke=color, sw=1.8, marker=True)

    def parallel_icon(self, cx, cy, r, color):
        for i in (-1, 0, 1):
            self.arrow(cx + i * r * 0.9, cy + r, cx + i * r * 0.9, cy - r * 0.9, stroke=color, sw=1.5)

    def tree_icon(self, cx, cy, r, color):
        self.line(cx, cy - r, cx - r, cy + r * 0.3, stroke=color, sw=1.5)
        self.line(cx, cy - r, cx + r, cy + r * 0.3, stroke=color, sw=1.5)
        self.line(cx - r, cy + r * 0.3, cx - r * 1.3, cy + r, stroke=color, sw=1.5)
        self.line(cx - r, cy + r * 0.3, cx - r * 0.4, cy + r, stroke=color, sw=1.5)
        for (x, y) in ((cx, cy - r), (cx - r, cy + r * 0.3), (cx + r, cy + r * 0.3)):
            self.parts.append('<circle cx="%.1f" cy="%.1f" r="2.2" fill="%s"/>' % (x, y, color))


# ------------------------------------------------------------------ layout
class Layout:
    """Computes row heights for one diagram at width W, then draws it at (ox, oy).
    compact=True drops sub-lines, tags and notes and tightens spacing (for slides)."""

    def __init__(self, spec, width=300, compact=False):
        self.spec = spec
        self.W = width
        self.compact = compact
        self.PAD = 6 if compact else 10
        self.GAP = 10 if compact else 15
        self.MAIN = 14.0 if compact else 13.0
        self.SUB = 11.5
        self.SMALL = 11.0 if compact else 10.5
        self.LH = 1.25
        d = spec["diagram"]
        self.loop = d.get("loop")
        self.right_margin = 22 if self.loop else 0
        self.bx = self.PAD
        self.bw = width - 2 * self.PAD - self.right_margin
        self.inner = self.bw - 20
        self.rows = []
        self._measure()

    # -- helpers --------------------------------------------------------------
    def _main(self, box, key="text"):
        if self.compact and box.get("short"):
            return box["short"]
        return box.get(key, "")

    def _sub(self, box):
        return None if self.compact else box.get("sub")

    def _box_h(self, text, sub):
        n = len(wrap(text, "body", self.MAIN, self.inner))
        h = (7 if self.compact else 8) + n * self.MAIN * self.LH
        if sub:
            h += len(wrap(sub, "body", self.SUB, self.inner)) * self.SUB * self.LH + 1
        return h + 6

    def _group_w(self, g):
        n = int(g[1]) if g[1] else 0
        shown = min(n, 8) if n else 1
        return shown * 11 + (10 if n > 8 else 0)

    # -- measuring -----------------------------------------------------------
    def _measure(self):
        d = self.spec["diagram"]
        spec = self.spec
        meta = spec.get("meta") or " · ".join(str(v) for v in (spec.get("year"), spec.get("org"), spec.get("params")) if v)
        if self.compact:
            meta = " · ".join(str(v) for v in (spec.get("year"), spec.get("org")) if v)
        self.meta_lines = wrap(meta, "body", self.SUB, self.W - 2 * self.PAD)[:2]
        self.header_h = 22 + len(self.meta_lines) * self.SUB * 1.3 + (1 if self.compact else 4)
        self.rows = []
        enc = d.get("encoder")
        if enc:
            self.rows.append(("encoder", self._box_h(self._main(enc), self._sub(enc)), self._draw_encoder))
        tok = d.get("tokens")
        if tok:
            self._tok = []
            maxlw = 118
            for g in tok["groups"]:
                sq = self._group_w(g)
                label = g[2] if len(g) > 2 else ""
                lw = max(sq, min(text_width(label, "body", self.SMALL), maxlw))
                ls = wrap(label, "body", self.SMALL, lw + 4)[:2] if label else []
                self._tok.append((g, sq, lw, ls))
            nlab = max([len(t[3]) for t in self._tok] + [0])
            h = (6 if self.compact else 7) + 9 + 3 + nlab * self.SMALL * self.LH + (4 if self.compact else 6)
            if tok.get("note") and not self.compact:
                h += self.SMALL * self.LH + 2
            self.rows.append(("tokens", h, self._draw_tokens))
        core = d.get("core")
        if core:
            h = 24 + 7
            self._core_rows = []
            rs = self.SUB + 0.5 if not self.compact else self.MAIN - 1
            for row in core.get("rows", []):
                kind, txt = row[0], row[1]
                if self.compact and len(row) > 2 and row[2]:
                    txt = row[2]          # optional short text for compact mode
                if kind == "note":
                    if self.compact:
                        continue
                    ls = wrap(txt, "body", self.SMALL, self.inner - 4)
                    rh = len(ls) * self.SMALL * self.LH + 2
                else:
                    ls = wrap(txt, "body", rs, self.inner - 12)
                    rh = len(ls) * rs * self.LH + (6 if self.compact else 7)
                self._core_rows.append((kind, ls, rh))
                h += rh + (3 if self.compact else 4)
            self._core_notes = []
            if not self.compact:
                for n in core.get("notes", []):
                    ls = wrap(n, "body", self.SMALL, self.inner - 4)
                    self._core_notes.append(ls)
                    h += len(ls) * self.SMALL * self.LH + 2
            h += 3
            self.rows.append(("core", h, self._draw_core))
        samp = d.get("sampling")
        if samp:
            icon = SAMPLING_ICON.get(samp.get("kind", "regress"))
            self._samp_textw = self.inner - (28 if icon else 0)
            n = len(wrap(self._main(samp), "body", self.MAIN, self._samp_textw))
            h = 8 + n * self.MAIN * self.LH
            sub = self._sub(samp)
            if sub:
                h += len(wrap(sub, "body", self.SUB, self._samp_textw)) * self.SUB * self.LH + 1
            h = max(h + 6, 30 if self.compact else 34)
            self.rows.append(("sampling", h, self._draw_sampling))
        heads = d.get("heads")
        if heads:
            self.rows.append(("heads", 24, self._draw_heads))
        dec = d.get("decoder")
        if dec:
            if dec.get("none"):
                h = self._box_h("No pixel decoder", None if self.compact else dec.get("none"))
            else:
                h = self._box_h(self._main(dec), self._sub(dec))
            self.rows.append(("decoder", h, self._draw_decoder))
        self.H = self.PAD + self.header_h + sum(r[1] for r in self.rows) + self.GAP * (len(self.rows) - 1) + self.PAD

    # -- drawing -------------------------------------------------------------
    def draw(self, cv, ox=0, oy=0):
        self.cv, self.ox, self.oy = cv, ox, oy
        x, y = ox + self.PAD, oy + self.PAD
        spec = self.spec
        cv.text(x, y + 16, spec["name"], "head", 17, C["navy"], anchor="start")
        yy = y + 16 + self.SUB * 1.3
        for ml in self.meta_lines:
            cv.text(x, yy, ml, "body", self.SUB, C["grey"], anchor="start")
            yy += self.SUB * 1.3
        ycur = oy + self.H - self.PAD
        self.row_pos = {}
        for name, h, fn in self.rows:
            top = ycur - h
            self.row_pos[name] = (top, h)
            fn(top, h)
            ycur = top - self.GAP
        names = [r[0] for r in self.rows]
        cx = ox + self.PAD + self.bw / 2
        for a, b in zip(names, names[1:]):
            top_a, h_a = self.row_pos[a]
            top_b, h_b = self.row_pos[b]
            cv.arrow(cx, top_a - 1, cx, top_b + h_b + 1.5, stroke=C["slate"], sw=1.4)
        if self.loop and "tokens" in self.row_pos and ("sampling" in self.row_pos or "decoder" in self.row_pos):
            dec = self.spec["diagram"].get("decoder") or {}
            src = "decoder" if ("decoder" in self.row_pos and not dec.get("none")) else "sampling"
            top_s, h_s = self.row_pos[src]
            top_t, h_t = self.row_pos["tokens"]
            xr = ox + self.PAD + self.bw
            xl = ox + self.W - self.PAD - 4
            ys = top_s + h_s / 2
            yt = top_t + h_t / 2
            cv.path("M %.1f %.1f L %.1f %.1f L %.1f %.1f L %.1f %.1f" % (xr, ys, xl, ys, xl, yt, xr + 2, yt),
                    stroke=C["orange"], sw=1.3, dash="4 3", marker=True)
            cv.text(xl - 4, (ys + yt) / 2, self.loop, "body", self.SMALL, C["orange"], anchor="middle", rotate=-90)

    def _box(self, top, h, text, sub, fill, stroke, tag=None, dash=None):
        cv = self.cv
        x = self.ox + self.bx
        cv.rect(x, top, self.bw, h, fill=fill, stroke=stroke, sw=1.2, dash=dash)
        ls = wrap(text, "body", self.MAIN, self.inner)
        subl = wrap(sub, "body", self.SUB, self.inner) if sub else []
        th = len(ls) * self.MAIN * self.LH + (len(subl) * self.SUB * self.LH + 1 if subl else 0)
        y = top + (h - th) / 2
        y = cv.lines(x + self.bw / 2, y, ls, "body", self.MAIN, C["text"])
        if subl:
            cv.lines(x + self.bw / 2, y + 1, subl, "body", self.SUB, C["grey"])
        if tag and not self.compact:
            tw = text_width(tag, "body", 9.5) + 8
            cv.rect(x + self.bw - tw - 4, top - 7, tw, 13, fill=C["white"], stroke=C["slate"], sw=0.8, rx=6.5)
            cv.text(x + self.bw - tw / 2 - 4, top + 2.6, tag, "body", 9.5, C["grey"])

    def _draw_encoder(self, top, h):
        e = self.spec["diagram"]["encoder"]
        self._box(top, h, self._main(e), self._sub(e), C["teal_t"], C["teal"], e.get("tag"))

    def _draw_decoder(self, top, h):
        e = self.spec["diagram"]["decoder"]
        if e.get("none"):
            self._box(top, h, "No pixel decoder", None if self.compact else e["none"], C["white"], C["slate"],
                      e.get("tag"), dash="4 3")
        else:
            self._box(top, h, self._main(e), self._sub(e), C["teal_t"], C["teal"], e.get("tag"))

    def _draw_tokens(self, top, h):
        cv, t = self.cv, self.spec["diagram"]["tokens"]
        x0 = self.ox + self.bx
        cv.rect(x0, top, self.bw, h, fill=C["white"], stroke=C["line"], sw=1.0)
        gap = 10
        total = sum(lw for _, _, lw, _ in self._tok) + gap * (len(self._tok) - 1)
        if total > self.bw - 8:
            cv.warnings.append("%s: token row too wide (%.0f > %.0f); shorten labels or drop a group"
                               % (self.spec["slug"], total, self.bw - 8))
        x = x0 + (self.bw - total) / 2
        ys = top + 7
        s = 9
        for g, sq, lw, ls in self._tok:
            kind, n = g[0], int(g[1]) if g[1] else 0
            shown = min(n, 8) if n else 1
            gx = x + (lw - sq) / 2
            for i in range(shown):
                cv.token(gx + i * 11, ys, s, kind)
            if n > 8:
                cv.text(gx + shown * 11 + 4, ys + 8, "…", "body", 11, C["grey"], anchor="middle")
            if ls:
                cv.lines(x + lw / 2, ys + s + 3, ls, "body", self.SMALL, C["grey"])
            x += lw + gap
        if t.get("note") and not self.compact:
            cv.text(x0 + self.bw / 2, top + h - 5, t["note"], "body", self.SMALL, C["grey"])

    def _draw_core(self, top, h):
        cv, core = self.cv, self.spec["diagram"]["core"]
        x = self.ox + self.bx
        cv.rect(x, top, self.bw, h, fill=C["white"], stroke=C["navy"], sw=1.6, rx=6)
        cv.rect(x, top, self.bw, 24, fill=C["navy"], stroke=None, rx=6)
        cv.rect(x, top + 12, self.bw, 12, fill=C["navy"], stroke=None, rx=0)
        title = core.get("title", "Transformer")
        ts = 13.5 if self.compact else 13.0
        while text_width(title, "head", ts) > self.bw - 12 and ts > 10:
            ts -= 0.5
        cv.text(x + self.bw / 2, top + 16.5, title, "head", ts, C["white"])
        y = top + 24 + 5
        rs = self.SUB + 0.5 if not self.compact else self.MAIN - 1
        for kind, ls, rh in self._core_rows:
            fill, stroke = ROW_STYLE.get(kind, ROW_STYLE["mlp"])
            if kind == "note":
                cv.lines(x + self.bw / 2, y + 1, ls, "body", self.SMALL, C["grey"])
            else:
                cv.rect(x + 6, y, self.bw - 12, rh, fill=fill, stroke=stroke, sw=1.0, rx=4)
                cv.lines(x + self.bw / 2, y + (2 if self.compact else 2.5), ls, "body", rs, C["text"])
            y += rh + (3 if self.compact else 4)
        for ls in self._core_notes:
            cv.lines(x + self.bw / 2, y + 1, ls, "body", self.SMALL, C["grey"])
            y += len(ls) * self.SMALL * self.LH + 2

    def _draw_sampling(self, top, h):
        cv, s = self.cv, self.spec["diagram"]["sampling"]
        x = self.ox + self.bx
        icon = SAMPLING_ICON.get(s.get("kind", "regress"))
        cv.rect(x, top, self.bw, h, fill=C["soft"], stroke=C["slate"], sw=1.0)
        tx = x + (28 if icon else 0) + self._samp_textw / 2 + 10
        ls = wrap(self._main(s), "body", self.MAIN, self._samp_textw)
        sub = self._sub(s)
        subl = wrap(sub, "body", self.SUB, self._samp_textw) if sub else []
        th = len(ls) * self.MAIN * self.LH + (len(subl) * self.SUB * self.LH + 1 if subl else 0)
        y = top + (h - th) / 2
        y = cv.lines(tx, y, ls, "body", self.MAIN, C["text"])
        if subl:
            cv.lines(tx, y + 1, subl, "body", self.SUB, C["grey"])
        if icon:
            cx, cy = x + 19, top + h / 2
            col = C["orange"]
            if icon == "loop":
                cv.loop_icon(cx, cy, 8, col)
            elif icon == "parallel":
                cv.parallel_icon(cx, cy, 7, col)
            elif icon == "tree":
                cv.tree_icon(cx, cy, 7, col)

    def _draw_heads(self, top, h):
        cv, heads = self.cv, self.spec["diagram"]["heads"]
        x0 = self.ox + self.bx
        ws = [text_width(t, "body", self.SUB) + 14 for t in heads]
        gap = 6
        total = sum(ws) + gap * (len(heads) - 1)
        if total > self.bw:
            cv.warnings.append("%s: heads row too wide" % self.spec["slug"])
        x = x0 + (self.bw - total) / 2
        for t, w in zip(heads, ws):
            cv.rect(x, top + 1, w, h - 2, fill=C["gold_t"], stroke=C["gold"], sw=1.0, rx=(h - 2) / 2)
            cv.text(x + w / 2, top + h / 2 + 4, t, "body", self.SUB, C["ink"])
            x += w + gap


# ------------------------------------------------------------------ public API
FONT_IMPORT = ('<style>@import url("https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;700'
               '&amp;family=Saira+Semi+Condensed:wght@500;600&amp;display=swap");</style>\n')


def svg_head(w, h, markers, fonts=True):
    defs = "".join('<marker id="ah_%s" markerWidth="7" markerHeight="7" refX="5.5" refY="3.5" orient="auto" '
                   'markerUnits="userSpaceOnUse"><path d="M0,0 L7,3.5 L0,7 z" fill="%s"/></marker>'
                   % (c.lstrip("#"), c) for c in sorted(markers))
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d" '
            'font-family="IBM Plex Sans">\n' % (w, h, w, h)) + (FONT_IMPORT if fonts else "") + "<defs>" + defs + "</defs>\n"


def render_svg(spec, width=300, background=True, compact=False, fonts=True):
    lay = Layout(spec, width, compact)
    cv = Canvas()
    if background:
        cv.rect(0, 0, width, math.ceil(lay.H) + 1, fill=C["white"], rx=0)
    lay.draw(cv, 0, 0)
    svg = svg_head(width, math.ceil(lay.H), cv.markers, fonts) + "\n".join(cv.parts) + "\n</svg>\n"
    return svg, cv.warnings, (width, lay.H)


def compose_row(specs, width=300, gap=24, background=True, align="top", compact=False, fonts=True):
    """Several diagrams side by side (for slides or comparison views)."""
    lays = [Layout(s, width, compact) for s in specs]
    H = max(l.H for l in lays)
    Wt = width * len(lays) + gap * (len(lays) - 1)
    cv = Canvas()
    if background:
        cv.rect(0, 0, Wt, math.ceil(H) + 1, fill=C["white"], rx=0)
    x = 0
    for l in lays:
        oy = 0 if align == "top" else H - l.H
        l.draw(cv, x, oy)
        x += width + gap
    svg = svg_head(Wt, math.ceil(H), cv.markers, fonts) + "\n".join(cv.parts) + "\n</svg>\n"
    return svg, cv.warnings, (Wt, H)


def draw_legend(cv, ox=0, oy=0, width=600):
    """Draw the legend (token colours, core rows, boxes) into cv at (ox, oy); returns the height used."""
    y = oy + 10
    X0 = ox + 12
    cv.text(ox + 10, y + 14, "Token squares (one step of the sequence)", "head", 14, C["navy"], anchor="start")
    y += 24
    x = X0
    for kind, label in TOKEN_LEGEND:
        w = 14 + text_width(label, "body", 11.5) + 14
        if x + w > ox + width - 10:
            x = X0
            y += 20
        cv.token(x, y + 2, 10, kind)
        cv.text(x + 15, y + 11, label, "body", 11.5, C["text"], anchor="start")
        x += w
    y += 30
    cv.text(ox + 10, y + 14, "Rows inside the transformer box", "head", 14, C["navy"], anchor="start")
    y += 24
    x = X0
    for kind, label in ROW_LEGEND:
        fill, stroke = ROW_STYLE[kind]
        w = text_width(label, "body", 11.5) + 22
        if x + w > ox + width - 10:
            x = X0
            y += 24
        cv.rect(x, y, w, 18, fill=fill, stroke=stroke or C["line"], sw=1.0, rx=4)
        cv.text(x + w / 2, y + 13, label, "body", 11.5, C["text"])
        x += w + 8
    y += 30
    cv.text(ox + 10, y + 14, "Boxes", "head", 14, C["navy"], anchor="start")
    y += 24
    items = [(C["teal_t"], C["teal"], "encoder / decoder"), (C["white"], C["navy"], "transformer core"),
             (C["soft"], C["slate"], "prediction and sampling"), (C["gold_t"], C["gold"], "heads")]
    x = X0
    for fill, stroke, label in items:
        w = text_width(label, "body", 11.5) + 22
        if x + w > ox + width - 10:
            x = X0
            y += 24
        cv.rect(x, y, w, 18, fill=fill, stroke=stroke, sw=1.2, rx=4)
        cv.text(x + w / 2, y + 13, label, "body", 11.5, C["text"])
        x += w + 8
    y += 26
    x = X0
    cv.loop_icon(x + 10, y + 9, 7, C["orange"])
    cv.text(x + 22, y + 13, "iterative sampling", "body", 11.5, C["text"], anchor="start")
    x += 22 + text_width("iterative sampling", "body", 11.5) + 14
    cv.path("M %.1f %.1f L %.1f %.1f" % (x, y + 9, x + 24, y + 9), stroke=C["orange"], sw=1.3, dash="4 3", marker=True)
    cv.text(x + 30, y + 13, "autoregressive feedback", "body", 11.5, C["text"], anchor="start")
    y += 26
    return y - oy + 4


def legend_svg(width=600):
    """A standalone legend card."""
    cv = Canvas()
    H = draw_legend(cv, 0, 0, width)
    svg = svg_head(width, H, cv.markers) + '<rect x="0" y="0" width="%d" height="%d" fill="#fff"/>\n' % (width, H)
    svg += "\n".join(cv.parts) + "\n</svg>\n"
    return svg


def svg_to_png(svg, out_path, scale=3.0):
    import cairosvg
    import re
    svg2 = svg.replace(FONT_IMPORT, "")   # local fonts via fontconfig; no network import for the rasteriser
    w = float(re.search(r'width="(\d+)"', svg2).group(1))
    cairosvg.svg2png(bytestring=svg2.encode("utf-8"), write_to=out_path, output_width=int(w * scale))
    return out_path


def write_outputs(spec, out_dir, width=300, png=True, scale=3.0, compact=False):
    svg, warns, size = render_svg(spec, width, compact=compact)
    sub = "compact" if compact else ""
    os.makedirs(os.path.join(out_dir, "svg", sub), exist_ok=True)
    p = os.path.join(out_dir, "svg", sub, spec["slug"] + ".svg")
    with open(p, "w") as f:
        f.write(svg)
    if png:
        os.makedirs(os.path.join(out_dir, "png", sub), exist_ok=True)
        svg_to_png(svg, os.path.join(out_dir, "png", sub, spec["slug"] + ".png"), scale)
    return p, warns, size
