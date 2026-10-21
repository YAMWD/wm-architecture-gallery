"""Stack diagrams: a Raschka-style architecture figure read from the bottom up.

The spec (MODEL["flow"]) describes the data path as nested stacks of small boxes. Everything flows
upward; numbers live in annotations outside the model, not inside the boxes.

    "flow": {
      "below": [{"text": "Game frame 64×64"}],                               # drawn under the model container
      "stack": [                                                            # inside the container, bottom -> top
        {"box": "VQ-VAE encoder", "id": "enc", "style": "teal"},
        {"box": "Token embedding", "id": "emb", "minor": True},
        {"group": [                                                        # tinted container with N× marker
            {"residual": [{"box": "LayerNorm", "minor": True},
                          {"box": "Masked self-attention", "id": "attn", "style": "dark", "side": "Learned positions"}]},
            {"residual": [{"box": "LayerNorm", "minor": True}, {"box": "Feed forward", "id": "ffn"}]},
         ], "repeat": "10 ×", "id": "block"},
        {"box": "Linear output layer", "id": "out"},
        {"fanout": [[{"box": "Next code"}], [{"box": "Reward head"}], [{"box": "Done head"}]]},
      ],
      "above": [{"box": "VQ-VAE decoder", "style": "teal"}, {"text": "Next frame"}],
      "insets": [{"for": "ffn", "stack": [{"box": "Linear"}, {"box": "GELU"}, {"box": "Linear"}]}],
      "annotations": [{"at": "enc", "text": "*16* codes per frame, vocabulary *512*", "side": "left", "key": True},
                      {"at": "attn", "text": "*4* heads · context *20* steps = *340* tokens"}],
      "feedback": "next step",                                               # optional dashed loop, top -> bottom
    }

Node kinds: box (label; id; style = plain|dark|teal|orange|soft; side = label of a side-input box; minor = dropped
in condensed mode; short = label used in condensed mode; w = fixed width), text (unboxed, monospace), group (children; repeat "N ×"; loop "4 steps";
tint navy|orange|teal|grey; label; id), residual (children; draws the ⊕ merge and the skip line), fanout (list
of branches, each a stack; a branch whose top node has "terminal": True ends there), merge ("x" or "+", a circled
operator joining the branches below it), gap (n). Annotation text: *…* marks numbers (accent colour); "key": True keeps the
annotation in condensed mode (otherwise the first three are kept). Condensed mode (slides) also drops minor
nodes, residual wrappers and insets.
"""
import math
from . import diagram as D
from .diagram import Canvas, text_width, wrap, esc, C

ACCENT = "#B95A08"
INK = "#1E2A3B"
BOX_STYLE = {
    "plain": (C["white"], INK, INK),
    "dark": (C["navy"], C["navy"], C["white"]),
    "teal": (C["teal_t"], C["teal"], INK),
    "orange": (C["orange_t"], C["orange"], INK),
    "soft": (C["soft"], C["slate"], INK),
}
GROUP_STYLE = {"navy": (C["navy_t"], C["navy"]), "orange": (C["orange_t"], C["orange"]),
               "teal": (C["teal_t"], C["teal"]), "grey": (C["slate_t"], C["slate"])}


class P:
    """Layout parameters for one mode."""
    def __init__(self, condensed):
        self.condensed = condensed
        self.box = 14.0 if condensed else 11.0        # box text size
        self.ann = 12.5 if condensed else 11.0        # annotation text size
        self.mono = 12.0 if condensed else 10.5
        self.gap = 14 if condensed else 16            # arrow length between nodes
        self.pad = 8 if condensed else 12             # group padding
        self.cont_pad = 12 if condensed else 18
        self.title_h = 34 if condensed else 46
        self.minw = 84 if condensed else 72
        self.maxw = 170 if condensed else 150
        self.ann_w = 140 if condensed else 130        # annotation text width
        self.margin = 28                              # container -> annotation gap
        self.side_gap = 14                            # side box -> node arrow length


