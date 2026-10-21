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
    "summary": "A navigation world model for robots that predicts the next egocentric frame latent from past frames and a "
               "3-DoF navigation action. Its Conditional Diffusion Transformer runs self-attention only over the tokens of "
               "the frame being denoised and reads the 4 context frames through cross-attention, so cost is linear in the "
               "context length (about 4x fewer FLOPs than a DiT over all frames). Planning is model-predictive control with "
               "the cross-entropy method, or ranking 32 trajectories from an external policy. The default 250 denoising "
               "steps make a 4 s trajectory cost 30.3 s on an RTX 6000 Ada; distillation to 6 steps and time skipping bring "
               "it to 0.4 s (authors).",
    "facts": [
        ("Representation", "Stable Diffusion VAE latents, 'similar as in DiT'; input resolution and tokens per frame are not stated "
                           "in the paper text read; rollouts at 4 FPS"),
        ("Core", "CDiT-XL, 1B parameters (sizes S to XL); depth, width and heads not stated in the text read; block = self-attention "
                 "over the target frame, cross-attention to context frames with a skip connection, MLP; AdaLN scale, shift and gates"),
        ("Attention", "Self-attention within the target frame only (n tokens); cross-attention from target queries to the tokens of "
                      "m = 4 context frames as keys and values; cost O(m n² d) vs O(m² n² d) for a full DiT; CDiT-L is 4x faster than "
                      "DiT-XL at equal parameters with better prediction"),
        ("Actions", "Navigation action a = (u ∈ R² translation, yaw φ) plus time shift k (up to ±16 s) and diffusion timestep t: each "
                    "scalar → sine-cosine features → 2-layer MLP, summed into one vector that drives AdaLN; actions omitted for "
                    "unlabeled Ego4D training"),
        ("Prediction", "DDPM with the DiT noise schedule and learned covariance (VLB loss); 250 denoising steps by default, distilled "
                       "to 6 (FastVideo DiT distillation); 'Time Skip' composes adjacent action pairs to simulate 8 instead of 16 states for 4 s"),
        ("Decoder", "SD VAE decoder → pixels, used for LPIPS goal scoring during planning and for visualization"),
        ("Memory", "4 context frames re-encoded as cross-attention keys and values at every step; no KV cache discussed; loses context "
                   "on out-of-distribution data (mode collapse noted by the authors)"),
        ("Speed", "One 4 s trajectory (16 states) on one RTX 6000 Ada: 30.3 s default → 14.7 s with Time Skip (8 states) → 0.4 s with "
                  "6-step distillation → 0.1 s with 4-bit quantization (estimated, not measured) (authors, Table 8); ≈7-8 ms per 1B pass "
                  "in every configuration [D]; trained on 64 H100s"),
        ("Key detail", "All of the 75x speedup comes from fewer passes (250 → 6 steps, 16 → 8 states), none from cheaper passes; planning "
                       "evaluates 32 independent trajectories, 8 states × 6 steps = 1,536 batchable passes per decision [D]"),
    ],
    "evidence": "read",
    "sources": ["NWM paper page (local src/nwm.txt): Sec. 3.1-3.3 (CDiT block, action encoding, AdaLN, complexity), 4 (implementation: "
                "CDiT-XL 1B, 4 context frames, SD VAE, 64 H100), 4.4 (planning), App. 7 and Table 8 (runtime)",
                "ar_token_and_physical_ai.md Group 2 (derived per-pass time)",
                "code link from the project page (release not re-verified in this pass)"],
    "diagram": {
        "encoder": {"text": "Frame → Stable Diffusion VAE", "sub": "resolution and tokens per frame not stated", "tag": "frozen",
                    "short": "SD VAE latents"},
        "tokens": {"groups": [("latent", 8, "target frame latents")],
                   "note": "4 context frames via cross-attention"},
        "core": {"title": "CDiT-XL (1B), depth and width not stated",
                 "rows": [("attn", "Self-attn within target frame only"),
                          ("xattn", "Cross-attention to 4 context frames"),
                          ("action", "Action, time shift, timestep → AdaLN"),
                          ("mlp", "MLP")],
                 "notes": ["cost O(m·n²·d), linear in context frames m; no KV cache",
                           "3-DoF action: forward/lateral translation + yaw"]},
        "sampling": {"kind": "diffusion", "text": "DDPM, 250 steps, distilled to 6", "sub": "per frame; ≈7-8 ms per pass on an RTX 6000 Ada [D]",
                     "short": "250 steps → 6 distilled"},
        "decoder": {"text": "SD VAE decoder → frame", "sub": "for LPIPS goal scoring and visualization", "tag": "frozen",
                    "short": "SD VAE decoder → frame"},
        "loop": "CEM rollout",
    },
}
