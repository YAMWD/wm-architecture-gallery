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
               "compute it is plain long-context LLM decoding, kept affordable by GQA and a 3:1 local/global pattern "
               "(47 layers with an 8k window, 17 with 131k) that allows a KV cache of about 10 GiB per 131k-token "
               "sequence when the local layers keep only their window [D].",
    "tagline": "Code LLM trained to predict execution traces",
    "facts": [
        ("Representation", "Text and code tokens, Llama 3 BPE tokenizer, vocabulary 128,256; an observation is the "
                           "stack-frame locals as JSON, an action is the Python line executed (custom separator tokens)"),
        ("Core", "Dense decoder-only: 64 layers, d 6144, FFN 21,504 (SwiGLU), 48 query heads of 128, 8 KV heads (GQA), "
                 "RMSNorm pre-norm; 32B parameters"),
        ("Attention", "Document-causal; local sliding window 8,192 tokens and global window 131,072 tokens interleaved 3:1, "
                      "with the last layer also global: 47 local + 17 global layers (global at 0, 4, …, 60 and 63; "
                      "Fig. 6a, config); scaled RoPE in every layer, θ 1M, scale factor 16"),
        ("Actions", "Actions are text in the stream (a Python statement or an agent tool call); the next observation is "
                    "generated as text after it"),
        ("Prediction", "Next-token softmax over 128k vocabulary; one pass per token, so one trace step costs as many "
                       "passes as its frame has tokens (locals JSON, separators and the source line)"),
        ("Decoder", "None; the output is text (trace frames, code, tool calls)"),
        ("Memory", "KV cache per token per layer 4 KiB in bf16 (K and V, 8 KV heads × 128); at 131k context 8.5 GiB for "
                   "the 17 global layers + 1.47 GiB for the 47 local layers (8k window) ≈ 10 GiB, vs 32 GiB if every "
                   "layer kept the full context [D]; the released FastGen engine (paged attention, host-side KV cache) "
                   "keeps full-length KV in all 64 layers, 256 KiB per token [D]"),
        ("Speed", "No decode-throughput figure; inference fits one 80 GB H100 with quantization (authors; bf16 weights "
                  "alone are 65 GB [D]); trained on 2,048 H100s for pre- and mid-training (Table 3)"),
        ("Key detail", "13T pre- and mid-training tokens, the last 5T in the code-world-model mid-training stage at 131k "
                       "context (trace and agent data are 30% of that mix); the world model is the LLM itself, so "
                       "running it is long-context LLM decoding"),
    ],
    "evidence": "read",
    "sources": ["arXiv 2510.02387 Sec. 2.2 and App. H (trace format), Sec. 4.1 and Table 2 (architecture), "
                "Fig. 6a (layer pattern: 17 global, 47 local)",
                "arXiv 2510.02387 Sec. 1 (single H100 with quantization), Sec. 6 Table 3 (training GPUs), Sec. 6.2 (FastGen)",
                "github.com/facebookresearch/cwm (commit 7930e02): cwm/model/transformer.py, cwm/fastgen/forward.py, "
                "cwm/fastgen/utils/cache.py (block order, RoPE in every layer, KV allocation)",
                "huggingface.co/facebook/cwm config.json (layer_types: 17 full-attention layers); KV-cache arithmetic is ours [D]"],
    "diagram": {
        "encoder": {"text": "Text and code → Llama 3 tokenizer (128k vocab)",
                    "sub": "observation = stack-frame locals as JSON; action = the Python line executed",
                    "short": "Llama 3 tokenizer, 128k vocab"},
        "tokens": {"groups": [("text", 8, "observation (JSON)"), ("text", 4, "action (code line)")],
                   "note": "free-length text; context up to 131,072 tokens"},
        "core": {"title": "Decoder-only LLM ×64 · d 6144 · 48 heads",
                 "rows": [("attn", "Local window 8,192 (47 layers)"),
                          ("attn", "Global window 131,072 (17 layers)"),
                          ("mlp", "SwiGLU FFN 21,504")],
                 "notes": ["GQA: 48 query heads, 8 KV heads; scaled RoPE", "KV cache ~10 GiB bf16 at 131k context"]},
        "sampling": {"kind": "ar", "text": "Next-token softmax, 128k vocab", "sub": "1 pass per token; a trace step is many tokens",
                     "short": "Next token, 1 pass per token"},
        "decoder": {"none": "output is text: trace frames, code, tool calls"},
        "loop": "AR rollout",
    },
    "flow": {
        "below": [{"text": "Trace: locals JSON + Python line"}],
        "stack": [
            {"box": "Llama 3 BPE tokenizer", "id": "tok", "style": "teal", "basis": "stated"},
            {"box": "Token embedding", "id": "emb", "minor": True, "basis": "stated"},
            {"group": [
                {"residual": [{"box": "RMSNorm", "minor": True, "basis": "stated"},
                              {"box": "Q, K, V projections", "id": "qkv", "side": "Scaled RoPE", "basis": "code",
                               "side_basis": "code"},
                              {"fanout": [[{"box": "Local-window attention", "short": "Local attention", "id": "local", "style": "dark", "basis": "stated"}],
                                          [{"box": "Global-window attention", "short": "Global attention", "id": "global", "style": "dark", "basis": "stated"}]]},
                              {"merge": "or", "id": "pick", "basis": "code"}]},
                {"residual": [{"box": "RMSNorm", "minor": True, "basis": "stated"},
                              {"box": "SwiGLU feed forward", "id": "ffn", "basis": "stated"}]},
            ], "repeat": "64 ×", "id": "block", "basis": "code"},
            {"box": "Final RMSNorm", "minor": True, "basis": "code"},
            {"box": "Linear output layer", "id": "out", "minor": True, "basis": "stated"},
            {"box": "Sample next token", "id": "sample", "basis": "stated"},
        ],
        "above": [{"text": "Next observation as text"}],
        "insets": [{"for": "ffn", "stack": [{"fanout": [[{"box": "Linear", "basis": "code"}],
                                                         [{"box": "Linear", "basis": "code"}, {"box": "SiLU", "basis": "code"}]]},
                                            {"merge": "x", "basis": "code"}, {"box": "Linear", "basis": "code"}]}],
        "annotations": [
            {"at": "tok", "text": "Vocabulary size of *128k*", "side": "left", "key": True},
            {"at": "emb", "text": "Embedding dimension of *6,144*", "side": "left"},
            {"at": "pick", "text": "*8k* local, *131k* global windows, *3:1*", "side": "left", "key": True},
            {"at": "qkv", "text": "*48* query, *8* KV heads", "side": "right"},
            {"at": "block", "text": "*64* layers · *32B* parameters", "side": "right", "key": True},
            {"at": "sample", "text": "*1* pass per token", "side": "left", "key": True},
        ],
        "feedback": "next token",
    },
    "audit": {"date": "2026-10-22", "checked": 48, "stated": 30, "code": 14, "derived": 4, "assumed": 0, "fixed": 7},
}
