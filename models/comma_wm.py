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
    "summary": "The learned driving simulator behind openpilot 0.11, the first shipped driving policy trained entirely inside "
               "a world model. A ViT compressor turns the two camera views into a 32x16x32 latent, and a 2B block-causal "
               "diffusion transformer predicts the next frame latent from 2 s of context, 6-DoF relative-pose actions and "
               "1 s of future frames (so it is also an inverse dynamics model). Sampling is frame by frame with 15 Euler "
               "steps and CFG 2.0; with KV caching comma reports 12.2 frames/s per GPU, a batched training-throughput "
               "number rather than an interactive latency.",
    "facts": [
        ("Representation", "ViT frame compressor (encoder 50M, decoder 100M, 2x deeper): two views (narrow, wide) of 3x128x256 → one "
                           "32x16x32 latent; tokens per frame after DiT patching not stated (512 if one token per 16x32 cell [D, assumption])"),
        ("Core", "2B diffusion transformer: 48 layers, d 1600, 25 heads (n_layer=48, n_head=25, n_embd=1600), 'adapted to 3 dimensional data'"),
        ("Attention", "Block-causal in every layer: tokens attend to their own frame and past frames; a sample = 2 s past context + 1 s "
                      "future conditioning + 0-7 s simulation window at 5 fps (10 context frames [D])"),
        ("Actions", "6-DoF relative positions, diffusion noise level and frame indices injected via AdaLN-single (PixArt-α style)"),
        ("Prediction", "Rectified flow with logit-normal noise sampling; frame by frame, 15 Euler steps, classifier-free guidance 2.0 "
                       "(up to 30 DiT passes per frame if the conditional and unconditional branches run separately [D]); noise-level "
                       "augmentation for rollout robustness"),
        ("Decoder", "ViT decoder (100M) → narrow and wide 128x256 frames"),
        ("Memory", "KV cache enabled by the block-causal mask; context 2 s at 5 fps"),
        ("Speed", "12.2 frames/s per GPU throughput with KV caching (company claim; GPU type not stated); ≈366 DiT frame-evaluations "
                  "per second per GPU at 15 steps × CFG, i.e. batched over rollouts [D]"),
        ("Key detail", "Low-resolution, 5 fps latents make a 2B DiT cheap enough to generate the policy's whole training set; trained on "
                       "2.5M minutes (≈41,700 h [D]) of driving video; weights release not stated on the page"),
    ],
    "evidence": "claim",
    "sources": ["blog.comma.ai/011release (17 Mar 2026): sections Frame Compressor, Diffusion Transformer, sampling and throughput",
                "ar_token_and_physical_ai.md Group 2 (derived counts)"],
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
}
