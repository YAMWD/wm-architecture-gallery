"""Render model diagrams.

    python3 -m wmgallery.render                 # all models -> docs/svg/stack, docs/png/stack (warnings printed)
    python3 -m wmgallery.render iris storm      # only these slugs
    python3 -m wmgallery.render --sheet /tmp/sheet.png   # also build a contact sheet of the PNGs
    python3 -m wmgallery.render --row iris storm dreamer4 --out /tmp/row.png   # one composite row (for slides)
"""
import os
import sys
import argparse

from . import diagram as D
from . import registry as R


def contact_sheet(png_paths, out, cols=4, thumb_w=360, label=True):
    from PIL import Image, ImageDraw, ImageFont
    ims = []
    for p in png_paths:
        im = Image.open(p).convert("RGB")
        s = thumb_w / im.width
        ims.append((os.path.basename(p)[:-4], im.resize((thumb_w, int(im.height * s)), Image.LANCZOS)))
    rows = (len(ims) + cols - 1) // cols
    row_h = [max(im.height for _, im in ims[r * cols:(r + 1) * cols]) + 22 for r in range(rows)]
    sheet = Image.new("RGB", (cols * (thumb_w + 16) + 16, sum(row_h) + 16), "white")
    dr = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype(os.path.join(D.FONT_DIR, D.FONT_FILES["bold"]), 16)
    except OSError:
        font = None
    y = 8
    for r in range(rows):
        for c in range(cols):
            i = r * cols + c
            if i >= len(ims):
                break
            name, im = ims[i]
            x = 16 + c * (thumb_w + 16)
            dr.text((x, y), name, fill="#333", font=font)
            sheet.paste(im, (x, y + 20))
        y += row_h[r]
    sheet.save(out)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("slugs", nargs="*")
    ap.add_argument("--out", default=None, help="output dir (default: docs/) or, with --row, the PNG path")
    ap.add_argument("--scale", type=float, default=3.0)
    ap.add_argument("--no-png", action="store_true")
    ap.add_argument("--sheet", default=None)
    ap.add_argument("--row", action="store_true", help="compose the given slugs side by side into one PNG")
    ap.add_argument("--gap", type=int, default=24)
    ap.add_argument("--compact", action="store_true", help="alias for --condensed")
    ap.add_argument("--stack", action="store_true", help="compatibility flag; the source-checked flow is always rendered")
    ap.add_argument("--condensed", action="store_true", help="the condensed slide version")
    ap.add_argument("--mini", action="store_true", help="the card thumbnail (boxes only)")
    a = ap.parse_args(argv)

    specs = R.load_models(only=set(a.slugs) or None)
    if a.slugs:
        order = {s: i for i, s in enumerate(a.slugs)}
        specs.sort(key=lambda m: order.get(m["slug"], 999))
    bad = False
    for m in specs:
        errs = R.validate(m)
        if errs:
            bad = True
            print("INVALID %s: %s" % (m["slug"], "; ".join(errs)))
    if bad:
        sys.exit(1)
    a.condensed = a.condensed or a.compact
    from . import stack as S
    out_dir = a.out or os.path.join(R.ROOT, "docs")
    sub = "stack_mini" if a.mini else ("stack_condensed" if a.condensed else "stack")
    if a.row:
        svg, warns, size = S.compose_stacks(specs, condensed=a.condensed, gap=a.gap)
        out = a.out or "row.png"
        D.svg_to_png(svg, out, a.scale) if not out.endswith(".svg") else open(out, "w").write(svg)
        for w in warns:
            print("WARN", w)
        print("wrote %s (%d x %d units)" % (out, size[0], size[1]))
        return
    pngs = []
    for m in specs:
        if "flow" not in m:
            print("%-28s no flow spec" % m["slug"])
            continue
        svg, warns, size = S.render_stack_svg(m, condensed=a.condensed, mini=a.mini)
        os.makedirs(os.path.join(out_dir, "svg", sub), exist_ok=True)
        os.makedirs(os.path.join(out_dir, "png", sub), exist_ok=True)
        with open(os.path.join(out_dir, "svg", sub, m["slug"] + ".svg"), "w") as f:
            f.write(svg)
        png = os.path.join(out_dir, "png", sub, m["slug"] + ".png")
        if not a.no_png:
            D.svg_to_png(svg, png, a.scale)
            pngs.append(png)
        for w in warns:
            print("WARN", w)
        flag = "" if round(size[1], 1) <= 430 or not a.condensed else "  (taller than 430: mark more boxes minor/short)"
        if a.mini and size[1] > 330:
            flag = "  (thumbnail taller than 330: mark more boxes minor)"
        print("%-28s %4d x %4d  %s%s" % (m["slug"], size[0], size[1], png, flag))
    if a.sheet and pngs:
        contact_sheet(pngs, a.sheet, cols=3, thumb_w=480)
        print("sheet:", a.sheet)
    return

if __name__ == "__main__":
    main()
