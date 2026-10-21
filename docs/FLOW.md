# Writing the architecture flow (MODEL["flow"])

The main figure of every card is a stack diagram in the style of Sebastian Raschka's LLM architecture
gallery: the data path runs from the bottom to the top through small boxes with one short label each,
repeated blocks sit in a tinted container with an "N ×" marker, residual connections are drawn as skip
lines into a ⊕, and every number lives in an annotation outside the model, not inside a box. Finished
examples: `models/iris.py` (token model with heads), `models/matrix_game_2.py` (diffusion transformer with
a denoising loop), `models/vjepa2_ac.py` (embedding predictor with a planning inset), `models/dreamer4.py`
(factorized attention, shortcut steps, SwiGLU inset).

Render and check (from the repository root):

```bash
python3 -m wmgallery.render <slug> --stack              # docs/png/stack/<slug>.png   (web version)
python3 -m wmgallery.render <slug> --stack --condensed  # docs/png/stack_condensed/<slug>.png (slide version)
```

Open both PNGs. A flow is done when there are no WARN lines, no label is cut, no leader line crosses a
box, and the condensed version is at most 430 units tall (the CLI flags taller ones).

## Grammar

```python
"flow": {
    "below": [{"text": "Frame 64×64 + action"}],            # plain text under the model (inputs)
    "stack": [ ... nodes, bottom → top ... ],                 # inside the grey model container
    "above": [{"box": "VQ-VAE decoder", "style": "teal"}, {"text": "Next frame"}],   # outputs
    "insets": [{"for": "ffn", "stack": [{"box": "Linear"}, {"box": "GELU"}, {"box": "Linear"}]}],
    "annotations": [{"at": "attn", "text": "*4* heads · context *340* tokens", "side": "left", "key": True}],
    "feedback": "next step",                                  # optional dashed loop from output to input
}
```

Nodes:

| node | draws | keys |
|---|---|---|
| `{"box": "Label"}` | one rounded box | `id`, `style` (`plain`, `dark` for the attention operator, `teal` for encoders and decoders, `orange` for action or conditioning modules, `soft` for data such as noisy latents), `side` (label of a small side-input box with an arrow into this box, e.g. `"RoPE"`, `"Timestep emb."`, `"Keys + mouse"`), `minor` (dropped in the condensed version), `short` (label used in the condensed version), `terminal` (a branch that ends here) |
| `{"text": "..."}` | unboxed monospace text (inputs and outputs) | |
| `{"group": [...]}` | tinted container around a sub-stack | `repeat` (`"30 ×"`), `loop` (`"3 denoising steps"`: dashed loop arrow on the right), `tint` (`navy` for the transformer block, `grey` for a sampling loop, `orange`, `teal`), `label`, `id` |
| `{"residual": [...]}` | the sub-stack, then ⊕ with a skip line from below the first node | |
| `{"fanout": [[...], [...]]}` | parallel branches side by side, joined by diagonal arrows | each branch is a stack; its top node may be `terminal` |
| `{"merge": "x"}` or `{"merge": "+"}` | a circled operator that joins the branches below it | |
| `{"gap": 10}` | vertical space | |

Annotations: `at` is a node id; `text` uses `*…*` around every number so it is set in the accent colour;
`side` is `left` or `right` (balance the two sides; put insets' targets on the right); `key: True` keeps the
annotation in the condensed version (keep three or four key ones).

## What a flow must show

From the bottom up:

1. **Input** as text: observation size and the action or conditioning inputs.
2. **Encoder or tokenizer** (teal): what turns pixels into the sequence, then the quantization or
   patchify step if there is one, then the embedding (mark embeddings and norms `minor`).
3. **Conditioning inputs** as `side` boxes on the node they enter: positional encoding into attention,
   timestep or action embeddings into AdaLN, text or image features into cross-attention, keyboard and
   mouse signals into an action module (orange).
4. **The transformer block** as a `group` with `repeat`: norms (`minor`), the attention operator (dark;
   say the mask in the label: `Masked self-attention`, `Block-causal self-attention`, `Spatial attention`,
   `Temporal attention`, `Cross-attention`), ⊕ via `residual`, the feed-forward box, modulation boxes.
   Add an inset for the feed-forward (Linear → GELU → Linear, or the SwiGLU fan-out with a `merge`) and
   for any other sub-block worth opening (an action module, a mixer, a tokenizer block).
5. **The sampling loop** for diffusion, flow matching, shortcut or MaskGIT models: a grey `group` with
   `loop` around the denoiser, holding the noisy input, the block group and the update step.
6. **Output heads** as a `fanout` when the model has more than one (next tokens or latents, reward, done,
   value, policy, action chunk); extra heads are `terminal` and `minor`.
7. **Decoder** (teal) in `above`, then the output as text. Models without a pixel decoder end with the
   predicted features and say what consumes them (`L1 distance to the goal embedding`).
8. **Annotations** for: tokens per frame or step and vocabulary; width, heads, KV heads; layers and
   parameters; context or window; steps per frame and passes per frame; cache or memory size; reported
   speed with hardware and whose claim it is. Numbers only inside `*…*`; the same numbers as `facts`.

Box labels: at most about four words; no numbers in boxes except in the encoder or decoder output shapes
when they are the point (`Patchify 1×2×2`, `256 latent tokens`). Keep the main path to at most ten boxes
between input and output in the full version, and use `minor` and `short` so the condensed version has at
most six or seven boxes and stays under 430 units tall.

Say what is not disclosed in an annotation (`layers and heads not disclosed`) rather than guessing a block
structure; when the paper gives no block details, draw the standard pre-norm block and annotate it as
`block details not disclosed`.
