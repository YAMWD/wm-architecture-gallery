# Changelog

## 2026-10-22 (version 4)
- Redesigned page: centered title block with crop marks over a faint engineering grid, monospace labels and figures, diagrams on blueprint-grid tiles, a sticky search and filter bar, more whitespace throughout.
- The full-page viewer shows each diagram once (no duplicate title) and both models' details when comparing.
- Plain backgrounds: the grid behind the page, the diagram tiles and the viewer was removed.

## 2026-10-22 (version 3)
- New page design: small two-column cards with a compact diagram, name and one-line tagline; facts fold behind *Details*, one fact at a time.
- Clicking a diagram opens the detailed version full-page, with zoom, previous and next (arrow keys), and a side-by-side compare.
- Diagram text cut to the essentials: at most 6 annotations of at most 44 characters, short box labels; caveats moved into the facts. The renderer enforces these limits.
- New compact thumbnail mode (`--stack --mini`); every card has a `tagline`.

## 2026-10-21 (version 2)
- Every card now leads with a bottom-up stack diagram in the style of the LLM Architecture Gallery: small boxes with one label each, repeated blocks with an N × marker, residual skip lines into ⊕, side inputs, zoom-in insets, and all numbers in annotations outside the model.
- New renderer `wmgallery/stack.py` with a condensed mode for slides; specs live in `MODEL["flow"]` (see `docs/FLOW.md`).
- The renderer checks every leader line and warns when one crosses a box; all 49 diagrams pass.
- The earlier token-square card stays available under each diagram as a compact summary.

## 2026-10-21
- First release: cards for the models covered by the "Transformer-based world models" research (RL world models, discrete-token video models, causal diffusion transformers, driving and robot models, embedding predictors, world-action models, LLM, object-centric and SSM designs).
- Renderer: one declarative spec per model produces the web card (SVG) and a compact slide card (PNG).
