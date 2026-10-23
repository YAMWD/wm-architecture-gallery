MODEL = {
    "slug": "hunyuan_gamecraft",
    "name": "Hunyuan-GameCraft",
    "year": 2025, "month": 6,
    "org": "Tencent Hunyuan and HUST",
    "family": "dit",
    "role": "Diffusion transformer",
    "status": "arXiv preprint",
    "params": "13B (HunyuanVideo base)",
    "params_num": 13e9,
    "open": "code + weights",
    "links": {"arXiv": "https://arxiv.org/abs/2506.17201", "page": "https://hunyuan-gamecraft.github.io/",
              "code": "https://github.com/Tencent-Hunyuan/Hunyuan-GameCraft-1.0"},
    "tagline": "Chunk-wise MM-DiT that re-reads its history",
    "summary": "An interactive game-video model made by full fine-tuning of the HunyuanVideo MM-DiT. Keyboard and mouse "
               "inputs are mapped to a continuous camera trajectory, turned into Plücker embeddings and added to the video "
               "tokens. It is not block-causal: each 33-frame chunk is denoised with the clean history latents concatenated "
               "into the sequence and marked by a binary mask, so history is re-processed at every step of the 8-step model "
               "(the 50-step model's DeepCache skips most blocks on some steps) and there is no KV cache. Phased Consistency Model distillation to 8 steps lifts throughput from 0.25 to 6.6 FPS, still about "
               "5 s per 33-frame action chunk.",
    "facts": [
        ("Representation", "HunyuanVideo causal 3D VAE latents; strides are not restated in the paper (HunyuanVideo's own report: "
                           "4x8x8, 16 channels; patch 1x2x2 from the released code). The official 720p run uses 704x1216, which "
                           "gives 76 x 44 = 3,344 tokens per latent frame and ≈30,100 per 33-frame chunk of 9 latent frames [D]"),
        ("Core", "HunyuanVideo MM-DiT: double-stream blocks followed by single-stream blocks (Fig. 4), full-parameter fine-tuned; "
                 "size not restated (13B in HunyuanVideo's report)"),
        ("Attention", "Bidirectional over the chunk plus the concatenated clean history latents (a single image, the last chunk or "
                      "several chunks); a binary mask marks history (1) vs predicted (0) tokens; no KV cache described"),
        ("Actions", "W/A/S/D, arrows, Space and mouse → shared continuous camera space (translation, rotation, speed; roll removed) "
                    "→ Plücker embeddings → light encoder (a few conv layers + temporal pooling) → added to the video tokens after "
                    "patchify with a learnable scale; token addition beat token and channel concatenation (Table 4)"),
        ("Prediction", "Flow matching; Phased Consistency Model distillation plus CFG distillation into an 8-step consistency model "
                       "(README: 8 steps, CFG 1.0); the undistilled model runs 50 steps with CFG 2.0 in the official code "
                       "(the paper gives no count)"),
        ("Decoder", "HunyuanVideo 3D VAE decoder → 33-frame chunk at 720p, 25 fps"),
        ("Memory", "Hybrid history condition: training mix of one history clip (0.7), several clips (0.05) and a single frame (0.25); "
                   "the released inference caps history at one chunk of latents (9 history + 9 predicted latent frames per "
                   "pass), so per-chunk cost does not grow with rollout length; no retrieval, no 3D state"),
        ("Speed", "0.25 FPS undistilled → 6.6 FPS with PCM (authors, Table 2; GPU not stated); 33 frames at 6.6 FPS ≈ 5.0 s per action "
                  "chunk, matching 'less than 5 s per action' [D]; trained on 192 H20 GPUs"),
        ("Key detail", "Control granularity is a whole 1.32 s chunk, and history is concatenated rather than cached, so every step "
                       "of the 8-step model re-processes the history tokens through all layers (the 50-step model's DeepCache "
                       "skips most blocks on 15 of 50 steps)"),
    ],
    "audit": {"date": "2026-10-23", "checked": 53, "stated": 17, "code": 31, "derived": 5, "assumed": 0, "fixed": 14},
    "evidence": "read",
    "sources": ["arXiv 2506.17201 Sec. 4.1-4.3, 5.1 (implementation), Table 2, Table 4, Fig. 4-5",
                "HunyuanVideo arXiv 2412.03603 Sec. 4.1 (VAE 4x8x8, 16 ch), Table 2 (13B, 20 double + 40 single blocks)",
                "GitHub Tencent-Hunyuan/Hunyuan-GameCraft-1.0: README, hymm_sp/modules/models.py, "
                "hymm_sp/diffusion/pipelines/pipeline_hunyuan_video_game.py, hymm_sp/config.py"],
    "diagram": {
        "encoder": {"text": "Frames → HunyuanVideo 3D causal VAE", "sub": "≈3,344 latents per latent frame at 704x1216 [D]",
                    "short": "HunyuanVideo VAE → latents"},
        "tokens": {"groups": [("latent", 24, "≈30,100 latents per chunk"), ("latent", 8, "history latents + mask")],
                   "note": "history concatenated, no KV cache"},
        "core": {"title": "HunyuanVideo MM-DiT, size not restated (13B)",
                 "rows": [("attn", "Full attention over chunk + history"),
                          ("action", "Camera Plücker map added to tokens"),
                          ("xattn", "Text via MM-DiT double stream"),
                          ("mlp", "MLP")],
                 "notes": ["binary mask: 1 = history latents, 0 = predicted", "history re-processed at every step (8-step model)"]},
        "sampling": {"kind": "diffusion", "text": "PCM-distilled consistency model, 8 steps", "sub": "per chunk of 33 frames (1.32 s at 25 fps)",
                     "short": "8 steps per 33-frame chunk"},
        "decoder": {"text": "HunyuanVideo VAE decoder → 33 frames at 720p", "short": "VAE decoder → 33 frames"},
        "loop": "AR rollout",
    },
    "flow": {
        "below": [{"text": "History frames + keys/mouse + text"}],
        "stack": [
            {"box": "HunyuanVideo VAE encoder", "short": "Video VAE encoder", "id": "vae", "style": "teal", "basis": "code"},
            {"group": [
                {"box": "Noisy chunk + history", "id": "noisy", "style": "soft", "minor": True, "basis": "code"},
                {"box": "Concat history + mask", "id": "hist", "minor": True, "basis": "code"},
                {"box": "Patchify", "id": "patch", "minor": True, "basis": "stated"},
                {"box": "Add Plücker embedding", "id": "act", "style": "orange", "side": "Actions → camera",
                 "basis": "stated", "side_basis": "stated"},
                {"group": [
                    {"fanout": [[{"box": "Text AdaLN + QKV", "short": "Text stream", "side": "Text emb.",
                                  "basis": "code", "side_basis": "code"}],
                                [{"box": "Video AdaLN + QKV", "short": "Video stream", "basis": "code"}]]},
                    {"box": "Joint full attention", "id": "attn", "style": "dark", "side": "3D RoPE",
                     "basis": "code", "side_basis": "code"},
                    {"fanout": [[{"box": "Text feed forward", "minor": True, "basis": "code"}],
                                [{"box": "Video feed forward", "id": "vffn", "minor": True, "basis": "code"}]]},
                ], "repeat": "20 ×", "label": "double-stream", "id": "dblock"},
                {"group": [
                    {"residual": [{"box": "AdaLN", "minor": True, "basis": "code"},
                                  {"fanout": [[{"box": "Full self-attention", "id": "sattn", "style": "dark", "minor": True,
                                                "basis": "code"}],
                                              [{"box": "MLP (GELU tanh)", "id": "ffn", "minor": True, "basis": "code"}]]},
                                  {"box": "Concat → Linear + gate", "minor": True, "basis": "code"}]},
                ], "repeat": "40 ×", "label": "single-stream", "id": "sblock"},
                {"box": "Predicted velocity", "id": "vel", "minor": True, "basis": "code"},
                {"box": "Consistency update", "id": "upd", "minor": True, "basis": "stated"},
            ], "loop": "8 steps (PCM)", "tint": "grey", "id": "denoise"},
        ],
        "above": [{"box": "HunyuanVideo VAE decoder", "short": "Video VAE decoder", "id": "dec", "style": "teal", "basis": "code"},
                  {"text": "33 frames at 720p per chunk"}],
        "annotations": [
            {"at": "vae", "text": "≈*30,100* tokens per *33*-frame chunk", "side": "left", "key": True},
            {"at": "hist", "text": "Mask: *1* = history, *0* = predicted", "side": "right"},
            {"at": "attn", "text": "History tokens re-run in all *8* steps", "side": "left", "key": True},
            {"at": "dblock", "text": "*13B* · *20* double + *40* single blocks", "side": "right", "key": True},
            {"at": "upd", "text": "*0.25* fps before distillation", "side": "right"},
            {"at": "dec", "text": "*6.6* fps · ≈*5* s per *33*-frame chunk", "side": "right", "key": True},
        ],
        "feedback": "next chunk (latents)",
    },
}
