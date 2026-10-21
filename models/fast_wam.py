MODEL = {
    "slug": "fast_wam",
    "name": "Fast-WAM",
    "year": 2026, "month": 3,
    "org": "Tsinghua IIIS, Galaxea AI",
    "family": "wam",
    "role": "LLM or mixture of transformers",
    "status": "arXiv preprint (v2 Mar 2026)",
    "params": "6B (5B video DiT + 1B action expert)",
    "params_num": 6e9,
    "open": "closed",
    "links": {"arXiv": "https://arxiv.org/abs/2603.16666", "page": "https://yuantianyuan01.github.io/FastWAM"},
    "summary": "A mixture-of-transformers world-action model that keeps video co-training but drops test-time imagination. "
               "A Wan2.2-5B video DiT and a 1B action-expert DiT (the same architecture at d 1024) share attention; in "
               "training, future video latents and the action chunk are denoised jointly under a structured mask, while at "
               "inference the video DiT runs once over the clean first-frame tokens and the action expert denoises a "
               "32-step chunk in 10 steps. That gives 190 ms per chunk on one RTX 5090D against 810 ms for the "
               "imagine-then-execute variant of the same model.",
    "facts": [
        ("Representation", "Wan2.2 VAE latents of the observation, with the multi-camera images concatenated into one image; "
                           "training video chunks of 9 frames after 4x temporal downsampling; tokens per frame not disclosed"),
        ("Core", "Video DiT from Wan2.2-5B (30 layers, d 3072, 24 heads, FFN 14,336 per its config.json) plus an action "
                 "expert with the same architecture at d 1024 (1B); T5 text reaches all tokens through cross-attention"),
        ("Attention", "Shared attention with a structured mask: clean first-frame tokens attend to nothing else; future video "
                      "tokens (training only) attend within the video branch and to the first frame; action tokens attend "
                      "within the action branch and to the first frame, never to future video"),
        ("Actions", "Action chunk of h = 32 as tokens in the action expert, denoised by flow matching; at inference the "
                    "expert reads the single-pass video features through the shared attention"),
        ("Prediction", "Training: joint flow matching over actions and future video latents (logit-normal t); inference: one "
                       "video-DiT pass over the clean first frame, then 10 action denoising steps at CFG 1.0 (no second pass)"),
        ("Decoder", "None at deployment: no future video tokens are instantiated, denoised or decoded"),
        ("Memory", "Single-chunk policy; the outer autoregressive loop is omitted and no KV cache is described"),
        ("Speed", "190 ms per chunk on one RTX 5090D V2 32 GB (authors); the imagine-then-execute variant Fast-WAM-IDM takes "
                  "810 ms on the same GPU"),
        ("Key detail", "Removing test-time imagination costs little accuracy while removing video co-training costs much; "
                       "the deployed graph is 1 pass of the 5B DiT plus 10 passes of the 1B expert [D]"),
    ],
    "evidence": "read",
    "sources": ["arXiv 2603.16666 Sec. 1, 3 (architecture, mask, inference), 4.1 (Wan2.2-5B, d_a 1024, h 32, 10 steps, CFG 1.0, "
                "RTX 5090D), 4.4 (190 vs 810 ms)",
                "Hugging Face Wan-AI/Wan2.2-TI2V-5B config.json (30 layers, d 3072, 24 heads, FFN 14336; fetched)"],
    "diagram": {
        "encoder": {"text": "Observation (cameras tiled) → Wan2.2 VAE", "sub": "clean first-frame latents; token count not disclosed",
                    "tag": "frozen", "short": "Wan2.2 VAE, first frame only"},
        "tokens": {"groups": [("latent", 16, "clean first-frame latents"), ("action", 8, "32 noisy action tokens")],
                   "note": "training adds noisy future-video tokens"},
        "core": {"title": "Wan2.2 DiT ×30 · d 3072 · 24 heads",
                 "rows": [("attn", "Shared attention, structured mask: actions see the first frame, never future video", "Shared attention, structured mask"),
                          ("xattn", "Cross-attention to T5 text (all tokens)"),
                          ("moe", "Action expert: same architecture at d 1024 (1B)", "Action expert ×30 · d 1024 (1B)"),
                          ("mlp", "Video MLP (FFN 14,336)")],
                 "notes": ["inference: one video pass, no future video tokens"]},
        "sampling": {"kind": "diffusion", "text": "Flow matching, 10 action steps, CFG 1.0",
                     "sub": "after one video-DiT pass over the first frame", "short": "1 video pass + 10 action steps"},
        "heads": ["action chunk"],
        "decoder": {"none": "no future video is denoised or decoded at deployment"},
    },
}
