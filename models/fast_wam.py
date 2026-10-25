MODEL = {
    "slug": "fast_wam",
    "name": "Fast-WAM",
    "year": 2026, "month": 3,
    "org": "Tsinghua IIIS, Galaxea AI",
    "family": "wam",
    "role": "LLM or mixture of transformers",
    "status": "arXiv preprint (v2 Mar 2026)",
    "params": "6B (5B video DiT + 1B action expert)",
    "params_num": 6e9,
    "open": "code + weights",
    "links": {"code": "https://github.com/yuantianyuan01/FastWAM", "arXiv": "https://arxiv.org/abs/2603.16666", "page": "https://yuantianyuan01.github.io/FastWAM"},
    "tagline": "Video DiT plus action expert, no imagined video",
    "summary": "A mixture-of-transformers world-action model that keeps video co-training but drops test-time imagination. "
               "A Wan2.2-5B video DiT and a 1B action-expert DiT (the same architecture at d 1024) share attention; in "
               "training, future video latents and the action chunk are denoised jointly under a structured mask, while at "
               "inference the video DiT runs once over the clean first-frame tokens and the action expert denoises a "
               "32-step chunk in 10 steps. That gives 190 ms per chunk on one RTX 5090D against 810 ms for the "
               "Fast-WAM-IDM variant.",
    "facts": [
        ("Representation", "Wan2.2 VAE latents of the observation, with the multi-camera images concatenated into one image; "
                           "training video chunks of 9 frames after 4x temporal downsampling; 98 tokens per latent frame on "
                           "LIBERO (224x448 input) and 120 on RoboTwin (384x320) [D from released config]; a "
                           "proprioceptive-state token joins the T5 context (code)"),
        ("Core", "Video DiT from Wan2.2-5B (30 layers, d 3072, 24 heads, FFN 14,336 per its config.json) plus an action "
                 "expert with the same architecture at d 1024 (1B); T5 text reaches all tokens through cross-attention. "
                 "The paper does not detail norms or timestep modulation; the released code uses the same Wan DiTBlock "
                 "for both experts: AdaLN-modulated LayerNorm, gated self-attention residual, LayerNorm cross-attention "
                 "residual, AdaLN-modulated gated GELU FFN residual. The video pass runs at timestep 0; the action expert "
                 "has its own timestep embedder and a Linear output head"),
        ("Attention", "Shared attention with a structured mask: clean first-frame tokens attend to nothing else; future video "
                      "tokens (training only) attend within the video branch and to the first frame; action tokens attend "
                      "within the action branch and to the first frame, never to future video"),
        ("Actions", "Action chunk of h = 32 as tokens in the action expert, denoised by flow matching; at inference the "
                    "expert reads the single-pass video features through the shared attention"),
        ("Prediction", "Training: joint flow matching over actions and future video latents (paper: logit-normal t; "
                       "released code: shift-warped uniform t with a bell-shaped loss weight); inference: one "
                       "video-DiT pass over the clean first frame, then 10 action denoising steps at CFG 1.0 (no second pass)"),
        ("Decoder", "None at deployment: no future video tokens are instantiated, denoised or decoded"),
        ("Memory", "Single-chunk policy; the outer autoregressive loop is omitted. Within a chunk, the video DiT's "
                   "per-layer K/V over the clean first-frame tokens is cached once and reused by all 10 action "
                   "steps (Fig. 1C; code prefill_video_cache)"),
        ("Speed", "190 ms per chunk on one RTX 5090D V2 32 GB (authors); the imagine-then-execute variant Fast-WAM-IDM takes "
                  "810 ms on the same GPU"),
        ("Key detail", "Removing test-time imagination costs little accuracy while removing video co-training costs much; "
                       "the deployed graph is 1 pass of the 5B DiT plus 10 passes of the 1B expert [D]"),
    ],
    "evidence": "read",
    "sources": ["arXiv 2603.16666 Sec. 1, 3.2 and Fig. 1(C) (architecture, mask, KV cache, inference), 4.1 (Wan2.2-5B, "
                "d_a 1024, h 32, 10 steps, CFG 1.0, RTX 5090D), 4.3.3 (190 vs 810 ms)",
                "Hugging Face Wan-AI/Wan2.2-TI2V-5B config.json (30 layers, d 3072, 24 heads, FFN 14336)",
                "GitHub yuantianyuan01/FastWAM (MIT): configs/model/fastwam.yaml, configs/data/libero_2cam.yaml and "
                "robotwin.yaml, src/fastwam/models/wan22/mot.py, fastwam.py, wan_video_dit.py (DiTBlock), action_dit.py (Linear head, "
                "action timestep embedder), schedulers/scheduler_continuous.py",
                "Hugging Face yuanty/fastwam LIBERO and RoboTwin checkpoints"],
    "figure_variant": "Released Fast-WAM policy: cached first-frame video K/V, 10 action steps",
    "flow": {
        "below": [{"text": "Cameras tiled + state + text"}],
        "stack": [
            {"box": "Wan2.2 VAE encoder", "id": "vae", "style": "teal", "basis": "stated"},
            {"box": "Clean first-frame tokens", "id": "first", "minor": True, "basis": "stated"},
            {"box": "Video DiT, one pass", "id": "vdit", "basis": "stated"},
            {"box": "Per-layer K/V cache", "id": "kv", "minor": True, "basis": "stated"},
            {"group": [
                {"box": "Add noisy action tokens", "short": "Add action tokens", "id": "noisy", "style": "soft", "minor": True,
                 "side": "Noisy action chunk", "basis": "stated", "side_basis": "stated"},
                {"group": [
                    {"residual": [{"box": "AdaLN", "minor": True, "side": "Action timestep", "basis": "code", "side_basis": "code"},
                                  {"box": "Action QKV", "id": "aqkv", "style": "orange", "minor": True, "basis": "code"},
                                  {"box": "Shared masked attention", "id": "attn", "style": "dark", "side": "Cached video K/V",
                                   "basis": "code", "side_basis": "code"},
                                  {"box": "Scale by gate", "minor": True, "basis": "code"}]},
                    {"residual": [{"box": "LayerNorm", "minor": True, "basis": "code"},
                                  {"box": "Cross-attention", "id": "xattn", "side": "T5 text", "basis": "stated", "side_basis": "stated"}]},
                    {"residual": [{"box": "AdaLN", "minor": True, "basis": "code"},
                                  {"box": "Action-expert MLP", "short": "Action MLP", "id": "amlp", "style": "orange", "basis": "code"},
                                  {"box": "Scale by gate", "minor": True, "basis": "code"}]},
                ], "repeat": "30 ×", "id": "block"},
                {"box": "Action velocity head", "minor": True, "basis": "code"},
                {"box": "Update action tokens", "id": "upd", "minor": True, "basis": "code"},
            ], "loop": "10 action steps", "tint": "grey", "id": "denoise"},
            {"box": "Action chunk", "id": "act", "style": "orange", "basis": "stated"},
        ],
        "above": [{"text": "32 actions; no video decoded"}],
        "insets": [{"for": "vdit", "label": "per layer, ×30", "stack": [
            {"residual": [{"box": "AdaLN", "minor": True, "side": "Timestep t=0", "basis": "code", "side_basis": "code"},
                          {"box": "First-frame self-attn", "style": "dark", "basis": "stated"},
                          {"box": "Scale by gate", "minor": True, "basis": "code"}]},
            {"residual": [{"box": "LayerNorm + cross-attn", "side": "T5 text", "basis": "code", "side_basis": "stated"}]},
            {"residual": [{"box": "AdaLN", "minor": True, "basis": "code"}, {"box": "Video MLP", "basis": "code"},
                          {"box": "Scale by gate", "minor": True, "basis": "code"}]}]}],
        "annotations": [
            {"at": "vae", "text": "≈*98* tokens per latent frame (RoboTwin *120*)", "side": "left", "key": True},
            {"at": "vdit", "text": "*30* layers · width *3,072* · ≈*5B*", "side": "left", "key": True},
            {"at": "attn", "text": "*24* heads · width *3,072* · cached K/V", "side": "left"},
            {"at": "block", "text": "*30* layers · width *1,024* · *1B*", "side": "left", "key": True},
            {"at": "denoise", "text": "*10* steps; video DiT not rerun", "side": "right"},
            {"at": "act", "text": "*190* ms per chunk · imagine-first *810* ms", "side": "right", "key": True},
        ],
    },
}
