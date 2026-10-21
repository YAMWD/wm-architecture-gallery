MODEL = {
    "slug": "uwm",
    "name": "UWM (Unified World Models)",
    "year": 2025, "month": 4,
    "org": "University of Washington, TRI",
    "family": "wam",
    "role": "Diffusion transformer",
    "status": "RSS 2025",
    "params": "~85M DiT blocks [D] + ResNet-18",
    "params_num": 85e6,
    "open": "code",
    "links": {"arXiv": "https://arxiv.org/abs/2504.02792", "page": "https://weirdlabuw.github.io/uwm/"},
    "summary": "A small diffusion transformer that couples an action diffusion process and a future-image diffusion process "
               "with two independent timesteps. Fixing a timestep at T marginalises that modality and fixing it at 0 "
               "conditions on it, so one network is a policy, a forward model, an inverse model or a video predictor. The "
               "current frames condition every block through AdaLN (ResNet-18 features), while the future frames are "
               "SDXL-VAE latents patchified into tokens next to 16 action tokens and 8 registers.",
    "facts": [
        ("Representation", "Future observation: 224x224 frames → frozen SDXL VAE → 28x28x4 latents, patchified (4,4,2) → "
                           "49 tokens per camera per 2-frame stack [D]; current observation (h_o = 2 frames per camera) → "
                           "trainable ImageNet-initialised ResNet-18 features, used only as AdaLN conditioning"),
        ("Core", "DiT with AdaLN: depth 12, d 768, 12 heads, MLP ratio 4, 8 register tokens; ~85M in the blocks "
                 "[D: 12 x 12 x 768^2]; trained from scratch, no base video model"),
        ("Attention", "Bidirectional over action tokens + future-image patches + registers; for the 3-camera DROID setup "
                      "16 + 3 x 49 + 8 = 171 tokens [D]; learnable positional embedding"),
        ("Actions", "16-step action chunk, one token per step through a shallow shared MLP; AdaLN carries the two timestep "
                    "embeddings (action, image) and the ResNet features; 8 actions executed before replanning"),
        ("Prediction", "DDPM training with 100 steps, DDIM sampling with 10; policy mode fixes the image timestep at T, so "
                       "the image tokens are pure noise but stay in the sequence"),
        ("Decoder", "SDXL VAE decoder, only when images are sampled (forward dynamics, video); the policy never decodes"),
        ("Memory", "None beyond the 2-frame observation stack"),
        ("Speed", "Inference latency not disclosed; the robot runs at 10 Hz with delta end-effector actions; DROID "
                  "pretraining of 100K steps takes 24 h on 4 A100 (authors)"),
        ("Key detail", "Per chunk ~10 passes of an 85M-parameter block stack over ~171 tokens ≈ 0.3 TFLOP [D]; about 165x "
                       "fewer backbone parameters than DreamZero [D]"),
    ],
    "evidence": "read",
    "sources": ["arXiv 2504.02792 Sec. III-B/C (coupled timesteps, architecture, registers), App. A (implementation, DDIM, "
                "24 h on 4 A100), App. C (10 Hz control), Table V (hyperparameters)"],
    "diagram": {
        "encoder": {"text": "Future frames 224x224 → SDXL VAE; current frames → ResNet-18",
                    "sub": "28x28x4 latents, patch (4,4,2) → 49 tokens per camera", "tag": "pretrained",
                    "short": "SDXL VAE (future) + ResNet-18 (now)"},
        "tokens": {"groups": [("action", 4, "16 actions"), ("latent", 12, "49 patches/camera"),
                              ("register", 3, "8 registers")],
                   "note": "3 cameras: 171 tokens per chunk [D]"},
        "core": {"title": "DiT ×12 · d 768 · 12 heads",
                 "rows": [("attn", "Bidirectional self-attention over actions, image patches and registers"),
                          ("action", "AdaLN: ResNet-18 features + action and image timesteps"),
                          ("mlp", "MLP (ratio 4)")],
                 "notes": ["two independent diffusion timesteps select the mode"]},
        "sampling": {"kind": "diffusion", "text": "DDIM, 10 steps (100 in training)",
                     "sub": "per 16-action chunk; policy fixes the image timestep at T", "short": "DDIM, 10 steps per chunk"},
        "heads": ["action chunk"],
        "decoder": {"text": "SDXL VAE decoder → 224x224 frames", "sub": "only for dynamics and video modes; the policy never decodes",
                    "tag": "frozen", "short": "SDXL VAE decoder (not for policy)"},
    },
}
