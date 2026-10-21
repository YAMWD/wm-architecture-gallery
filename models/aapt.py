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
    "summary": "Autoregressive Adversarial Post-Training, the one-pass-per-frame design: a pre-trained 8B video diffusion transformer is made block-causal and "
               "post-trained adversarially so that each latent frame (4 video frames) is generated with a single network "
               "evaluation from noise, the previous generated frame recycled through channel concatenation, and a KV cache "
               "over a sliding window of 30 latent frames. Per-frame conditions (human pose, or camera rays relative to the "
               "previous frame) enter as extra input channels. The authors report 24 fps at 736x416 on one H100 with 0.16 s "
               "latency, or 1280x720 on 8 H100s, for streams up to a minute.",
    "facts": [
        ("Representation", "Causal 3D convolution VAE, 4x temporal and 8x spatial; one latent frame = 4 video frames, the first frame its "
                           "own latent; DiT patch size not stated, so tokens per frame are not computed (latent grid 92x52 at 736x416 [D])"),
        ("Core", "8B MMDiT-style diffusion transformer with 36 blocks (base model not named); width and heads not stated; text tokens "
                 "and visual tokens in one sequence; the discriminator reuses the same causal architecture (16B in training)"),
        ("Attention", "Block-causal: text tokens attend only to themselves, visual tokens to the text tokens and to visual tokens of the "
                      "current and previous frames; window N = 30 latent frames (5 s) plus the text tokens and the first frame always; "
                      "FlashAttention-3; 3D RoPE with a fixed temporal interval for arbitrary length"),
        ("Actions", "Per-frame conditions shifted to align with the frames: human pose, or camera origin and direction (CameraCtrl II style, "
                    "relative to the previous frame) as new input channels with a randomly initialized input projection; the previous "
                    "generated frame enters by channel concatenation"),
        ("Prediction", "1 NFE per latent frame: diffusion adaptation, consistency-distillation initialization, then adversarial training "
                       "with student forcing (the generator rolls out with its KV cache during training; frame-wise discriminator logits, "
                       "approximated R1/R2); 'one frame of compute per step' vs two for one-step diffusion forcing"),
        ("Decoder", "Lightweight VAE decoder: residual blocks per scale 3 → 2, channels [128, 256, 512, 512] → [64, 128, 256, 512], "
                    "≈3x faster; causal VAE allows streaming decode of 4 frames per step"),
        ("Memory", "Sliding window of 30 latent frames in the KV cache (constant speed and memory); the effective receptive field still "
                   "grows across layers and steps, which is why training uses long student-forced rollouts"),
        ("Speed", "24 fps at 736x416 on one H100, 1280x720 on 8×H100, 0.16 s latency, 60 s streams of 1,440 frames (authors); "
                  "6 DiT passes per second, so ≤167 ms per latent-frame pass including decode [D]; trained on 256 H100s with "
                  "8-GPU Ulysses context parallelism"),
        ("Key detail", "Lowest DiT work per frame in this gallery: one pass per 4 frames (Self Forcing: 5 per 12, Matrix-Game 3.5: 3 per 12) [D]; "
                       "no code or weights found"),
    ],
    "evidence": "read",
    "sources": ["arXiv 2506.09350 Sec. 1, 2.1 (causal architecture, window), 2.2 (adversarial training), 3 (VAE 4x8, N = 30), "
                "App. A (8B, 36 blocks, FlashAttention-3, RoPE, Ulysses), App. C (lightweight decoder), App. G (camera conditioning)",
                "interactive_video_dits.md (AAPT section, derived pass counts)"],
    "diagram": {
        "encoder": {"text": "Frames → causal 3D conv VAE (4x8x8)", "sub": "one latent frame = 4 video frames; 92x52 latent grid at 736x416 [D]",
                    "short": "Causal 3D VAE, 4 frames per latent"},
        "tokens": {"groups": [("latent", 8, "1 latent frame = 4 frames"), ("text", 2, "text tokens")],
                   "note": "patch size not stated; window 30 latent frames"},
        "core": {"title": "Block-causal MMDiT ×36 · 8B (width not stated)",
                 "rows": [("attn", "Block-causal attn, window 30 latents"),
                          ("action", "Camera or pose → input channels"),
                          ("note", "previous frame recycled via channel concat"),
                          ("mlp", "MLP")],
                 "notes": ["KV cache; text tokens and first frame always attended",
                           "temporal RoPE with a fixed interval for arbitrary length"]},
        "sampling": {"kind": "diffusion", "text": "Adversarial post-training: 1 step (1 NFE) per latent frame",
                     "sub": "one pass per 4 video frames; student forcing", "short": "1 pass per latent frame"},
        "decoder": {"text": "Lightweight VAE decoder → 4 frames at 736x416", "sub": "blocks 3 → 2 per scale, channels halved: ≈3x faster",
                    "short": "Light VAE decoder → 4 frames"},
        "loop": "AR rollout",
    },
}
