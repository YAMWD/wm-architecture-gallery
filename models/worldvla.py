MODEL = {
    "slug": "worldvla",
    "name": "WorldVLA",
    "year": 2025, "month": 6,
    "org": "Alibaba DAMO Academy",
    "family": "wam",
    "role": "Discrete-token model",
    "status": "arXiv preprint",
    "params": "~7B (Chameleon backbone)",
    "params_num": 7e9,
    "open": "code + weights",
    "links": {"arXiv": "https://arxiv.org/abs/2506.21539", "code": "https://github.com/alibaba-damo-academy/WorldVLA",
              "weights": "https://huggingface.co/Alibaba-DAMO-Academy/WorldVLA"},
    "summary": "A single autoregressive transformer, initialised from Chameleon, that treats images, text and actions as one "
               "token vocabulary: it predicts the next frame's VQ-GAN codes as a world model and the next action's 7 tokens "
               "as a VLA, and training both together improves both. There are no diffusion steps; everything is next-token "
               "decoding, so an action costs 7 serial passes and an imagined frame 256 or 1,024. A custom mask hides the "
               "earlier actions of a chunk so that each action depends only on text and images, which lets the chunk be "
               "generated in parallel.",
    "facts": [
        ("Representation", "VQ-GAN image tokenizer (compression 16, codebook 8192): 256 tokens per 256x256 frame or 1,024 per "
                           "512x512; BPE text; one shared vocabulary of 65,536 including the 8192 image and 256 action tokens"),
        ("Core", "Chameleon-initialised decoder-only LLM; the paper gives no size, the released base_model config.json has "
                 "32 layers, d 4096, 32 heads, FFN 11,008 (~7B; 14 GB of bf16 safetensors [D])"),
        ("Attention", "Causal over text, image and action tokens in world-model mode; in action mode a mask lets each action "
                      "attend to text and images but not to earlier actions of the chunk; default M = 2 input frames"),
        ("Actions", "7 discrete tokens per action (3 relative positions, 3 relative angles, 1 gripper), 256 bins per dimension; "
                    "chunks of K = 5 (K = 10 on LIBERO-Long)"),
        ("Prediction", "Next-token softmax; 7 tokens per action, and the masked chunk can be generated in parallel (authors); "
                       "256 or 1,024 serial passes per generated frame"),
        ("Decoder", "VQ-GAN decoder for predicted image tokens (world-model mode); actions need no decoding"),
        ("Memory", "LLM KV cache over the prompt (history frames + text); 1, 2 or 4 history frames evaluated, 2 by default"),
        ("Speed", "LIBERO, GPU not stated (authors, Table 5): 2.27 / 1.77 / 1.22 FPS with 1 / 2 / 4 history frames without "
                  "chunking, 3.67 / 3.13 / 2.78 FPS with chunking"),
        ("Key detail", "An LLM-style decode workload, token-serial and memory-bandwidth-bound, the opposite profile from the "
                       "diffusion WAMs; each imagined frame is 256 to 1,024 decode steps"),
    ],
    "evidence": "read",
    "sources": ["arXiv 2506.21539 Sec. 3.2 (tokenizers, Chameleon init), 3.3 (attention mask), 4.1 (M = 2, K), 4.3 and "
                "Table 5 (history length, FPS)",
                "Hugging Face Alibaba-DAMO-Academy/WorldVLA base_model/config.json (32 layers, hidden 4096, 32 heads, "
                "FFN 11008, vocab 65536; fetched) and file sizes (2 safetensors, 14.0 GB)",
                "GitHub alibaba-damo-academy/WorldVLA README (now RynnVLA-002; LIBERO checkpoints)"],
    "diagram": {
        "encoder": {"text": "Frame 256x256 or 512x512 → VQ-GAN tokenizer", "sub": "256 or 1,024 codes per frame, codebook 8192",
                    "tag": "pretrained", "short": "VQ-GAN, 256 / 1,024 codes per frame"},
        "tokens": {"groups": [("text", 3, "text"), ("frame", 16, "256–1,024 codes"), ("action", 7, "7 action tokens")],
                   "note": "M = 2 history frames; chunk K = 5"},
        "core": {"title": "Chameleon LLM ×32 · d 4096 · 32 heads",
                 "rows": [("attn", "Causal self-attention; action mask: actions see text + images, not earlier actions"),
                          ("mlp", "MLP (FFN 11,008)")],
                 "notes": ["KV cache over the prompt"]},
        "sampling": {"kind": "ar", "text": "Next-token softmax over 65,536 tokens",
                     "sub": "7 passes per action (chunk in parallel); 256-1,024 per frame",
                     "short": "Next token: 7 per action, 256+ per frame"},
        "decoder": {"text": "VQ-GAN decoder → 256x256 / 512x512 frame", "sub": "world-model mode only", "tag": "pretrained",
                    "short": "VQ-GAN decoder (world-model mode)"},
        "loop": "AR rollout",
    },
    "flow": {
        "below": [{"text": "Text + 2 history frames"}],
        "stack": [
            {"box": "VQ-GAN image tokenizer", "short": "VQ-GAN tokenizer", "id": "tok", "style": "teal"},
            {"box": "One shared vocabulary", "id": "seq", "side": "BPE text, action bins", "minor": True},
            {"box": "Token embedding", "id": "emb", "minor": True},
            {"group": [
                {"residual": [{"box": "Norm", "minor": True}, {"box": "Masked self-attention", "id": "attn", "style": "dark"}]},
                {"residual": [{"box": "Norm", "minor": True}, {"box": "Feed forward", "id": "ffn"}]},
            ], "repeat": "32 ×", "id": "block"},
            {"box": "Final norm", "id": "fnorm", "minor": True},
            {"box": "Linear output layer", "id": "out", "minor": True},
            {"box": "Sample next token", "id": "sample"},
            {"fanout": [[{"box": "Image tokens", "id": "img"}],
                        [{"box": "Action tokens", "id": "act", "style": "orange", "terminal": True}]]},
        ],
        "above": [{"box": "VQ-GAN decoder", "id": "dec", "style": "teal"}, {"text": "Next frame (world-model mode)"}],
        "annotations": [
            {"at": "tok", "text": "VQ-GAN, compression *16*, codebook *8,192*: *256* codes per 256×256 frame, *1,024* per 512×512",
             "short": "*256* codes per 256×256 frame (*1,024* at 512), codebook *8,192*", "side": "left", "key": True},
            {"at": "seq", "text": "one vocabulary of *65,536* incl. *8,192* image and *256* action tokens; *7* tokens per action (3 position, 3 angle, 1 gripper); M = *2* history frames by default", "side": "left"},
            {"at": "attn", "text": "causal over text, image and action tokens; in action mode each action sees text and images but not earlier actions of its chunk",
             "short": "causal; actions do not see earlier actions of their chunk", "side": "left", "key": True},
            {"at": "block", "text": "Chameleon-initialised: *32* layers, d *4,096*, *32* heads, FFN *11,008* (~*7B*, released config); block details not disclosed in the paper",
             "short": "*32* layers, d *4,096*, *32* heads (~*7B*)", "side": "right", "key": True},
            {"at": "sample", "text": "next token over *65,536*: *7* passes per action (a chunk of K = *5* can be generated in parallel), *256* or *1,024* per imagined frame",
             "short": "*7* passes per action, *256*–*1,024* per frame", "side": "right", "key": True},
            {"at": "act", "text": "LIBERO: *3.13* FPS with chunking at *2* history frames (*1.77* without); GPU not stated (authors)", "side": "right"},
            {"at": "dec", "text": "world-model mode only; actions need no decoding", "side": "right"},
        ],
        "feedback": "next token",
    },
}
