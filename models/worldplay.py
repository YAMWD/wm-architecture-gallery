MODEL = {
    "slug": "worldplay",
    "name": "WorldPlay (HY-World 1.5)",
    "year": 2025, "month": 12,
    "org": "Tencent Hunyuan",
    "family": "dit",
    "role": "Diffusion transformer",
    "status": "arXiv preprint (ICML 2026 format), v2 Jun 2026",
    "params": "8B (HunyuanVideo-1.5); 5B Wan variant",
    "params_num": 8e9,
    "open": "code + weights",
    "links": {"arXiv": "https://arxiv.org/abs/2512.14614", "code": "https://github.com/Tencent-Hunyuan/HY-WorldPlay",
              "weights": "https://huggingface.co/tencent/HY-WorldPlay"},
    "summary": "Tencent's real-time interactive world model: the HunyuanVideo-1.5 MM-DiT made chunk-wise block-causal "
               "(4 latent frames = 16 video frames per chunk) and distilled with Context Forcing to 4 steps. Each chunk "
               "attends to a memory rebuilt from the 3 most recent chunks plus 1 chunk retrieved by field-of-view overlap "
               "and camera distance, with RoPE indices re-assigned so old frames look recent. Keys enter through the "
               "timestep embedding, camera pose through a relative encoding inside attention. The company's 24 FPS at 720p "
               "needs 8 H800 GPUs with token parallelism, quantization and streaming VAE decode.",
    "facts": [
        ("Representation", "HunyuanVideo-1.5 causal 3D VAE: 16x spatial, 4x temporal, 32 channels; patch 1x1x1 → 3,600 tokens "
                           "per latent frame at 720p, 14,400 per 4-latent chunk of 16 frames [D]"),
        ("Core", "HunyuanVideo-1.5 480P-I2V transformer: 54 double-stream MM-DiT blocks, d 2048, 16 heads, MLP ratio 4 "
                 "(HF config); the paper describes each block as 3D self-attention + cross-attention + FFN with timestep adaLN; "
                 "8B per the README (a 5B Wan-based variant is lighter but weaker)"),
        ("Attention", "Block-causal over chunks with a KV cache; context = 3 temporal + 1 spatial memory chunk = 57,600 tokens at "
                      "720p [D]; first chunk kept as an attention sink; temporal reframing re-assigns RoPE indices so a retrieved "
                      "chunk sits at a small relative distance"),
        ("Actions", "Dual representation: discrete keys → PE + zero-initialized MLP added to the timestep embedding (adaLN); "
                    "camera pose → PRoPE relative encoding in a second attention term, output = Attn1 + zero_init(Attn2)"),
        ("Prediction", "Flow matching; Context Forcing distillation (memory-augmented bidirectional teacher, DMD loss) from "
                       "100 NFE to 4 denoising steps per 16-frame chunk"),
        ("Decoder", "HunyuanVideo-1.5 VAE decoder → 16 frames per chunk; progressive decode in small batches streamed over "
                    "Triton, parallelized over 8 GPUs; the open checkpoints are 480P"),
        ("Memory", "Reconstituted context memory rebuilt per chunk by FOV-overlap and camera-distance retrieval from past "
                   "chunks; no explicit 3D state; KV ≈25.5 GB in BF16 for the 57,600-token context, ≈3.2 GB per GPU when split 8 ways [D]"),
        ("Speed", "24 FPS at 720p on 8×H800 (company claim); Table 4: 2.80 → 3.80 (DiT parallelism + quantization) → 16.0 (+VAE) "
                  "→ 24.0 FPS (+streaming decode); 4.95 FPS for the 8B model on 4×H200 (measured by WorldKV); 28 GB per GPU at sp=8 (README)"),
        ("Key detail", "Distillation cuts passes 25x, but the remaining 8.57x to real time is systems work; ≈85% of per-chunk "
                       "FLOPs is attention against the 72,000-token sequence [D]"),
    ],
    "evidence": "read",
    "sources": ["arXiv 2512.14614 Sec. 3.1-3.5, Table 4, App. A, Table 8",
                "HF tencent/HunyuanVideo-1.5 transformer/480p_i2v/config.json and vae/config.json (local copies)",
                "HY-WorldPlay README (8B HY Video / 5B Wan lines, 480P checkpoints, GPU memory at sp=8)",
                "WorldKV arXiv 2605.22718 Table 1 (4.95 FPS on 4×H200)"],
    "diagram": {
        "encoder": {"text": "Frames → HunyuanVideo-1.5 3D causal VAE", "sub": "16x spatial, 4x temporal, 32 ch; 3,600 tokens per latent frame at 720p",
                    "short": "HY-1.5 VAE → 3,600 latents"},
        "tokens": {"groups": [("latent", 24, "14,400 latents per chunk")],
                   "note": "memory 4 chunks = 57,600 tokens"},
        "core": {"title": "HunyuanVideo-1.5 DiT ×54 · d 2048 · 16 heads",
                 "rows": [("attn", "Block-causal self-attention, 3D RoPE"),
                          ("action", "Camera pose: PRoPE inside attention"),
                          ("action", "Keys: PE + MLP → timestep adaLN"),
                          ("xattn", "Cross-attention to text (MM-DiT)"),
                          ("mlp", "MLP (ratio 4)")],
                 "notes": ["KV cache; memory rebuilt per chunk: 3 recent + 1 retrieved, first chunk as sink",
                           "temporal reframing: retrieved chunk gets a recent RoPE index"]},
        "sampling": {"kind": "diffusion", "text": "Context Forcing (DMD), 4 denoising steps", "sub": "per chunk of 16 frames; teacher 100 NFE",
                     "short": "4 steps per 16-frame chunk"},
        "decoder": {"text": "HY-1.5 VAE decoder → 16 frames at 720p", "sub": "progressive streaming decode, split over 8 GPUs",
                    "short": "HY-1.5 VAE decoder → 16 frames"},
        "loop": "AR rollout",
    },
}
