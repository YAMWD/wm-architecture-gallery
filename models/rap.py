MODEL = {
    "slug": "rap",
    "name": "RAP (Reasoning via Planning)",
    "year": 2023, "month": 5,
    "org": "UC San Diego",
    "family": "llm",
    "role": "LLM or mixture of transformers",
    "status": "EMNLP 2023",
    "params": "33B (LLaMA-33B, frozen)",
    "params_num": 32.5e9,
    "open": "code",
    "links": {"arXiv": "https://arxiv.org/abs/2305.14992", "code": "https://github.com/maitrix-org/llm-reasoners"},
    "tagline": "Frozen LLM as world model inside tree search",
    "summary": "Uses an off-the-shelf LLM as a world model. A frozen LLaMA-33B is prompted three ways: "
               "as the policy that proposes actions, as the world model that writes the next state in natural language, "
               "and as the reward model. Monte Carlo tree search runs 10-20 iterations over these text states before one "
               "answer is committed. Every tree expansion costs several 33B LLM calls (action proposals, next-state "
               "generation, reward scoring) inside a sequential search loop, with no training at all.",
    "facts": [
        ("Representation", "A state is natural-language text: the block configuration (Blocksworld), the values of intermediate "
                           "variables (GSM8k) or the current fact (PrOntoQA); an action is a text step (a block move, a "
                           "sub-question, a rule)"),
        ("Core", "LLaMA-33B used frozen with prompts (60 layers, d 6656, 52 heads, 32.5B; LLaMA paper Table 2); the same model "
                 "serves as policy, world model and reward model; Llama-2 70B in the full-Blocksworld experiment"),
        ("Attention", "Ordinary causal LLM attention over prompt (in-context demonstrations + state) and generated text; each "
                      "generation is cut at 2,048 tokens or a newline"),
        ("Actions", "Text in the prompt: the world model is queried with (state, action) and writes the next state; the "
                    "policy samples d candidate actions per expansion"),
        ("Prediction", "Sampled next-token decoding at temperature 0.8; one LLM generation per transition in Blocksworld and "
                       "PrOntoQA, several sampled answers per transition in GSM8k; rewards from action log-probability, "
                       "answer confidence (share of the most frequent sampled answer) and the probability of 'Yes' "
                       "to 'Is this reasoning step correct?'"),
        ("Decoder", "None; states are text"),
        ("Memory", "The MCTS tree stores text states and Q-values; reward prompts hide the history and feed only the current state"),
        ("Speed", "No latency figure; all experiments on 4× NVIDIA A5000 24 GB (authors). Per iteration: d expansions × "
                  "(action proposal + next-state generation + reward) plus a roll-out to a terminal state [D: structural, "
                  "from Algorithm 1]; the log-prob and 'Yes' rewards are single scoring passes, not decodes (released code)"),
        ("Key detail", "RAP(20) with LLaMA-33B solves 42% of 6-step Blocksworld tasks vs 40% for GPT-4 CoT; cost grows with "
                       "iterations × depth × branching [D: Algorithm 1 loops]"),
    ],
    "evidence": "read",
    "sources": ["arXiv 2305.14992 Sec. 3.1-3.3 (world model, rewards, MCTS), Sec. 4.1 (LLaMA-33B, T 0.8), Table 1",
                "arXiv 2305.14992 App. A (MCTS changes), App. B.1-B.2 (decoding limit, 4× A5000), Algorithm 1",
                "LLaMA arXiv 2302.13971 Sec. 2 and Table 2 (33B config); LLaMA v1 model.py",
                "llm-reasoners code: examples/rap_gsm8k/world_model.py, reasoners/lm/llama_model.py"],
    "diagram": {
        "encoder": {"text": "Prompt text → LLaMA tokenizer", "sub": "in-context demonstrations + state + action, all natural language",
                    "short": "Text prompt → LLaMA tokenizer"},
        "tokens": {"groups": [("text", 8, "state (text)"), ("text", 4, "action (text)")],
                   "note": "one LLM generation per transition, ≤ 2,048 tokens"},
        "core": {"title": "LLaMA-33B (frozen, prompted)",
                 "rows": [("attn", "Causal self-attention, RoPE"),
                          ("mlp", "SwiGLU MLP")],
                 "notes": ["60 layers · d 6656 · 52 heads (LLaMA paper)", "one LLM: policy, world model and reward"]},
        "sampling": {"kind": "search", "text": "MCTS over text states, 10–20 iterations",
                     "sub": "per expansion: d actions × (propose + next state + reward), T 0.8",
                     "short": "MCTS, 10–20 iterations"},
        "decoder": {"none": "states are text"},
        "loop": "MCTS",
    },
    "flow": {
        "below": [{"text": "Prompt: examples + state + action"}],
        "stack": [
            {"box": "LLaMA tokenizer", "id": "tok", "style": "teal", "basis": "stated"},
            {"box": "Token embedding", "id": "emb", "minor": True, "basis": "code"},
            {"group": [
                {"residual": [{"box": "RMSNorm", "minor": True, "basis": "stated"},
                              {"box": "Masked self-attention", "id": "attn", "style": "dark", "side": "RoPE",
                               "basis": "stated", "side_basis": "stated"}]},
                {"residual": [{"box": "RMSNorm", "minor": True, "basis": "stated"}, {"box": "SwiGLU feed forward", "id": "ffn", "basis": "stated"}]},
            ], "repeat": "60 ×", "id": "block", "basis": "code"},
            {"box": "Final RMSNorm", "minor": True, "basis": "code"},
            {"box": "Linear output layer", "id": "out", "minor": True, "basis": "code"},
            {"box": "Sample next token", "id": "sample", "basis": "stated"},
        ],
        "above": [{"text": "Next state, action or reward"}],
        "insets": [
            {"for": "ffn", "stack": [{"fanout": [[{"box": "Linear", "basis": "code"}], [{"box": "Linear", "basis": "code"}, {"box": "SiLU", "basis": "code"}]]},
                                    {"merge": "x", "basis": "code"}, {"box": "Linear", "basis": "code"}]},
            {"for": "sample", "label": "MCTS iteration", "stack": [{"box": "Select a leaf by UCT", "basis": "stated"},
                                                                    {"box": "Propose d actions (LLM)", "basis": "stated"},
                                                                    {"box": "Predict next state (LLM)", "basis": "stated"},
                                                                    {"box": "Roll out to terminal", "basis": "stated"},
                                                                    {"box": "Score, back-propagate Q", "basis": "stated"}]},
        ],
        "annotations": [
            {"at": "attn", "text": "*52* heads, width *6,656*", "side": "left", "key": True},
            {"at": "block", "text": "*60* layers, *32.5B* parameters, frozen", "side": "left", "key": True},
            {"at": "out", "text": "≤ *2,048* tokens per call, cut at newline", "side": "left"},
            {"at": "sample", "text": "*10–20* MCTS iterations per answer", "side": "left", "key": True},
        ],
        "feedback": "MCTS",
    },
    "audit": {"date": "2026-10-23", "checked": 47, "stated": 34, "code": 12, "derived": 1, "assumed": 0, "fixed": 7},
}
