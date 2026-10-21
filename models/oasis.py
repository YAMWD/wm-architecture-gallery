MODEL = {
    "slug": "oasis",
    "name": "Oasis",
    "year": 2024, "month": 10,
    "org": "Decart and Etched",
    "family": "dit",
    "role": "Diffusion transformer",
    "status": "blog post (web technical report)",
    "params": "500M (demo checkpoint larger)",
    "params_num": 500e6,
    "open": "code + weights",
    "links": {"page": "https://oasis-model.github.io/", "code": "https://github.com/etched-ai/open-oasis",
              "weights": "https://huggingface.co/Etched/oasis-500m"},
    "summary": "An early playable real-time diffusion world model (Minecraft), released with open 500M weights. A ViT autoencoder maps each "
               "360x640 frame to 144 latent tokens, and a small DiT generates one frame at a time with full spatial "
               "attention inside the frame and causal temporal attention over a 32-frame window, trained with "
               "Diffusion Forcing. Each pass carries only 144 tokens, so batch-1 serving is bound by weight reads "
               "rather than by FLOPs; Decart's custom kernels and multi-GPU engine behind the 20 fps demo are closed.",
    "facts": [
        ("Representation", "ViT-L/20 KL-VAE: 360x640 frame → 18x32 latent with 16 channels, no temporal compression; "
                           "DiT patch 2 → 144 tokens per frame [D]"),
        ("Core", "DiT-S/2 (open-oasis): 16 blocks, d 1024, 16 heads, MLP ratio 4; each block = spatial attention + MLP, "
                 "then temporal attention + MLP, each pair with its own adaLN; no pretrained video base named"),
        ("Attention", "Factorized: full (bidirectional) spatial attention over the 144 tokens of a frame; causal temporal "
                      "axial attention per spatial position over up to 32 frames; axial RoPE in space, RoPE in time"),
        ("Actions", "25-dim one-hot keyboard and mouse vector per frame → Linear(25, 1024), added to the timestep "
                    "embedding that drives the adaLN modulations"),
        ("Prediction", "Diffusion Forcing (independent noise level per frame), v-prediction, sigmoid beta schedule; "
                       "reference sampler DDIM with 10 steps per frame, context frames held at noise level 14; "
                       "the demo's step count is not disclosed"),
        ("Decoder", "ViT-L/20 decoder (12 layers, width 1024) → 360x640 frame, once per generated frame"),
        ("Memory", "Sliding window of 32 frames; no KV cache in the reference loop, so every DDIM step re-runs the "
                   "whole window (up to 32 × 144 = 4,608 tokens [D]); blog lists limited long-horizon memory as a known failure"),
        ("Speed", "360p at 20 fps, 47 ms per frame, on NVIDIA H100s (company claim; GPUs per stream and demo checkpoint "
                  "size not disclosed); the open 500M model runs at 2.58 FPS in MineWorld's Table 1 (third party, GPU not stated)"),
        ("Key detail", "Per-frame generation with 144-token passes: ≈0.12 TFLOP per cached pass against ≈1 GB of BF16 "
                       "weights, so single-stream decoding is weight-bandwidth-bound and batching users is the lever [D]"),
    ],
    "evidence": "read",
    "sources": ["open-oasis dit.py (DiT_S_2: hidden 1024, depth 16, 16 heads; external_cond Linear(25, 1024); max_frames 32)",
                "open-oasis attention.py (spatial is_causal=False, temporal is_causal=True)",
                "open-oasis vae.py (ViT-L/20: patch 20, enc 6 / dec 12 layers, width 1024, latent 16)",
                "open-oasis generate.py (DDIM 10 steps, stabilization level 15, 20 fps output)",
                "oasis-model.github.io (Diffusion Forcing, 500M weights, 20 fps)",
                "Decart release article (47 ms per frame on H100s, custom kernels)",
                "MineWorld arXiv 2504.08388 Table 1 (Oasis 500M at 2.58 FPS)"],
    "diagram": {
        "encoder": {"text": "Frame 360x640 → ViT-L/20 VAE (6-layer encoder)", "sub": "18x32x16 latent, patch 2 → 144 tokens per frame",
                    "short": "ViT-L/20 VAE, 144 tokens per frame"},
        "tokens": {"groups": [("latent", 144, "144 latents per frame")],
                   "note": "window 32 frames = 4,608 tokens, no KV cache"},
        "core": {"title": "DiT ×16 · d 1024 · 16 heads",
                 "rows": [("attn", "Spatial attention, full per frame"),
                          ("attn", "Temporal axial attention, causal"),
                          ("action", "25-dim action → Linear → adaLN"),
                          ("mlp", "MLP, one after each attention")],
                 "notes": ["32-frame window re-run every step: no KV cache",
                           "axial RoPE in space, RoPE in time"]},
        "sampling": {"kind": "diffusion", "text": "Diffusion Forcing, DDIM 10 steps (reference sampler)",
                     "sub": "per frame; demo sampler not disclosed", "short": "DDIM 10 steps per frame"},
        "decoder": {"text": "ViT-L/20 decoder → 360x640 frame", "sub": "12 layers, width 1024, one frame per step"},
        "loop": "AR rollout",
    },
}
