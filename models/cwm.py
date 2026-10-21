MODEL = {
    "slug": "cwm",
    "name": "CWM (Code World Model)",
    "year": 2025, "month": 9,
    "org": "Meta FAIR",
    "family": "llm",
    "role": "LLM or mixture of transformers",
    "status": "arXiv preprint (open weights)",
    "params": "32B",
    "params_num": 32e9,
    "open": "code + weights",
    "links": {"arXiv": "https://arxiv.org/abs/2510.02387", "code": "https://github.com/facebookresearch/cwm",
              "weights": "https://huggingface.co/facebook/cwm"},
    "summary": "A 32B dense decoder-only LLM mid-trained on observation-action trajectories: Python execution traces "
               "(stack-frame locals after each executed line) and agentic Docker sessions. The same transformer is "
               "policy and world model; a world-model step is ordinary text generation of the next observation. For "
               "compute it is plain long-context LLM decoding, kept affordable by GQA and a 3:1 mix of 8k local and "
               "131k global sliding-window layers that caps the KV cache at about 9.5 GiB [D].",
    "facts": [
        ("Representation", "Text and code tokens, Llama 3 BPE tokenizer, vocabulary 128,256; an observation is the "
                           "stack-frame locals as JSON, an action is the Python line executed (custom separator tokens)"),
        ("Core", "Dense decoder-only: 64 layers, d 6144, FFN 21,504 (SwiGLU), 48 query heads of 128, 8 KV heads (GQA), "
                 "RMSNorm pre-norm; 32B parameters"),
        ("Attention", "Document-causal; local sliding window 8,192 tokens and global window 131,072 tokens interleaved 3:1 "
                      "(48 local + 16 global layers [D]); scaled RoPE, θ 1M, scale factor 16"),
        ("Actions", "Actions are text in the stream (a Python statement or an agent tool call); the next observation is "
                    "generated as text after it"),
        ("Prediction", "Next-token softmax over 128k vocabulary; one pass per token, so one trace step costs as many "
                       "passes as the JSON frame has tokens"),
        ("Decoder", "None; the output is text (trace frames, code, tool calls)"),
        ("Memory", "KV cache per token per layer 4 KiB in bf16 (8 KV heads × 128); at 131k context ~8 GiB for the 16 "
                   "global layers + ~1.5 GiB for the 48 local layers ≈ 9.5 GiB, vs 32 GiB if all layers were global [D]; "
                   "FastGen serving with paged attention and host-side KV cache"),
        ("Speed", "No decode-throughput figure; inference fits one 80 GB H100 with quantization (authors; bf16 weights "
                  "alone are 64 GB [D]); trained on 2,048 H100s for pre- and mid-training (Table 3)"),
        ("Key detail", "13T training tokens, 5T of them world-model mid-training at 131k context; the world model is the "
                       "LLM itself, so acceleration means long-context, memory-bound decoding"),
    ],
    "evidence": "read",
    "sources": ["arXiv 2510.02387 Sec. 2.2 (trace format), Sec. 4.1 and Table 2 (architecture), Fig. 6a (3:1 layer pattern)",
                "arXiv 2510.02387 Sec. 1 (single H100 with quantization), Sec. 6 Table 3 (training GPUs), Sec. 6.2 (FastGen)",
                "research_notes rl_llm_objectcentric_ssm.md Sec. 2 (KV-cache arithmetic)"],
    "diagram": {
        "encoder": {"text": "Text and code → Llama 3 tokenizer (128k vocab)",
                    "sub": "observation = stack-frame locals as JSON; action = the Python line executed",
                    "short": "Llama 3 tokenizer, 128k vocab"},
        "tokens": {"groups": [("text", 8, "observation (JSON)"), ("text", 4, "action (code line)")],
                   "note": "free-length text; context up to 131,072 tokens"},
        "core": {"title": "Decoder-only LLM ×64 · d 6144 · 48 heads",
                 "rows": [("attn", "Local window 8,192 (48 layers)"),
                          ("attn", "Global window 131,072 (16 layers)"),
                          ("mlp", "SwiGLU FFN 21,504")],
                 "notes": ["GQA: 48 query heads, 8 KV heads; scaled RoPE", "KV cache ~9.5 GiB bf16 at 131k context"]},
        "sampling": {"kind": "ar", "text": "Next-token softmax, 128k vocab", "sub": "1 pass per token; a trace step is many tokens",
                     "short": "Next token, 1 pass per token"},
        "decoder": {"none": "output is text: trace frames, code, tool calls"},
        "loop": "AR rollout",
    },
    "flow": {
        "below": [{"text": "Trace text: locals JSON (observation) + Python line (action)"}],
        "stack": [
            {"box": "Llama 3 BPE tokenizer", "id": "tok", "style": "teal"},
            {"box": "Token embedding", "id": "emb", "minor": True},
            {"group": [
                {"residual": [{"box": "RMSNorm", "minor": True},
                              {"fanout": [[{"box": "Local-window attention (GQA)", "short": "Local-window attention", "id": "local", "style": "dark", "side": "Scaled RoPE"}],
                                          [{"box": "Global-window attention (GQA)", "short": "Global-window attention", "id": "global", "style": "dark"}]]},
                              {"merge": "or"}]},
                {"residual": [{"box": "RMSNorm", "minor": True}, {"box": "SwiGLU feed forward", "id": "ffn"}]},
            ], "repeat": "64 ×", "id": "block"},
            {"box": "Final RMSNorm", "minor": True},
            {"box": "Linear output layer", "id": "out", "minor": True},
            {"box": "Sample next token", "id": "sample"},
        ],
        "above": [{"text": "Next observation as text: JSON frame, code, tool call"}],
        "insets": [{"for": "ffn", "stack": [{"fanout": [[{"box": "Linear"}], [{"box": "Linear"}, {"box": "SiLU"}]]}, {"merge": "x"}, {"box": "Linear"}]}],
        "annotations": [
            {"at": "tok", "text": "vocabulary *128,256*; observations are stack-frame locals as JSON, actions are the Python lines executed", "short": "vocabulary *128,256*; traces as JSON", "side": "left", "key": True},
            {"at": "emb", "text": "width *6,144*", "side": "left"},
            {"at": "global", "text": "*48* query heads, *8* KV heads; windows of *8,192* (local) and *131,072* (global) tokens, interleaved *3:1*", "short": "windows of *8,192* and *131,072*, *3:1*", "side": "right", "key": True},
            {"at": "block", "text": "*64* layers, *32B* parameters; KV cache ≈ *9.5 GiB* at *131k* context [D]", "short": "*64* layers, *32B*; KV ≈ *9.5 GiB* at *131k* [D]", "side": "right", "key": True},
            {"at": "ffn", "text": "FFN width *21,504*; document-causal mask; scaled RoPE θ *1M*, scale factor *16*; *48* local + *16* global layers [D]", "side": "right"},
            {"at": "sample", "text": "*1* pass per token over the *128k* vocabulary: a trace step costs as many passes as its JSON frame has tokens", "side": "left"},
            {"at": "out", "text": "inference fits one 80 GB H100 with quantization (authors); no decode-throughput figure", "side": "right"},
        ],
        "feedback": "next token",
    },
}
