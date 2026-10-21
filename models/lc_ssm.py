MODEL = {
    "slug": "lc_ssm",
    "name": "Long-Context SSM World Model",
    "year": 2025, "month": 5,
    "org": "Stanford / Adobe",
    "family": "ssm",
    "role": "SSM hybrid",
    "status": "arXiv preprint",
    "params": "200M",
    "params_num": 200e6,
    "open": "closed",
    "links": {"arXiv": "https://arxiv.org/abs/2505.20171"},
    "summary": "An action-conditioned autoregressive video diffusion model whose backbone swaps full attention for a hybrid: "
               "a block-wise Mamba scan carries long-term memory across frames in a fixed-size state, and frame-local "
               "attention keeps nearby frames sharp. Trained with diffusion forcing (independent per-frame noise) plus a "
               "clean-prefix scheme that forces the model to use distant context. Per-frame inference cost and memory stay "
               "constant with rollout length, unlike a growing KV cache.",
    "facts": [
        ("Representation", "VAE latents per frame: an internal spatio-temporal VAE on Memory Maze, the DFoT image VAE on Minecraft; "
                           "tokens scanned spatial-major, time-minor; resolution not stated ('low-resolution synthetic videos')"),
        ("Core", "CogVideoX-style diffusion blocks (AdaLN, FFN) with the attention block replaced by a block-wise SSM scan followed "
                 "by frame-local attention; 200M parameters (all compared models matched at 200M by adjusting the layer count); "
                 "layers and width not disclosed"),
        ("Attention", "Frame-local attention: bidirectional within a 5-frame chunk, causal to the previous chunk, effective window "
                      "k = 10 frames (FlexAttention). The SSM scans over time independently per spatial block (b_h, b_w), block "
                      "sizes differing by layer to trade spatial coherence for temporal memory"),
        ("Actions", "Continuous actions (camera position) through a small MLP added to the noise-level embedding, injected by "
                    "adaptive normalisation; discrete Minecraft actions as learned embeddings"),
        ("Prediction", "Diffusion forcing: one frame per autoregressive step, denoised conditioned on clean past frames; training "
                       "keeps a random clean prefix (p = 0.5, longer than half the sequence); number of denoising steps not disclosed"),
        ("Decoder", "VAE decoder of the respective latent space (not described further)"),
        ("Memory", "Per layer: a KV cache for the last k frames plus one fixed-size SSM state per block, so memory and per-frame "
                   "time are constant in rollout length (Table 1: linear training, constant per-frame inference, long memory); "
                   "recalls content from 400+ frames back"),
        ("Speed", "No numbers in the text: Fig. 8 plots training time per iteration vs 200-800 training frames and inference "
                  "memory and time per frame vs frames generated (flat for this model, growing for causal attention); hardware "
                  "not stated"),
        ("Key detail", "Trained on 400-frame videos, then fine-tuned on 800; FVD 38.9 on 560 frames after 240 context vs 45.1 for a "
                       "full-context causal transformer and 163 for plain Mamba2 (authors, Table S1)"),
    ],
    "evidence": "read",
    "sources": ["arXiv 2505.20171 Sec. 3-4 (architecture, block-wise scan, frame-local attention, action condition, fixed-length state), Table 1",
                "arXiv 2505.20171 Sec. 5.1 (datasets), Sec. 5.3 and Fig. 8 (costs), Supp. S1 Table S1 (FVD)",
                "arXiv 2505.20171 Supp. S2 (VAEs, CogVideoX-style blocks, 200M, k = 10, chunks of 5, training schedule)"],
    "diagram": {
        "encoder": {"text": "Frames → video VAE latents", "sub": "spatio-temporal VAE (Memory Maze) or DFoT image VAE (Minecraft)",
                    "tag": "pretrained", "short": "Video VAE latents"},
        "tokens": {"groups": [("latent", 8, "latent tokens per frame"), ("noise", 1, "per-frame noise level")],
                   "note": "spatial-major token order; actions enter via AdaLN"},
        "core": {"title": "Hybrid SSM/attention blocks · 200M",
                 "rows": [("ssm", "Block-wise Mamba scan over frames"),
                          ("attn", "Frame-local attention, last 10 frames"),
                          ("action", "Action MLP + noise level → AdaLN"),
                          ("mlp", "FFN")],
                 "notes": ["per layer: KV cache of 10 frames + fixed SSM state per block", "block size (b_h, b_w) varies by layer"]},
        "sampling": {"kind": "diffusion", "text": "Diffusion forcing denoising", "sub": "steps not disclosed; one frame per AR step, clean past frames as context",
                     "short": "Diffusion, 1 frame per AR step"},
        "decoder": {"text": "VAE decoder → frame", "sub": "low-resolution synthetic video", "tag": "pretrained"},
        "loop": "AR rollout",
    },
}
