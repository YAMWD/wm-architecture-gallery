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
    "links": {"arXiv": "https://arxiv.org/abs/2305.14992", "code": "https://github.com/Ber666/llm-reasoners"},
    "summary": "The template for using an off-the-shelf LLM as a world model. A frozen LLaMA-33B is prompted three ways: "
               "as the policy that proposes actions, as the world model that writes the next state in natural language, "
               "and as the reward model. Monte Carlo tree search runs 10-20 iterations over these text states before one "
               "answer is committed. Every tree expansion is a full LLM generation, so inference is serial 33B decoding "
               "inside a search loop, with no training at all.",
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
        ("Prediction", "Sampled next-token decoding at temperature 0.8; one LLM generation per state transition; rewards from "
                       "action log-probability, answer confidence (majority over several samples) and the probability of 'Yes' "
                       "to 'Is this reasoning step correct?'"),
        ("Decoder", "None; states are text"),
        ("Memory", "The MCTS tree stores text states and Q-values; reward prompts hide the history and feed only the current state"),
        ("Speed", "No latency figure; all experiments on 4× NVIDIA A5000 24 GB (authors). Per iteration: d expansions × "
                  "(action proposal + next-state generation + reward queries) plus a roll-out to a terminal state, each a 33B "
                  "decode [D: structural, from Algorithm 1]"),
        ("Key detail", "RAP(20) with LLaMA-33B solves 42% of 6-step Blocksworld tasks vs 40% for GPT-4 CoT; cost grows with "
                       "iterations × depth × branching and is bound by memory-bandwidth-limited decoding"),
    ],
    "evidence": "read",
    "sources": ["arXiv 2305.14992 Sec. 3.1-3.3 (world model, rewards, MCTS), Sec. 4.1 (LLaMA-33B, T 0.8), Table 1",
                "arXiv 2305.14992 App. A (MCTS changes), App. B.1-B.2 (decoding limit, 4× A5000), Algorithm 1",
                "LLaMA arXiv 2302.13971 Table 2 (33B config, fetched from ar5iv to fill the layer/width/head numbers)"],
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
        "below": [{"text": "Prompt: demonstrations + state + action (text)"}],
        "stack": [
            {"box": "LLaMA tokenizer", "id": "tok", "style": "teal"},
            {"box": "Token embedding", "id": "emb", "minor": True},
            {"group": [
                {"residual": [{"box": "RMSNorm", "minor": True},
                              {"box": "Masked self-attention", "id": "attn", "style": "dark", "side": "RoPE"}]},
                {"residual": [{"box": "RMSNorm", "minor": True}, {"box": "SwiGLU feed forward", "id": "ffn"}]},
            ], "repeat": "60 ×", "id": "block"},
            {"box": "Final RMSNorm", "minor": True},
            {"box": "Linear output layer", "id": "out", "minor": True},
            {"box": "Sample next token", "id": "sample"},
        ],
        "above": [{"text": "Next state, action or reward as text"}],
        "insets": [
            {"for": "ffn", "stack": [{"fanout": [[{"box": "Linear"}], [{"box": "Linear"}, {"box": "SiLU"}]]}, {"merge": "x"}, {"box": "Linear"}]},
            {"for": "sample", "label": "MCTS iteration", "stack": [{"box": "Select a leaf by UCT"}, {"box": "Propose d actions (LLM)"},
                                                                    {"box": "Predict next state (LLM)"}, {"box": "Score, back-propagate Q"}]},
        ],
        "annotations": [
            {"at": "tok", "text": "frozen LLaMA-33B, no training; states and actions are natural-language text", "side": "left", "key": True},
            {"at": "attn", "text": "*52* heads, width *6,656*; causal over prompt and generated text, cut at *2,048* tokens or a newline", "side": "left", "key": True},
            {"at": "block", "text": "*60* layers, *32.5B* parameters (LLaMA paper); MCTS: *10–20* iterations of LLM generations", "side": "right", "key": True},
            {"at": "sample", "text": "temperature *0.8*; one full generation per state transition; the same model is policy, world model and reward model", "side": "left"},
            {"at": "out", "text": "rewards: action log-probability, answer confidence, P('Yes' | 'is this step correct?'); runs on 4× A5000 24 GB, no latency figure", "side": "left"},
        ],
        "feedback": "MCTS",
    },
}
