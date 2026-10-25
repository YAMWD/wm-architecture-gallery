MODEL = {
    "slug": "ge_act",
    "name": "Genie Envisioner (GE-Act)",
    "year": 2025, "month": 8,
    "org": "AgiBot",
    "family": "wam",
    "role": "Diffusion transformer",
    "status": "ICLR 2026",
    "params": "2B + 160M action decoder",
    "params_num": 2.16e9,
    "open": "code + weights",
    "links": {"code": "https://github.com/AgibotTech/Genie-Envisioner-V1", "arXiv": "https://arxiv.org/abs/2508.05635", "page": "https://genie-envisioner.github.io"},
    "tagline": "Thin action DiT reads a video DiT's cached latents",
    "summary": "A two-stream world-action model on top of GE-Base, an instruction-conditioned multi-view video DiT built from "
               "LTX-Video 2B and pretrained on ~3,000 h of AgiBot-World-Beta. GE-Act adds a parallel 160M action branch with "
               "the same depth but a smaller hidden size; it reads the visual latents of every GE-Base block through "
               "cross-attention and denoises a 54-step action trajectory by flow matching. At deployment the video DiT runs "
               "a single denoising step whose latents are cached, the action branch runs 5 steps, and a 54-step trajectory "
               "comes out in 200 ms on a robot-mounted RTX 4090.",
    "facts": [
        ("Representation", "Frozen LTX video-VAE latents of three views (head, left wrist, right wrist); 4 conditioning frames "
                           "per view (sparse memory, the last being the current frame in the code), each one latent frame, plus "
                           "2 predicted latent frames from 9-frame clips at 5 Hz; 48 tokens per latent frame per view at 192x256 "
                           "(32x VAE, patch 1) [D], so 288 per view and 864 for 3 views [D]"),
        ("Core", "GE-Base: LTX-Video 2B DiT (28 layers, 32 heads of 64 = d 2048 [D]); RoPE on Q/K (paper: 2D; code: 3D over "
                 "latent frame, H, W); in code the view embedding is added to the AdaLN-single timestep modulation (shift, "
                 "scale, gate), RMSNorm without affine before self-attention and FFN, un-normalised text cross-attention, "
                 "GELU-tanh FFN; GE-Act: same block design, 28 blocks, width 512 (16 heads x 32) in the policy config, 160M "
                 "parameters"),
        ("Attention", "Video: unmasked self-attention over all (T, H, W) tokens of each view; in every third block (10 of 28 "
                      "[D]) over all 3 views jointly (code; the paper says selected blocks); T5-XXL instruction via "
                      "cross-attention; GE-Act action tokens cross-attend to every block's video hidden states, all views "
                      "concatenated"),
        ("Actions", "54-step trajectories at 30 Hz of 14-D dual-arm actions (released AgiBot config: per-step end-effector "
                    "xyz/rpy deltas + gripper; the paper intro calls them torque trajectories), denoised by flow matching "
                    "from noise-initialised action tokens; a new action DiT is trained from scratch for each new embodiment"),
        ("Prediction", "Slow-fast asynchronous inference: 1 flow-matching step of the video DiT with its latents cached, then "
                       "5 action denoising steps on that cache; video DiT at 5 Hz vs action model at 30 Hz (1:6); closed loop through "
                       "the robot: each chunk consumes live camera views (Sec. 3.1), with no tensor path from actions back to "
                       "the encoder"),
        ("Decoder", "Frozen video VAE decoder, used when GE-Base / GE-Sim generate video; GE-Act deployment skips video "
                    "decoding (return_video=False), though the paper also shows GE-Act generating videos"),
        ("Memory", "Sparse memory: 4 conditioning frames per view (code: 3 sampled earlier frames plus the current one), "
                   "each one latent frame; the paper's GE-Base text counts the initial frame separately"),
        ("Speed", "54-step trajectory in 200 ms on an onboard RTX 4090 mounted on the robot (authors), i.e. 5 chunks/s [D]; "
                  "training: GE-Base-MR 32 A100 x ~7 days, GE-Base-LF 32 A100 x ~3 days, GE-Act pretraining 16 A100 x ~3 days"),
        ("Key detail", "Partial video denoising in deployment: one 2B video pass plus 5 passes of a thin action DiT per "
                       "trajectory [D]"),
    ],
    "evidence": "read",
    "sources": ["arXiv 2508.05635 Sec. 2.1 (GE-Base architecture, views, attention), 2.2 (MR/LF stages, training hardware), "
                "3.1 (GE-Act, 160M), 3.2 (action training), 3.3 (slow-fast inference, 200 ms), Sec. 4 (new embodiments)",
                "Hugging Face Lightricks/LTX-Video transformer/config.json and vae/config.json",
                "Official code github.com/AgibotTech/Genie-Envisioner-V1 @ d41358f (policy_model.yaml, "
                "transformer_ltx_multiview.py, action_patches/patches.py, custom_pipeline.py)",
                "OpenReview fHLtSxDFKC (ICLR 2026 venue)"],
    "figure_variant": "Released GE-Base video cache + GE-Act 160M action decoder",
    "flow": {
        "below": [{"text": "Live views + memory frames + text"}],
        "stack": [
            {"box": "Video VAE encoder", "id": "vae", "style": "teal", "basis": "stated"},
            {"box": "View tokens + noise maps", "id": "tok", "style": "soft", "minor": True, "basis": "stated"},
            {"group": [
                {"residual": [{"box": "AdaLN (scale, shift)", "minor": True, "side": "Timestep + view",
                               "basis": "code", "side_basis": "code"},
                              {"box": "Per-view self-attention", "id": "attn", "style": "dark", "side": "3D RoPE",
                               "basis": "code", "side_basis": "code"},
                              {"box": "Scale by gate", "minor": True, "basis": "code"}]},
                {"residual": [{"box": "Cross-attention", "id": "xattn", "side": "T5-XXL text", "minor": True,
                               "basis": "stated", "side_basis": "stated"}]},
                {"residual": [{"box": "AdaLN (scale, shift)", "minor": True, "basis": "code"},
                              {"box": "Feed forward", "id": "ffn", "basis": "code"},
                              {"box": "Scale by gate", "minor": True, "basis": "code"}]},
            ], "repeat": "28 ×", "id": "vblock", "basis": "code"},
            {"box": "Cache all block latents", "id": "cache", "minor": True, "basis": "code"},
            {"group": [
                {"box": "Noisy action tokens", "id": "noisy", "style": "soft", "minor": True, "basis": "stated"},
                {"group": [
                    {"residual": [{"box": "AdaLN (scale, shift)", "minor": True, "basis": "code"},
                                  {"box": "Self-attention", "id": "aattn", "style": "dark", "minor": True, "basis": "code"},
                                  {"box": "Scale by gate", "minor": True, "basis": "code"}]},
                    {"residual": [{"box": "Cross-attention", "id": "axattn", "side": "Video latents",
                                   "basis": "stated", "side_basis": "stated"}]},
                    {"residual": [{"box": "AdaLN (scale, shift)", "minor": True, "basis": "code"},
                                  {"box": "Feed forward", "id": "affn", "basis": "code"},
                                  {"box": "Scale by gate", "minor": True, "basis": "code"}]},
                ], "repeat": "28 ×", "tint": "orange", "id": "ablock", "basis": "code"},
                {"box": "Update actions", "id": "upd", "minor": True, "basis": "code"},
            ], "loop": "5 action steps", "tint": "grey", "id": "denoise", "basis": "stated"},
            {"box": "Action trajectory", "id": "act", "style": "orange", "minor": True, "basis": "stated"},
        ],
        "above": [{"text": "54 actions at 30 Hz, no video", "id": "out"}],
        "annotations": [
            {"at": "vae", "text": "≈*48* tokens per latent frame per view", "side": "left", "key": True},
            {"at": "attn", "text": "*32* heads · *2,048* · all views every *3rd*", "side": "left"},
            {"at": "vblock", "text": "*28* layers · *2B* parameters", "side": "right", "key": True},
            {"at": "cache", "text": "*1* video step per chunk", "side": "left"},
            {"at": "ablock", "text": "*28* thin blocks · *160M*", "side": "right", "key": True},
            {"at": "out", "text": "*200* ms per trajectory", "side": "left", "key": True},
        ],
    },
}