class Node:
    def __init__(self, spec):
        self.spec = spec
        self.kind = next(k for k in ("box", "text", "group", "residual", "fanout", "merge", "gap") if k in spec)
        self.id = spec.get("id")
        self.children = []
        self.x = self.y = self.w = self.h = 0.0      # top-left and size of the node's own extent
        self.cx = 0.0
        self.lines = []
        self.side = None                              # (label, w, h, x) of the side-input box
        self.group_left = None                        # x of the enclosing group's left border
        self.row = None                               # (left, right) extent of the row (fanouts)
        if self.kind in ("group", "residual"):
            self.children = [Node(s) for s in spec[self.kind]]
        elif self.kind == "fanout":
            self.children = [[Node(s) for s in br] for br in spec["fanout"]]

    def label(self, condensed=False):
        if self.kind not in ("box", "text"):
            return ""
        if condensed and self.spec.get("short"):
            return self.spec["short"]
        return self.spec.get(self.kind, "")


def _flatten(nodes, out):
    for n in nodes:
        out.append(n)
        if n.kind == "fanout":
            for br in n.children:
                _flatten(br, out)
        else:
            _flatten(n.children, out)
    return out


def condense(nodes):
    """Drop minor nodes, unwrap residuals (keep their inner boxes), keep groups."""
    out = []
    for n in nodes:
        if n.spec.get("minor"):
            continue
        if n.kind == "residual":
            out.extend(condense(n.children))
        elif n.kind == "group":
            n.children = condense(n.children)
            if n.children:
                out.append(n)
        elif n.kind == "fanout":
            n.children = [condense(br) for br in n.children]
            n.children = [br for br in n.children if br]
            if len(n.children) == 1:
                out.extend(n.children[0])        # a single surviving branch becomes part of the main path
            elif n.children:
                out.append(n)
        else:
            out.append(n)
    return out


def parse_markup(raw):
    """'*16* codes per *512*-way' -> words, each a list of (run, accent)."""
    words = [[]]
    for i, seg in enumerate(raw.split("*")):
        acc = i % 2 == 1
        parts = seg.split(" ")
        for j, part in enumerate(parts):
            if j > 0:
                words.append([])
            if part:
                words[-1].append((part, acc))
    return [w for w in words if w]


