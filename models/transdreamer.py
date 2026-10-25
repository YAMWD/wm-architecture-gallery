MODEL = {
    "slug": "transdreamer",
    "name": "TransDreamer",
    "year": 2021, "month": 10,
    "org": "Rutgers / KAIST",
    "family": "rl",
    "role": "Per-step latent model",
    "status": "arXiv preprint (v2 Nov 2024)",
    "params": "size not disclosed",
    "params_num": None,
    "open": "code",
    "links": {"arXiv": "https://arxiv.org/abs/2202.09481", "code": "https://github.com/changchencc/TransDreamer"},
    "summary": "The first transformer-based model-based RL agent (authors' claim), in the Dreamer setting. The Transformer State-Space Model (TSSM) replaces "
               "the RSSM's GRU: the deterministic state h_t is a causal transformer over the past stochastic latents and "
               "actions, one token per step, and the posterior drops h_t so every step trains in parallel. Everything "
               "else is DreamerV2: CNN encoder and decoder, discrete latents, reward and discount heads, actor-critic in "
               "imagination. The transformer is small: 2 layers in the DMC/Atari runs, 6 in the Hidden Order tasks and the "
               "released Atari config. The released code re-runs it over the whole window (up to 49 steps) for every "
               "imagined step, with no KV cache, so the cost of every layer grows with the imagined history.",
    "tagline": "Dreamer with a transformer in place of the GRU",
    "facts": [
        ("Representation", "DreamerV2 CNN encoder; posterior q(z_t | x_t) computed from the frame alone (no h_t), discrete "
                           "stochastic latent; full state is the concatenation [h_t, z_t]"),
        ("Core", "TSSM per App. A.3 (DMC, Atari): 2-layer transformer, 10 heads, attention and MLP hidden size 200 (DMC) or "
                 "600 (Atari), no dropout, gating or identity-map reordering (except Atari Pong); ~0.5M (DMC) to ~4.3M "
                 "(Atari) block weights [D]. App. A.4 (Hidden Order Discovery): 6 layers with identity-map reordering. "
                 "Released Atari config: 6 pre-LN layers, d_model 600, 8 heads x 64, FFN 1024, dropout 0.1; ~14.8M block "
                 "weights [D], as drawn; deter_type concat_o: h_t is the concatenation of all 6 layer outputs (3600-d), "
                 "which feeds the prior and the decoder, reward and discount heads. Residual layout from the code: x + LN(f(x)) without reordering, "
                 "x + f(LN(x)) with it"),
        ("Attention", "Causal over past steps: h_t = transformer(z_{1:t-1}, a_{1:t-1}); the drawn Atari config uses pos_enc "
                      "'temporal', an absolute sinusoidal embedding added to the input (code); the paper lists relative "
                      "positional embedding (Transformer-XL style) as a tunable option; sequence length per DreamerV2 config"),
        ("Actions", "One token per step: the flattened one-hot z_t is concatenated with a_t, projected by Linear + ELU to "
                    "d_model, plus a sinusoidal position embedding (released code; the paper does not describe it)"),
        ("Prediction", "Prior p(z_t | h_t) sampled and fed back (the figure's 'next' is step t, given inputs up to t-1); 1 transformer pass per imagined step; image, reward and "
                       "discount predictors read (h_t, z_t); ELBO with KL(q(z_t|x_t) || p(z_t|h_t))"),
        ("Decoder", "DreamerV2 CNN decoder from (h_t, z_t), used for the reconstruction loss and visualisation only"),
        ("Memory", "Attends over the whole (z, a) history: the 50-step training sequence; in imagination, context plus "
                   "imagined steps (up to a 49-step window in the released code), re-run in full every step with no KV cache "
                   "(code). Transformer memory limits imagination to K = 3 trajectories per sample (DMC, Atari; Sec. 3.2, "
                   "App. A.3); App. A.4 and the released code start one rollout per sequence from a random state"),
        ("Speed", "No wall-clock or throughput figure; hardware not stated. On DMC and Atari it reaches returns comparable to "
                  "Dreamer but is 'slower to saturate in general' (authors, Sec. 5.5); in the Hidden Order Discovery tasks "
                  "it imagines from one random start state until the trajectory's max step (App. A.4)"),
        ("Key detail", "One token per step (z_t and a_t fused by Linear + ELU in the code); the myopic posterior q(z_t | x_t), "
                       "without h_t, is what lets the transformer compute h_1:T for all steps in one parallel pass (Sec. 3.1)"),
    ],
    "evidence": "read",
    "sources": ["arXiv 2202.09481 Sec. 3.1 and Table 1 (TSSM components), Sec. 3.2 (prioritized replay, K imagined trajectories)",
                "arXiv 2202.09481 App. A.3 (2 layers, 10 heads, hidden 200/600, no gating/dropout, K = 3), Fig. 6 (rollout)",
                "arXiv 2202.09481 App. A.4 (Hidden Order Discovery: 6 layers, identity-map reordering, one random start)",
                "Official code github.com/changchencc/TransDreamer: src/model/transformer.py, src/model/modules_transformer.py, src/config_files/configs_atari.py",
                "OpenReview ICLR 2022 submission s3K0arSRl4d (first public release, Oct 2021)",
                "DreamerV2 config referenced in App. A.3 (github.com/danijar/dreamerv2) for encoder/decoder and latent type"],
    "figure_variant": "Released Atari config: 6 layers, width 600, 8 heads of 64, h = all 6 layer outputs",
    "flow": {
        "below": [{"text": "Frame x_t + action a_t"}],
        "stack": [
            {"box": "DreamerV2 CNN encoder", "short": "DreamerV2 encoder", "id": "enc", "style": "teal", "basis": "code"},
            {"box": "Posterior q(z_t | x_t)", "id": "post", "minor": True, "basis": "stated"},
            {"box": "Step token (z_t, a_t)", "short": "Token (z_t, a_t)", "id": "tok", "side": "Action a_t", "basis": "code", "side_basis": "code"},
            {"box": "Linear + ELU + positions", "minor": True, "basis": "code"},
            {"group": [
                {"residual": [{"box": "LayerNorm", "minor": True, "basis": "code"},
                              {"box": "Masked self-attention", "id": "attn", "style": "dark", "basis": "code"}]},
                {"residual": [{"box": "LayerNorm", "minor": True, "basis": "code"},
                              {"box": "MLP", "id": "mlp", "basis": "code"}]},
            ], "repeat": "6 ×", "id": "block", "basis": "code"},
            {"box": "Concat all layer outputs", "short": "Deterministic state h", "id": "h", "minor": True, "basis": "code"},
            {"box": "Next-state prior", "id": "prior", "minor": True, "basis": "stated"},
            {"box": "Sample next latent z", "short": "Sample prior z", "id": "sample", "basis": "stated"},
            {"box": "Concat next h and z", "id": "feat", "minor": True, "basis": "code"},
            {"fanout": [[{"box": "Reward head", "id": "rew", "terminal": True, "basis": "stated"}],
                        [{"box": "DreamerV2 CNN decoder", "short": "DreamerV2 decoder", "id": "dec", "style": "teal", "basis": "code"}],
                        [{"box": "Discount head", "terminal": True, "minor": True, "basis": "stated"}]]},
        ],
        "above": [{"text": "Next frame (training only)"}],
        "annotations": [
            {"at": "tok", "text": "*1* token per step", "side": "left", "key": True},
            {"at": "attn", "text": "Atari code: *8* heads · width *600*", "side": "left", "key": True},
            {"at": "block", "text": "*6* layers · ≈*14.8M* block weights", "side": "right", "key": True},
            {"at": "h", "text": "h = *6* × *600* = *3600*-d (concat_o)", "side": "left"},
            {"at": "sample", "text": "*1* pass per frame", "side": "left", "key": True},
        ],
        "feedback": "next latent z",
        "feedback_from": "sample",
        "feedback_to": "tok",
    },
}
