# World Model Architecture Gallery

Architecture figures for 49 world models, drawn from the bottom up in a shared visual language. The local gallery is [docs/index.html](docs/index.html); each card opens a detailed figure and a source check naming the configuration and its limits. The visual style follows Sebastian Raschka's [LLM Architecture Gallery](https://sebastianraschka.com/llm-architecture-gallery/).

The [2026-10-25 source review](docs/architecture_audit.md) covers all 49 original publications or official technical pages and matching released code for 42 models. The other seven have no matching official implementation in the consulted sources. Their undisclosed details remain undisclosed. Paper/code disagreements are recorded explicitly, including substantial differences in LingBot-VA, SlotFormer, SOLD, UniZero and TransDreamer.

Figures show one named configuration. A paper's distilled sampler, a base checkpoint's layers and another variant's latency must not be combined. The previous audit's verification badges and counters are superseded by this review.

## Layout

```text
models/<slug>.py             metadata, facts, sources and the single canonical "flow"
wmgallery/stack.py           full, condensed and thumbnail SVG rendering
wmgallery/diagram.py         shared drawing, text measurement and PNG helpers
wmgallery/registry.py        card/flow validation, including named feedback ports
wmgallery/audit.py           review, source-byte and generated-artifact integrity checks
wmgallery/build.py          static gallery builder
wmgallery/render.py         PNG/SVG exports, contact sheets and slide rows
docs/architecture_audit.md   per-model findings and primary-source links
docs/architecture_audit.json machine-readable review, immutable revisions and hashes
docs/                       generated gallery, data.json and SVG variants
fonts/                      bundled OFL fonts
```

## Build and check

```bash
pip install --user pillow cairosvg
python3 -m wmgallery.audit
python3 -m wmgallery.build
python3 -m wmgallery.render --no-png --condensed
python3 -m wmgallery.render --no-png --mini
python3 -m wmgallery.audit --artifacts
python3 -m wmgallery.render iris --scale 2
python3 -m wmgallery.render iris storm --condensed --row --out row.png
```

Open `docs/index.html` in a browser. No JavaScript build toolchain is needed. Rendering defaults to the same reviewed flow used by the site; `--stack` remains a compatibility flag. There is no alternate token-square architecture specification. PNGs and the old `site/` output directory are generated artifacts, not the gallery source.

The review JSON records a local primary-source cache path. On the review machine, downloaded bytes can also be checked with:

```bash
python3 -m wmgallery.audit --sources '/home/yaoz0b/wm_accel/research_notes/Architecture audit/2026-10-25'
```

These checks detect stale cards/exports and changed source bytes. They do not prove architecture correctness by looking for names in code. The review compared operation order and data flow; no downloaded model code or weights were executed, and no new performance benchmarks were run.

## Add or correct a model

1. Read the original publication, official configuration and actual forward/sampling paths. Choose one figure configuration and record differences between paper and code.
2. Copy [models/_TEMPLATE.py](models/_TEMPLATE.py), following [docs/SPEC.md](docs/SPEC.md) and [docs/FLOW.md](docs/FLOW.md). Cite every number; mark computed arithmetic `[D]`. Never infer a norm, residual, cache policy or sampler from a related model.
3. Render full, condensed and thumbnail figures. Inspect the PNGs and clear layout warnings without changing architecture to fit the page.
4. Update the per-model review in `docs/architecture_audit.json`, including source hashes, immutable revisions, findings, limits and the reviewed card's `wmgallery.audit.fingerprint`. The build rejects a card changed after its review.
5. Rebuild, run the integrity checks, and update `CHANGELOG.md`. Inspect the generated site before committing.

`read` means primary sources were read, subject to each review's limits. `claim` means an official developer page only. Neither badge is a guarantee of source completeness. A `basis` tag records where an element comes from; it is not evidence by itself.

## Publish

The static site lives in `docs/`. Configure GitHub Pages to serve that directory from the intended branch. Rebuild before publishing. External hosted copies are not updated by a local build.

## License

Cards and diagrams: CC BY 4.0. Code: MIT. Fonts: SIL Open Font License (see `fonts/`).