class StackLayout:
    def __init__(self, spec, condensed=False):
        self.spec = spec
        self.flow = spec["flow"]
        self.p = P(condensed)
        self.condensed = condensed
        self.warnings = []
        self.below = [Node(s) for s in self.flow.get("below", [])]
        self.stack = [Node(s) for s in self.flow.get("stack", [])]
        self.above = [Node(s) for s in self.flow.get("above", [])]
        if condensed:
            self.below, self.stack, self.above = condense(self.below), condense(self.stack), condense(self.above)
        self.insets = [] if condensed else self.flow.get("insets", [])
        anns = self.flow.get("annotations", [])
        if condensed:
            keyed = [a for a in anns if a.get("key")]
            anns = [dict(a, side="right") for a in (keyed or anns[:3])]   # one column keeps the slide figure narrow
        self.annotations = anns
        self.by_id = {}
        for n in _flatten(self.below + self.stack + self.above, []):
            if n.id:
                self.by_id[n.id] = n
        self.measure_all()

    # ---------------------------------------------------------------- measuring
    def _box_size(self, n):
        p = self.p
        label = n.label(self.condensed)
        if n.kind == "text":
            n.lines = wrap(label, "mono", p.mono, 280)
            n.w = max(text_width(l, "mono", p.mono) for l in n.lines) + 6
            n.h = len(n.lines) * p.mono * 1.3
            return
        fixed = n.spec.get("w")
        tw = text_width(label, "body", p.box)
        w = fixed or max(p.minw, min(p.maxw, tw + 18))
        n.lines = wrap(label, "body", p.box, w - 12)
        if len(n.lines) > 2:
            self.warnings.append("%s: box text too long for two lines: %r" % (self.spec["slug"], label))
            n.lines = n.lines[:2]
        n.w = w if fixed else max(p.minw, min(p.maxw, max(text_width(l, "body", p.box) for l in n.lines) + 18))
        n.h = len(n.lines) * p.box * 1.3 + 9
        if n.spec.get("side"):
            s = n.spec["side"]
            sw = max(56, text_width(s, "body", p.box - 1) + 14)
            n.side = [s, sw, p.box * 1.3 + 8, 0.0]

    def _measure(self, n):
        p = self.p
        if n.kind == "gap":
            n.w, n.h = 0, float(n.spec["gap"])
        elif n.kind == "merge":
            n.w, n.h = 18, 18
        elif n.kind in ("box", "text"):
            self._box_size(n)
        elif n.kind == "residual":
            for c in n.children:
                self._measure(c)
            inner_w = max(c.w for c in n.children)
            n.w = inner_w + 2 * 22                        # room for the skip line on the right (kept symmetric)
            n.h = sum(c.h for c in n.children) + p.gap * (len(n.children) - 1) + p.gap + 16
        elif n.kind == "group":
            for c in n.children:
                self._measure(c)
            inner_w = max(c.w for c in n.children)
            n.w = inner_w + 2 * p.pad
            n.h = sum(c.h for c in n.children) + p.gap * (len(n.children) - 1) + 2 * (p.pad + 2)
        elif n.kind == "fanout":
            widths, heights = [], []
            for br in n.children:
                for c in br:
                    self._measure(c)
                widths.append(max(c.w for c in br))
                heights.append(sum(c.h for c in br) + p.gap * (len(br) - 1))
            n.branch_w = widths
            n.w = sum(widths) + 14 * (len(widths) - 1)
            n.h = max(heights) + p.gap        # extra gap below the branches for the diagonal arrows
        return n

    def _stack_size(self, nodes):
        if not nodes:
            return 0.0, 0.0
        for n in nodes:
            self._measure(n)
        w = max(n.w for n in nodes)
        h = sum(n.h for n in nodes) + self.p.gap * (len(nodes) - 1)
        return w, h

    def _ann_lines(self, raw):
        """Wrap marked-up annotation text into lines of words (each word = runs of (text, accent))."""
        p = self.p
        words = parse_markup(raw)
        space = text_width(" ", "body", p.ann)
        lines, cur, cur_w = [], [], 0.0
        for w in words:
            ww = sum(text_width(t, "bold" if acc else "body", p.ann) for t, acc in w)
            add = ww + (space if cur else 0)
            if cur and cur_w + add > p.ann_w:
                lines.append((cur, cur_w))
                cur, cur_w = [w], ww
            else:
                cur.append(w)
                cur_w += add
        if cur:
            lines.append((cur, cur_w))
        return lines

    def measure_all(self):
        p = self.p
        self.col_w, self.stack_h = self._stack_size(self.stack)
        self.below_w, self.below_h = self._stack_size(self.below)
        self.above_w, self.above_h = self._stack_size(self.above)
        # provisional placement at cx = 0 to learn the horizontal extents (side boxes, repeat labels)
        self._place_stack(self.stack, 0.0, 0.0)
        xs = self._extents(self.stack)
        self.ext_left, self.ext_right = xs
        self.cont_pad = p.cont_pad
        self.cont_w = (self.ext_right - self.ext_left) + 2 * self.cont_pad
        self.cont_h = self.stack_h + 2 * self.cont_pad
        # insets
        self.inset_layouts = []
        for ins in self.insets:
            nodes = [Node(s) for s in ins["stack"]]
            w, h = self._stack_size(nodes)
            self.inset_layouts.append({"spec": ins, "nodes": nodes, "w": w + 2 * 14, "h": h + 2 * 14})
        # annotation text blocks
        self.ann_layouts = []
        for a in self.annotations:
            lines = self._ann_lines(a["text"])
            self.ann_layouts.append({"spec": a, "lines": lines, "h": len(lines) * p.ann * 1.3,
                                     "w": max(lw for _, lw in lines), "side": a.get("side", "right")})
        left_items = [a for a in self.ann_layouts if a["side"] == "left"]
        right_items = [a for a in self.ann_layouts if a["side"] == "right"]
        self.left_w = (max(a["w"] for a in left_items) + p.margin) if left_items else 0
        right_need = (max(a["w"] for a in right_items) + p.margin) if right_items else 0
        if self.inset_layouts:
            right_need = max(right_need, max(i["w"] for i in self.inset_layouts) + p.margin)
        self.right_w = right_need
        self.fb_w = 34 if (self.flow.get("feedback") and not self.condensed) else 0
        self.title_h = p.title_h
        # the column may be wider than the container when below/above stacks are wider
        extra = max(0, max(self.below_w, self.above_w) - self.cont_w)
        self.W = 10 + self.left_w + self.cont_w + extra + self.right_w + self.fb_w + 10
        self.H = (self.title_h + self.above_h + (p.gap if self.above else 0) + self.cont_h
                  + (p.gap if self.below else 0) + self.below_h + 12)

    def _extents(self, nodes):
        lo, hi = 1e9, -1e9
        for n in _flatten(nodes, []):
            if n.kind == "gap":
                continue
            lo = min(lo, n.x)
            hi = max(hi, n.x + n.w)
            if n.side:
                lo = min(lo, n.side[3])
            if n.kind == "group" and n.spec.get("repeat"):
                lo = min(lo, n.x - 12 - text_width(n.spec["repeat"], "headm", 12.5))
            if n.kind == "group" and n.spec.get("loop"):
                hi = max(hi, n.x + n.w + 10 + 22)
        return lo, hi

    # ---------------------------------------------------------------- placing
    def _place_stack(self, nodes, cx, y_bottom, group_left=None):
        y = y_bottom
        for n in nodes:
            self._place(n, cx, y, group_left)
            y = n.y - self.p.gap
        return y

    def _place(self, n, cx, y_bottom, group_left=None):
        p = self.p
        n.cx = cx
        n.y = y_bottom - n.h
        n.x = cx - n.w / 2
        n.group_left = group_left
        n.row = (n.x, n.x + n.w)
        if n.kind == "box" and n.side:
            sx = n.x - p.side_gap - n.side[1]
            if group_left is not None:
                sx = min(sx, group_left - 10 - n.side[1])
            n.side[3] = sx
            n.row = (sx, n.x + n.w)
        if n.kind == "residual":
            self._place_stack(n.children, cx, y_bottom, group_left)
        elif n.kind == "group":
            self._place_stack(n.children, cx, y_bottom - p.pad - 2, n.x)
        elif n.kind == "fanout":
            x = cx - n.w / 2
            for br, bw in zip(n.children, n.branch_w):
                self._place_stack(br, x + bw / 2, y_bottom - p.gap, group_left)
                x += bw + 14
            for c in _flatten([c for br in n.children for c in br], []):
                c.row = (n.x, n.x + n.w)

    def place_all(self):
        p = self.p
        self.cont_x = 10 + self.left_w
        self.cont_y = self.title_h + self.above_h + (p.gap if self.above else 0)
        cx = self.cont_x + self.cont_pad - self.ext_left
        self.cx = cx
        y = self.cont_y + self.cont_h - self.cont_pad
        self._place_stack(self.stack, cx, y)
        if self.below:
            self._place_stack(self.below, cx, self.cont_y + self.cont_h + p.gap + self.below_h)
        if self.above:
            self._place_stack(self.above, cx, self.cont_y - p.gap)

    # ---------------------------------------------------------------- drawing
    def draw(self, cv, ox=0, oy=0):
        p = self.p
        self.cv = cv
        self.place_all()
        self.ox, self.oy = ox, oy
        cv.warnings.extend(self.warnings)
        spec = self.spec
        if self.condensed:
            cv.text(ox + self.cx, oy + 18, spec["name"], "head", 17, C["navy"])
            sub = " · ".join(str(v) for v in (spec.get("org"), spec.get("year")) if v)
            cv.text(ox + self.cx, oy + 31, sub, "body", 10, C["grey"])
        else:
            cv.text(ox + self.cx, oy + 22, spec["name"], "head", 18, C["navy"])
            sub = " · ".join(str(v) for v in (spec.get("org"), spec.get("year"), spec.get("params")) if v)
            cv.text(ox + self.cx, oy + 38, sub, "body", 10.5, C["grey"])
        cv.rect(ox + self.cont_x, oy + self.cont_y, self.cont_w, self.cont_h, fill=C["soft"], stroke=C["slate"], sw=1.0, rx=20)
        self._draw_stack(self.stack)
        if self.below:
            self._draw_stack(self.below)
            self._connect(self.below[-1], self.stack[0])
        if self.above:
            self._draw_stack(self.above)
            self._connect(self.stack[-1], self.above[0])
        else:
            t = self.stack[-1]
            src = self._top_point(t)
            cv.arrow(src[0], src[1], src[0], oy + self.cont_y - 12, stroke=INK, sw=1.2)
        self._draw_right_column()
        self._draw_left_annotations()
        if self.flow.get("feedback") and not self.condensed:
            self._draw_feedback()

    def _top_point(self, n):
        """Where an arrow leaving `n` upward starts."""
        if n.kind == "fanout":
            return None
        return (self.ox + n.cx, self.oy + n.y - 1)

    def _bottom_point(self, n):
        return (self.ox + n.cx, self.oy + n.y + n.h + 1)

    def _connect(self, lower, upper):
        """Arrow(s) from the top of `lower` to the bottom of `upper`, handling fanouts on either side."""
        cv = self.cv
        if upper.kind == "fanout":
            src = self._top_point(lower)
            for br in upper.children:
                dst = self._bottom_point(br[0])
                cv.arrow(src[0], src[1], dst[0], dst[1], stroke=INK, sw=1.2)
            return
        dst = self._bottom_point(upper)
        if lower.kind == "fanout":
            for br in lower.children:
                if br[-1].spec.get("terminal"):
                    continue
                src = self._top_point(br[-1])
                cv.arrow(src[0], src[1], dst[0], dst[1], stroke=INK, sw=1.2)
            return
        src = self._top_point(lower)
        cv.arrow(src[0], src[1], dst[0], dst[1], stroke=INK, sw=1.2)

    def _draw_stack(self, nodes):
        for i, n in enumerate(nodes):
            self._draw_node(n)
            if i + 1 < len(nodes):
                self._connect(n, nodes[i + 1])

    def _draw_node(self, n):
        cv, p = self.cv, self.p
        ox, oy = self.ox, self.oy
        if n.kind == "gap":
            return
        if n.kind == "merge":
            cx, cy = ox + n.cx, oy + n.y + 9
            cv.parts.append('<circle cx="%.1f" cy="%.1f" r="8" fill="%s" stroke="%s" stroke-width="1.1"/>' % (cx, cy, C["white"], INK))
            sym = n.spec["merge"]
            if sym in ("x", "×", "⊗"):
                cv.line(cx - 3.5, cy - 3.5, cx + 3.5, cy + 3.5, stroke=INK, sw=1.3)
                cv.line(cx - 3.5, cy + 3.5, cx + 3.5, cy - 3.5, stroke=INK, sw=1.3)
            elif sym in ("+", "⊕"):
                cv.line(cx - 4, cy, cx + 4, cy, stroke=INK, sw=1.3)
                cv.line(cx, cy - 4, cx, cy + 4, stroke=INK, sw=1.3)
            else:
                cv.text(cx, cy + 4, sym, "body", 11, INK)
            return
        if n.kind == "text":
            y = oy + n.y + p.mono * 0.95
            for l in n.lines:
                cv.text(ox + n.cx, y, l, "mono", p.mono, INK)
                y += p.mono * 1.3
            return
        if n.kind == "box":
            fill, stroke, color = BOX_STYLE.get(n.spec.get("style", "plain"), BOX_STYLE["plain"])
            cv.rect(ox + n.x, oy + n.y, n.w, n.h, fill=fill, stroke=stroke, sw=1.0, rx=6)
            th = len(n.lines) * p.box * 1.3
            cv.lines(ox + n.cx, oy + n.y + (n.h - th) / 2, n.lines, "body", p.box, color)
            if n.side:
                s, sw, sh, sx = n.side
                sy = oy + n.y + (n.h - sh) / 2
                cv.rect(ox + sx, sy, sw, sh, fill=C["white"], stroke=INK, sw=1.0, rx=6)
                cv.text(ox + sx + sw / 2, sy + sh / 2 + (p.box - 1) * 0.35, s, "body", p.box - 1, INK)
                cv.arrow(ox + sx + sw + 1, sy + sh / 2, ox + n.x - 1, sy + sh / 2, stroke=INK, sw=1.1)
            return
        if n.kind == "group":
            fill, stroke = GROUP_STYLE.get(n.spec.get("tint", "navy"), GROUP_STYLE["navy"])
            cv.rect(ox + n.x, oy + n.y, n.w, n.h, fill=fill, stroke=stroke, sw=1.0, rx=14)
            if n.spec.get("label"):
                cv.text(ox + n.x + 8, oy + n.y + 12, n.spec["label"], "body", p.box - 1, C["grey"], anchor="start")
            self._draw_stack(n.children)
            if n.spec.get("repeat"):
                by = oy + n.y + n.h - 14
                # avoid a side box that sits at the same height on the left border
                for c in _flatten(n.children, []):
                    if c.side and (oy + c.y - 12) < by < (oy + c.y + c.h + 12):
                        by = oy + n.y + 16
                        break
                bx = ox + n.x
                cv.rect(bx - 4, by - 9, 8, 18, fill=fill, stroke=None, rx=0)
                cv.path("M %.1f %.1f l 5 -6 l -8 -4 l 5 -6" % (bx - 1, by + 8), stroke=INK, sw=1.4, fill="none")
                cv.text(bx - 10, by + 2, n.spec["repeat"], "headm", 12.5, ACCENT, anchor="end")
            if n.spec.get("loop"):
                x = ox + n.x + n.w + 10
                cv.path("M %.1f %.1f L %.1f %.1f L %.1f %.1f L %.1f %.1f" % (
                    ox + n.x + n.w, oy + n.y + 14, x, oy + n.y + 14, x, oy + n.y + n.h - 14, ox + n.x + n.w + 2, oy + n.y + n.h - 14),
                    stroke=ACCENT, sw=1.2, dash="4 3", marker=True)
                cv.text(x + 14, oy + n.y + n.h / 2, n.spec["loop"], "body", p.ann - 0.5, ACCENT, anchor="middle", rotate=-90)
            return
        if n.kind == "residual":
            self._draw_stack(n.children)
            top, bottom = n.children[-1], n.children[0]
            cx = ox + n.cx
            cy = oy + n.y + 8
            cv.arrow(cx, oy + top.y - 1, cx, cy + 9, stroke=INK, sw=1.2)
            cv.parts.append('<circle cx="%.1f" cy="%.1f" r="7.5" fill="%s" stroke="%s" stroke-width="1.1"/>' % (cx, cy, C["white"], INK))
            cv.line(cx - 4, cy, cx + 4, cy, stroke=INK, sw=1.2)
            cv.line(cx, cy - 4, cx, cy + 4, stroke=INK, sw=1.2)
            xr = ox + n.x + n.w - 6
            y0 = oy + bottom.y + bottom.h + p.gap * 0.55
            cv.parts.append('<circle cx="%.1f" cy="%.1f" r="2" fill="%s"/>' % (cx, y0, INK))
            cv.path("M %.1f %.1f L %.1f %.1f L %.1f %.1f L %.1f %.1f" % (cx, y0, xr, y0, xr, cy, cx + 9, cy),
                    stroke=INK, sw=1.1, marker=True)
            return
        if n.kind == "fanout":
            for br in n.children:
                self._draw_stack(br)

    def _anchor(self, n, side):
        """Point on the row's outer edge for a leader line (never through a sibling box)."""
        left, right = n.row if n.row else (n.x, n.x + n.w)
        x = self.ox + (left if side == "left" else right)
        return x, self.oy + n.y + n.h / 2

    def _resolve(self, items, ymin, ymax):
        """Push overlapping items apart (1-D), keeping them inside [ymin, ymax]."""
        items.sort(key=lambda i: i["yc"])
        gap = 8
        for k in range(1, len(items)):
            prev, cur = items[k - 1], items[k]
            need = prev["yc"] + prev["h"] / 2 + gap + cur["h"] / 2
            if cur["yc"] < need:
                cur["yc"] = need
        for k in range(len(items) - 1, -1, -1):
            it = items[k]
            if it["yc"] + it["h"] / 2 > ymax:
                it["yc"] = ymax - it["h"] / 2
            if k + 1 < len(items):
                nxt = items[k + 1]
                lim = nxt["yc"] - nxt["h"] / 2 - gap - it["h"] / 2
                if it["yc"] > lim:
                    it["yc"] = lim
        for it in items:
            if it["yc"] - it["h"] / 2 < ymin:
                it["yc"] = ymin + it["h"] / 2

    def _ann_text(self, x_edge, y, lines, align):
        """Annotation lines; align 'start' grows right from x_edge, 'end' grows left to x_edge."""
        p, cv = self.p, self.cv
        size = p.ann
        space = text_width(" ", "body", size)
        yy = y + size * 0.95
        for words, lw in lines:
            x = x_edge if align == "start" else x_edge - lw
            for wi, w in enumerate(words):
                if wi:
                    x += space
                for t, acc in w:
                    cv.text(x, yy, t, "bold" if acc else "body", size, ACCENT if acc else INK, anchor="start")
                    x += text_width(t, "bold" if acc else "body", size)
            yy += size * 1.3

    def _draw_right_column(self):
        p, cv = self.p, self.cv
        ox, oy = self.ox, self.oy
        items = []
        x0 = ox + self.cont_x + self.cont_w + p.margin
        for il in self.inset_layouts:
            t = self.by_id.get(il["spec"]["for"])
            if not t:
                cv.warnings.append("%s: inset target %r not found" % (self.spec["slug"], il["spec"]["for"]))
                continue
            items.append({"kind": "inset", "il": il, "target": t, "h": il["h"], "yc": oy + t.y + t.h / 2})
        for a in self.ann_layouts:
            if a["side"] != "right":
                continue
            t = self.by_id.get(a["spec"]["at"])
            if not t:
                cv.warnings.append("%s: annotation target %r not found" % (self.spec["slug"], a["spec"]["at"]))
                continue
            items.append({"kind": "ann", "a": a, "target": t, "h": a["h"], "yc": oy + t.y + t.h / 2})
        self._resolve(items, oy + self.title_h, oy + self.H - 6)
        for it in items:
            t = it["target"]
            ax, ay = self._anchor(t, "right")
            if it["kind"] == "inset":
                il = it["il"]
                y = it["yc"] - il["h"] / 2
                cv.rect(x0, y, il["w"], il["h"], fill=C["soft"], stroke=C["slate"], sw=1.0, rx=12, dash="4 3")
                self._place_stack(il["nodes"], x0 + il["w"] / 2 - ox, y + il["h"] - 14 - oy)
                self._draw_stack(il["nodes"])
                if il["spec"].get("label"):
                    cv.text(x0 + il["w"] / 2, y - 5, il["spec"]["label"], "body", p.box - 1, C["grey"])
                cv.path("M %.1f %.1f L %.1f %.1f" % (ax + 1, ay, x0 - 1, it["yc"]), stroke=INK, sw=0.9, dash="2 3")
            else:
                a = it["a"]
                y = it["yc"] - a["h"] / 2
                self._ann_text(x0, y, a["lines"], "start")
                cv.path("M %.1f %.1f L %.1f %.1f" % (ax + 1, ay, x0 - 5, it["yc"]), stroke=INK, sw=0.9, dash="2 3")

    def _draw_left_annotations(self):
        p, cv = self.p, self.cv
        ox, oy = self.ox, self.oy
        items = []
        x1 = ox + self.cont_x - p.margin
        for a in self.ann_layouts:
            if a["side"] != "left":
                continue
            t = self.by_id.get(a["spec"]["at"])
            if not t:
                cv.warnings.append("%s: annotation target %r not found" % (self.spec["slug"], a["spec"]["at"]))
                continue
            items.append({"kind": "ann", "a": a, "target": t, "h": a["h"], "yc": oy + t.y + t.h / 2})
        self._resolve(items, oy + self.title_h, oy + self.H - 6)
        for it in items:
            t = it["target"]
            ax, ay = self._anchor(t, "left")
            a = it["a"]
            y = it["yc"] - a["h"] / 2
            self._ann_text(x1, y, a["lines"], "end")
            cv.path("M %.1f %.1f L %.1f %.1f" % (ax - 1, ay, x1 + 5, it["yc"]), stroke=INK, sw=0.9, dash="2 3")

    def _draw_feedback(self):
        cv, p = self.cv, self.p
        ox, oy = self.ox, self.oy
        top = (self.above or self.stack)[-1]
        bottom = (self.below or self.stack)[0]
        x = ox + self.W - 12
        y_top = oy + top.y + top.h / 2
        y_bot = oy + bottom.y + bottom.h / 2
        cv.path("M %.1f %.1f L %.1f %.1f L %.1f %.1f L %.1f %.1f" % (
            ox + top.x + top.w + 4, y_top, x, y_top, x, y_bot, ox + bottom.x + bottom.w + 5, y_bot),
            stroke=ACCENT, sw=1.1, dash="4 3", marker=True)
        cv.text(x + 13, (y_top + y_bot) / 2, self.flow["feedback"], "body", p.ann - 0.5, ACCENT, anchor="middle", rotate=-90)


