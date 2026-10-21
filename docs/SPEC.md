# Writing a model card

A model card is one Python file `models/<slug>.py` that defines a dict `MODEL`. The build renders its
`diagram` into an SVG card (web) and a compact PNG (slides), and prints the rest as a fact sheet.
Start from `models/_TEMPLATE.py`; `models/iris.py`, `models/matrix_game_2.py` and `models/vjepa2_ac.py`
are complete examples for the three main shapes (token model, diffusion transformer, embedding predictor).

Render and check:

```bash
python3 -m wmgallery.render <slug>            # writes site/svg/<slug>.svg and site/png/<slug>.png, prints WARN lines
python3 -m wmgallery.render <slug> --compact  # the slide version (site/png/compact/<slug>.png)
```

Open the PNGs and look at them. A card is done when there are no WARN lines, no text touches a box edge,
the title bar text fits, and the compact version still reads correctly.

## Keys

| key | meaning |
|---|---|
| `slug` | file name without `.py`; lowercase, digits, underscores |
| `name` | as the authors write it (`Dreamer 4`, `V-JEPA 2-AC`) |
| `year`, `month` | first public release (arXiv v1 or announcement) |
| `org` | developer, short (`Google DeepMind`, `Skywork AI`, `NYU`) |
| `family` | `rl`, `token`, `dit`, `driving`, `jepa`, `wam`, `llm`, `object`, `ssm` |
| `role` | the transformer's role, one of: `Discrete-token model`, `Per-step latent model`, `Diffusion transformer`, `Embedding predictor`, `LLM or mixture of transformers`, `Object-centric model`, `SSM hybrid` |
| `status` | venue if peer-reviewed (`ICLR 2023`), else `arXiv preprint`, `company technical report`, `blog post` |
| `params` | short string for the header (`~30M`, `1.3B`, `8.4B + 285M tokenizer`); keep under ~30 characters |
| `params_num` | number for sorting, or `None` |
| `open` | `code + weights`, `code`, `weights`, `closed` |
| `links` | dict of label -> URL (`arXiv`, `code`, `page`, `report`) |
| `summary` | 2-4 sentences: what it is, what the transformer does inside it, why it matters for compute |
| `facts` | list of `(label, text)`; use the nine labels below in this order, drop a label only if nothing is known |
| `evidence` | `verified` (adversarially verified findings), `read` (read from the primary paper or code), `claim` (developer blog or page only) |
| `sources` | list of short strings naming paper sections, tables, config files |
| `diagram` | see below |

Fact labels: `Representation`, `Core`, `Attention`, `Actions`, `Prediction`, `Decoder`, `Memory`, `Speed`, `Key detail`.

## Diagram grammar

The card is read from the bottom up. Each row is optional except `core`.

```python
"diagram": {
    "encoder":  {"text": "Frames → Wan2.1 3D causal VAE", "sub": "880 latents per latent frame",
                 "tag": "frozen", "short": "Wan2.1 3D VAE"},
    "tokens":   {"groups": [("latent", 24, "2,640 latents per chunk"), ("action", 3, "actions")],
                 "note": "window 6 latent frames = 5,280 tokens"},
    "core":     {"title": "Wan-style DiT ×30 · d 1536 · 12 heads",
                 "rows": [("attn", "Block-causal self-attention, 3D RoPE"),
                          ("xattn", "Cross-attention to first-frame CLIP features"),
                          ("action", "Action modules in blocks 1–15"),
                          ("mlp", "MLP")],
                 "notes": ["rolling KV cache: 6 latent frames"]},
    "sampling": {"kind": "diffusion", "text": "DMD Self-Forcing, 3 denoising steps", "sub": "per 12-frame chunk",
                 "short": "3 DMD steps per chunk"},
    "heads":    ["reward", "value"],
    "decoder":  {"text": "Wan VAE decoder → 12 frames", "sub": "352×640", "tag": "frozen"},
    "loop":     "AR rollout",
}
```

- `encoder.text`: observation → encoder, one line (`Frame 64×64 → VQ-VAE (CNN)`). `sub`: what comes out
  (tokens per frame, latent shape). `tag`: `frozen`, `trained jointly`, `pretrained`. `short`: compact-mode text.
- `tokens.groups`: what one step (one frame, one chunk, one environment step) puts into the sequence. Each
  group is `(kind, count, label)`. Kinds: `frame` discrete codes, `latent` continuous latents or features,
  `action`, `state`, `reward`, `text`, `register`, `slot`, `noise`, `audio`. The count drives the squares
  (capped at 8 drawn); put the real number in the label. Keep labels under ~25 characters; 2-3 groups.
  When actions do not enter as tokens (AdaLN, cross-attention, channel concatenation), do not add an action
  group; add an `action` row inside `core` instead.
- `core.title`: `<name> ×<layers> · d <width> · <heads> heads` when known; otherwise the shortest honest
  description (`Transformer, size not disclosed`). It must fit one line.
- `core.rows`: 2-5 rows, each `(kind, text)` or `(kind, text, short)`, where `short` replaces `text` in
  compact mode (keep it under ~34 characters so the row stays on one line). Kinds: `attn` self-attention (say the mask: causal over tokens,
  block-causal over frames, spatial / temporal factorized, bidirectional), `xattn` cross-attention (say to what),
  `mlp`, `action` (how actions enter: AdaLN, action modules, mixer, channel concat), `ssm` (Mamba, GDN,
  retention), `moe` (experts or a second stream), `note` (grey text, no box).
- `core.notes`: short grey lines for KV cache, context, position encoding.
- `sampling.kind`: `ar` (one token per pass), `parallel` (MaskGIT-style, all tokens per pass), `diffusion`
  (denoising or flow steps), `regress` (one deterministic pass), `search` (planning loop over the model).
  `text` names the objective and step count; `sub` gives passes per frame or per chunk.
- `heads`: short names only (`reward`, `done`, `value`, `policy`, `action chunk`).
- `decoder`: `text` says what produces pixels and at what resolution. `{"none": "reason"}` draws a dashed
  box (`planning in feature space`, `video head skipped at deployment`).
- `loop`: label of the feedback arrow (`AR rollout`, `CEM rollout`, `MCTS`, `closed loop with real frames`).
  Omit for offline clip generators.

## Style

- Terse. Numbers with units. `×` for multiplication, `→` for flow, `d` for width, `~` for approximations.
- Every number must come from `sources`. Your own arithmetic is marked `[D]` in `facts` (not in the diagram).
- In `Speed`, say whose number it is: `(authors)`, `(company claim)`, `(measured by WorldKV on 4×H200)`.
- Do not copy marketing. Say what is not disclosed: `size not disclosed`.
- `evidence` describes the whole card: `verified` only if the architecture facts come from the adversarially
  verified findings; `read` if you read the paper or code; `claim` for blog-only systems.
