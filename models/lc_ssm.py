MODEL = {
    "slug": "lc_ssm",
    "name": "Long-Context SSM World Model",
    "year": 2025, "month": 5,
    "org": "Stanford / Princeton / Adobe",
    "family": "ssm",
    "role": "SSM hybrid",
    "status": "ICCV 2025",
    "params": "200M",
    "params_num": 200e6,
    "open": "closed",
    "links": {"arXiv": "https://arxiv.org/abs/2505.20171"},
    "tagline": "Mamba scan plus local attention for long memory",
    "summary": "An action-conditioned autoregressive video diffusion model whose backbone swaps full attention for a hybrid: "
               "a block-wise Mamba scan carries long-term memory across frames in a fixed-size state, and frame-local "
               "attention keeps nearby frames sharp. Trained with diffusion forcing (independent per-frame noise) plus a "
               "clean-prefix scheme that encourages the model to use distant context. Per-frame inference cost and memory stay "
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
        ("Prediction", "Diffusion forcing: frames generated autoregressively, denoised conditioned on clean past frames; the "
                       "implementation groups frames into bidirectional 5-frame chunks for training and sampling; training "
                       "keeps a random clean prefix (p = 0.5, longer than half the sequence); number of denoising steps not disclosed"),
        ("Decoder", "Not described (the paper never mentions a decoder); outputs are scored as frames, so the same VAE's "
                    "decoder is assumed"),
        ("Memory", "Per layer: a KV cache for the last k frames plus one fixed-size SSM state per block, so memory and per-frame "
                   "time are constant in rollout length (Table 1: linear training, constant per-frame inference, long memory); "
                   "recalls content from 400+ frames back"),
        ("Speed", "No speed numbers in the text. Fig. 8 plots training time per iteration at 160-800 training frames (linear "
                  "for this model) and inference memory and single-forward-pass time vs frames generated (flat for this model, "
                  "growing for full attention with KV cache). Training about 4.3 H100 GPU-days for the 150K-iteration Maze "
                  "retrieval model vs 5.3 for full-context causal (ICCV supp.)"),
        ("Key detail", "Trained on 400-frame videos, then fine-tuned on 800; FVD 38.9 on 560 frames after 240 context vs 45.1 for a "
                       "full-context causal transformer and 163 for plain Mamba2 (authors, Table S1)"),
    ],
    "evidence": "read",
    "audit": {"date": "2026-10-23", "checked": 47, "stated": 43, "code": 0, "derived": 0, "assumed": 4, "fixed": 13},
    "sources": ["arXiv 2505.20171 Sec. 3-4 (architecture, block-wise scan, frame-local attention, action condition, fixed-length state), Table 1",
                "arXiv 2505.20171 Sec. 5.1 (datasets), Sec. 5.3 and Fig. 8 (costs), Supp. S1 Table S1 (FVD)",
                "arXiv 2505.20171 Supp. S2 (VAEs, CogVideoX-style blocks, 200M, k = 10, chunks of 5, training schedule); Fig. 3 (block layout)",
                "ICCV 2025 paper (CVF Open Access, pp. 8733-8744) and supp. S2 (H100 GPU-days)"],
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
    "flow": {
        "below": [{"text": "Past frames + action"}],
        "stack": [
            {"box": "VAE encoder", "id": "vae", "style": "teal", "basis": "stated"},
            {"box": "Spatial-major tokens", "id": "order", "minor": True, "basis": "stated"},
            {"group": [
                {"box": "Noisy latent frame", "id": "noisy", "style": "soft", "minor": True, "basis": "stated"},
                {"group": [
                    {"residual": [{"box": "AdaLN", "minor": True, "side": "Noise + action", "basis": "stated", "side_basis": "stated"},
                                  {"box": "Block-wise Mamba scan", "id": "ssm", "style": "soft", "basis": "stated"},
                                  {"box": "Scale", "minor": True, "basis": "stated"}]},
                    {"residual": [{"box": "AdaLN", "minor": True, "basis": "stated"},
                                  {"box": "Frame-local attention", "id": "attn", "style": "dark", "basis": "stated"},
                                  {"box": "Scale", "minor": True, "basis": "stated"}]},
                    {"residual": [{"box": "AdaLN", "minor": True, "basis": "stated"}, {"box": "Feed forward", "id": "ffn", "basis": "stated"},
                                  {"box": "Scale", "minor": True, "basis": "stated"}]},
                ], "repeat": "N ×", "id": "block", "basis": "stated"},
                {"box": "Denoising update", "id": "upd", "minor": True, "basis": "assumed"},
            ], "loop": "K denoising steps", "loop_short": "K steps", "tint": "grey", "id": "denoise", "basis": "assumed"},
            {"box": "Update KV + SSM states", "id": "state", "minor": True, "basis": "stated"},
        ],
        "above": [{"box": "VAE decoder", "id": "dec", "style": "teal", "basis": "assumed"}, {"text": "Next frame"}],
        "insets": [
            {"for": "ssm", "label": "block-wise scan", "stack": [{"box": "Split frame into blocks", "basis": "stated"}, {"box": "Scan blocks over time", "basis": "stated"}, {"box": "One SSM state per block", "basis": "stated"}]},
        ],
        "annotations": [
            {"at": "vae", "text": "Resolution not disclosed", "side": "left", "key": True},
            {"at": "ssm", "text": "Fixed state recalls *400+* frames back", "side": "left", "key": True},
            {"at": "attn", "text": "*10*-frame window, *5*-frame chunks", "side": "left"},
            {"at": "block", "text": "*200M* parameters · layers not disclosed", "side": "right", "key": True},
            {"at": "upd", "text": "*5*-frame chunks; steps not disclosed", "side": "right"},
            {"at": "state", "text": "*10*-frame KV + *1* state per block", "side": "right"},
        ],
        "feedback": "next frame",
    },
}