def render_stack_svg(spec, condensed=False, background=True, fonts=True):
    lay = StackLayout(spec, condensed)
    cv = Canvas()
    if background:
        cv.rect(0, 0, math.ceil(lay.W) + 1, math.ceil(lay.H) + 1, fill=C["white"], rx=0)
    lay.draw(cv, 0, 0)
    svg = D.svg_head(math.ceil(lay.W), math.ceil(lay.H), cv.markers, fonts) + "\n".join(cv.parts) + "\n</svg>\n"
    return svg, cv.warnings, (lay.W, lay.H)


def compose_stacks(specs, condensed=True, gap=30, background=True, fonts=True):
    lays = [StackLayout(s, condensed) for s in specs]
    H = max(l.H for l in lays)
    Wt = sum(l.W for l in lays) + gap * (len(lays) - 1)
    cv = Canvas()
    if background:
        cv.rect(0, 0, math.ceil(Wt) + 1, math.ceil(H) + 1, fill=C["white"], rx=0)
    x = 0
    for l in lays:
        l.draw(cv, x, 0)
        x += l.W + gap
    svg = D.svg_head(math.ceil(Wt), math.ceil(H), cv.markers, fonts) + "\n".join(cv.parts) + "\n</svg>\n"
    return svg, cv.warnings, (Wt, H)
