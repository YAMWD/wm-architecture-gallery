MODEL = {
    "slug": "worldplay",
    "name": "WorldPlay (HY-World 1.5)",
    "year": 2025, "month": 12,
    "org": "Tencent Hunyuan",
    "family": "dit",
    "role": "Diffusion transformer",
    "status": "ICML 2026 (poster, PMLR 306); arXiv v2, 9 Jun 2026",
    "params": "8B (HunyuanVideo-1.5)",
    "params_num": 8e9,
    "open": "code + weights",
    "links": {"arXiv": "https://arxiv.org/abs/2512.14614", "code": "https://github.com/Tencent-Hunyuan/HY-WorldPlay",
              "weights": "https://huggingface.co/tencent/HY-WorldPlay"},
    "tagline": "Causal DiT with memory retrieved by camera view",
    "summary": "Tencent's real-time interactive world model: the HunyuanVideo-1.5 MM-DiT made chunk-wise block-causal "
               "(4 latent frames = 16 video frames per chunk) and distilled with Context Forcing to 4 steps. Each chunk "
               "attends to a memory rebuilt from the 3 most recent chunks, 1 chunk retrieved by field-of-view overlap "
               "and camera distance, and the first chunk kept as an attention sink, with RoPE indices re-assigned so old frames look recent. Keys enter through the "
               "timestep embedding, camera pose through a relative encoding inside attention. The open checkpoints are "
               "480P; the company's 24 FPS at 720p (paper setting) needs 8 H800 GPUs with token parallelism, quantization "
               "and streaming VAE decode.",
    "facts": [
        ("Representation", "HunyuanVideo-1.5 causal 3D VAE: 16x spatial, 4x temporal, 32 channels; patch 1x1x1 → 1,560 tokens "
                           "per latent frame at the released 480×832, 6,240 per 4-latent chunk of 16 frames [D]; paper's 720p: "
                           "3,600 and 14,400 [D]"),
        ("Core", "HunyuanVideo-1.5 480P-I2V transformer: 54 double-stream MM-DiT blocks, d 2048, 16 heads, MLP ratio 4, "
                 "GELU-tanh (HF config); no cross-attention in the released code: text tokens (2-layer token refiner) run in a "
                 "parallel stream whose K/V join the video attention; timestep adaLN; "
                 "8B per the README (a 5B Wan-based variant is lighter but weaker)"),
        ("Attention", "Block-causal over chunks with a KV cache; context = 3 temporal + 1 spatial chunk + the first chunk as attention "
                      "sink = 20 latents = 31,200 tokens at 480×832 (37,440 with the current chunk) [D]; 72,000 (86,400) at 720p [D]; temporal reframing "
                      "re-assigns RoPE indices so context frames sit at a small relative distance"),
        ("Actions", "Dual representation: discrete keys → PE + zero-initialized MLP added to the timestep embedding (adaLN); "
                    "camera pose → PRoPE relative encoding in a second attention term, output = Attn1 + zero_init(Attn2)"),
        ("Prediction", "Flow matching; Context Forcing distillation (memory-augmented bidirectional teacher, DMD loss) from "
                       "100 NFE to 4 denoising steps per 16-frame chunk"),
        ("Decoder", "HunyuanVideo-1.5 VAE decoder → 16 frames per chunk; progressive decode in small batches streamed over "
                    "Triton, parallelized over 8 GPUs; the open checkpoints are 480P"),
        ("Memory", "Reconstituted context memory rebuilt per chunk by FOV-overlap and camera-distance retrieval from past "
                   "chunks; no explicit 3D state; its KV cache is recomputed in one extra pass per chunk; KV ≈27.6 GB in BF16 for "
                   "the 31,200-token context at 480×832 (RoPE and PRoPE K/V both cached), ≈3.5 GB per GPU split 8 ways; "
                   "720p paper setting: ≈63.7 GB for 72,000 tokens [D]"),
        ("Speed", "Paper setting: 24 FPS at 720p on 8×H800 (company claim); Table 4: 2.80 → 3.80 (DiT parallelism + quantization) → 16.0 (+VAE) "
                  "→ 24.0 FPS (+streaming decode); 4.95 FPS for the 8B model on 4×H200 (measured by WorldKV); 28 GB per GPU at sp=8 (README)"),
        ("Key detail", "Distillation cuts passes 25x, but the remaining 8.57x to real time (paper, 720p) is systems work; at 720p "
                       "≈90% of per-chunk DiT FLOPs is attention: two attention terms (RoPE and PRoPE) per block over ≈86,400 tokens [D]"),
    ],
    "evidence": "read",
    "sources": ["arXiv 2512.14614 Sec. 3.1-3.5, Table 4, App. A, Table 8",
                "HF tencent/HunyuanVideo-1.5 transformer/480p_i2v/config.json and vae/config.json",
                "HY-WorldPlay code: worldplay_1_5_transformer.py, modules/attention.py, utils/retrieval_context.py, worldplay_video_pipeline.py",
                "ICML 2026 poster page (WorldPlay)",
                "HY-WorldPlay README (8B HY Video / 5B Wan lines, 480P checkpoints, GPU memory at sp=8)",
                "WorldKV arXiv 2605.22718 Table 1 (4.95 FPS on 4×H200)"],
    "figure_variant": "Released 480P distilled AR model: HY-1.5 8B, 54 blocks, 4 steps",
    "flow": {
        "below": [{"text": "Frames + keys + camera + text"}],
        "stack": [
            {"box": "HY-1.5 VAE encoder", "id": "vae", "style": "teal", "basis": "code"},
            {"box": "Rebuild memory", "id": "mem", "side": "FOV + distance", "basis": "stated", "side_basis": "stated"},
            {"box": "Recompute memory KV", "id": "kv", "minor": True, "basis": "stated"},
            {"group": [
                {"box": "Noisy latent chunk", "id": "noisy", "style": "soft", "minor": True, "basis": "stated"},
                {"box": "Patchify 1×1×1", "id": "patch", "minor": True, "basis": "code"},
                {"group": [
                    {"residual": [{"box": "AdaLN (timestep + keys)", "short": "AdaLN", "id": "ada", "side": "Keys → PE + MLP",
                                   "basis": "code", "side_basis": "stated"},
                                  {"box": "Block-causal attention", "id": "attn", "style": "dark", "side": "Text + memory",
                                   "basis": "stated", "side_basis": "code"},
                                  {"box": "Scale by gate", "minor": True, "basis": "code"}]},
                    {"residual": [{"box": "AdaLN", "minor": True, "basis": "code"},
                                  {"box": "Feed forward", "id": "ffn", "basis": "stated"},
                                  {"box": "Scale by gate", "minor": True, "basis": "code"}]},
                ], "repeat": "54 ×", "id": "block"},
                {"box": "Predicted velocity", "id": "vel", "minor": True, "basis": "stated"},
                {"box": "Update latents", "id": "upd", "minor": True, "basis": "code"},
            ], "loop": "4 steps (DMD)", "tint": "grey", "id": "denoise"},
        ],
        "above": [{"box": "HY-1.5 VAE decoder", "id": "dec", "style": "teal", "basis": "code"}, {"text": "16 frames per chunk at 480p"}],
        "insets": [{"for": "attn", "label": "parallel attention", "stack": [
            {"fanout": [[{"box": "RoPE attention", "basis": "code"}],
                        [{"box": "PRoPE attention", "basis": "code"}]]},
            {"box": "Project + sum", "basis": "code"}]}],
        "annotations": [
            {"at": "vae", "text": "≈*6,240* tokens per *16*-frame chunk, *480p*", "side": "left", "key": True},
            {"at": "mem", "text": "*3* recent + *1* retrieved + sink ≈ *31k* tokens", "side": "left", "key": True},
            {"at": "attn", "text": "*16* heads · width *2,048*", "side": "left"},
            {"at": "block", "text": "*54* blocks · *8B* parameters", "side": "right", "key": True},
            {"at": "kv", "text": "KV cache ≈*27.6 GB* at *480p*", "side": "right"},
            {"at": "dec", "text": "Paper: *24* fps at *720p*, *8* H800s", "side": "right", "key": True},
        ],
        "feedback": "chunk latents",
        "feedback_from": "upd",
        "feedback_to": "mem",
    },
}
