MODEL = {
    "slug": "lingbot_va",
    "name": "LingBot-VA",
    "year": 2026, "month": 1,
    "org": "Robbyant",
    "family": "wam",
    "role": "LLM or mixture of transformers",
    "status": "RSS 2026 (arXiv 2601.21998, v2 Mar 2026)",
    "params": "5.3B (5B video + 0.35B action)",
    "params_num": 5.3e9,
    "open": "code + weights (shared-backbone variant only)",
    "links": {"arXiv": "https://arxiv.org/abs/2601.21998", "code": "https://github.com/robbyant/lingbot-va",
              "weights": "https://huggingface.co/robbyant/lingbot-va", "page": "https://technology.robbyant.com/lingbot-va"},
    "tagline": "Interleaves video and actions in one causal sequence",
    "summary": "A causal world-action model that interleaves video latents and actions in one autoregressive sequence with "
               "a KV cache. Two parallel transformer streams of the same depth, a 5B video stream initialised from Wan2.2-5B "
               "(d 3072) and a 0.35B action stream (d 768), are joined by shared attention. Each step denoises the next chunk "
               "(K = 4) with 3 Euler steps only to s = 0.6 (partial denoising, enabled by noisy-history "
               "augmentation), then decodes the chunk's actions (τK = 16 by the paper's formula) as inverse dynamics "
               "in 10 steps; real observations re-enter the "
               "cache in closed loop.",
    "facts": [
        ("Representation", "Wan2.2 causal VAE (4x16x16) plus 2x patchify; all camera views concatenated along the width → "
                           "192 spatial tokens per latent frame; video at 12.5 Hz with 4 actions per frame (50 Hz)"),
        ("Core", "MoT: video stream from Wan2.2-5B, 30 layers, d 3072 (24 heads, FFN 14,336 per the Wan2.2-TI2V-5B "
                 "config); action stream of the same depth at d 768 (~350M), initialised by interpolating the video weights "
                 "scaled by sqrt(d_v/d_a); RoPE in both; T5 text through cross-attention (which stream reads it is not "
                 "stated); norms and timestep modulation not given in the paper"),
        ("Attention", "Causal over the interleaved video-action sequence (teacher forcing), bidirectional inside a chunk; "
                      "action tokens are projected to d 3072 for the joint attention and back; training packs episodes "
                      "into sequences of up to 10K tokens"),
        ("Actions", "Action tokens in the sequence (single-layer MLP encoder and decoder, hidden 256; quantile-normalised), "
                    "decoded by inverse dynamics conditioned on the predicted visual transition; chunk K = 4 video frames = "
                    "τK = 16 actions by the paper's formula [D]; released configs give 16-80 actions per chunk"),
        ("Prediction", "Flow matching with an Euler solver: video 3 steps to s = 0.6 (partial denoising) at CFG 5.0, actions "
                       "10 steps to s = 1.0 at CFG 1.0; a forward-dynamics step re-grounds the cache on the latest real frame"),
        ("Decoder", "Wan2.2 VAE decoder exists for visualisation, but actions are read from latents and the partially "
                    "denoised video is never decoded for control"),
        ("Memory", "Causal KV cache over the interleaved history (released server: FIFO of the last 36 chunks for "
                   "RoboTwin, 15 otherwise); the async-pipeline prose limits the active context to the last step, "
                   "but Alg. 2 and Sec. 4.5.2 keep all cached history"),
        ("Speed", "Not disclosed: no latency, control rate or GPU is given; the authors name video-token denoising as the "
                  "primary inference bottleneck"),
        ("Key detail", "Per chunk: 3 video steps x 2 CFG passes = 6 passes of the 5B stream over the new video tokens "
                       "(768 if K = 4 latent frames of 192), plus 10 passes of the 0.35B stream, plus a cache-write "
                       "pass over the encoded real frames and executed actions [D]"),
    ],
    "evidence": "read",
    "sources": ["arXiv 2601.21998 Sec. 1, 3.2-3.4 (interleaving, MoT block, noisy-history augmentation, KV cache, async "
                "pipeline), Sec. 4.2 (dimensions, VAE, 192 tokens, sampling), Sec. 4 (12.5 Hz video / 50 Hz actions)",
                "Hugging Face Wan-AI/Wan2.2-TI2V-5B config.json (30 layers, d 3072, 24 heads, FFN 14336)",
                "github.com/robbyant/lingbot-va README, wan_va/configs/*.py, modules/model.py, wan_va_server.py",
                "Project page technology.robbyant.com/lingbot-va (RSS 2026)"],
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
        "below": [{"text": "Camera views + task text"}],
        "stack": [
            {"box": "Wan2.2 causal VAE", "id": "vae", "style": "teal", "basis": "stated"},
            {"box": "Patchify (2× spatial)", "id": "patch", "minor": True, "basis": "stated"},
            {"group": [
                {"box": "Interleave noisy tokens", "short": "Interleave tokens", "id": "seq", "style": "soft", "side": "Action MLP enc.", "basis": "stated", "side_basis": "stated"},
                {"group": [
                    {"fanout": [[{"box": "Video QKV", "id": "vqkv", "minor": True, "basis": "stated"}],
                                [{"box": "Action QKV", "id": "aqkv", "style": "orange", "minor": True, "basis": "stated"}]]},
                    {"box": "Shared causal attention", "id": "attn", "style": "dark", "side": "RoPE", "basis": "stated", "side_basis": "stated"},
                    {"box": "Cross-attention", "id": "xattn", "side": "T5 text", "minor": True, "basis": "stated", "side_basis": "stated"},
                    {"fanout": [[{"box": "Video MLP", "id": "vmlp", "basis": "stated"}],
                                [{"box": "Action MLP", "id": "amlp", "style": "orange", "basis": "stated"}]]},
                ], "repeat": "30 ×", "id": "block", "basis": "code"},
                {"box": "Action head (linear)", "id": "ahead", "style": "orange", "minor": True, "basis": "stated"},
                {"box": "Euler update", "id": "upd", "minor": True, "basis": "stated"},
            ], "loop": "3 + 10 Euler steps", "loop_short": "3 + 10 steps", "tint": "grey", "id": "denoise", "basis": "stated"},
            {"box": "Append chunk to KV cache", "id": "kv", "minor": True, "basis": "code"},
            {"fanout": [[{"box": "Partly denoised video", "short": "Video latents", "id": "vid", "terminal": True, "basis": "stated"}],
                        [{"box": "De-normalise actions", "id": "act", "style": "orange", "basis": "code"}]]},
        ],
        "above": [{"text": "16 actions; video not decoded"}],
        "annotations": [
            {"at": "vae", "text": "*192* tokens per latent frame = *4* video frames", "side": "left", "key": True},
            {"at": "seq", "text": "*4* actions per video frame (≈*16* per latent)", "side": "left"},
            {"at": "attn", "text": "*24* heads · width *3,072* (actions *768*)", "side": "left"},
            {"at": "block", "text": "*30* layers · *5.3B* parameters", "side": "right", "key": True},
            {"at": "denoise", "text": "Video *3* steps to s = *0.6*, actions *10* steps", "side": "right", "key": True},
            {"at": "act", "text": "Latency not disclosed", "side": "right", "key": True},
        ],
        "feedback": "next chunk",
    },
    "audit": {"date": "2026-10-23", "checked": 47, "stated": 40, "code": 4, "derived": 3, "assumed": 0, "fixed": 8},
}
