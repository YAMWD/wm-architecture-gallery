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
      "feedback": "next code",                                               # named tensor route, not a generic control loop
      "feedback_from": "sample", "feedback_to": "emb",
    }

Node kinds: box (label; id; style = plain|dark|teal|orange|soft; side = label of a side-input box; minor = dropped
in condensed mode; short = label used in condensed mode; w = fixed width; basis = "stated" | "code",
the evidence for the box; side_basis likewise for the side box; only sourced elements are drawn, and the lint warns on "assumed"), text (unboxed, monospace), group (children; repeat "N ×"; loop "4 steps";
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


LIMITS = {"annotations": 6, "ann_chars": 44, "box_chars": 24, "side_chars": 18, "text_chars": 34,
          "loop_chars": 20, "label_chars": 16}


class P:
    """Layout parameters for one mode."""
    def __init__(self, condensed, mini=False):
        self.condensed = condensed
        self.mini = mini
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
        if mini:                                      # card thumbnail: boxes only
            self.box, self.gap, self.pad, self.cont_pad, self.title_h = 11.5, 10, 7, 9, 14
            self.minw, self.maxw = 64, 136


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
        self.fan = None                               # (branch index, branch count) inside a fanout
        self.strip = 0                                # header strip height of a group
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
            if n.spec.get("condensed_box"):
                n.children = [Node({"box": n.spec["condensed_box"], "basis": n.spec["basis"]})]
            else:
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
    def __init__(self, spec, condensed=False, mini=False, title=True):
        self.spec = spec
        self.show_title = title
        self.flow = spec["flow"]
        self.mini = mini
        condensed = condensed or mini
        self.p = P(condensed, mini)
        self.condensed = condensed
        self.warnings = []
        self.below = [Node(s) for s in self.flow.get("below", [])]
        self.stack = [Node(s) for s in self.flow.get("stack", [])]
        self.above = [Node(s) for s in self.flow.get("above", [])]
        if condensed:
            self.below, self.stack, self.above = condense(self.below), condense(self.stack), condense(self.above)
        if mini:
            def strip(nodes):
                out = []
                for n in nodes:
                    if n.kind == "text":
                        continue
                    if n.kind == "fanout":
                        n.children = [b for b in (strip(br) for br in n.children) if b]
                        if not n.children:
                            continue
                        if len(n.children) == 1:
                            out.extend(n.children[0]); continue
                    out.append(n)
                return out
            self.below, self.above = strip(self.below), strip(self.above)
        self.insets = [] if condensed else self.flow.get("insets", [])
        anns = self.flow.get("annotations", [])
        if condensed:
            keyed = [a for a in anns if a.get("key")]
            anns = [dict(a, side="right") for a in (keyed or anns[:3])]   # one column keeps the slide figure narrow
        if mini:
            anns = []
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
        if n.spec.get("side") and not self.mini:
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
            # header strip: group label (left) and loop label (right) sit above the children,
            # so leader lines from the children never cross them
            hs = p.ann - 0.5 if not self.mini else p.box - 1
            gl, lt = self._group_label(n), self._loop_text(n)
            wl = text_width(gl, "body", p.box - 1) if gl else 0
            wr = text_width(lt, "body", hs) if lt else 0
            n.strip = (hs * 1.3 + 8) if (wl or wr) else 0
            if wl and wr:
                n.w = max(n.w, wl + wr + 36)
            elif wl or wr:
                n.w = max(n.w, wl + wr + 24)
            top_pad = max(p.pad + 2, n.strip)
            n.h = sum(c.h for c in n.children) + p.gap * (len(n.children) - 1) + (p.pad + 2) + top_pad
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
            _, h = self._stack_size(nodes)
            self._place_stack(nodes, 0.0, 0.0)
            left, right = self._extents(nodes)
            self.inset_layouts.append({"spec": ins, "nodes": nodes, "w": right - left + 2 * 14,
                                       "h": h + 2 * 14, "cx": 14 - left})
        # annotation text blocks
        self.ann_layouts = []
        for a in self.annotations:
            text = a.get("short") if (self.condensed and a.get("short")) else a["text"]
            lines = self._ann_lines(text)
            if self.condensed and len(lines) > 3:
                self.warnings.append("%s: condensed annotation at %r runs to %d lines; add a \"short\" text"
                                     % (self.spec["slug"], a["at"], len(lines)))
            self.ann_layouts.append({"spec": a, "lines": lines, "h": len(lines) * p.ann * 1.3,
                                     "w": max(lw for _, lw in lines), "side": a.get("side", "right")})
        left_items = [a for a in self.ann_layouts if a["side"] == "left"]
        right_items = [a for a in self.ann_layouts if a["side"] == "right"]
        self.left_w = (max(a["w"] for a in left_items) + p.margin) if left_items else 0
        right_need = (max(a["w"] for a in right_items) + p.margin) if right_items else 0
        if self.inset_layouts:
            right_need = max(right_need, max(i["w"] for i in self.inset_layouts) + p.margin)
        self.right_w = right_need
        self.fb_w = 40 if (self.flow.get("feedback") and not self.condensed) else 0
        self.title_h = p.title_h if self.show_title else 14
        # the column may be wider than the container when below/above stacks are wider
        extra = max(0, max(self.below_w, self.above_w) - self.cont_w)
        self.W = 10 + self.left_w + self.cont_w + extra + self.right_w + self.fb_w + 10
        self.variant_lines = []
        if self.show_title and not self.condensed and self.spec.get("figure_variant"):
            self.variant_lines = wrap("Figure: " + self.spec["figure_variant"], "body", 10, self.W - 24)
            self.title_h += len(self.variant_lines) * 13 + 4
        self.H = (self.title_h + self.above_h + (p.gap if self.above else 0) + self.cont_h
                  + (p.gap if self.below else 0) + self.below_h + (16 if (self.mini and not self.below) else 12))
        if not self.condensed:
            self._lint()
        right_items = ([i["h"] + (14 if i["spec"].get("label") else 0) for i in self.inset_layouts]
                       + [a["h"] for a in self.ann_layouts if a["side"] == "right"])
        left_items = [a["h"] for a in self.ann_layouts if a["side"] == "left"]
        # Reserve space above the right column for external routing.
        self.col_floor = self.title_h
        if self.flow.get("feedback") and not self.condensed:
            top = (self.above or self.stack)[-1]
            self.col_floor = self.title_h + top.h + 10
        for col, floor in ((right_items, self.col_floor), (left_items, self.title_h)):
            if col:
                need = floor + sum(col) + 8 * (len(col) - 1) + 12
                self.H = max(self.H, need)

    def _lint(self):
        """Concision limits for the detailed diagram (docs/FLOW.md)."""
        slug, L = self.spec["slug"], LIMITS
        anns = self.flow.get("annotations", [])
        if len(anns) > L["annotations"]:
            self.warnings.append("%s: %d annotations; keep at most %d" % (slug, len(anns), L["annotations"]))
        for a in anns:
            plain = a["text"].replace("*", "")
            if len(plain) > L["ann_chars"]:
                self.warnings.append("%s: annotation at %r has %d characters (max %d): %r"
                                     % (slug, a["at"], len(plain), L["ann_chars"], plain))
        for n in _flatten(self.below + self.stack + self.above, []):
            if n.kind == "box":
                if len(n.spec["box"]) > L["box_chars"]:
                    self.warnings.append("%s: box label %r is longer than %d characters" % (slug, n.spec["box"], L["box_chars"]))
                if n.spec.get("side") and len(n.spec["side"]) > L["side_chars"]:
                    self.warnings.append("%s: side label %r is longer than %d characters" % (slug, n.spec["side"], L["side_chars"]))
            if n.kind == "text" and len(n.spec["text"]) > L["text_chars"]:
                self.warnings.append("%s: input/output text %r is longer than %d characters" % (slug, n.spec["text"], L["text_chars"]))
            if n.kind == "group":
                if n.spec.get("loop") and len(n.spec["loop"]) > L["loop_chars"]:
                    self.warnings.append("%s: loop label %r is longer than %d characters" % (slug, n.spec["loop"], L["loop_chars"]))
                if n.spec.get("label") and len(n.spec["label"]) > L["label_chars"]:
                    self.warnings.append("%s: group label %r is longer than %d characters" % (slug, n.spec["label"], L["label_chars"]))
        for ins in self.flow.get("insets", []):
            for n in _flatten([Node(x) for x in ins["stack"]], []):
                if n.kind == "box" and len(n.spec["box"]) > L["box_chars"]:
                    self.warnings.append("%s: inset box %r is longer than %d characters" % (slug, n.spec["box"], L["box_chars"]))
        # Only what a source states is drawn: an element no paper, page, code or config states is left out,
        # and a block whose remaining layers are undisclosed gets a plain "Rest of block not stated" box.
        unsourced = []
        nodes = _flatten(self.below + self.stack + self.above, [])
        for ins in self.flow.get("insets", []):
            nodes += _flatten([Node(x) for x in ins["stack"]], [])
        for n in nodes:
            if n.spec.get("basis") == "assumed" or n.spec.get("side_basis") == "assumed":
                unsourced.append(n.spec.get("box") or n.spec.get("repeat") or n.spec.get("label") or n.kind)
        for u in unsourced:
            self.warnings.append("%s: %r is tagged assumed; draw only what a source states (remove it or cite a source)"
                                 % (slug, u))
        tl = self.spec.get("tagline")
        if not tl:
            self.warnings.append("%s: no tagline" % slug)
        elif len(tl) > 52:
            self.warnings.append("%s: tagline has %d characters (max 52)" % (slug, len(tl)))

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
                lo = min(lo, self._repeat_x(n) - text_width(n.spec["repeat"], "headm", 12.5) - 2)
            if n.kind == "group" and n.spec.get("loop"):
                hi = max(hi, n.x + n.w + 10 + 6)
        return lo, hi

    def _loop_text(self, n):
        """Loop label: as written, or in the mini thumbnail a short form such as "3 steps"."""
        lab = n.spec.get("loop")
        if not lab or not self.mini:
            return lab
        if n.spec.get("loop_short"):
            return n.spec["loop_short"]
        import re
        m = re.search(r"(\d[\d,]*(?:\s*(?:→|->)\s*\d[\d,]*)*)\s+(?:[A-Za-z-]+\s+){0,2}?(steps?|passes|iterations|NFE|samples)",
                      lab)
        if m:
            return "%s %s" % (m.group(1), m.group(2))
        return lab if len(lab) <= 14 else ""

    def _group_label(self, n):
        return None if self.mini else n.spec.get("label")

    def _repeat_x(self, n):
        """Right edge (text-anchor end) of a group's "N ×" label: left of its own border, and left of the
        enclosing group's border when nested, so no border runs through it."""
        x = n.x - 10
        if n.group_left is not None:
            x = min(x, n.group_left - 6)
        return x

    def _repeat_y(self, n):
        """Baseline height for the "N ×" label: lowest spot on the left that no side box occupies."""
        sides = []
        for c in _flatten(n.children, []):
            if c.kind == "box" and c.side:
                sh = c.side[2]
                top = c.y + (c.h - sh) / 2
                sides.append((top - 4, top + sh + 4))
        y = n.y + n.h - 14
        while y > n.y + 16:
            if all(not (a < y + 8 and y - 10 < b) for a, b in sides):
                return y
            y -= 4
        return n.y + 16

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
            for i, br in enumerate(n.children):
                for c in _flatten(br, []):
                    lo, hi = c.row if c.row else (c.x, c.x + c.w)
                    c.row = (min(lo, n.x), max(hi, n.x + n.w))      # keep a branch's own side box in its row
                    c.fan = (i, len(n.children))

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
        self.geo_boxes = []      # (x0, y0, x1, y1, tag) of everything a leader must not cross
        self.geo_leaders = []    # (points, set of tags the leader may touch)
        self.place_all()
        self.ox, self.oy = ox, oy
        cv.warnings.extend(self.warnings)
        spec = self.spec
        if self.mini or not self.show_title:
            pass
        elif self.condensed:
            cv.text(ox + self.cx, oy + 18, spec["name"], "head", 17, C["navy"])
            sub = " · ".join(str(v) for v in (spec.get("org"), spec.get("year")) if v)
            cv.text(ox + self.cx, oy + 31, sub, "body", 10, C["grey"])
        else:
            cv.text(ox + self.cx, oy + 22, spec["name"], "head", 18, C["navy"])
            org = str(spec.get("org", "")).split(" (")[0]
            import re as _re
            size = _re.sub(r"\s*\[D[^\]]*\]", "", str(spec.get("params", ""))).split(" (")[0].split(",")[0]
            sub = " · ".join(str(v) for v in (org, spec.get("year"), size) if v)
            cv.text(ox + self.cx, oy + 38, sub, "body", 10.5, C["grey"])
            if self.variant_lines:
                cv.lines(ox + self.W / 2, oy + 45, self.variant_lines, "body", 10, C["grey"], lh=13)
        cv.rect(ox + self.cont_x, oy + self.cont_y, self.cont_w, self.cont_h, fill=C["soft"], stroke=C["slate"], sw=1.0, rx=20)
        self._draw_stack(self.stack)
        if self.below:
            self._draw_stack(self.below)
            self._connect(self.below[-1], self.stack[0])
        elif self.mini:
            first = self.stack[0]
            while first.kind in ("group", "residual") and first.children:
                first = first.children[0]
            if first.kind == "fanout":
                first = first.children[0][0]
            b = self._bottom_point(first)
            cv.arrow(b[0], oy + self.cont_y + self.cont_h + 12, b[0], b[1], stroke=INK, sw=1.2)
        if self.above:
            self._draw_stack(self.above)
            self._connect(self.stack[-1], self.above[0])
        else:
            t = self.stack[-1]
            tops = [br[-1] for br in t.children if not br[-1].spec.get("terminal")] if t.kind == "fanout" else [t]
            for tt in tops:
                src = self._top_point(tt)
                cv.arrow(src[0], src[1], src[0], oy + self.cont_y - 12, stroke=INK, sw=1.2)
        self._draw_right_column()
        self._draw_left_annotations()
        if self.flow.get("feedback") and not self.condensed:
            self._draw_feedback()
        self._check_leaders()

    def _box(self, x0, y0, x1, y1, tag):
        self.geo_boxes.append((x0, y0, x1, y1, tag))

    def _check_leaders(self):
        """Warn when a leader line crosses a box, a side box, an inset or another annotation."""
        def crosses(p0, p1, r):
            x0, y0, x1, y1 = r[0] + 1.5, r[1] + 1.5, r[2] - 1.5, r[3] - 1.5
            if x1 <= x0 or y1 <= y0:
                return False
            dx, dy = p1[0] - p0[0], p1[1] - p0[1]
            t0, t1 = 0.0, 1.0
            for pp, qq in ((-dx, p0[0] - x0), (dx, x1 - p0[0]), (-dy, p0[1] - y0), (dy, y1 - p0[1])):
                if pp == 0:
                    if qq < 0:
                        return False
                else:
                    t = qq / pp
                    if pp < 0:
                        t0 = max(t0, t)
                    else:
                        t1 = min(t1, t)
                    if t0 > t1:
                        return False
            return True
        for pts, ok in self.geo_leaders:
            hit = set()
            for a, b in zip(pts, pts[1:]):
                for r in self.geo_boxes:
                    if r[4] in ok or r[4] in hit:
                        continue
                    if crosses(a, b, r):
                        hit.add(r[4])
            for tag in sorted(hit):
                self.cv.warnings.append("%s: leader to %r crosses %s" % (self.spec["slug"], sorted(ok)[0], tag))

    def _top_point(self, n):
        """Where an arrow leaving `n` upward starts."""
        if n.kind == "fanout":
            return None
        return (self.ox + n.cx, self.oy + n.y - 1)

    def _bottom_point(self, n):
        return (self.ox + n.cx, self.oy + n.y + n.h + 1)

    def _entries(self, n):
        """Nodes an arrow arriving at `n` from below must reach: for a fanout, the first node of every
        branch, recursively, so an arrow into a nested fanout splits to its boxes instead of ending
        between them."""
        if n.kind == "fanout":
            out = []
            for br in n.children:
                out += self._entries(br[0])
            return out
        return [n]

    def _connect(self, lower, upper):
        """Arrow(s) from the top of `lower` to the bottom of `upper`, handling fanouts on either side."""
        cv = self.cv
        if upper.kind == "fanout" and lower.kind == "fanout":
            lows = [br[-1] for br in lower.children if not br[-1].spec.get("terminal")]
            ups = self._entries(upper)
            if len(lows) != len(ups):
                cv.warnings.append("%s: fanout feeds a fanout with a different branch count; each branch "
                                   "connects to the nearest one above" % self.spec["slug"])
            for lo in lows:
                up = min(ups, key=lambda u: abs(u.cx - lo.cx))
                src, dst = self._top_point(lo), self._bottom_point(up)
                cv.arrow(src[0], src[1], dst[0], dst[1], stroke=INK, sw=1.2)
            return
        if upper.kind == "fanout":
            src = self._top_point(lower)
            for up in self._entries(upper):
                dst = self._bottom_point(up)
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
        if n.kind in ("merge", "text", "box"):
            self._box(ox + n.x, oy + n.y, ox + n.x + n.w, oy + n.y + n.h, "box %r" % (n.id or n.label()))
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
            dash = None
            if n.spec.get("basis") == "assumed":      # not stated in the sources: dashed outline
                dash = "3.5 2.5"
                if n.spec.get("style") == "dark":
                    fill, stroke, color = C["navy_t"], C["navy"], INK
            cv.rect(ox + n.x, oy + n.y, n.w, n.h, fill=fill, stroke=stroke, sw=1.1 if dash else 1.0, rx=6, dash=dash)
            th = len(n.lines) * p.box * 1.3
            cv.lines(ox + n.cx, oy + n.y + (n.h - th) / 2, n.lines, "body", p.box, color)
            if n.side:
                s, sw, sh, sx = n.side
                sy = oy + n.y + (n.h - sh) / 2
                self._box(ox + sx, sy, ox + sx + sw, sy + sh, "side box %r" % s)
                sdash = "3.5 2.5" if n.spec.get("side_basis") == "assumed" else None
                cv.rect(ox + sx, sy, sw, sh, fill=C["white"], stroke=INK, sw=1.1 if sdash else 1.0, rx=6, dash=sdash)
                cv.text(ox + sx + sw / 2, sy + sh / 2 + (p.box - 1) * 0.35, s, "body", p.box - 1, INK)
                cv.arrow(ox + sx + sw + 1, sy + sh / 2, ox + n.x - 1, sy + sh / 2, stroke=INK, sw=1.1)
            return
        if n.kind == "group":
            fill, stroke = GROUP_STYLE.get(n.spec.get("tint", "navy"), GROUP_STYLE["navy"])
            gdash = "4 3" if n.spec.get("basis") == "assumed" else None
            cv.rect(ox + n.x, oy + n.y, n.w, n.h, fill=fill, stroke=stroke, sw=1.0, rx=14 if not self.mini else 10, dash=gdash)
            hs = p.ann - 0.5 if not self.mini else p.box - 1
            base = oy + n.y + 5 + 0.9 * hs
            gl, lt = self._group_label(n), self._loop_text(n)
            if gl:
                cv.text(ox + n.x + 10, base, gl, "body", p.box - 1, C["grey"], anchor="start")
            if lt:
                cv.text(ox + n.x + n.w - 12, base, lt, "body", hs, ACCENT, anchor="end")
            self._draw_stack(n.children)
            if n.spec.get("repeat"):
                by = oy + self._repeat_y(n)
                bx = ox + n.x
                cv.rect(bx - 4, by - 9, 8, 18, fill=fill, stroke=None, rx=0)
                cv.path("M %.1f %.1f l 5 -6 l -8 -4 l 5 -6" % (bx - 1, by + 8), stroke=INK, sw=1.4, fill="none")
                cv.text(ox + self._repeat_x(n), by + 2, n.spec["repeat"], "headm", 12.5, ACCENT, anchor="end")
            if n.spec.get("loop"):
                x = ox + n.x + n.w + 10
                ytop = base - 0.35 * hs
                cv.path("M %.1f %.1f L %.1f %.1f L %.1f %.1f L %.1f %.1f" % (
                    ox + n.x + n.w, ytop, x, ytop, x, oy + n.y + n.h - 14, ox + n.x + n.w + 2, oy + n.y + n.h - 14),
                    stroke=ACCENT, sw=1.2, dash="4 3", marker=True)
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
        """Point where a leader line leaves the diagram: the outer edge of every node drawn at the target's
        height (siblings in a fanout, side boxes of a group's children), so the line never crosses a box."""
        y = n.y + n.h / 2
        left, right = n.row if n.row else (n.x, n.x + n.w)
        for d in _flatten([n], []):
            if d is n or d.kind == "gap":
                continue
            if d.y - 2 <= y <= d.y + d.h + 2:
                l, r = d.row if d.row else (d.x, d.x + d.w)
                left, right = min(left, l), max(right, r)
        prefix = []
        if n.fan:
            i, k = n.fan
            if (side == "right" and i != k - 1) or (side == "left" and i != 0):
                # inner branch: leave from the box's top corner and pass over the sibling boxes
                ye = n.y - 7
                xs = (n.x + n.w - 8) if side == "right" else (n.x + 8)
                blocked = any(d.kind in ("box", "text", "merge") and d is not n and d.y - 2 <= ye <= d.y + d.h + 2
                              and ((side == "right" and d.x > n.x) or (side == "left" and d.x < n.x))
                              for d in _flatten(self.stack + self.below + self.above, []))
                if blocked:
                    self.cv.warnings.append("%s: %s annotation on %r: a taller sibling branch blocks the leader; "
                                            "move it to the other side" % (self.spec["slug"], side, n.id))
                prefix = [(self.ox + xs, self.oy + n.y - 1), (self.ox + xs, self.oy + ye)]
                y = ye
        x = self.ox + (left if side == "left" else right)
        return x, self.oy + y, prefix

    def _resolve(self, items, ymin, ymax):
        """Stack items (sorted by target height) without overlaps inside [ymin, ymax].
        measure_all() makes the canvas tall enough for every column, so this never has to overlap."""
        items.sort(key=lambda i: i["yc"])
        gap = 8
        floor = ymin
        for it in items:                                   # forward: push down below the previous item
            it["yc"] = max(it["yc"], floor + it["h"] / 2)
            floor = it["yc"] + it["h"] / 2 + gap
        ceil = ymax
        for it in reversed(items):                         # backward: pull up above the next item
            if it["yc"] + it["h"] / 2 > ceil:
                it["yc"] = ceil - it["h"] / 2
            ceil = it["yc"] - it["h"] / 2 - gap

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
            lab = 14 if il["spec"].get("label") else 0
            items.append({"kind": "inset", "il": il, "target": t, "h": il["h"] + lab, "lab": lab,
                          "yc": oy + t.y + t.h / 2})
        for a in self.ann_layouts:
            if a["side"] != "right":
                continue
            t = self.by_id.get(a["spec"]["at"])
            if not t:
                cv.warnings.append("%s: annotation target %r not found" % (self.spec["slug"], a["spec"]["at"]))
                continue
            items.append({"kind": "ann", "a": a, "target": t, "h": a["h"], "yc": oy + t.y + t.h / 2})
        for it in items:
            if it["target"].fan:
                i, k = it["target"].fan
                if i != k - 1:
                    it["yc"] = oy + it["target"].y - 7
        self._resolve(items, oy + self.col_floor, oy + self.H - 6)
        for it in items:
            t = it["target"]
            ax, ay, pre = self._anchor(t, "right")
            if pre:
                cv.path("M %.1f %.1f L %.1f %.1f L %.1f %.1f" % (pre[0][0], pre[0][1], pre[1][0], pre[1][1], ax + 1, ay),
                        stroke=INK, sw=0.9, dash="2 3")
            tgt = "box %r" % (t.id or t.label())
            if it["kind"] == "inset":
                il = it["il"]
                y = it["yc"] - it["h"] / 2 + it["lab"]
                itag = "inset for %r" % il["spec"]["for"]
                self._box(x0, y - it["lab"], x0 + il["w"], y + il["h"], itag)
                self.geo_leaders.append((pre + [(ax + 1, ay), (x0 - 1, y + il["h"] / 2)], {tgt, itag}))
                cv.rect(x0, y, il["w"], il["h"], fill=C["soft"], stroke=C["slate"], sw=1.0, rx=12, dash="4 3")
                self._place_stack(il["nodes"], x0 + il["cx"] - ox, y + il["h"] - 14 - oy)
                self._draw_stack(il["nodes"])
                if il["spec"].get("label"):
                    cv.text(x0 + il["w"] / 2, y - 5, il["spec"]["label"], "body", p.box - 1, C["grey"])
                cv.path("M %.1f %.1f L %.1f %.1f" % (ax + 1, ay, x0 - 1, y + il["h"] / 2), stroke=INK, sw=0.9, dash="2 3")
            else:
                a = it["a"]
                y = it["yc"] - a["h"] / 2
                atag = "annotation at %r" % a["spec"]["at"]
                self._box(x0, y, x0 + a["w"], y + a["h"], atag)
                self.geo_leaders.append((pre + [(ax + 1, ay), (x0 - 5, it["yc"])], {tgt, atag}))
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
        for it in items:
            if it["target"].fan and it["target"].fan[0] != 0:
                it["yc"] = oy + it["target"].y - 7
        self._resolve(items, oy + self.title_h, oy + self.H - 6)
        for it in items:
            t = it["target"]
            ax, ay, pre = self._anchor(t, "left")
            if pre:
                cv.path("M %.1f %.1f L %.1f %.1f L %.1f %.1f" % (pre[0][0], pre[0][1], pre[1][0], pre[1][1], ax - 1, ay),
                        stroke=INK, sw=0.9, dash="2 3")
            a = it["a"]
            y = it["yc"] - a["h"] / 2
            atag = "annotation at %r" % a["spec"]["at"]
            self._box(x1 - a["w"], y, x1, y + a["h"], atag)
            self.geo_leaders.append((pre + [(ax - 1, ay), (x1 + 5, it["yc"])], {"box %r" % (t.id or t.label()), atag}))
            self._ann_text(x1, y, a["lines"], "end")
            cv.path("M %.1f %.1f L %.1f %.1f" % (ax - 1, ay, x1 + 5, it["yc"]), stroke=INK, sw=0.9, dash="2 3")

    def _draw_feedback(self):
        cv, p = self.cv, self.p
        ox, oy = self.ox, self.oy
        top = self.by_id[self.flow["feedback_from"]]
        bottom = self.by_id[self.flow["feedback_to"]]
        x = ox + self.W - 26
        # Join the named tensor ports between rows.  Returning every output to
        # the pixel encoder incorrectly depicted re-encoding in latent rollouts.
        y_top = oy + top.y - p.gap * 0.35
        y_bot = oy + bottom.y + bottom.h + p.gap * 0.35
        cv.path("M %.1f %.1f L %.1f %.1f L %.1f %.1f L %.1f %.1f L %.1f %.1f L %.1f %.1f" % (
            ox + top.cx, oy + top.y - 1, ox + top.cx, y_top,
            x, y_top, x, y_bot, ox + bottom.cx, y_bot,
            ox + bottom.cx, oy + bottom.y + bottom.h + 1),
            stroke=ACCENT, sw=1.1, dash="4 3", marker=True)
        cv.text(x + 15, (y_top + y_bot) / 2, self.flow["feedback"], "body", p.ann - 0.5, ACCENT, anchor="middle", rotate=-90)


def render_stack_svg(spec, condensed=False, background=True, fonts=True, mini=False, title=True):
    lay = StackLayout(spec, condensed, mini, title)
    cv = Canvas()
    if background:
        cv.rect(0, 0, math.ceil(lay.W) + 1, math.ceil(lay.H) + 1, fill=C["white"], rx=0)
    lay.draw(cv, 0, 0)
    description = "<desc>%s — %s</desc>\n" % (esc(spec["name"]), esc(spec.get("figure_variant", "")))
    svg = D.svg_head(math.ceil(lay.W), math.ceil(lay.H), cv.markers, fonts) + description + "\n".join(cv.parts) + "\n</svg>\n"
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
