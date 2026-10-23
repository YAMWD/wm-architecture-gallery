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
               "timestep embedding, camera pose through a relative encoding inside attention. The company's 24 FPS at 720p "
               "needs 8 H800 GPUs with token parallelism, quantization and streaming VAE decode.",
    "facts": [
        ("Representation", "HunyuanVideo-1.5 causal 3D VAE: 16x spatial, 4x temporal, 32 channels; patch 1x1x1 → 3,600 tokens "
                           "per latent frame at 720p, 14,400 per 4-latent chunk of 16 frames [D]"),
        ("Core", "HunyuanVideo-1.5 480P-I2V transformer: 54 double-stream MM-DiT blocks, d 2048, 16 heads, MLP ratio 4, "
                 "GELU-tanh (HF config); no cross-attention in the released code: text tokens (2-layer token refiner) run in a "
                 "parallel stream whose K/V join the video attention; timestep adaLN; "
                 "8B per the README (a 5B Wan-based variant is lighter but weaker)"),
        ("Attention", "Block-causal over chunks with a KV cache; context = 3 temporal + 1 spatial chunk + the first chunk as attention "
                      "sink = 20 latents = 72,000 tokens at 720p (86,400 with the current chunk) [D]; temporal reframing "
                      "re-assigns RoPE indices so context frames sit at a small relative distance"),
        ("Actions", "Dual representation: discrete keys → PE + zero-initialized MLP added to the timestep embedding (adaLN); "
                    "camera pose → PRoPE relative encoding in a second attention term, output = Attn1 + zero_init(Attn2)"),
        ("Prediction", "Flow matching; Context Forcing distillation (memory-augmented bidirectional teacher, DMD loss) from "
                       "100 NFE to 4 denoising steps per 16-frame chunk"),
        ("Decoder", "HunyuanVideo-1.5 VAE decoder → 16 frames per chunk; progressive decode in small batches streamed over "
                    "Triton, parallelized over 8 GPUs; the open checkpoints are 480P"),
        ("Memory", "Reconstituted context memory rebuilt per chunk by FOV-overlap and camera-distance retrieval from past "
                   "chunks; no explicit 3D state; its KV cache is recomputed in one extra pass per chunk; KV ≈63.7 GB in BF16 for "
                   "the 72,000-token context (RoPE and PRoPE K/V both cached), ≈8.0 GB per GPU when split 8 ways [D]"),
        ("Speed", "24 FPS at 720p on 8×H800 (company claim); Table 4: 2.80 → 3.80 (DiT parallelism + quantization) → 16.0 (+VAE) "
                  "→ 24.0 FPS (+streaming decode); 4.95 FPS for the 8B model on 4×H200 (measured by WorldKV); 28 GB per GPU at sp=8 (README)"),
        ("Key detail", "Distillation cuts passes 25x, but the remaining 8.57x to real time is systems work; ≈90% of per-chunk "
                       "DiT FLOPs is attention: two attention terms (RoPE and PRoPE) per block over ≈86,400 tokens [D]"),
    ],
    "evidence": "read",
    "sources": ["arXiv 2512.14614 Sec. 3.1-3.5, Table 4, App. A, Table 8",
                "HF tencent/HunyuanVideo-1.5 transformer/480p_i2v/config.json and vae/config.json",
                "HY-WorldPlay code: worldplay_1_5_transformer.py, modules/attention.py, utils/retrieval_context.py, worldplay_video_pipeline.py",
                "ICML 2026 poster page (WorldPlay)",
                "HY-WorldPlay README (8B HY Video / 5B Wan lines, 480P checkpoints, GPU memory at sp=8)",
                "WorldKV arXiv 2605.22718 Table 1 (4.95 FPS on 4×H200)"],
    "diagram": {
        "encoder": {"text": "Frames → HunyuanVideo-1.5 3D causal VAE", "sub": "16x spatial, 4x temporal, 32 ch; 3,600 tokens per latent frame at 720p",
                    "short": "HY-1.5 VAE → 3,600 latents"},
        "tokens": {"groups": [("latent", 24, "14,400 latents per chunk")],
                   "note": "memory 3 + 1 chunks + sink = 72,000 tokens"},
        "core": {"title": "HunyuanVideo-1.5 DiT ×54 · d 2048 · 16 heads",
                 "rows": [("attn", "Block-causal self-attention, 3D RoPE"),
                          ("action", "Camera pose: PRoPE inside attention"),
                          ("action", "Keys: PE + MLP → timestep adaLN"),
                          ("attn", "Text tokens join attention K/V (no cross-attn)"),
                          ("mlp", "MLP (ratio 4)")],
                 "notes": ["KV cache; memory rebuilt per chunk: 3 recent + 1 retrieved, first chunk as sink",
                           "temporal reframing: retrieved chunk gets a recent RoPE index"]},
        "sampling": {"kind": "diffusion", "text": "Context Forcing (DMD), 4 denoising steps", "sub": "per chunk of 16 frames; teacher 100 NFE",
                     "short": "4 steps per 16-frame chunk"},
        "decoder": {"text": "HY-1.5 VAE decoder → 16 frames at 720p", "sub": "progressive streaming decode, split over 8 GPUs",
                    "short": "HY-1.5 VAE decoder → 16 frames"},
        "loop": "AR rollout",
    },
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
                                  {"box": "Block-causal attention", "id": "attn", "style": "dark", "side": "Text+memory+PRoPE",
                                   "basis": "stated", "side_basis": "code"}]},
                    {"residual": [{"box": "AdaLN", "minor": True, "basis": "code"}, {"box": "Feed forward", "id": "ffn", "basis": "stated"}]},
                ], "repeat": "54 ×", "id": "block"},
                {"box": "Predicted velocity", "id": "vel", "minor": True, "basis": "stated"},
                {"box": "Update latents", "id": "upd", "minor": True, "basis": "code"},
            ], "loop": "4 steps (DMD)", "tint": "grey", "id": "denoise"},
        ],
        "above": [{"box": "HY-1.5 VAE decoder", "id": "dec", "style": "teal", "basis": "code"}, {"text": "16 frames per chunk at 720p"}],
        "annotations": [
            {"at": "vae", "text": "≈*14,400* tokens per chunk of *16* frames", "side": "left", "key": True},
            {"at": "mem", "text": "*3* recent + *1* retrieved + sink ≈ *72k* tokens", "side": "left", "key": True},
            {"at": "attn", "text": "*16* heads · width *2,048*", "side": "left"},
            {"at": "block", "text": "*54* blocks · *8B* parameters", "side": "right", "key": True},
            {"at": "kv", "text": "KV cache ≈*63.7 GB*", "side": "right"},
            {"at": "dec", "text": "*24* fps at *720p*", "side": "right", "key": True},
        ],
        "feedback": "next chunk",
    },
    "audit": {"date": "2026-10-23", "checked": 48, "stated": 22, "code": 19, "derived": 7, "assumed": 0, "fixed": 16},
}
