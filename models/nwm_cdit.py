MODEL = {
    "slug": "nwm_cdit",
    "name": "Navigation World Model (CDiT)",
    "year": 2024, "month": 12,
    "org": "Meta FAIR",
    "family": "driving",
    "role": "Diffusion transformer",
    "status": "CVPR 2025",
    "params": "1B (CDiT-XL)",
    "params_num": 1e9,
    "open": "code + weights",
    "links": {"arXiv": "https://arxiv.org/abs/2412.03572", "code": "https://github.com/facebookresearch/nwm"},
    "tagline": "Navigation DiT that cross-attends to past frames",
    "summary": "A navigation world model for robots that predicts the next egocentric frame latent from past frames and a "
               "3-DoF navigation action. Its Conditional Diffusion Transformer runs self-attention only over the tokens of "
               "the frame being denoised and reads the 4 context frames through cross-attention, so cost is linear in the "
               "context length (about 4x fewer FLOPs than a DiT over all frames). Planning is model-predictive control with "
               "the cross-entropy method, or ranking 32 trajectories from an external policy. The default 250 denoising "
               "steps make a 4 s trajectory cost 30.3 s on an RTX 6000 Ada; distillation to 6 steps and time skipping bring "
               "it to 0.4 s (authors).",
    "facts": [
        ("Representation", "Stable Diffusion VAE (sd-vae-ft-ema) latents of 224×224 frames (4:3 centre crop, then resize): "
                           "4×28×28 latent, 2×2 patches → 196 tokens per frame (code) [D]; rollouts at 4 FPS"),
        ("Core", "CDiT-XL, 1B parameters (sizes S to XL); XL/2 = 28 blocks, width 1152, 16 heads, patch 2, MLP ratio 4, the "
                 "DiT-XL/2 shape (code); block = self-attention over the target frame, cross-attention to context frames with a "
                 "skip connection, MLP; AdaLN scale, shift and gates"),
        ("Attention", "Self-attention within the target frame only (n tokens); cross-attention from target queries to the tokens of "
                      "m = 4 context frames as keys and values; cost O(m n² d) vs O(m² n² d) for a full DiT; CDiT-L is 4x faster than "
                      "DiT-XL at equal parameters with better prediction"),
        ("Actions", "Navigation action a = (u ∈ R² translation, yaw φ): each scalar → sine-cosine features → 2-layer MLP to d/3 "
                    "dims, concatenated into ψ_a; time shift k (up to ±16 s) and diffusion timestep t each embedded to R^d the same "
                    "way; ξ = ψ_a + ψ_k + ψ_t drives AdaLN; actions omitted for unlabeled Ego4D training"),
        ("Prediction", "DDPM with the DiT noise schedule and learned covariance (VLB loss); 250 denoising steps by default, distilled "
                       "to 6 (FastVideo DiT distillation); 'Time Skip' composes adjacent action pairs to simulate 8 instead of 16 states for 4 s"),
        ("Decoder", "SD VAE decoder → pixels, used for LPIPS goal scoring during planning and for visualization"),
        ("Memory", "4 context frames re-encoded as cross-attention keys and values at every step; no KV cache discussed; loses context "
                   "on out-of-distribution data (mode collapse noted by the authors)"),
        ("Speed", "One 4 s trajectory (16 states) on one RTX 6000 Ada: 30.3 s default → 14.7 s with Time Skip (8 states) → 0.4 s with "
                  "6-step distillation → 0.1 s with 4-bit quantization (estimated, not measured) (authors, Table 8); ≈7.4-8.3 ms per pass "
                  "in the three measured configurations, ≈2.1 ms implied by the 4-bit estimate [D]; trained on 64 H100s "
                  "(8 machines × 8 GPUs)"),
        ("Key detail", "All of the ≈76x speedup comes from fewer passes (4,000 → 48: 250 → 6 steps, 16 → 8 states), none from "
                       "cheaper passes; ranking 32 trajectories costs 32 × 8 × 6 = 1,536 passes per decision, run as 48 sequential "
                       "batch-32 passes [D]"),
    ],
    "evidence": "read",
    "sources": ["NWM paper, arXiv 2412.03572: Sec. 3.1-3.3 (CDiT block, action encoding, AdaLN, complexity), 4.1 (implementation: "
                "CDiT-XL 1B, 4 context frames, SD VAE, 64 H100), Fig. 2, App. 8.2 and Table 8 (runtime)",
                "Official code github.com/facebookresearch/nwm: models.py (CDiT, XL/2 config), misc.py (224 crop), "
                "config/wm_debug_bs_32.yaml, diffusion/ (DDPM sampler)"],
    "diagram": {
        "encoder": {"text": "Frame → Stable Diffusion VAE", "sub": "224×224 frames, 196 tokens per frame (code)", "tag": "frozen",
                    "short": "SD VAE latents"},
        "tokens": {"groups": [("latent", 8, "target frame latents")],
                   "note": "4 context frames via cross-attention"},
        "core": {"title": "CDiT-XL (1B), 28 blocks, d = 1152",
                 "rows": [("attn", "Self-attn within target frame only"),
                          ("xattn", "Cross-attention to 4 context frames"),
                          ("action", "Action, time shift, timestep → AdaLN"),
                          ("mlp", "MLP")],
                 "notes": ["cost O(m·n²·d), linear in context frames m; no KV cache",
                           "3-DoF action: forward/lateral translation + yaw"]},
        "sampling": {"kind": "diffusion", "text": "DDPM, 250 steps, distilled to 6", "sub": "per frame; ≈7.4-8.3 ms per pass on an RTX 6000 Ada [D]",
                     "short": "250 steps → 6 distilled"},
        "decoder": {"text": "SD VAE decoder → frame", "sub": "for LPIPS goal scoring and visualization", "tag": "frozen",
                    "short": "SD VAE decoder → frame"},
        "loop": "CEM rollout",
    },
    "flow": {
        "below": [{"text": "Frame + navigation action"}],
        "stack": [
            {"box": "SD VAE encoder", "id": "vae", "style": "teal", "basis": "stated"},
            {"group": [
                {"box": "Noisy target latents", "id": "noisy", "style": "soft", "minor": True, "basis": "stated"},
                {"box": "Patchify 2×2 + pos. emb.", "short": "Patchify", "id": "patch", "minor": True, "basis": "code"},
                {"group": [
                    {"residual": [{"box": "AdaLN scale, shift, gate", "short": "AdaLN", "id": "ada", "side": "Action + k + t",
                                   "basis": "stated", "side_basis": "stated"},
                                  {"box": "Target self-attention", "id": "attn", "style": "dark", "basis": "stated"}]},
                    {"residual": [{"box": "AdaLN", "minor": True, "basis": "stated"},
                                  {"box": "Cross-attention", "id": "xattn", "side": "Past frames (K, V)",
                                   "basis": "stated", "side_basis": "stated"}]},
                    {"residual": [{"box": "AdaLN", "minor": True, "basis": "stated"}, {"box": "MLP", "id": "mlp", "basis": "stated"}]},
                ], "repeat": "N ×", "id": "block"},
                {"box": "Noise + covariance", "id": "eps", "minor": True, "basis": "code"},
                {"box": "DDPM update", "id": "upd", "minor": True, "basis": "code"},
            ], "loop": "250 → 6 steps", "tint": "grey", "id": "denoise"},
        ],
        "above": [{"box": "SD VAE decoder", "id": "dec", "style": "teal", "basis": "stated"}, {"text": "Next frame (LPIPS goal scoring)"}],
        "insets": [{"for": "ada", "label": "conditioning", "stack": [{"box": "Sine-cosine features", "basis": "stated"}, {"box": "2-layer MLP", "basis": "stated"},
                                                                       {"box": "Sum a, k, t → ξ", "basis": "stated"}]}],
        "annotations": [
            {"at": "vae", "text": "≈*196* tokens per frame (224², 2×2 patch)", "side": "left"},
            {"at": "xattn", "text": "*4* context frames", "side": "left", "key": True},
            {"at": "block", "text": "*1B* parameters, *28* blocks, d = 1152", "side": "right", "key": True},
            {"at": "upd", "text": "≈*7.4–8.3* ms per pass, RTX 6000 Ada", "side": "right"},
            {"at": "dec", "text": "*30.3* s → *0.4* s per *4* s rollout", "side": "right", "key": True},
        ],
        "feedback": "CEM planning rollout",
    },
    "audit": {"date": "2026-10-23", "checked": 47, "stated": 33, "code": 10, "derived": 4, "assumed": 0, "fixed": 10},
}
