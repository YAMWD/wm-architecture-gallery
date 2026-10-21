MODEL = {
    "slug": "dreamzero",
    "name": "DreamZero",
    "year": 2026, "month": 2,
    "org": "NVIDIA",
    "family": "wam",
    "role": "Diffusion transformer",
    "status": "arXiv preprint (company)",
    "params": "14B (Wan2.1-I2V-14B)",
    "params_num": 14e9,
    "open": "code + weights",
    "links": {"arXiv": "https://arxiv.org/abs/2602.15922", "code": "https://github.com/dreamzero0/dreamzero",
              "page": "https://dreamzero0.github.io"},
    "summary": "A 14B world-action model: the Wan2.1-I2V-14B image-to-video DiT is fully fine-tuned into a chunk-wise "
               "autoregressive flow-matching model that denoises the next 2 latent frames of video and the matching 1.6 s "
               "action chunk together, with one shared timestep and separate output decoders. Clean context sits in a KV "
               "cache of at most 8 latent frames, and after each chunk executes the predicted frames are replaced by "
               "encoded real observations. Naive inference costs 5.7 s per chunk; CFG on 2 GPUs, velocity caching "
               "(16 → 4 steps), compilation, NVFP4 and the 1-step DreamZero-Flash schedule bring it to 150 ms on 2 GB200.",
    "facts": [
        ("Representation", "Frozen Wan2.1 VAE latents (480p model); multi-view inputs tiled into one frame; 8 latent frames = "
                           "33 raw frames (4x temporal); tokens per latent frame not disclosed"),
        ("Core", "Wan2.1-I2V-14B-480P DiT with all blocks fine-tuned: 40 layers, d 5120, 40 heads, FFN 13,824 (base "
                 "config.json); only state and action encoders plus an action decoder are added; text encoder, image "
                 "encoder and VAE stay frozen"),
        ("Attention", "Chunk-causal: the noisy current chunk (K = 2 latent frames + its action chunk) attends to the clean "
                      "previous chunks; frames inside a chunk share one timestep; max context 8 latent frames (4 chunks) = 6.6 s"),
        ("Actions", "Action latents denoised jointly with the video in the same DiT, same timestep; chunks of 48 actions at "
                    "30 Hz (AgiBot) or 24 at 15 Hz (DROID) = 1.6 s; proprioceptive state through a state encoder; relative "
                    "joint positions, Savitzky-Golay smoothed"),
        ("Prediction", "Flow matching: 16 steps baseline → 4 effective with velocity caching (cached velocity reused when "
                       "cosine similarity exceeds a threshold) → 1 step with DreamZero-Flash (video timesteps biased to high "
                       "noise, t = 1 − Beta(7,1); action timesteps uniform)"),
        ("Decoder", "Wan VAE decoder for the predicted video; control does not need it, since predicted frames are replaced by "
                    "encoded real frames (paper does not say whether video is decoded at deployment)"),
        ("Memory", "KV cache bounded at 8 latent frames; refreshed with VAE-encoded real observations after every chunk"),
        ("Speed", "5.7 s per chunk naive on one GPU; 9.6x on one H100 (~0.59 s [D]); 16.6x with NVFP4 (~350 ms at 4 steps) "
                  "and 38x with Flash (150 ms at 1 step, ~7 Hz) on 2 GB200 with CFG split across the GPUs (company claims, "
                  "Tables 1 and 3)"),
        ("Key detail", "Generating actions only does not help at 14B (steps x blocks dominate); the 38x comes from step count "
                       "(16 → 1), 2-GPU CFG, CUDA graphs and NVFP4 (E2M1 weights and activations, FP8 QKV and softmax)"),
    ],
    "evidence": "read",
    "sources": ["arXiv 2602.15922 Sec. 3 (architecture, inference), Sec. 3.2 (optimizations), Table 1 (speedups), Table 3 "
                "(Flash), Sec. 4 (training), App. C (chunking, context), App. D (CFG parallelism, caching, NVFP4)",
                "Hugging Face Wan-AI/Wan2.1-I2V-14B-480P config.json (40 layers, d 5120, 40 heads, FFN 13824; fetched)"],
    "diagram": {
        "encoder": {"text": "Frames (views tiled) → Wan2.1 VAE", "sub": "4x temporal; tokens per latent frame not disclosed",
                    "tag": "frozen", "short": "Wan2.1 VAE, views tiled"},
        "tokens": {"groups": [("latent", 16, "2 noisy latent frames"), ("action", 8, "48-action chunk (1.6 s)")],
                   "note": "per chunk; cache ≤ 8 clean latent frames"},
        "core": {"title": "Wan2.1 I2V DiT ×40 · d 5120 · 40 heads",
                 "rows": [("attn", "Chunk-causal self-attention: noisy chunk → clean cached chunks", "Chunk-causal attention, cached chunks"),
                          ("xattn", "Cross-attention to text and image-encoder features", "Cross-attention: text + image features"),
                          ("action", "Action latents denoised in the same blocks, shared timestep", "Action latents denoised jointly"),
                          ("mlp", "MLP (FFN 13,824)")],
                 "notes": ["KV cache ≤ 8 latent frames, refreshed with real frames"]},
        "sampling": {"kind": "diffusion", "text": "Flow matching, 16 → 4 cached → 1 step (Flash)",
                     "sub": "per chunk; CFG passes on 2 GPUs", "short": "Flow matching, 4 or 1 step"},
        "heads": ["action chunk"],
        "decoder": {"text": "Wan VAE decoder → video frames", "sub": "not needed for control: real frames replace predictions",
                    "tag": "frozen", "short": "Wan VAE decoder (optional)"},
        "loop": "closed loop with real frames",
    },
}
