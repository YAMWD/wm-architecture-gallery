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
    "flow": {
        "below": [{"text": "Current + future frames 224×224 + actions", "short": "Frames 224×224 + actions"}],
        "stack": [
            {"box": "SDXL VAE encoder (frozen)", "short": "SDXL VAE encoder", "id": "vae", "style": "teal"},
            {"box": "Patchify 4×4×2 (3D conv)", "id": "patch", "minor": True},
            {"group": [
                {"box": "Actions + patches + registers", "short": "Token sequence", "id": "seq", "style": "soft", "side": "Action MLP enc."},
                {"group": [
                    {"residual": [{"box": "AdaLN", "id": "ada", "style": "orange", "side": "ResNet-18 + timesteps"},
                                  {"box": "Bidirectional self-attention", "short": "Bidirectional attention", "id": "attn", "style": "dark"}]},
                    {"residual": [{"box": "AdaLN", "minor": True}, {"box": "MLP", "id": "mlp"}]},
                ], "repeat": "12 ×", "id": "block"},
                {"box": "DDIM update", "id": "upd", "minor": True},
            ], "loop": "10 DDIM steps", "tint": "grey", "id": "denoise"},
            {"fanout": [[{"box": "Future image latents", "short": "Future images", "id": "img"}],
                        [{"box": "Action chunk", "id": "act", "style": "orange", "terminal": True}]]},
        ],
        "above": [{"box": "SDXL VAE decoder", "id": "dec", "style": "teal", "minor": True}, {"text": "Future frames (not used by the policy)", "short": "Future frames (not for the policy)"}],
        "annotations": [
            {"at": "vae", "text": "frozen SDXL VAE: future 224×224 frames → 28×28×4 latents, patch (4,4,2) → *49* tokens per camera per 2-frame stack [D]",
             "short": "SDXL VAE: *49* tokens per camera per 2-frame stack [D]", "side": "left", "key": True},
            {"at": "seq", "text": "*16* action tokens (shallow shared MLP) + *49* patches per camera + *8* registers, learnable positional embedding: *171* tokens with *3* cameras [D]", "side": "left"},
            {"at": "ada", "text": "current frames (*2* per camera) → trainable ResNet-18; its features + the action and image timestep embeddings drive AdaLN in every block",
             "short": "AdaLN: ResNet-18 features + *2* timestep embeddings", "side": "left", "key": True},
            {"at": "attn", "text": "*12* heads, width *768*; bidirectional over action tokens, image patches and registers", "side": "left"},
            {"at": "mlp", "text": "*12* layers, d *768*, MLP ratio *4* (activation not stated); ~*85M* in the blocks [D]; trained from scratch",
             "short": "*12* layers, d *768*, *12* heads; ~*85M* [D]", "side": "right", "key": True},
            {"at": "upd", "text": "DDIM, *10* steps (*100* in training); the policy fixes the image timestep at T, so the image tokens stay in the sequence as pure noise", "side": "right"},
            {"at": "act", "text": "*16* actions per chunk, *8* executed, robot at *10* Hz; inference latency not disclosed",
             "short": "*16* actions per chunk; latency not disclosed", "side": "right", "key": True},
            {"at": "dec", "text": "only in forward-dynamics and video modes; the policy never decodes", "side": "right"},
        ],
    },
}
