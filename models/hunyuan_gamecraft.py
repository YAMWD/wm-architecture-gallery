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
    "summary": "An interactive game-video model made by full fine-tuning of the HunyuanVideo MM-DiT. Keyboard and mouse "
               "inputs are mapped to a continuous camera trajectory, turned into Plücker embeddings and added to the video "
               "tokens. It is not block-causal: each 33-frame chunk is denoised with the clean history latents concatenated "
               "into the sequence and marked by a binary mask, so history is re-processed at every step and there is no KV "
               "cache. Phased Consistency Model distillation to 8 steps lifts throughput from 0.25 to 6.6 FPS, still about "
               "5 s per 33-frame action chunk.",
    "facts": [
        ("Representation", "HunyuanVideo causal 3D VAE latents; strides are not restated in the paper (HunyuanVideo's own report: "
                           "4x8x8, 16 channels, patch 1x2x2, which gives 3,600 tokens per latent frame at 1280x720 and ≈32,400 per "
                           "33-frame chunk of 9 latent frames [D])"),
        ("Core", "HunyuanVideo MM-DiT: double-stream blocks followed by single-stream blocks (Fig. 4), full-parameter fine-tuned; "
                 "size not restated (13B in HunyuanVideo's report)"),
        ("Attention", "Bidirectional over the chunk plus the concatenated clean history latents (a single image, the last chunk or "
                      "several chunks); a binary mask marks history (1) vs predicted (0) tokens; no KV cache described"),
        ("Actions", "W/A/S/D, arrows, Space and mouse → shared continuous camera space (translation, rotation, speed; roll removed) "
                    "→ Plücker embeddings → light encoder (a few conv layers + temporal pooling) → added to the video tokens after "
                    "patchify with a learnable scale; token addition beat token and channel concatenation (Table 4)"),
        ("Prediction", "Flow matching; Phased Consistency Model distillation plus CFG distillation into an 8-step consistency model; "
                       "the pre-distillation step count is not stated"),
        ("Decoder", "HunyuanVideo 3D VAE decoder → 33-frame chunk at 720p, 25 fps"),
        ("Memory", "Hybrid history condition: training mix of one history clip (0.7), several clips (0.05) and a single frame (0.25); "
                   "history tokens re-enter every chunk, so cost grows with the history used; no retrieval, no 3D state"),
        ("Speed", "0.25 FPS undistilled → 6.6 FPS with PCM (authors, Table 2; GPU not stated); 33 frames at 6.6 FPS ≈ 5.0 s per action "
                  "chunk, matching 'less than 5 s per action' [D]; trained on 192 H20 GPUs"),
        ("Key detail", "Control granularity is a whole 1.32 s chunk, and history is concatenated rather than cached, so every denoising "
                       "step re-processes the history tokens through all layers"),
    ],
    "evidence": "read",
    "sources": ["arXiv 2506.17201 Sec. 4.1-4.3, 5.1 (implementation), Table 2, Table 4, Fig. 4-5",
                "HunyuanVideo arXiv 2412.03603 (VAE 4x8x8x16, patch 1x2x2, 13B; not in the local corpus)",
                "GitHub Tencent-Hunyuan/Hunyuan-GameCraft-1.0 (release not re-verified in this pass)"],
    "diagram": {
        "encoder": {"text": "Frames → HunyuanVideo 3D causal VAE", "sub": "≈3,600 latents per latent frame at 720p [D]",
                    "short": "HunyuanVideo VAE → latents"},
        "tokens": {"groups": [("latent", 24, "≈32,400 latents per chunk"), ("latent", 8, "history latents + mask")],
                   "note": "history concatenated, no KV cache"},
        "core": {"title": "HunyuanVideo MM-DiT, size not restated (13B)",
                 "rows": [("attn", "Full attention over chunk + history"),
                          ("action", "Camera Plücker map added to tokens"),
                          ("xattn", "Text via MM-DiT double stream"),
                          ("mlp", "MLP")],
                 "notes": ["binary mask: 1 = history latents, 0 = predicted", "history re-processed at every step"]},
        "sampling": {"kind": "diffusion", "text": "PCM-distilled consistency model, 8 steps", "sub": "per chunk of 33 frames (1.32 s at 25 fps)",
                     "short": "8 steps per 33-frame chunk"},
        "decoder": {"text": "HunyuanVideo VAE decoder → 33 frames at 720p", "short": "VAE decoder → 33 frames"},
        "loop": "AR rollout",
    },
    "flow": {
        "below": [{"text": "Reference image or history frames + keys/mouse + text"}],
        "stack": [
            {"box": "HunyuanVideo 3D causal VAE encoder", "short": "HunyuanVideo VAE encoder", "id": "vae", "style": "teal"},
            {"box": "Patchify", "id": "patch", "minor": True},
            {"box": "Add camera Plücker embedding", "id": "act", "style": "orange", "side": "Keys + mouse → camera"},
            {"box": "Concat clean history latents + mask", "id": "hist", "minor": True},
            {"group": [
                {"box": "Noisy chunk + history latents", "id": "noisy", "style": "soft", "minor": True},
                {"group": [
                    {"fanout": [[{"box": "Text stream (AdaLN, QKV)", "short": "Text stream", "side": "Text emb."}],
                                [{"box": "Video stream (AdaLN, QKV)", "short": "Video stream"}]]},
                    {"box": "Joint full attention over chunk + history", "short": "Joint full attention", "id": "attn", "style": "dark", "side": "3D RoPE"},
                    {"fanout": [[{"box": "Text feed forward", "minor": True}], [{"box": "Video feed forward", "id": "vffn", "minor": True}]]},
                ], "repeat": "N ×", "label": "double-stream MM-DiT", "id": "dblock"},
                {"group": [
                    {"residual": [{"box": "AdaLN", "minor": True},
                                  {"box": "Full self-attention (video + text)", "id": "sattn", "style": "dark", "minor": True}]},
                    {"residual": [{"box": "AdaLN", "minor": True}, {"box": "Feed forward", "id": "ffn", "minor": True}]},
                ], "repeat": "M ×", "label": "single-stream", "id": "sblock"},
                {"box": "Predicted velocity", "id": "vel", "minor": True},
                {"box": "Consistency update", "id": "upd", "minor": True},
            ], "loop": "8 steps (PCM-distilled)", "tint": "grey", "id": "denoise"},
        ],
        "above": [{"box": "HunyuanVideo VAE decoder", "id": "dec", "style": "teal"}, {"text": "33 frames at 720p per chunk"}],
        "annotations": [
            {"at": "vae", "text": "strides not restated; HunyuanVideo's 4×8×8 VAE and 1×2×2 patch give *3,600* tokens per latent frame, ≈*32,400* per 33-frame chunk of *9* latent frames [D]", "side": "left", "key": True},
            {"at": "act", "text": "W/A/S/D, arrows, mouse → continuous camera (translation, rotation, speed) → Plücker map → light conv + pooling encoder, added to the video tokens with a learnable scale", "side": "left"},
            {"at": "hist", "text": "binary mask: *1* = history latents, *0* = predicted; history re-processed at every step, no KV cache", "side": "right"},
            {"at": "attn", "text": "bidirectional over the chunk + concatenated clean history latents (one image, the last chunk or several chunks), re-processed at every step; no KV cache", "side": "left", "key": True},
            {"at": "dblock", "text": "HunyuanVideo MM-DiT (double-stream, then single-stream blocks), full-parameter fine-tuned; block counts and widths not restated (*13B* in HunyuanVideo's report)", "side": "right", "key": True},
            {"at": "upd", "text": "flow matching → Phased Consistency Model + CFG distillation, *8* steps per chunk; pre-distillation step count not stated", "side": "right"},
            {"at": "dec", "text": "*0.25* FPS undistilled → *6.6* FPS with PCM (authors; GPU not stated): ≈*5.0* s per 33-frame chunk [D]", "side": "right", "key": True},
        ],
        "feedback": "next chunk",
    },
}
