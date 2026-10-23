# World Model Architecture Gallery

Architecture diagrams for world models whose core is a transformer, drawn in one visual language so that
designs can be compared side by side. Each diagram reads from the bottom up: input, encoder or tokenizer,
the transformer block (norms, attention operators, modulation, feed-forward, residuals, repeated N ×), the
sampling loop where there is one, the output heads and the decoder. Boxes carry one short label; every
number sits in an annotation beside the model.
The idea follows Sebastian Raschka's [LLM Architecture Gallery](https://sebastianraschka.com/llm-architecture-gallery/),
applied to world models.

Published copy (private claude.ai page, share from its menu): https://claude.ai/artifact/Ds373si23Shvz56ZVURwaj

The site is a single static page (`docs/index.html`). Models appear as small cards in two columns: a compact
diagram, the name and a one-line tagline. Facts stay folded until you open *Details*, one fact at a time.
Clicking a diagram opens the detailed version full-page, with zoom, previous and next, and a side-by-side
compare. Search, family chips, filters and sorting sit in a sticky bar. `docs/data.json` holds every card as data.

## Layout

```
models/<slug>.py        one card per model (metadata, facts, sources, "flow" diagram spec, "audit" counts)
wmgallery/stack.py      flow -> bottom-up stack diagram (SVG/PNG); full version for the web, condensed for slides
wmgallery/diagram.py    summary card (token squares) and shared SVG helpers
wmgallery/registry.py   loads and validates cards
wmgallery/render.py     CLI: render one card, a contact sheet, or a side-by-side row for a slide
wmgallery/build.py      CLI: build the site into docs/
docs/                   the built site (index.html, svg/stack, svg/mini, data.json) and the spec docs
fonts/                  IBM Plex and Saira SemiCondensed (OFL), used for text measurement and PNG rendering
```

## Build

```bash
pip install --user pillow cairosvg        # cairosvg needs libcairo (present on most Linux and macOS systems)
python3 -m wmgallery.build                # -> docs/index.html, docs/svg/*.svg, docs/data.json
python3 -m wmgallery.render iris --stack              # one diagram -> docs/png/stack/iris.png
python3 -m wmgallery.render iris --stack --condensed  # slide version -> docs/png/stack_condensed/iris.png
python3 -m wmgallery.render iris storm --stack --condensed --row --out row.png   # a two-model slide figure
```

Open `docs/index.html` in a browser. Nothing else is needed; the page has no build-time JavaScript dependencies.

## Add or correct a model

1. Copy `models/_TEMPLATE.py` to `models/<slug>.py` and fill it in following `docs/SPEC.md`; write the
   `flow` diagram following `docs/FLOW.md`.
2. `python3 -m wmgallery.render <slug> --stack` and `--stack --condensed`; open the PNGs and fix every warning.
3. `python3 -m wmgallery.build`, add a line to `CHANGELOG.md`, commit.

Every number on a card must be traceable to the sources listed on the card; our own arithmetic is marked [D];
developer claims are labelled as such. Evidence levels: `verified` (adversarially checked), `read` (read from
the paper or code), `claim` (developer page only).

## How the cards were checked

In October 2026 every card was cross-checked against its primary sources: the paper or official report, the
official page, and the released code or config. The 49 cards hold 2,340 checkable elements: box labels, the
order of sub-layers, residuals, side inputs, repeat counts, numbers, facts and metadata.

1. An auditor judged every element and quoted its evidence.
2. A script looked up every quoted piece of evidence in the downloaded sources; rows it could not match, and
   every row judged wrong, unclear, assumed or derived, went to a second checker.
3. The second checker re-verified those rows and applied the corrections it confirmed.
4. A third checker reviewed every changed line against its evidence.

Of the 2,340 elements, 1,441 are stated in the paper or report, 677 come from released code or config and 184
are our arithmetic. 445 elements were corrected, and 38 that no source states were removed from the diagrams.
The diagrams draw only what a source states: each box records its basis (`"basis"` in the flow spec, see
`docs/FLOW.md`), and a block whose remaining layers are undisclosed shows a plain "Rest of block not stated" box.
A card's *Source check* panel gives its own counts. New or edited cards should keep the same standard: tag
every box, quote the source for every number, and mark our arithmetic.

## Publish

The site lives in `docs/`, so GitHub Pages serves it directly: push the repository, then in the repository
settings choose Pages → Deploy from a branch → `main` / `docs`. Rebuild and push after every card change.

## License

Cards and diagrams: CC BY 4.0. Code: MIT. Fonts: SIL Open Font License (see `fonts/`).
