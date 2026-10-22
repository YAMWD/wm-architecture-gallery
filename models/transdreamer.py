MODEL = {
    "slug": "transdreamer",
    "name": "TransDreamer",
    "year": 2022, "month": 2,
    "org": "Rutgers / KAIST",
    "family": "rl",
    "role": "Per-step latent model",
    "status": "arXiv preprint (v2 Nov 2024)",
    "params": "size not disclosed",
    "params_num": None,
    "open": "closed",
    "links": {"arXiv": "https://arxiv.org/abs/2202.09481"},
    "summary": "The first transformer world model in the Dreamer setting. The Transformer State-Space Model (TSSM) replaces "
               "the RSSM's GRU: the deterministic state h_t is a causal transformer over the past stochastic latents and "
               "actions, one token per step, and the posterior drops h_t so every step trains in parallel. Everything "
               "else is DreamerV2: CNN encoder and decoder, discrete latents, reward and discount heads, actor-critic in "
               "imagination. The transformer is tiny (2 layers), so imagination is latency-bound per step and attention "
               "over the growing imagined history is the only cost that scales.",
    "tagline": "Dreamer with a transformer in place of the GRU",
    "facts": [
        ("Representation", "DreamerV2 CNN encoder; posterior q(z_t | x_t) computed from the frame alone (no h_t), discrete "
                           "stochastic latent; full state is the concatenation [h_t, z_t]"),
        ("Core", "TSSM: 2-layer transformer, 10 heads, attention and MLP hidden size 200 (DMC) or 600 (Atari), no dropout, no "
                 "gating, no identity-map reordering (except Atari Pong); ~0.5M (DMC) to ~4.3M (Atari) block weights [D]"),
        ("Attention", "Causal over past steps: h_t = transformer(z_{1:t-1}, a_{1:t-1}); relative positional embedding "
                      "(Transformer-XL style) is a tunable option; sequence length per DreamerV2 config"),
        ("Actions", "The action is part of each step's input token together with the stochastic latent; how z_t and a_t are combined is not stated"),
        ("Prediction", "Prior p(z_t | h_t) sampled and fed back; 1 transformer pass per imagined step; image, reward and "
                       "discount predictors read (h_t, z_t); ELBO with KL(q(z_t|x_t) || p(z_t|h_t))"),
        ("Decoder", "DreamerV2 CNN decoder from (h_t, z_t), used for the reconstruction loss and visualisation only"),
        ("Memory", "Attends over the whole (z, a) history of the training sequence or imagined rollout; no KV cache "
                   "mentioned; transformer memory forces only K = 3 imagined trajectories per replay sample (DMC, Atari)"),
        ("Speed", "No wall-clock or throughput figure; hardware not stated. On DMC and Atari it reaches returns comparable to "
                  "Dreamer but is 'slower to saturate in general' (authors, Sec. 5.5); on Crafter it imagines until the "
                  "trajectory's max step (App.)"),
        ("Key detail", "One token per step and a 2-layer core: the template for TWM, STORM and UniZero; the parallel-training "
                       "trick (posterior without h_t) is what makes the transformer usable here"),
    ],
    "evidence": "read",
    "sources": ["arXiv 2202.09481 Sec. 3.1 and Table 1 (TSSM components), Sec. 3.2 (prioritized replay, K imagined trajectories)",
                "arXiv 2202.09481 App. A.3 (2 layers, 10 heads, hidden 200/600, no gating/dropout, K = 3), Fig. 6 (rollout)",
                "DreamerV2 config referenced in App. A.3 (github.com/danijar/dreamerv2) for encoder/decoder and latent type"],
    "diagram": {
        "encoder": {"text": "Frame → DreamerV2 CNN encoder", "sub": "posterior q(z_t | x_t) without h_t, discrete latent",
                    "tag": "trained jointly", "short": "DreamerV2 CNN → discrete z_t"},
        "tokens": {"groups": [("latent", 1, "stochastic latent z_t"), ("action", 1, "action a_t")],
                   "note": "one token per step → h_{t+1}"},
        "core": {"title": "TSSM ×2 · d 200 (DMC) / 600 (Atari) · 10 heads",
                 "rows": [("attn", "Causal attention over past (z, a) steps"),
                          ("mlp", "MLP, hidden 200 / 600")],
                 "notes": ["no gating, no dropout; relative P.E. optional", "h_t = transformer(z_1:t-1, a_1:t-1)"]},
        "sampling": {"kind": "ar", "text": "Sample prior p(z_t | h_t), feed back", "sub": "1 pass per imagined step; K = 3 trajectories per sample",
                     "short": "Sample z_t, 1 pass per step"},
        "heads": ["reward", "discount"],
        "decoder": {"text": "DreamerV2 CNN decoder → frame", "sub": "from (h_t, z_t); training loss only", "tag": "trained jointly",
                    "short": "CNN decoder → frame (training only)"},
        "loop": "AR rollout",
    },
    "flow": {
        "below": [{"text": "Frame x_t + action a_t"}],
        "stack": [
            {"box": "DreamerV2 CNN encoder", "short": "DreamerV2 encoder", "id": "enc", "style": "teal"},
            {"box": "Posterior q(z_t | x_t)", "id": "post", "minor": True},
            {"box": "Step token (z_t, a_t)", "short": "Token (z_t, a_t)", "id": "tok", "side": "Action a_t"},
            {"group": [
                {"residual": [{"box": "Masked self-attention", "id": "attn", "style": "dark"}]},
                {"box": "LayerNorm", "minor": True},
                {"residual": [{"box": "MLP", "id": "mlp"}]},
                {"box": "LayerNorm", "minor": True},
            ], "repeat": "2 ×", "id": "block"},
            {"box": "Deterministic state h_t", "id": "h", "minor": True},
            {"fanout": [[{"box": "Prior p(z_t | h_t)", "id": "prior", "minor": True}, {"box": "Sample z_t, feed back", "short": "Sample prior z_t", "id": "sample"}],
                        [{"box": "Reward head", "id": "rew", "terminal": True}], [{"box": "Discount head", "terminal": True, "minor": True}]]},
        ],
        "above": [{"box": "DreamerV2 CNN decoder", "short": "DreamerV2 decoder", "id": "dec", "style": "teal"}, {"text": "Frame x_t (training only)"}],
        "annotations": [
            {"at": "tok", "text": "*1* token per step", "side": "left", "key": True},
            {"at": "attn", "text": "*10* heads · width *200* (DMC), *600* (Atari)", "side": "left", "key": True},
            {"at": "block", "text": "*2* layers · ~*0.5M*–*4.3M* block weights", "side": "right", "key": True},
            {"at": "sample", "text": "*1* pass per frame", "side": "left", "key": True},
            {"at": "sample", "text": "*3* rollouts per replay sample", "side": "right"},
        ],
        "feedback": "next step: z_t",
    },
}
