# Changelog

## 2026-10-21 (version 2)
- Every card now leads with a bottom-up stack diagram in the style of the LLM Architecture Gallery: small boxes with one label each, repeated blocks with an N × marker, residual skip lines into ⊕, side inputs, zoom-in insets, and all numbers in annotations outside the model.
- New renderer `wmgallery/stack.py` with a condensed mode for slides; specs live in `MODEL["flow"]` (see `docs/FLOW.md`).
- The renderer checks every leader line and warns when one crosses a box; all 49 diagrams pass.
- The earlier token-square card stays available under each diagram as a compact summary.

## 2026-10-21
- First release: cards for the models covered by the "Transformer-based world models" research (RL world models, discrete-token video models, causal diffusion transformers, driving and robot models, embedding predictors, world-action models, LLM, object-centric and SSM designs).
- Renderer: one declarative spec per model produces the web card (SVG) and a compact slide card (PNG).
