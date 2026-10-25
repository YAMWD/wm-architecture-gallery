MODEL = {
    "slug": "uwm",
    "name": "UWM (Unified World Models)",
    "year": 2025, "month": 4,
    "org": "University of Washington, TRI",
    "family": "wam",
    "role": "Diffusion transformer",
    "status": "RSS 2025",
    "params": "≈385M + ResNet-18",
    "params_num": 3.85e8,
    "open": "code + weights",
    "links": {"arXiv": "https://arxiv.org/abs/2504.02792", "page": "https://weirdlabuw.github.io/uwm/",
              "code": "https://github.com/WEIRDLabUW/unified-world-model"},
    "tagline": "Two timesteps turn one DiT into policy or dynamics",
    "summary": "A diffusion transformer that couples an action diffusion process and a future-image diffusion process "
               "with two independent timesteps. Fixing a timestep at T marginalises that modality and fixing it at 0 "
               "conditions on it, so one network is a policy, a forward model, an inverse model or a video predictor. The "
               "current frames condition every block through AdaLN (ResNet-18 features), while the future frames are "
               "SDXL-VAE latents patchified into tokens next to 16 action tokens and 8 registers.",
    "facts": [
        ("Representation", "Future observation: 224x224 frames → frozen SDXL VAE → 28x28x4 latents, patchified (4,4,2) → "
                           "49 tokens per camera per 2-frame stack [D]; current observation (h_o = 2 frames per camera) → "
                           "trainable ImageNet-initialised ResNet-18 features, used only as AdaLN conditioning"),
        ("Core", "DiT with AdaLN: depth 12, d 768, 12 heads, MLP ratio 4, 8 register tokens; ≈368M in the 12 blocks [D] "
                 "(85.0M attention + MLP, 283.2M AdaLN modulation from a 5120-d condition), ≈385M for the whole "
                 "denoiser [D] (DROID config, 3 cameras); trained from scratch, no base video model; MLP Linear → "
                 "GELU → Linear (code)"),
        ("Attention", "Bidirectional over action tokens + future-image patches + registers; for the 3-camera DROID setup "
                      "16 + 3 x 49 + 8 = 171 tokens [D]; learnable positional embedding"),
        ("Actions", "16-step action chunk, one token per step through a shallow shared MLP; AdaLN carries the two timestep "
                    "embeddings (action, image) and the ResNet features; 8 actions executed before replanning"),
        ("Prediction", "DDPM training with 100 steps, DDIM sampling with 10; policy mode fixes the image timestep at T "
                       "(paper; the released code uses the first DDIM timestep, 90 of 0-99), so the image tokens are "
                       "pure noise but stay in the sequence"),
        ("Decoder", "SDXL VAE decoder, only when images are sampled (forward dynamics, video); the policy never decodes"),
        ("Memory", "None beyond the 2-frame observation stack"),
        ("Speed", "Inference latency not disclosed; the robot runs at 10 Hz with delta end-effector actions; DROID "
                  "pretraining of 100K steps takes 24 h on 4 A100 (authors)"),
        ("Key detail", "Per chunk 10 passes of the 12-block stack (≈368M parameters, ≈85M of them applied per "
                       "token) over 171 tokens ≈ 0.3 TFLOP [D]; about 36x fewer parameters than DreamZero's 14B [D]"),
    ],
    "evidence": "read",
    "sources": ["arXiv 2504.02792 Sec. III-B/C (coupled timesteps, architecture, registers), App. A (implementation, DDIM, "
                "24 h on 4 A100), App. C (10 Hz control), Table V (hyperparameters)",
                "github.com/WEIRDLabUW/unified-world-model: configs/model/uwm.yaml, configs/dataset/droid.yaml, "
                "models/uwm/uwm.py, models/uwm/obs_encoder.py, models/common/adaln_attention.py, "
                "models/common/attention.py, README (released checkpoints)"],
    "figure_variant": "Released three-camera DROID configuration: 12x768, 10 DDIM steps",
    "flow": {
        "below": [{"text": "Frames 224×224 + actions"}],
        "stack": [
            {"box": "SDXL VAE encoder", "id": "vae", "style": "teal", "basis": "stated"},
            {"group": [
                {"box": "Noisy image latents", "minor": True, "basis": "code"},
                {"box": "Patchify 4×4×2 (3D conv)", "id": "patch", "minor": True, "basis": "stated"},
                {"box": "Tokens + registers", "short": "Token sequence", "id": "seq", "style": "soft", "side": "Action MLP enc.", "basis": "stated", "side_basis": "stated"},
                {"group": [
                    {"residual": [{"box": "AdaLN", "id": "ada", "style": "orange", "side": "ResNet + timesteps", "basis": "stated", "side_basis": "stated"},
                                  {"box": "Bidirectional attention", "id": "attn", "style": "dark", "basis": "code"},
                                  {"box": "Scale by gate", "minor": True, "basis": "code"}]},
                    {"residual": [{"box": "AdaLN", "minor": True, "basis": "code"},
                                  {"box": "MLP", "id": "mlp", "basis": "stated"},
                                  {"box": "Scale by gate", "minor": True, "basis": "code"}]},
                ], "repeat": "12 ×", "id": "block"},
                {"box": "DDIM update", "id": "upd", "minor": True, "basis": "stated"},
            ], "loop": "10 DDIM steps", "tint": "grey", "id": "denoise"},
            {"fanout": [[{"box": "Future image latents", "short": "Future images", "id": "img", "basis": "stated"}],
                        [{"box": "Action chunk", "id": "act", "style": "orange", "terminal": True, "basis": "stated"}]]},
        ],
        "above": [{"box": "SDXL VAE decoder", "id": "dec", "style": "teal", "minor": True, "basis": "stated"}, {"text": "Future frames (not for the policy)"}],
        "annotations": [
            {"at": "vae", "text": "*49* tokens per camera · *2*-frame stack", "side": "left", "key": True},
            {"at": "seq", "text": "*171* tokens (*3* cameras)", "side": "left"},
            {"at": "ada", "text": "*2* frames per camera", "side": "left"},
            {"at": "attn", "text": "*12* heads · width *768*", "side": "left", "key": True},
            {"at": "block", "text": "*12* layers · ≈*385M* in total", "side": "right", "key": True},
            {"at": "act", "text": "*16* actions per chunk · latency not disclosed", "side": "right", "key": True},
        ],
    },
}
