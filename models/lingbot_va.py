MODEL = {
    "slug": "lingbot_va",
    "name": "LingBot-VA",
    "year": 2026, "month": 1,
    "org": "Robbyant",
    "family": "wam",
    "role": "LLM or mixture of transformers",
    "status": "arXiv preprint (v2 Mar 2026)",
    "params": "5.3B (5B video + 0.35B action)",
    "params_num": 5.3e9,
    "open": "code + weights",
    "links": {"arXiv": "https://arxiv.org/abs/2601.21998", "code": "https://github.com/robbyant/lingbot-va",
              "weights": "https://huggingface.co/robbyant/lingbot-va", "page": "https://technology.robbyant.com/lingbot-va"},
    "summary": "A causal world-action model that interleaves video latents and actions in one autoregressive sequence with "
               "a KV cache. Two parallel transformer streams of the same depth, a 5B video stream initialised from Wan2.2-5B "
               "(d 3072) and a 0.35B action stream (d 768), are joined by shared attention. Each step denoises the next chunk "
               "of 4 latent frames with 3 Euler steps only to s = 0.6 (partial denoising, enabled by noisy-history "
               "augmentation), then decodes the 16 actions as inverse dynamics in 10 steps; real observations re-enter the "
               "cache in closed loop.",
    "facts": [
        ("Representation", "Wan2.2 causal VAE (4x16x16) plus 2x patchify; all camera views concatenated along the width → "
                           "192 spatial tokens per latent frame; video at 12.5 Hz with 4 actions per frame (50 Hz)"),
        ("Core", "MoT: video stream from Wan2.2-5B, 30 layers, d 3072 (24 heads, FFN 14,336 per the Wan2.2-TI2V-5B "
                 "config); action stream of the same depth at d 768 (~350M), initialised by interpolating the video weights "
                 "scaled by sqrt(d_v/d_a); RoPE in both; T5 text through cross-attention"),
        ("Attention", "Causal over the interleaved video-action sequence (teacher forcing), bidirectional inside a chunk; "
                      "action tokens are projected to d 3072 for the joint attention and back; training packs episodes "
                      "into sequences of up to 10K tokens"),
        ("Actions", "Action tokens in the sequence (single-layer MLP encoder and decoder, hidden 256; quantile-normalised), "
                    "decoded by inverse dynamics conditioned on the predicted visual transition; chunk K = 4 frames = "
                    "16 actions [D]"),
        ("Prediction", "Flow matching with an Euler solver: video 3 steps to s = 0.6 (partial denoising) at CFG 5.0, actions "
                       "10 steps to s = 1.0 at CFG 1.0; a forward-dynamics step re-grounds the cache on the latest real frame"),
        ("Decoder", "Wan2.2 VAE decoder exists for visualisation, but actions are read from latents and the partially "
                    "denoised video is never decoded for control"),
        ("Memory", "Causal KV cache over the interleaved history; the asynchronous pipeline keeps only the last executed "
                   "chunk, the latest real frame, the executing chunk and its forecast"),
        ("Speed", "Not disclosed: no latency, control rate or GPU is given; the authors name video-token denoising as the "
                  "primary inference bottleneck"),
        ("Key detail", "Per step: 3 video steps x 2 CFG passes = 6 passes of the 5B stream over 768 new tokens, plus "
                       "10 passes of the 0.35B stream [D]"),
    ],
    "evidence": "read",
    "sources": ["arXiv 2601.21998 Sec. 1, 3.2-3.4 (interleaving, MoT block, noisy-history augmentation, KV cache, async "
                "pipeline), Sec. 4.2 (dimensions, VAE, 192 tokens, sampling), Sec. 4 (12.5 Hz video / 50 Hz actions)",
                "Hugging Face Wan-AI/Wan2.2-TI2V-5B config.json (30 layers, d 3072, 24 heads, FFN 14336; fetched)"],
    "diagram": {
        "encoder": {"text": "Frames (views side by side) → Wan2.2 causal VAE",
                    "sub": "4x16x16 + 2x patchify = 192 tokens per latent frame", "tag": "frozen",
                    "short": "Wan2.2 VAE, 192 tokens per frame"},
        "tokens": {"groups": [("latent", 16, "4 × 192 video latents"), ("action", 8, "4 × 4 action tokens")],
                   "note": "per chunk K = 4, interleaved sequence"},
        "core": {"title": "Wan2.2 DiT ×30 · d 3072 · 24 heads",
                 "rows": [("attn", "Causal self-attention over the interleaved sequence, shared by both streams, RoPE"),
                          ("xattn", "Cross-attention to T5 text"),
                          ("moe", "Action stream: same 30 layers at d 768 (~350M), projected into the joint attention"),
                          ("mlp", "Video MLP (FFN 14,336)")],
                 "notes": ["causal KV cache; training sequences up to 10K tokens"]},
        "sampling": {"kind": "diffusion", "text": "Euler flow matching: video 3 steps to s = 0.6, actions 10 steps",
                     "sub": "per chunk; video CFG 5.0, action CFG 1.0", "short": "Video 3 partial steps, actions 10 steps"},
        "heads": ["action chunk"],
        "decoder": {"none": "actions read from latents; the partially denoised video is not decoded for control"},
        "loop": "closed loop with real frames",
    },
    "flow": {
        "below": [{"text": "Frames (views side by side) + text"}],
        "stack": [
            {"box": "Wan2.2 causal VAE encoder", "short": "Wan2.2 VAE encoder", "id": "vae", "style": "teal"},
            {"box": "Patchify (2× spatial)", "id": "patch", "minor": True},
            {"group": [
                {"box": "Interleave noisy video + actions", "short": "Interleave tokens", "id": "seq", "style": "soft", "side": "Action MLP enc."},
                {"group": [
                    {"fanout": [[{"box": "Video QKV", "id": "vqkv", "minor": True}],
                                [{"box": "Action QKV", "id": "aqkv", "style": "orange", "minor": True}]]},
                    {"box": "Shared causal self-attention", "short": "Shared causal attention", "id": "attn", "style": "dark", "side": "RoPE"},
                    {"box": "Cross-attention", "id": "xattn", "side": "T5 text", "minor": True},
                    {"fanout": [[{"box": "Video MLP", "id": "vmlp"}],
                                [{"box": "Action MLP", "id": "amlp", "style": "orange"}]]},
                ], "repeat": "30 ×", "id": "block"},
                {"box": "Euler update", "id": "upd", "minor": True},
            ], "loop": "3 video + 10 action steps", "tint": "grey", "id": "denoise"},
            {"box": "Append chunk to KV cache", "id": "kv", "minor": True},
            {"fanout": [[{"box": "Partly denoised video", "short": "Video latents", "id": "vid", "terminal": True}],
                        [{"box": "Action decoder (linear)", "short": "Action decoder", "id": "act", "style": "orange"}]]},
        ],
        "above": [{"text": "16 actions per chunk; video not decoded", "short": "16 actions per chunk"}],
        "annotations": [
            {"at": "vae", "text": "Wan2.2 causal VAE (*4×16×16*) + *2×* patchify; all views side by side = *192* tokens per latent frame; video at *12.5* Hz",
             "short": "*192* tokens per latent frame, all views together", "side": "left", "key": True},
            {"at": "seq", "text": "each latent frame is followed by its *4* actions (*50* Hz); a chunk of K = *4* frames adds *768* video tokens [D]; single-layer MLP action encoder (hidden *256*)", "side": "left"},
            {"at": "attn", "text": "causal over chunks (teacher forcing), bidirectional inside a chunk; action tokens are projected to d *3,072* for the joint attention and back; training sequences up to *10K* tokens",
             "short": "causal over chunks, bidirectional inside one", "side": "left", "key": True},
            {"at": "xattn", "text": "frozen T5 text through cross-attention (the paper does not say which stream); norms and timestep modulation not detailed", "side": "left"},
            {"at": "amlp", "text": "*30* layers; video stream from Wan2.2-5B (d *3,072*, *24* heads, FFN *14,336*); action stream of the same depth at d *768* (~*350M*), initialised from the video weights; *5.3B* total",
             "short": "*30* layers: video d *3,072* (*5B*) + action d *768* (~*0.35B*)", "side": "right", "key": True},
            {"at": "upd", "text": "Euler flow matching: video *3* steps only to s = *0.6* at CFG *5.0* (*6* passes of the 5B stream [D]), then actions *10* steps to s = *1.0* at CFG *1.0*", "side": "left"},
            {"at": "kv", "text": "causal KV cache over the interleaved history; a forward-dynamics pass re-grounds it on the latest real frame", "side": "right"},
            {"at": "act", "text": "inverse dynamics: actions decoded from the predicted visual transition; latency, control rate and GPU not disclosed (video denoising named as the bottleneck)",
             "short": "*16* actions per chunk [D]; latency not disclosed", "side": "right", "key": True},
        ],
        "feedback": "next chunk",
    },
}
