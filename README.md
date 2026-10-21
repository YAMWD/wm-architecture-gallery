# World Model Architecture Gallery

Architecture diagrams for world models whose core is a transformer, drawn in one visual language so that
designs can be compared side by side. Each diagram reads from the bottom up: input, encoder or tokenizer,
the transformer block (norms, attention operators, modulation, feed-forward, residuals, repeated N ×), the
sampling loop where there is one, the output heads and the decoder. Boxes carry one short label; every
number sits in an annotation beside the model.
The idea follows Sebastian Raschka's [LLM Architecture Gallery](https://sebastianraschka.com/llm-architecture-gallery/),
applied to world models.

Published copy (private claude.ai page, share from its menu): https://claude.ai/artifact/Ds373si23Shvz56ZVURwaj

The site is a single static page (`docs/index.html`) with filters (family, role, evidence level, availability),
sorting, search, a two-model comparison view, per-card permalinks and downloadable SVGs. `docs/data.json`
holds every card as data.

## Layout

```
models/<slug>.py        one card per model (metadata, facts, sources, "flow" diagram spec, summary-card spec)
wmgallery/stack.py      flow -> bottom-up stack diagram (SVG/PNG); full version for the web, condensed for slides
wmgallery/diagram.py    summary card (token squares) and shared SVG helpers
wmgallery/registry.py   loads and validates cards
wmgallery/render.py     CLI: render one card, a contact sheet, or a side-by-side row for a slide
wmgallery/build.py      CLI: build the site into docs/
docs/                   the built site (index.html, svg/, data.json, legend.svg) and docs/SPEC.md
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

## Publish

The site lives in `docs/`, so GitHub Pages serves it directly: push the repository, then in the repository
settings choose Pages → Deploy from a branch → `main` / `docs`. Rebuild and push after every card change.

## License

Cards and diagrams: CC BY 4.0. Code: MIT. Fonts: SIL Open Font License (see `fonts/`).
