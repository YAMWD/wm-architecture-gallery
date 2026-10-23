MODEL = {
    "slug": "trajectory_transformer",
    "name": "Trajectory Transformer",
    "year": 2021, "month": 6,
    "org": "UC Berkeley",
    "family": "rl",
    "role": "Discrete-token model",
    "status": "NeurIPS 2021",
    "params": "size not disclosed (~1.5M [D] for HalfCheetah)",
    "params_num": None,
    "open": "code + weights",
    "links": {"arXiv": "https://arxiv.org/abs/2106.02039", "code": "https://github.com/jannerm/trajectory-transformer",
              "page": "https://trajectory-transformer.github.io"},
    "summary": "Offline RL as one big sequence-modeling problem: every state dimension, action dimension, the reward and the "
               "reward-to-go are discretized into 100 bins and become separate tokens of a small GPT. There is no "
               "learned encoder and no policy network; acting is beam search over the model's own trajectory "
               "predictions, extended one token at a time. Latency scales with state dimensionality, and the authors note "
               "it can take seconds per action, which, they say, precludes real-time control for most dynamical systems.",
    "tagline": "GPT over binned states, actions and rewards",
    "facts": [
        ("Representation", "Each of the N state and M action dimensions, the reward and the reward-to-go is one token: "
                           "per-dimension uniform or quantile discretization into V = 100 bins; input vocabulary V × (N + M + 2), "
                           "output logits over V"),
        ("Core", "GPT-style decoder: 4 layers, 4 heads, token embedding d 128, dropout 0.1; parameter count not disclosed "
                 "(~12·4·128² ≈ 0.8M block weights if the MLP is 4× wide [D])"),
        ("Attention", "Causal, with every reward-to-go token masked out as a key (official code); context 5 transitions "
                      "of (s, a, r, R), at most 5 × (N + M + 2) − 1 tokens, e.g. 124 for a 17-D state and 6-D action [D]; "
                      "training uses 10-transition sequences (code)"),
        ("Actions", "Action dimensions are ordinary tokens in the stream, decoded after the state tokens of the same step"),
        ("Prediction", "Next-token softmax, one token per pass, teacher-forced training; planning = beam search, horizon 15 "
                       "transitions, observations decoded greedily (k_obs 1); paper (App. E): width 256, actions from the top 20 "
                       "tokens; released code: 128 beams × 2 expansions, actions sampled after dropping the least likely tokens "
                       "holding 60% of the mass (cdf_act 0.6); offline RL ranks transitions by reward plus reward-to-go instead "
                       "of log-probability"),
        ("Decoder", "None; states are discretized scalars, decoded back by bin centres"),
        ("Memory", "Fixed context of 5 transitions; no KV-cache details given"),
        ("Speed", "'Up to multiple seconds for action selection when the context window grows too large', hardware not stated "
                  "(authors, Sec. 5); training 6-12 h per model on one V100 for 80 epochs (authors, App. A)"),
        ("Key detail", "Per executed action: 15 × (N + M + 2) − N sequential single-token decodes (the current state is given "
                       "and the last state is not sampled), e.g. 358 for HalfCheetah at horizon 15 [D]; code batches 256 rows "
                       "for action and reward tokens, 128 for state tokens; a latency-bound ~1.5M-parameter workload [D]"),
    ],
    "evidence": "read",
    "sources": ["arXiv 2106.02039 Sec. 3.1 (tokenization, 4 layers/4 heads), Sec. 3.2 (beam search, reward-to-go), Algorithm 1, Sec. 5 (seconds per action)",
                "arXiv 2106.02039 App. A (d 128, dropout 0.1, V100 6-12 h), App. E (beam width 256, horizon 15, V 100, context 5, k_obs, k_act)",
                "Official code jannerm/trajectory-transformer: trajectory/models/transformers.py (pre-norm blocks, GELU MLP, R-to-go key mask, position embedding), trajectory/search/core.py and sampling.py (beam plan, cdf filter), config/offline.py, scripts/train.py, README (hyperparameters differ from paper)",
                "Environment dimensions for the [D] examples: D4RL HalfCheetah (17-D state, 6-D action)"],
    "diagram": {
        "encoder": {"text": "State and action scalars → uniform/quantile bins", "sub": "no learned encoder; V = 100 bins per dimension",
                    "short": "Per-dimension bins, V = 100"},
        "tokens": {"groups": [("state", 5, "N state dims"), ("action", 2, "M action dims"), ("reward", 2, "r, reward-to-go")],
                   "note": "N + M + 2 tokens per step; context 5 transitions"},
        "core": {"title": "GPT ×4 · d 128 · 4 heads",
                 "rows": [("attn", "Causal self-attention over all tokens"),
                          ("mlp", "MLP")],
                 "notes": ["context 5 × (N + M + 2) tokens; dropout 0.1", "output logits over V = 100 bins"]},
        "sampling": {"kind": "search", "text": "Beam search, width 256, horizon 15", "sub": "1 token per pass: 15 × (N + M + 2) serial passes per action",
                     "short": "Beam search, width 256, H 15"},
        "decoder": {"none": "states are discretized scalars"},
        "loop": "beam search",
    },
    "flow": {
        "below": [{"text": "State, action, reward, R-to-go"}],
        "stack": [
            {"box": "Per-dimension bins", "id": "disc", "style": "teal", "basis": "stated"},
            {"box": "Token embedding", "id": "emb", "minor": True, "basis": "stated", "side": "Position emb.",
             "side_basis": "code"},
            {"group": [
                {"residual": [{"box": "LayerNorm", "minor": True, "basis": "code"},
                              {"box": "Masked self-attention", "id": "attn", "style": "dark", "basis": "stated"}]},
                {"residual": [{"box": "LayerNorm", "minor": True, "basis": "code"}, {"box": "Feed forward", "id": "ffn", "basis": "code"}]},
            ], "repeat": "4 ×", "id": "block"},
            {"box": "Linear output layer", "id": "out", "minor": True, "basis": "stated"},
            {"box": "Sample next token", "id": "sample", "basis": "stated"},
        ],
        "above": [{"box": "Bin centre lookup", "id": "dec", "style": "teal", "basis": "code"}, {"text": "Plan → first action executed"}],
        "insets": [
            {"for": "ffn", "stack": [{"box": "Linear", "basis": "code"}, {"box": "GELU", "basis": "code"},
                                     {"box": "Linear", "basis": "code"}]},
            {"for": "sample", "label": "beam search", "stack": [{"box": "Grow each beam one token", "basis": "stated"},
                                                                 {"box": "Sample from top-k tokens", "basis": "stated"},
                                                                 {"box": "Rank by reward + R-to-go", "basis": "stated"},
                                                                 {"box": "Repeat to the horizon", "basis": "stated"}]},
        ],
        "annotations": [
            {"at": "disc", "text": "*N + M + 2* tokens per step, *100* bins each", "side": "left", "key": True},
            {"at": "emb", "text": "Embedding dimension of *128*", "side": "left"},
            {"at": "attn", "text": "*4* heads · context of *5* transitions", "side": "left", "key": True},
            {"at": "block", "text": "*4* layers · ~*0.8M* block weights", "side": "left", "key": True},
            {"at": "sample", "text": "*15 × (N + M + 2) − N* passes per action", "side": "left", "key": True},
            {"at": "sample", "text": "*256* beams · horizon *15* (paper)", "side": "right"},
        ],
        "feedback": "receding horizon",
    },
    "audit": {"date": "2026-10-23", "checked": 46, "stated": 25, "code": 15, "derived": 6, "assumed": 0, "fixed": 10},
}
