MODEL = {
    "slug": "matrix_game_35",
    "name": "Matrix-Game 3.5",
    "year": 2026, "month": 8,
    "org": "Riemann Dynamics",
    "family": "dit",
    "role": "Diffusion transformer",
    "status": "arXiv preprint (technical report)",
    "params": "5B (Wan2.2-TI2V-5B)",
    "params_num": 5e9,
    "open": "code + weights",
    "links": {"arXiv": "https://arxiv.org/abs/2608.29910", "code": "https://github.com/Riemann-Dynamics/Matrix-Game-3.5"},
    "tagline": "Causal DiT with 3D re-projected patch memory",
    "summary": "Matrix-Game 3.5 distills a bidirectional world model into a few-step fully causal generator and keeps "
               "long-term memory as geometry: historical VAE-latent patches are lifted to 3D with metric depth, re-projected "
               "into the target view and inserted as tokens of one pose-aware sequence. Each 3-latent-frame chunk attends "
               "causally to a clean anchor, the preceding chunks, one chunk-local context frame and its patch memory; "
               "third-person models add multi-view reference tokens for the controlled character. Camera pose enters "
               "through tiled PRoPE with no new parameters. A 3-step causal student reaches up to 20 fps at 1280x704 on one "
               "H100 with INT8, GPU retrieval and a 75%-pruned decoder (company claim).",
    "facts": [
        ("Representation", "Wan2.2 VAE 4x16x16 → 44x80x48 latent per latent frame at 1280x704; 2x2 patchify (Wan2.2-TI2V-5B config) "
                           "→ 22x40 = 880 tokens per latent frame, 2,640 per 3-latent chunk of 12 frames [D]; 48 latent channels"),
        ("Core", "Wan2.2-TI2V-5B DiT: 30 layers, d 3072, 24 heads, FFN 14336 (HF config); the full DiT is fine-tuned with the text "
                 "encoder and VAE frozen; the only learnable additions are the reference-token embeddings"),
        ("Attention", "Block-causal chunks of 3 latent frames: the chunk's 2,640 queries attend to a rolling KV window (clean anchor + "
                      "≤6 previous chunks = ≤19 latent frames, released config), 1 chunk-local context frame, 3 frames of patch memory "
                      "(≤1 token per target cell) and itself: ≤26 latent frames ≈ 22,880 K/V tokens per chunk [D]; causal training window "
                      "1 anchor + 7 chunks = 22 positions; after the last step a clean t = 0 cache-fill pass writes the chunk's K/V into "
                      "the window, oldest chunks trimmed (code); decoded frames feed the patch memory; the paper's ≈2.3x sequence bound is for the bidirectional base model's 21-frame sample"),
        ("Actions", "Camera pose via tiled PRoPE in every block: after RoPE, queries × Pᵀ, keys and values × P⁻¹, outputs × P, tiled over all "
                    "head channels, no new parameters; translations recentred on the first target frame and log-compressed"),
        ("Prediction", "Perceptual flow matching causal adaptation (10k steps), then curriculum self-rollout DMD (1,000 outer steps, 5:1 update "
                       "ratio) → 3-step causal generator; prefix and chunk-local context held at the next noise level each substep (HiAR), anchor clean"),
        ("Decoder", "MG-LightVAE, 75%-pruned Wan2.2 decoder → 12 frames per chunk at 1280x704; 'VAE decoding becomes the primary latency "
                    "bottleneck' once the DiT is accelerated"),
        ("Memory", "Patch memory (MosaicMem-style): patches lifted to 3D with metric depth and poses, frustum-queried, z-buffered and scattered "
                   "into a target-aligned memory frame; retrieval runs for every generated chunk (on GPU, inside the real-time loop), and each "
                   "chunk is decoded and registered before the next query; only the dynamic-object filter runs once per segment, outside the "
                   "denoising loop; the memory bank grows with rollout length, the per-chunk sequence does not"),
        ("Speed", "Up to 20 output frames/s at 1280x704, batch 1, one H100, including the INT8 3-step DiT, online retrieval and MG-LightVAE "
                  "decode (company claim; the VLM prompt rewriter runs asynchronously); undistilled model in the SANA-WM benchmark: 10.9 "
                  "one-minute videos/hour at 77.0 GB peak, #G = 1, measured on an 8xH100 node (authors' Table 1)"),
        ("Key detail", "Long-term memory is geometric (patch memory); short-term context is a bounded rolling KV window (anchor + ≤6 chunks), "
                       "so per-chunk DiT cost stops growing once the window fills [D]; memory retrieval runs every chunk on the real-time "
                       "path, and only the dynamic-object filter is amortised per segment"),
    ],
    "evidence": "read",
    "sources": ["arXiv 2608.29910 Sec. 2.1 (tiled PRoPE), 2.2 (patch, context and reference memory), 2.3 (distillation), 4.1 (implementation), "
                "4.4 (real-time inference), Table 1",
                "HF Wan-AI/Wan2.2-TI2V-5B config.json (30 layers, dim 3072, 24 heads, ffn 14336, 48 latent channels); Wan2.2 README (VAE 4x16x16)",
                "Official code github.com/Riemann-Dynamics/Matrix-Game-3.5 (model_configs.py, wan_video_dit.py, causal_rollout.py rolling KV window, "
                "configs/infer_distilled_6blocks.yaml); weights HF RiemannDynamics/Matrix-Game-3.5-Base and -Distilled"],
    "figure_variant": "Released 5B distilled causal rollout with reprojected patch memory",
    "flow": {
        "below": [{"text": "Previous frames + camera + text"}],
        "stack": [
            {"box": "Wan2.2 VAE encoder", "id": "vae", "style": "teal", "basis": "code"},
            {"box": "Re-project patch memory", "id": "mem", "minor": True, "side": "Depth + poses", "basis": "stated", "side_basis": "stated"},
            {"box": "Patchify 2×2", "id": "patch", "minor": True, "basis": "code"},
            {"group": [
                {"box": "Pose-aware sequence", "id": "seq", "style": "soft", "basis": "stated"},
                {"group": [
                    {"residual": [{"box": "AdaLN (scale, shift)", "minor": True, "side": "Timestep emb.", "basis": "code", "side_basis": "code"},
                                  {"box": "Block-causal attention", "id": "attn", "style": "dark", "side": "RoPE + tiled PRoPE", "basis": "stated", "side_basis": "stated"},
                                  {"box": "Scale by gate", "minor": True, "basis": "code"}]},
                    {"residual": [{"box": "LayerNorm", "minor": True, "basis": "code"},
                                  {"box": "Cross-attention", "id": "xattn", "side": "umT5 text", "basis": "stated", "side_basis": "code"}]},
                    {"residual": [{"box": "AdaLN (scale, shift)", "minor": True, "basis": "code"},
                                  {"box": "Feed forward", "id": "ffn", "basis": "code"},
                                  {"box": "Scale by gate", "minor": True, "basis": "code"}]},
                ], "repeat": "30 ×", "id": "block"},
                {"box": "Predicted velocity", "id": "vel", "minor": True, "basis": "stated"},
                {"box": "Update latents", "id": "upd", "minor": True, "basis": "code"},
            ], "loop": "3 steps (DMD)", "tint": "grey", "id": "denoise"},
            {"box": "Write chunk to KV cache", "id": "kv", "minor": True, "basis": "code"},
        ],
        "above": [{"box": "MG-LightVAE decoder", "id": "dec", "style": "teal", "basis": "stated"}, {"text": "12 frames at 1280×704"}],
        "insets": [{"for": "ffn", "stack": [{"box": "Linear", "basis": "code"}, {"box": "GELU", "basis": "code"}, {"box": "Linear", "basis": "code"}]},
                   {"for": "block", "label": "tiled PRoPE", "stack": [
                       {"fanout": [[{"box": "RoPE on q", "basis": "stated"}, {"box": "q × P-transpose", "basis": "stated"}],
                                   [{"box": "RoPE on k (not v)", "basis": "stated"}, {"box": "k, v × P-inverse", "basis": "stated"}]]},
                       {"box": "Attention", "basis": "stated"}, {"box": "out × P", "basis": "stated"}]}],
        "annotations": [
            {"at": "vae", "text": "≈*2,640* target tokens per chunk", "side": "left", "key": True},
            {"at": "mem", "text": "≤*1* memory token per target cell", "side": "left"},
            {"at": "seq", "text": "K/V up to ≈*22,880* tokens per chunk", "side": "left", "key": True},
            {"at": "attn", "text": "*30* layers · *24* heads · width *3,072*", "side": "left", "key": True},
            {"at": "dec", "text": "Up to *20* fps at *1280×704*", "side": "right", "key": True},
        ],
        "feedback": "rolling K/V",
        "feedback_from": "kv",
        "feedback_to": "attn",
    },
}
