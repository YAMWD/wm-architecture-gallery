# Changelog

## 2026-10-29: author and repository links
- The page header carries a byline whose name links to github.com/YAMWD; the footer repeats the link, and the About text links issues and pull requests to the repository.

## 2026-10-25: follow-up fixes to the recheck
- An independent check of the recheck confirmed most edits and found four wrong ones, now fixed: SOLD keeps 4 slot-aggregation layers (paper and released checkpoint), LingBot-VA keeps its per-chunk real-observation cache write and loop, the long-context SSM model keeps its frame-by-frame rollout loop, and Genie's block count stays the paper's L.
- Restored source-backed content the recheck had removed, among them Cosmos 3's video, audio and action input lane, NWM's CEM planning note, LingBot-World-Fast's >200 GB per minute and WorldPlay's block-causal attention.
- Figures, annotations and facts now describe one configuration per card; numbers from another setting carry its name. Thirty cards changed; their source reviews and hashes were updated, and all integrity checks pass.

## 2026-10-25: primary-source architecture recheck
- Compared all 49 original publications/official technical pages and pinned released code for 42 models. Added per-model configurations, findings, disagreements and evidence limits in docs/architecture_audit.md and its hashed JSON ledger. Seven models lack matching official implementation evidence in the consulted sources.
- Corrected LingBot-VA's released shared transformer versus the paper's separate towers, incompatible variant/sampler combinations in Cosmos-Predict1, Cosmos-Predict2.5 and NWM, and configuration differences in SOLD, SlotFormer, TransDreamer, UniZero and UVA. Added omitted norms, projections and residual gates where the original code establishes them.
- Rollout feedback now connects named tensor endpoints. Removed incorrect action-to-image-encoder loops and the duplicated action-module residual in Matrix-Game 2/3. Cached reasoner/video work stays outside denoising loops.
- Removed all 49 stale alternate diagram specifications and historical audit counters; default rendering uses the canonical flow. Source checks show current evidence and limits in the card and figure viewer. Build/integrity checks reject stale reviews and exports.
- Removed the documentation instruction to guess a standard pre-norm block when details are undisclosed. Earlier audit totals and verification claims below are historical and are superseded by this review.

## 2026-10-23 (version 6): only what a source states
- Diagrams now draw only what a source states. The 38 elements that no source states were removed: guessed norms, feed-forward layers and residual lines in AAPT, comma.ai, GAIA-1, GAIA-2 and Genie, invented steps (a KV-cache write, a codebook lookup, a denoising update), the SwiGLU inset in Dreamer 4, and the decoder and sampling loop of the long-context SSM model.
- A block whose remaining layers are undisclosed shows one plain "Rest of block not stated" box, and its facts name the missing parts.
- Dreamer 4 keeps its pre-norm residual layout: the paper starts from "a standard transformer with pre-layer RMSNorm, RoPE, and SwiGLU".
- The dashed-outline style is gone, the Source check panel reports removed elements, and the renderer warns about any element tagged `assumed`.

## 2026-10-23 (version 5): source audit
- Every card was cross-checked against its primary sources in three independent passes: 2,340 elements over 49 cards, 440 of them corrected. Examples: IRIS adds its learned positions at the token embedding and its transformer has about 8.5M parameters (30M is the whole agent); Dreamer 4 runs causal time attention in one layer of four and has a reward head; WorldPlay has no cross-attention in the released code; Matrix-Game 2.0's real-time model has 1.62B parameters.
- Each box records its basis: stated in the paper, shown in the released code or config, or assumed. Assumed boxes are drawn with a dashed outline, and each card gains a *Source check* panel with its counts.
- Sources lists name primary sources only.
- The renderer now splits an arrow into a nested fanout to each of its boxes.
- `data.json` no longer carries the unaudited token-square `diagram` spec, and the legacy token-square SVGs were removed from `docs/`.

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
