MODEL = {
    "slug": "comma_wm",
    "name": "comma.ai world model (openpilot 0.11)",
    "year": 2026, "month": 3,
    "org": "comma.ai",
    "family": "driving",
    "role": "Diffusion transformer",
    "status": "blog post",
    "params": "2B DiT + 150M compressor",
    "params_num": 2e9,
    "open": "closed",
    "links": {"page": "https://blog.comma.ai/011release/"},
    "tagline": "Block-causal driving DiT that trains openpilot",
    "summary": "The learned driving simulator behind openpilot 0.11, whose driving policy comma calls the first robotics agent "
               "shipped to real users that was fully trained in a learned simulation. A ViT compressor turns the two camera "
               "views into a 32x16x32 latent, and a 2B block-causal diffusion transformer predicts the next frame latent, plus "
               "future actions, from 2 s of context, 6-DoF relative-pose actions and 1 s of future frames (so it is also an "
               "inverse dynamics model). Sampling is frame by frame with 15 Euler steps and CFG 2.0; with KV caching comma "
               "reports a sampling throughput of 12.2 frames/s per GPU (GPU and batch size not stated), not a latency.",
    "facts": [
        ("Representation", "ViT frame compressor (encoder 50M, decoder 100M, 2x deeper): two views (narrow, wide) of 3x128x256 → one "
                           "32x16x32 latent; DiT patch size and tokens per frame not stated (comma's later 4B world model uses 2x2 "
                           "latent patches = 128 tokens per frame)"),
        ("Core", "2B diffusion transformer: 48 layers, d 1600, 25 heads (n_layer=48, n_head=25, n_embd=1600), 'adapted to 3 dimensional data'; "
                 "norm, MLP and residual layout not disclosed, so the diagram draws only AdaLN-single and the attention layer; "
                 "the post does not say what is written to the KV cache or when"),
        ("Attention", "Block-causal in every layer: tokens attend to their own frame and past frames; a sample = 2 s past context + 1 s "
                      "future conditioning + 0-7 s simulation window at 5 fps (10 context frames [D])"),
        ("Actions", "6-DoF relative positions, diffusion noise level and frame indices injected via AdaLN-single (PixArt-α style)"),
        ("Prediction", "Rectified flow with logit-normal noise sampling; frame by frame, 15 Euler steps, classifier-free guidance 2.0 "
                       "(up to 30 DiT passes per frame if the conditional and unconditional branches run separately [D]); noise-level "
                       "augmentation for rollout robustness"),
        ("Decoder", "ViT decoder (100M) → narrow and wide 128x256 frames"),
        ("Memory", "KV cache enabled by the block-causal mask; context 2 s at 5 fps"),
        ("Speed", "12.2 frames/s per GPU throughput with KV caching (company claim; GPU type and batch size not stated); ≈366 DiT "
                  "frame-evaluations per second per GPU at 15 steps × CFG [D]"),
        ("Key detail", "The on-policy driving model (a small transformer) is trained to predict the world model's suggested actions on "
                       "rollouts generated with the world model and the latest policy checkpoint ('near on-policy'); the world model is "
                       "trained on 2.5M minutes (≈41,700 h [D]) of driving video; weights release not stated on the page"),
    ],
    "evidence": "claim",
    "sources": ["blog.comma.ai/011release (17 Mar 2026): sections Frame Compressor, Diffusion Transformer, sampling and throughput",
                "arXiv 2504.19077 (Learning to Drive from a World Model, comma.ai), Sec. 4.2-4.3: RF objective, Euler step, latent rollout",
                "PixArt-α (arXiv 2310.00426), Sec. 2.3: AdaLN-single",
                "huggingface.co/commaai/worldmodel-4B README (later 4B model; patching and KV-cache comparison only)"],
    "diagram": {
        "encoder": {"text": "2 cameras 128x256 → ViT compressor (50M)", "sub": "one 32x16x32 latent per frame at 5 fps", "tag": "frozen",
                    "short": "ViT compressor → 32x16x32 latent"},
        "tokens": {"groups": [("latent", 8, "latent 32x16x32 per frame")],
                   "note": "2 s context + 1 s future at 5 fps"},
        "core": {"title": "DiT ×48 · d 1600 · 25 heads",
                 "rows": [("attn", "Block-causal self-attention"),
                          ("action", "6-DoF pose → AdaLN-single"),
                          ("mlp", "MLP")],
                 "notes": ["KV cache; also conditioned on 1 s of future frames (inverse dynamics)"]},
        "sampling": {"kind": "diffusion", "text": "Rectified flow, 15 Euler steps, CFG 2.0", "sub": "per frame", "short": "15 Euler steps per frame"},
        "decoder": {"text": "ViT decoder (100M) → 2 views at 128x256", "tag": "frozen", "short": "ViT decoder → 2 views"},
        "loop": "AR rollout",
    },
    "flow": {
        "below": [{"text": "2 views 128×256 + 6-DoF pose"}],
        "stack": [
            {"box": "ViT frame compressor", "short": "ViT compressor", "id": "enc", "style": "teal", "basis": "stated"},
            {"box": "Latent 32×16×32", "id": "lat", "minor": True, "basis": "stated"},
            {"group": [
                {"box": "Noisy latent + context", "id": "noisy", "style": "soft", "minor": True, "basis": "stated"},
                {"group": [
                    {"box": "AdaLN-single", "id": "ada", "side": "Pose + noise level",
                     "basis": "stated", "side_basis": "stated"},
                    {"box": "Block-causal attention", "id": "attn", "style": "dark", "basis": "stated"},
                    {"box": "Rest of block not stated", "id": "rest", "style": "soft", "basis": "stated"},
                ], "repeat": "48 ×", "id": "block", "basis": "stated"},
                {"box": "Predicted velocity", "id": "vel", "minor": True, "basis": "stated"},
                {"box": "Euler update with CFG", "id": "upd", "minor": True, "basis": "stated"},
            ], "loop": "15 Euler steps", "tint": "grey", "id": "denoise", "basis": "stated"},
        ],
        "above": [{"box": "ViT decoder", "id": "dec", "style": "teal", "basis": "stated"}, {"text": "Next frame, 2 views at 128×256"}],
        "annotations": [
            {"at": "enc", "text": "One *32×16×32* latent per frame at *5* fps", "side": "left", "key": True},
            {"at": "ada", "text": "*6*-DoF pose, noise level, frame index", "side": "left"},
            {"at": "attn", "text": "*25* heads, width *1,600*", "side": "left"},
            {"at": "block", "text": "*48* layers, *2B* parameters", "side": "right", "key": True},
            {"at": "noisy", "text": "Context of *2* s past + *1* s future frames", "side": "right"},
            {"at": "dec", "text": "*12.2* frames/s per GPU at *15* steps", "side": "right", "key": True},
        ],
        "feedback": "next latent frame",
    },
    "audit": {"date": "2026-10-23", "checked": 42, "stated": 34, "code": 0, "derived": 3, "assumed": 0, "removed": 5, "fixed": 6},
}
