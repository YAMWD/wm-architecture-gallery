MODEL = {
    "slug": "oasis",
    "name": "Oasis",
    "year": 2024, "month": 10,
    "org": "Decart and Etched",
    "family": "dit",
    "role": "Diffusion transformer",
    "status": "blog post (web technical report)",
    "params": "≈608M DiT (released as 'Oasis 500M'); demo checkpoint larger",
    "params_num": 608e6,
    "open": "code + weights",
    "links": {"page": "https://oasis-model.github.io/", "code": "https://github.com/etched-ai/open-oasis",
              "weights": "https://huggingface.co/Etched/oasis-500m"},
    "tagline": "Open per-frame Minecraft DiT, space-time attention",
    "summary": "An early playable real-time diffusion world model (Minecraft), released with open weights ('Oasis 500M'). A ViT autoencoder maps each "
               "360x640 frame to an 18x32x16 latent, which the DiT patchifies into 144 tokens; the DiT generates one frame at a time with full spatial "
               "attention inside the frame and causal temporal attention over a 32-frame window, trained with "
               "Diffusion Forcing. With context keys and values cached, each pass adds only 144 new tokens, so batch-1 serving "
               "is bound by weight reads rather than by FLOPs (the open reference loop has no cache); Decart's custom kernels and multi-GPU engine behind the 20 fps demo are closed.",
    "facts": [
        ("Representation", "ViT-L/20 KL-VAE: 360x640 frame → 18x32 latent with 16 channels, no temporal compression; "
                           "DiT patch 2 → 144 tokens per frame [D]"),
        ("Core", "DiT-S/2 (open-oasis): 16 blocks, d 1024, 16 heads, MLP ratio 4; each block = spatial attention + MLP, "
                 "then temporal attention + MLP, each pair with its own adaLN; no pretrained video base named"),
        ("Attention", "Factorized: full (bidirectional) spatial attention over the 144 tokens of a frame; causal temporal "
                      "axial attention per spatial position over up to 32 frames; axial RoPE in space, RoPE in time"),
        ("Actions", "25-dim action vector per frame (23 binary key/button flags, several can be on at once, plus 2 "
                    "continuous camera axes in [−1, 1]) → Linear(25, 1024), added to the timestep "
                    "embedding that drives the adaLN modulations"),
        ("Prediction", "Diffusion Forcing (independent noise level per frame), v-prediction, sigmoid beta schedule; "
                       "reference sampler DDIM with 10 steps per frame, context frames held at noise level 14; "
                       "the demo's step count is not disclosed"),
        ("Decoder", "ViT-L/20 decoder (12 layers, width 1024) → 360x640 frame, once per generated frame"),
        ("Memory", "Sliding window of 32 frames; no KV cache in the reference loop, so every DDIM step re-runs the "
                   "whole window (up to 32 × 144 = 4,608 tokens [D]); generated latents join the window directly, with no decode and "
                   "re-encode; blog lists limited long-horizon memory as a known failure"),
        ("Speed", "360p at 20 fps, 47 ms per frame, on NVIDIA H100s (company claim; GPUs per stream and demo checkpoint "
                  "size not disclosed); the open 500M model runs at 2.58 FPS in MineWorld's Table 1 (third party, GPU not stated)"),
        ("Key detail", "Per-frame generation with 144-token passes: ≈0.12 TFLOP per cached pass against ≈1.2 GB of 16-bit "
                       "weights (≈608M params), so single-stream decoding is weight-bandwidth-bound and batching users is the lever [D]"),
    ],
    "evidence": "read",
    "sources": ["open-oasis dit.py (DiT_S_2: hidden 1024, depth 16, 16 heads; external_cond Linear(25, 1024); max_frames 32)",
                "open-oasis attention.py (spatial is_causal=False, temporal is_causal=True)",
                "open-oasis vae.py (ViT-L/20: patch 20, enc 6 / dec 12 layers, width 1024, latent 16)",
                "open-oasis generate.py (DDIM 10 steps, stabilization level 15, 20 fps output)",
                "oasis-model.github.io (Diffusion Forcing, 500M weights, 20 fps)",
                "Decart release article (47 ms per frame on H100s, custom kernels)",
                "MineWorld arXiv 2504.08388 Table 1 (Oasis 500M at 2.58 FPS)"],
    "figure_variant": "Released Oasis small DiT-S/2: 16 space-time pairs, 10 DDIM steps",
    "flow": {
        "below": [{"text": "Frame 360×640 + keys/mouse"}],
        "stack": [
            {"box": "ViT-L/20 VAE encoder", "id": "vae", "style": "teal", "basis": "code"},
            {"group": [
                {"box": "Noisy frame + context", "id": "noisy", "style": "soft", "minor": True, "basis": "code"},
                {"box": "Patchify 2×2", "id": "patch", "minor": True, "basis": "code"},
                {"group": [
                    {"residual": [{"box": "AdaLN", "id": "ada", "side": "Action + timestep", "basis": "code", "side_basis": "code"},
                                  {"box": "Spatial attention (full)", "short": "Spatial attention", "id": "sattn", "style": "dark", "side": "Axial RoPE", "basis": "code", "side_basis": "code"},
                                  {"box": "Scale by gate", "minor": True, "basis": "code"}]},
                    {"residual": [{"box": "AdaLN", "minor": True, "basis": "code"},
                                  {"box": "MLP", "id": "smlp", "minor": True, "basis": "code"},
                                  {"box": "Scale by gate", "minor": True, "basis": "code"}]},
                    {"residual": [{"box": "AdaLN", "minor": True, "basis": "code"},
                                  {"box": "Causal time attention", "id": "tattn", "style": "dark", "side": "RoPE", "basis": "code", "side_basis": "code"},
                                  {"box": "Scale by gate", "minor": True, "basis": "code"}]},
                    {"residual": [{"box": "AdaLN", "minor": True, "basis": "code"},
                                  {"box": "MLP", "short": "MLP (one per attention)", "id": "tmlp", "basis": "code"},
                                  {"box": "Scale by gate", "minor": True, "basis": "code"}]},
                ], "repeat": "16 ×", "id": "block"},
                {"box": "Predicted velocity", "id": "vel", "minor": True, "basis": "code"},
                {"box": "DDIM update", "id": "upd", "minor": True, "basis": "code"},
            ], "loop": "10 DDIM steps", "tint": "grey", "id": "denoise"},
        ],
        "above": [{"box": "ViT-L/20 VAE decoder", "id": "dec", "style": "teal", "basis": "code"}, {"text": "Next frame 360×640"}],
        "insets": [{"for": "tmlp", "stack": [{"box": "Linear", "basis": "code"}, {"box": "GELU", "basis": "code"}, {"box": "Linear", "basis": "code"}]}],
        "annotations": [
            {"at": "vae", "text": "*6*-layer ViT encoder · *18×32×16* latent", "side": "left", "key": True},
            {"at": "ada", "text": "*25*-dim action vector (keys + camera)", "side": "left"},
            {"at": "sattn", "text": "*144* tokens · *16* heads · width *1,024*", "side": "left"},
            {"at": "tattn", "text": "*32*-frame sliding window", "side": "left", "key": True},
            {"at": "block", "text": "*16* layers · *≈608M* parameters", "side": "right", "key": True},
            {"at": "dec", "text": "*12*-layer decoder · width *1,024*", "side": "right", "key": True},
        ],
        "feedback": "latent context",
        "feedback_from": "upd",
        "feedback_to": "noisy",
    },
}
