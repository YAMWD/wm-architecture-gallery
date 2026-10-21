MODEL = {
    "slug": "ge_act",
    "name": "Genie Envisioner (GE-Act)",
    "year": 2025, "month": 8,
    "org": "AgiBot",
    "family": "wam",
    "role": "Diffusion transformer",
    "status": "ICLR 2026",
    "params": "2B GE-Base + 160M action decoder",
    "params_num": 2.16e9,
    "open": "code + weights",
    "links": {"arXiv": "https://arxiv.org/abs/2508.05635", "page": "https://genie-envisioner.github.io"},
    "summary": "A two-stream world-action model on top of GE-Base, an instruction-conditioned multi-view video DiT built from "
               "LTX-Video 2B and pretrained on ~3,000 h of AgiBot-World-Beta. GE-Act adds a parallel 160M action branch with "
               "the same depth but a smaller hidden size; it reads the visual latents of every GE-Base block through "
               "cross-attention and denoises a 54-step action trajectory by flow matching. At deployment the video DiT runs "
               "a single denoising step whose latents are cached, the action branch runs 5 steps, and a 54-step trajectory "
               "comes out in 200 ms on a robot-mounted RTX 4090.",
    "facts": [
        ("Representation", "Frozen video VAE latents of three views (head, left wrist, right wrist); initial frame plus 4 sparse "
                           "memory frames per view; GE-Base-LF maps 9-frame clips at 5 Hz to 2 latent frames; tokens per frame "
                           "not disclosed"),
        ("Core", "GE-Base: LTX-Video 2B DiT (28 layers, 32 heads of 64 = d 2048 per its config.json) with 2D RoPE plus view "
                 "embeddings, cross-view attention in selected blocks and a causal cross-view block; GE-Act: same block "
                 "design and depth with a reduced hidden size, 160M parameters (width not stated)"),
        ("Attention", "Video: spatial self-attention per view, cross-view self-attention over (views, H, W) in sparse blocks, "
                      "T5-XXL instruction via cross-attention; GE-Act action tokens cross-attend to the visual latents of "
                      "every GE-Base block"),
        ("Actions", "54-step trajectories at 30 Hz (dual-arm 14-D end-effector poses) denoised by flow matching from "
                    "noise-initialised action tokens; a new action DiT is trained from scratch for each new embodiment"),
        ("Prediction", "Slow-fast asynchronous inference: 1 flow-matching step of the video DiT with its latents cached, then "
                       "5 action denoising steps on that cache; video DiT at 5 Hz vs action model at 30 Hz (1:6)"),
        ("Decoder", "Frozen video VAE decoder, used only when GE-Base generates video (GE-Sim); GE-Act never produces pixels"),
        ("Memory", "Sparse memory: 4 frames sampled from earlier chunks, concatenated with the initial frame per view"),
        ("Speed", "54-step trajectory in 200 ms on an onboard RTX 4090 mounted on the robot (authors), i.e. 5 chunks/s [D]; "
                  "training: GE-Base-MR 32 A100 x ~7 days, GE-Base-LF 32 A100 x ~3 days, GE-Act pretraining 16 A100 x ~3 days"),
        ("Key detail", "Partial video denoising in deployment: one 2B video pass plus 5 passes of a thin action DiT [D]; the "
                       "only model in this set timed on a single robot-mounted consumer GPU"),
    ],
    "evidence": "read",
    "sources": ["arXiv 2508.05635 Sec. 2.1 (GE-Base architecture, views, attention), 2.2 (MR/LF stages, training hardware), "
                "3.1 (GE-Act, 160M), 3.2 (action training), 3.3 (slow-fast inference, 200 ms), Sec. 4 (new embodiments)",
                "Hugging Face Lightricks/LTX-Video transformer/config.json (28 layers, 32 heads x 64; fetched)",
                "ICLR 2026 page (venue; code and models promised, release not verified here)"],
    "diagram": {
        "encoder": {"text": "3 views → video VAE", "sub": "initial frame + 4 sparse memory frames per view; tokens per frame not disclosed",
                    "tag": "frozen", "short": "Video VAE, 3 views + memory"},
        "tokens": {"groups": [("latent", 16, "3-view latents + noise"), ("action", 8, "54 noisy action tokens")],
                   "note": "video DiT at 5 Hz; action branch at 30 Hz"},
        "core": {"title": "LTX-Video DiT ×28 · d 2048 · 32 heads",
                 "rows": [("attn", "Spatial self-attention; cross-view attention (views, H, W) in selected blocks"),
                          ("xattn", "Cross-attention to T5-XXL instruction embeddings"),
                          ("moe", "GE-Act branch: same depth, smaller width (160M), cross-attends to each block's latents"),
                          ("mlp", "MLP")],
                 "notes": ["2D RoPE + view embeddings; 1 video step cached for 5 action steps"]},
        "sampling": {"kind": "diffusion", "text": "Flow matching: 1 video step (cached) + 5 action steps",
                     "sub": "per 54-step trajectory", "short": "1 video step + 5 action steps"},
        "heads": ["action chunk"],
        "decoder": {"none": "GE-Act never decodes video; the VAE decoder serves GE-Base / GE-Sim generation"},
        "loop": "closed loop with real frames",
    },
    "flow": {
        "below": [{"text": "3 views + memory frames + instruction"}],
        "stack": [
            {"box": "Video VAE encoder (frozen)", "short": "Video VAE encoder", "id": "vae", "style": "teal"},
            {"box": "View tokens + noise maps", "id": "tok", "style": "soft", "minor": True, "side": "Timestep enc."},
            {"group": [
                {"residual": [{"box": "Spatial / cross-view attention", "short": "Spatial attention", "id": "attn", "style": "dark", "side": "2D RoPE + view emb."}]},
                {"residual": [{"box": "Cross-attention", "id": "xattn", "side": "T5-XXL text", "minor": True}]},
                {"residual": [{"box": "Feed forward", "id": "ffn"}]},
            ], "repeat": "28 ×", "id": "vblock"},
            {"box": "Cache every block's latents", "short": "Cached block latents", "id": "cache", "minor": True},
            {"group": [
                {"box": "Noisy action tokens", "id": "noisy", "style": "soft", "minor": True},
                {"group": [
                    {"residual": [{"box": "Self-attention", "id": "aattn", "style": "dark", "minor": True}]},
                    {"residual": [{"box": "Cross-attention", "id": "axattn", "side": "Video latents"}]},
                    {"residual": [{"box": "Feed forward", "id": "affn"}]},
                ], "repeat": "28 ×", "tint": "orange", "id": "ablock"},
                {"box": "Update actions", "id": "upd", "minor": True},
            ], "loop": "5 action steps", "tint": "grey", "id": "denoise"},
            {"box": "Action trajectory", "id": "act", "style": "orange"},
        ],
        "above": [{"text": "54 actions at 30 Hz; no video decoded", "short": "54 actions; no video decoded"}],
        "annotations": [
            {"at": "vae", "text": "frozen video VAE; head and two wrist views, each with the initial frame + *4* sparse memory frames; tokens per frame not disclosed",
             "short": "*3* views + *4* memory frames; tokens per frame not disclosed", "side": "left", "key": True},
            {"at": "attn", "text": "spatial self-attention per view; cross-view attention over (views, H, W) only in selected blocks; *32* heads of *64*", "side": "left"},
            {"at": "vblock", "text": "GE-Base: LTX-Video 2B DiT, *28* layers, d *2,048*; *1* flow-matching step per inference pass, then the latents of every block are cached; norms and modulation not detailed",
             "short": "GE-Base: *28* layers, d *2,048*; *1* video step, latents cached", "side": "right", "key": True},
            {"at": "axattn", "text": "each action block cross-attends to the cached latents of the matching GE-Base block", "side": "left"},
            {"at": "affn", "text": "GE-Act: same block design and depth, reduced width (not stated), *160M*; a new action DiT is trained for each embodiment",
             "short": "GE-Act: *28* thin blocks, *160M*", "side": "right", "key": True},
            {"at": "upd", "text": "*5* flow-matching steps on the cached video latents; video latents at *5* Hz, actions at *30* Hz (*1:6*)", "side": "left"},
            {"at": "act", "text": "*54*-step trajectory (dual-arm 14-D poses) in *200* ms on an RTX 4090 mounted on the robot (authors)",
             "short": "*54* actions in *200* ms on one RTX 4090 (authors)", "side": "right", "key": True},
        ],
        "feedback": "next chunk",
    },
}
