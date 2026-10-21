MODEL = {
    "slug": "trajectory_transformer",
    "name": "Trajectory Transformer",
    "year": 2021, "month": 6,
    "org": "UC Berkeley",
    "family": "rl",
    "role": "Discrete-token model",
    "status": "NeurIPS 2021",
    "params": "size not disclosed (~0.8M [D])",
    "params_num": None,
    "open": "code + weights",
    "links": {"arXiv": "https://arxiv.org/abs/2106.02039", "code": "https://github.com/jannerm/trajectory-transformer",
              "page": "https://trajectory-transformer.github.io"},
    "summary": "Offline RL as one big sequence-modeling problem: every state dimension, action dimension, the reward and the "
               "reward-to-go are discretized into 100 bins and become separate tokens of a small GPT. There is no "
               "learned encoder and no policy network; acting is beam search over the model's own trajectory "
               "predictions, extended one token at a time. Latency scales with state dimensionality, and the authors note "
               "it can take seconds per action, which rules out real-time control.",
    "facts": [
        ("Representation", "Each of the N state and M action dimensions, the reward and the reward-to-go is one token: "
                           "per-dimension uniform or quantile discretization into V = 100 bins; input vocabulary V × (N + M + 2), "
                           "output logits over V"),
        ("Core", "GPT-style decoder: 4 layers, 4 heads, token embedding d 128, dropout 0.1; parameter count not disclosed "
                 "(~12·4·128² ≈ 0.8M block weights if the MLP is 4× wide [D])"),
        ("Attention", "Causal over all tokens; context 5 transitions of (s, a, r, R) = 5 × (N + M + 2) tokens, e.g. 125 tokens "
                      "for a 17-D state and 6-D action [D]"),
        ("Actions", "Action dimensions are ordinary tokens in the stream, decoded after the state tokens of the same step"),
        ("Prediction", "Next-token softmax, one token per pass, teacher-forced training; planning = beam search, width 256, "
                       "horizon 15 transitions, observations decoded greedily (k_obs 1), actions sampled from the top 20 tokens; "
                       "offline RL ranks transitions by reward plus reward-to-go instead of log-probability"),
        ("Decoder", "None; states are discretized scalars, decoded back by bin centres"),
        ("Memory", "Fixed context of 5 transitions; no KV-cache details given"),
        ("Speed", "'Up to multiple seconds for action selection when the context window grows too large', hardware not stated "
                  "(authors, Sec. 6); training 6-12 h per model on one V100 for 80 epochs (authors, App. A)"),
        ("Key detail", "Per executed action: 15 × (N + M + 2) sequential single-token decodes with the 256 beams batched, e.g. "
                       "375 for HalfCheetah [D]; a latency-bound sub-1M-parameter workload"),
    ],
    "evidence": "read",
    "sources": ["arXiv 2106.02039 Sec. 3.1 (tokenization, 4 layers/4 heads), Sec. 3.2 (beam search, reward-to-go), Algorithm 1, Sec. 6 (seconds per action)",
                "arXiv 2106.02039 App. A (d 128, dropout 0.1, V100 6-12 h), App. E (beam width 256, horizon 15, V 100, context 5, k_obs, k_act)",
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
}
