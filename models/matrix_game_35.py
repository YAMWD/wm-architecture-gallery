MODEL = {
    "slug": "matrix_game_35",
    "name": "Matrix-Game 3.5",
    "year": 2026, "month": 8,
    "org": "Skywork AI (Matrix-Game team)",
    "family": "dit",
    "role": "Diffusion transformer",
    "status": "arXiv preprint (company)",
    "params": "5B (Wan2.2-TI2V-5B)",
    "params_num": 5e9,
    "open": "code + weights",
    "links": {"arXiv": "https://arxiv.org/abs/2608.29910", "code": "https://github.com/SkyworkAI/Matrix-Game"},
    "summary": "Matrix-Game 3.5 returns to a fully causal generator and moves memory out of the KV cache into geometry: "
               "historical VAE-latent patches are lifted to 3D with metric depth, re-projected into the target view and "
               "inserted as tokens, so each 3-latent-frame chunk attends to a bounded pose-aware sequence of noisy targets, "
               "one clean anchor, a few context frames, patch-memory tokens and a reference prefix. Camera pose enters "
               "through tiled PRoPE with no new parameters. A 3-step causal student reaches 20 fps at 1280x704 on one H100 "
               "with INT8, GPU retrieval and a 75%-pruned decoder (company claim).",
    "facts": [
        ("Representation", "Wan2.2 VAE 4x16x16 + patchify (2x2 assumed) → 880 tokens per 22x40 latent frame at 1280x704, 2,640 per "
                           "3-latent chunk of 12 frames [D]; 48 latent channels"),
        ("Core", "Wan2.2-TI2V-5B DiT: 30 layers, d 3072, 24 heads, FFN 14336 (HF config); the full DiT is fine-tuned with the text "
                 "encoder and VAE frozen; the only learnable additions are the reference-token embeddings"),
        ("Attention", "Block-causal chunks of 3 latent frames over one pose-aware sequence: noisy targets + clean anchor + context frames "
                      "(1 per chunk in causal training, up to 5 in base training) + patch-memory tokens (≤1 per target cell) + a reference "
                      "prefix of ≈1 frame; ≤≈7,900 tokens per chunk [D], bounded by ≈2.3x the target track; training window 1 anchor + 7 chunks = 22 latent positions"),
        ("Actions", "Camera pose via tiled PRoPE in every block: after RoPE, queries × Pᵀ, keys and values × P⁻¹, outputs × P, tiled over all "
                    "head channels, no new parameters; translations recentred on the first target frame and log-compressed"),
        ("Prediction", "Perceptual flow matching causal adaptation (10k steps), then curriculum self-rollout DMD (1,000 outer steps, 5:1 update "
                       "ratio) → 3-step causal generator; prefix and chunk-local context held at the next noise level each substep (HiAR), anchor clean"),
        ("Decoder", "MG-LightVAE, 75%-pruned Wan2.2 decoder → 12 frames per chunk at 1280x704; 'VAE decoding becomes the primary latency "
                    "bottleneck' once the DiT is accelerated"),
        ("Memory", "Patch memory (MosaicMem-style): patches lifted to 3D with metric depth and poses, frustum-queried, z-buffered and scattered "
                   "into a target-aligned memory frame; retrieval and dynamic-object filtering run once per segment, off the per-frame loop; "
                   "the sequence does not grow with rollout length"),
        ("Speed", "Up to 20 output frames/s at 1280x704, batch 1, one H100, including the INT8 3-step DiT, online retrieval and MG-LightVAE "
                  "decode (company claim; the VLM prompt rewriter runs asynchronously); 10.9 one-minute videos/hour at 77.0 GB peak on one H100 "
                  "in the SANA-WM benchmark, undistilled model (authors' Table 1)"),
        ("Key detail", "Memory is geometry, not cache: the per-chunk sequence is capped at ≈2.3x the target track, so DiT cost is constant in "
                       "rollout length and the depth, lift and projection work sits off the per-frame critical path"),
    ],
    "evidence": "read",
    "sources": ["arXiv 2608.29910 Sec. 2.1 (tiled PRoPE), 2.2 (patch, context and reference memory), 2.3 (distillation), 4.1 (implementation), "
                "4.4 (real-time inference), Table 1",
                "HF Wan-AI/Wan2.2-TI2V-5B config.json (local copy: 30 layers, dim 3072, 24 heads, ffn 14336, 48 latent channels)",
                "Wan2.2 README (VAE compression 4x16x16; local copy)",
                "code link on the paper's title page (weights release not verified in this pass)"],
    "diagram": {
        "encoder": {"text": "Frames → Wan2.2 VAE (4x16x16) + patchify", "sub": "880 latents per 22x40 latent frame at 1280x704 [D]",
                    "tag": "frozen", "short": "Wan2.2 VAE → 880 latents"},
        "tokens": {"groups": [("latent", 24, "2,640 noisy latents"), ("latent", 24, "≤5,280 context + memory")],
                   "note": "≤ ≈7,900 tokens per chunk, bounded"},
        "core": {"title": "Wan2.2 DiT ×30 · d 3072 · 24 heads",
                 "rows": [("attn", "Block-causal attention, pose-aware"),
                          ("action", "Camera pose: tiled PRoPE on Q, K, V"),
                          ("xattn", "Cross-attention to text (umT5)"),
                          ("mlp", "MLP (FFN 14336)")],
                 "notes": ["memory tokens re-projected from 3D, ≤1 per target cell; retrieval once per segment",
                           "context prefix held at the next noise level each substep, not cached"]},
        "sampling": {"kind": "diffusion", "text": "PFM + self-rollout DMD, 3 denoising steps", "sub": "per chunk of 12 frames (3 latent frames); INT8 DiT",
                     "short": "3 steps per 12-frame chunk"},
        "decoder": {"text": "MG-LightVAE (75% pruned) → 12 frames at 1280x704", "sub": "VAE decode is the stated latency bottleneck",
                    "short": "MG-LightVAE → 12 frames"},
        "loop": "AR rollout",
    },
    "flow": {
        "below": [{"text": "Previous frames + camera trajectory (from keys/mouse) + text", "short": "Previous frames + camera + text"}],
        "stack": [
            {"box": "Wan2.2 VAE encoder (4×16×16)", "short": "Wan2.2 VAE encoder", "id": "vae", "style": "teal"},
            {"box": "Patchify 2×2", "id": "patch", "minor": True},
            {"box": "Patch memory: lift to 3D, re-project", "id": "mem", "minor": True, "side": "Metric depth + poses"},
            {"group": [
                {"box": "Pose-aware token sequence", "short": "Pose-aware sequence", "id": "seq", "style": "soft"},
                {"group": [
                    {"residual": [{"box": "AdaLN (scale, shift)", "minor": True, "side": "Timestep emb."},
                                  {"box": "Block-causal self-attention", "short": "Block-causal attention", "id": "attn", "style": "dark", "side": "RoPE + tiled PRoPE"}]},
                    {"residual": [{"box": "Cross-attention", "id": "xattn", "side": "umT5 text"}]},
                    {"residual": [{"box": "AdaLN (scale, shift)", "minor": True}, {"box": "Feed forward", "id": "ffn"}]},
                ], "repeat": "30 ×", "id": "block"},
                {"box": "Predicted velocity", "id": "vel", "minor": True},
                {"box": "Update latents", "id": "upd", "minor": True},
            ], "loop": "3 denoising steps (DMD)", "tint": "grey", "id": "denoise"},
        ],
        "above": [{"box": "MG-LightVAE decoder (75% pruned)", "short": "MG-LightVAE decoder", "id": "dec", "style": "teal"}, {"text": "12 frames at 1280×704"}],
        "insets": [{"for": "ffn", "stack": [{"box": "Linear"}, {"box": "GELU"}, {"box": "Linear"}]},
                   {"for": "attn", "label": "tiled PRoPE", "stack": [{"box": "RoPE"}, {"box": "q × P-transpose; k, v × P-inverse"}, {"box": "Attention"}, {"box": "out × P"}]}],
        "annotations": [
            {"at": "vae", "text": "*880* tokens per 22×40 latent frame; a chunk of *3* latent frames = *2,640* target tokens = *12* frames [D]", "short": "*2,640* tokens per *12*-frame chunk", "side": "left", "key": True},
            {"at": "mem", "text": "patch memory: ≤*1* token per target cell, frustum-queried and z-buffered; retrieval once per segment, off the per-frame loop", "side": "left"},
            {"at": "seq", "text": "noisy targets + clean anchor + context frames + re-projected memory patches + reference prefix: ≤≈*7,900* tokens per chunk [D], bounded in rollout length", "side": "right", "key": True},
            {"at": "attn", "text": "*24* heads, width *3,072*; camera pose via tiled PRoPE in every block, no new parameters", "side": "left", "key": True},
            {"at": "block", "text": "*30* layers, *5B* (Wan2.2-TI2V-5B); INT8 DiT at inference", "side": "right", "key": True},
            {"at": "upd", "text": "PFM causal adaptation, then self-rollout DMD → *3* steps; prefix and context held at the next noise level each substep (HiAR), not cached", "side": "right"},
            {"at": "dec", "text": "up to *20* fps at 1280×704 on one H100 incl. retrieval and decode (company claim)", "side": "right", "key": True},
        ],
        "feedback": "next chunk",
    },
}
