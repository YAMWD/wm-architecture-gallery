MODEL = {
    "slug": "aapt",
    "name": "AAPT",
    "year": 2025, "month": 6,
    "org": "ByteDance Seed",
    "family": "dit",
    "role": "Diffusion transformer",
    "status": "NeurIPS 2025",
    "params": "8B (36 blocks)",
    "params_num": 8e9,
    "open": "closed",
    "links": {"arXiv": "https://arxiv.org/abs/2506.09350", "page": "https://seaweed-apt.com/2"},
    "tagline": "Causal DiT, one adversarial pass per latent frame",
    "summary": "Autoregressive Adversarial Post-Training, the one-pass-per-frame design: a pre-trained 8B video diffusion transformer is made block-causal and "
               "post-trained adversarially so that each latent frame (4 video frames) is generated with a single network "
               "evaluation from noise, the previous generated frame recycled through channel concatenation, and a KV cache "
               "over a sliding window of 30 latent frames. Per-frame conditions (human pose, or camera rays relative to the "
               "previous frame) enter as extra input channels. The authors report 24 fps at 736x416 on one H100 with 0.16 s "
               "latency, or 1280x720 on 8 H100s, for streams up to a minute.",
    "facts": [
        ("Representation", "Causal 3D convolution VAE, 4x temporal and 8x spatial; one latent frame = 4 video frames, the first frame its "
                           "own latent; DiT patch size not stated, so tokens per frame are not computed (latent grid 92x52 at 736x416 [D])"),
        ("Core", "8B MMDiT-style diffusion transformer with 36 blocks (base model not named); width and heads not stated; inputs are text "
                 "embedding tokens, noisy visual tokens and diffusion timesteps (Sec. 2.1), with text and visual tokens in one sequence; "
                 "where the timestep enters the block, and its value in the 1-NFE generator, are not stated (listed with the figure "
                 "inputs only); the discriminator reuses the same causal architecture (generator + discriminator "
                 "= 16B in training); norm, FFN and residual layout not stated, so the diagram draws only the attention layer"),
        ("Attention", "Block-causal: text tokens attend only to themselves, visual tokens to the text tokens and to visual tokens of the "
                      "current and previous frames; window N = 30 latent frames (5 s; N = 15 at 1280x720) plus the text tokens and the "
                      "first frame always; FlashAttention-3; 3D RoPE with a fixed temporal interval for arbitrary length"),
        ("Actions", "Each step channel-concatenates noise k, condition k and the previous generated latent frame (the encoded user frame "
                    "at step 1); camera: ray origin and direction relative to the previous frame (modified CameraCtrl II) as new input "
                    "channels with a randomly initialized input projection; pose: per-frame condition following OmniHuman-1; the "
                    "discriminator shifts the conditions to align with its frame inputs"),
        ("Prediction", "1 NFE per latent frame: diffusion adaptation, consistency-distillation initialization, then adversarial training "
                       "with student forcing (the generator rolls out with its KV cache during training; frame-wise discriminator logits, "
                       "approximated R1/R2); one frame of computation per AR step vs two for one-step diffusion forcing (Sec. 2.1, Fig. 2)"),
        ("Decoder", "Lightweight VAE decoder: residual blocks per scale 3 → 2, channels [128, 256, 512, 512] → [64, 128, 256, 512], "
                    "≈3x faster; causal VAE allows streaming decode of 4 frames per step"),
        ("Memory", "Sliding window of 30 latent frames in the KV cache (constant speed and memory); the effective receptive field still "
                   "grows across layers and steps, which is why training uses long student-forced rollouts"),
        ("Speed", "24 fps at 736x416 on one H100, 1280x720 on 8×H100, 0.16 s latency (0.17 s at 1280x720), 60 s streams of 1,440 "
                  "frames (authors); 6 DiT passes per second, so ≤167 ms per latent-frame pass including decode [D]; trained on 256 "
                  "H100s with 8-GPU Ulysses context parallelism"),
        ("Key detail", "One frame of DiT compute per AR step: the previous latent rides along as input channels, so no clean frame is "
                       "computed again (one-step diffusion forcing computes two frames per step; Sec. 2.1, Fig. 2); each pass yields one "
                       "latent frame = 4 video frames; no code or weights (authors: proprietary, not scheduled for release)"),
    ],
    "evidence": "read",
    "sources": ["arXiv 2506.09350 Sec. 1, 2.1 (causal architecture, window), 2.2 (adversarial training), 3 (VAE 4x8, N = 30), "
                "App. A (8B, 36 blocks, FlashAttention-3, RoPE, Ulysses), App. C (lightweight decoder), App. F (N = 15 at 1280x720), "
                "App. G (camera conditioning), Fig. 1-2, Table 4 (latency)",
                "NeurIPS 2025 camera-ready, Paper Checklist Q5 (no release)", "Project page https://seaweed-apt.com/2"],
    "figure_variant": "Paper: 8B, 36-block causal adversarial generator",
    "flow": {
        "below": [{"text": "Frame + cam/pose + text + timestep", "short": "Frame + camera/pose + text"}],
        "stack": [
            {"box": "Causal 3D VAE encoder", "id": "vae", "style": "teal", "basis": "stated"},
            {"group": [
                {"box": "Concat noise+cond+frame", "id": "cond", "style": "orange", "side": "Camera or pose",
                 "basis": "stated", "side_basis": "stated"},
                {"box": "Input projection", "id": "patch", "minor": True, "basis": "stated"},
                {"box": "Concat text tokens", "minor": True, "side": "Text embeddings", "basis": "stated", "side_basis": "stated"},
                {"group": [
                    {"box": "Block-causal attention", "id": "attn", "style": "dark", "side": "3D RoPE",
                     "basis": "stated", "side_basis": "stated"},
                    {"box": "Rest of block not stated", "id": "rest", "style": "soft", "basis": "stated"},
                ], "repeat": "36 ×", "id": "block", "basis": "stated"},
                {"box": "Clean latent frame", "id": "out", "minor": True, "basis": "stated"},
            ], "label": "1 NFE per latent", "loop": "next latent frame", "loop_short": "next latent", "tint": "grey",
               "id": "onepass", "basis": "stated"},
        ],
        "above": [{"box": "Lightweight VAE decoder", "id": "dec", "style": "teal", "basis": "stated"},
                  {"text": "4 frames at 736×416"}],
        "annotations": [
            {"at": "vae", "text": "*4* frames per latent; patch not disclosed", "side": "left", "key": True},
            {"at": "attn", "text": "KV cache window *30* latent frames = *5* s", "side": "left", "key": True},
            {"at": "block", "text": "*36* blocks · *8B* · width not disclosed", "side": "right", "key": True},
            {"at": "dec", "text": "Nearly *3*× faster lightweight decoder", "side": "left"},
            {"at": "dec", "text": "*24* fps · *0.16* s latency", "side": "right", "key": True},
        ],
    },
}
