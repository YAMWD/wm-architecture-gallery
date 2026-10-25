MODEL = {
    "slug": "lingbot_world_fast",
    "name": "LingBot-World-Fast",
    "year": 2026, "month": 1,
    "org": "Robbyant",
    "family": "dit",
    "role": "Diffusion transformer",
    "status": "arXiv preprint (company), Jan 2026",
    "params": "≈18.5B dense (14.3B Wan2.2 expert + 4.3B camera layers)",
    "params_num": 18.5e9,
    "open": "code + weights",
    "links": {"arXiv": "https://arxiv.org/abs/2601.20540", "code": "https://github.com/robbyant/lingbot-world",
              "weights": "https://huggingface.co/robbyant/lingbot-world-fast"},
    "tagline": "Causal Wan DiT that keeps the whole rollout in KV",
    "summary": "A real-time open world model: the high-noise expert of the middle-trained LingBot-World MoE (Wan2.2 I2V "
               "A14B architecture, two ≈14B experts, one active per timestep) is adapted to block-causal attention and distilled "
               "with DMD plus an adversarial head to 4 steps. In the released checkpoint, camera poses enter as Plücker-style ray "
               "maps through scale-and-shift adapters in every block (≈18.5B parameters in all); the paper's W/A/S/D-key variant is "
               "the Base (Act) model. By default it keeps the full KV cache of the whole rollout, so memory is emergent from context, "
               "but the cache grows by about 3.4 GB per 12-frame chunk, past 200 GB in a minute (WorldKV; ≈3.83 GB in BF16 by "
               "our count [D]), and throughput falls from 8.9 to 3.6 FPS over a minute "
               "(WorldKV, 4×B200). The company claims 16 fps at 480p on one GPU node; the release script uses 8 GPUs.",
    "facts": [
        ("Representation", "Wan 3D causal VAE, stride 4x8x8 → 60x104 latent frame at 480x832; patch (1,2,2) → 1,560 tokens (30x52 grid) "
                           "per latent frame [D]; chunk = 3 latent frames = 4,680 tokens = 12 output frames, 9 for the first chunk [D]"),
        ("Core", "Wan2.2 I2V A14B config: 40 layers, d 5120, 40 heads, FFN 13824; initialized from the high-noise expert of the "
                 "middle-trained LingBot-World MoE (two ≈14B experts, one active per timestep), a dense causal DiT: 18.54B in the "
                 "released checkpoint (14.29B Wan backbone + 4.26B camera layers; 14B in the paper)"),
        ("Attention", "Block-causal: bidirectional within a chunk, causal across chunks, KV cache; local_attn_size -1 and "
                      "sink_size 0 by default = full KV over the whole rollout (window and sink exist as flags)"),
        ("Actions", "Released Fast: camera poses → per-pixel [ray origin, ray direction] → Plücker encoder (Linear 1536→5120 + "
                    "residual MLP) → per-block MLP → scale and shift of the residual stream (no norm). The paper's rotation Plücker + "
                    "multi-hot W/A/S/D keys is the Base (Act) variant; in Stage II only the action adapters were trained"),
        ("Prediction", "DMD with self-rollout plus an adversarial head on the fake-score network (APT-style, no R1/R2); 4 steps "
                       "at indices [0, 179, 358, 679] of the 1,000-step schedule, shift 10 in the release CLI (generate() default 5); "
                       "the bidirectional base samples 70 steps"),
        ("Decoder", "Wan VAE decoder at 480x832, 12 frames per chunk (9 for the first); the release decodes all chunks in one call "
                    "after the rollout loop (README lists 480P & 720P)"),
        ("Memory", "No memory module: 'an emergent ability derived from the context window'; full KV ≈3.4 GB per 3-latent-frame "
                   "chunk and >200 GB per minute (WorldKV Sec. 4.3; ≈3.83 GB per chunk in BF16 by our count: 4,680 tokens x 40 layers x "
                   "K,V x 5,120 x 2 B [D])"),
        ("Speed", "16 fps at 480p with <1 s latency on one GPU node (company claim; release script uses 8 GPUs with Ulysses "
                  "sequence parallelism, GPU type not stated); WorldKV on 4×B200: 8.87 → 3.61 FPS over a one-minute rollout with "
                  "full KV, WorldKV Table 1 at the last chunk of a rollout: 3.83 FPS vs 8.10 with a sliding window (4×H200: 2.36 vs 5.05)"),
        ("Key detail", "Attention, not the GEMMs, sets the decay: after one minute each pass attends to ≈374k cached keys, "
                       "≈1.4 PFLOP of attention against ≈151 TFLOP of linear work per pass (≈112 Wan backbone + ≈39 camera "
                       "adapters), ≈9.5x [D]"),
    ],
    "evidence": "read",
    "sources": ["arXiv 2601.20540 Sec. 3.1.3, 3.3 (action injection), 3.4 (causal adaptation, DMD + adversarial), 4.1, 6.2",
                "lingbot-world code: wan/configs/wan_i2v_A14B.py (40 layers, dim 5120, 40 heads, ffn 13824, 70 steps); "
                "wan/image2video_fast.py (timesteps_index, local_attn_size -1, sink_size 0, chunk_size 3); run_fast.sh (8 GPUs, ulysses 8); wan/modules/model_fast.py (camera scale and shift)",
                "HF robbyant/lingbot-world-fast model card (16 fps, <1 s latency, Apache-2.0), config.json and safetensors index (18.54B, F32)",
                "WorldKV arXiv 2605.22718 Sec. 1, 4.3 (3.4 GB per chunk, >200 GB per minute), Table 1, Fig. 2"],
    "figure_variant": "Released dense LingBot-World-Fast: 40x5120, 4 steps",
    "flow": {
        "below": [{"text": "Image + camera poses + text"}],
        "stack": [
            {"box": "Wan VAE encoder", "id": "vae", "style": "teal", "basis": "code"},
            {"group": [
                {"box": "Noisy latent chunk", "id": "noisy", "style": "soft", "minor": True, "basis": "stated"},
                {"box": "Patchify 1×2×2", "id": "patch", "minor": True, "basis": "code"},
                {"group": [
                    {"residual": [{"box": "AdaLN (scale, shift)", "minor": True, "side": "Timestep emb.",
                                   "basis": "code", "side_basis": "code"},
                                  {"box": "Block-causal attention", "id": "attn", "style": "dark", "side": "3D RoPE",
                                   "basis": "stated", "side_basis": "code"},
                                  {"box": "Scale by gate", "minor": True, "basis": "code"}]},
                    {"box": "Camera scale & shift", "id": "act", "style": "orange", "side": "Camera Plücker",
                     "basis": "code", "side_basis": "code"},
                    {"residual": [{"box": "LayerNorm", "minor": True, "basis": "code"},
                                  {"box": "Cross-attention", "id": "xattn", "side": "umT5 text",
                                   "basis": "stated", "side_basis": "code"}]},
                    {"residual": [{"box": "AdaLN (scale, shift)", "minor": True, "basis": "code"},
                                  {"box": "Feed forward", "id": "ffn", "basis": "stated"},
                                  {"box": "Scale by gate", "minor": True, "basis": "code"}]},
                ], "repeat": "40 ×", "id": "block"},
                {"box": "Predicted velocity", "id": "vel", "minor": True, "basis": "code"},
                {"box": "Update latents", "id": "upd", "minor": True, "basis": "code"},
            ], "loop": "4 steps (DMD + GAN)", "tint": "grey", "id": "denoise"},
            {"box": "Write chunk to KV cache", "id": "kv", "minor": True, "basis": "code"},
        ],
        "above": [{"box": "Wan VAE decoder", "id": "dec", "style": "teal", "basis": "code"}, {"text": "12 frames at 480×832"}],
        "insets": [{"for": "ffn", "stack": [{"box": "Linear", "basis": "code"}, {"box": "GELU", "basis": "code"},
                                         {"box": "Linear", "basis": "code"}]}],
        "annotations": [
            {"at": "patch", "text": "≈*4,680* tokens per *12*-frame chunk", "side": "left"},
            {"at": "attn", "text": "*40* heads, full KV of the whole rollout", "side": "left", "key": True},
            {"at": "block", "text": "*40* layers, width *5,120*, ≈*18.5B*", "side": "right", "key": True},
            {"at": "upd", "text": "*4* steps instead of *70*", "side": "right"},
            {"at": "kv", "text": "*3.4 GB* KV per chunk, >*200 GB* per minute", "side": "right"},
            {"at": "dec", "text": "*16* fps at *480p*, <*1* s latency", "side": "right", "key": True},
        ],
        "feedback": "cached chunk K/V",
        "feedback_from": "kv",
        "feedback_to": "attn",
    },
}
