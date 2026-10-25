MODEL = {
    "slug": "dreamzero",
    "name": "DreamZero",
    "year": 2026, "month": 2,
    "org": "NVIDIA",
    "family": "wam",
    "role": "Diffusion transformer",
    "status": "arXiv preprint (company)",
    "params": "14B (Wan2.1-I2V-14B)",
    "params_num": 14e9,
    "open": "code + weights (non-Flash)",
    "links": {"arXiv": "https://arxiv.org/abs/2602.15922", "code": "https://github.com/dreamzero0/dreamzero",
              "page": "https://dreamzero0.github.io"},
    "tagline": "One 14B DiT denoises video and actions together",
    "summary": "A 14B world-action model: the Wan2.1-I2V-14B image-to-video DiT is fully fine-tuned into a chunk-wise "
               "autoregressive flow-matching model that denoises the next 2 latent frames of video and the matching 1.6 s "
               "action chunk together, with one shared timestep and separate output decoders. Clean context sits in a KV "
               "cache (with the chunk being denoised, at most 4 chunks plus the first frame: 33 raw frames, 6.6 s), and "
               "after each chunk executes the predicted frames are replaced by encoded real observations. Naive inference "
               "costs 5.7 s per chunk; CFG on 2 GPUs, velocity caching (16 → 4 DiT steps), compilation, kernel and "
               "scheduler tuning, NVFP4 and the 1-step DreamZero-Flash schedule bring it to 150 ms on 2 GB200. The figure draws "
               "Flash, a paper-only variant: the released DROID and AgiBot checkpoints are not Flash-trained and sample 16 "
               "steps.",
    "facts": [
        ("Representation", "Frozen Wan2.1 VAE latents (480p model; 8x spatial, 4x temporal); 3 camera views resized to "
                           "176×320 and tiled 2×2 into one frame (code); 880 tokens per latent frame (DreamZero checkpoint "
                           "config frame_seqlen); a full context of 33 raw frames encodes to 9 latent frames, the first "
                           "frame plus 4 chunks of 2 [D: 33 = 1 + 4×8]"),
        ("Core", "Wan2.1-I2V-14B-480P DiT with all blocks fine-tuned: 40 layers, d 5120, 40 heads, FFN 13,824 (base "
                 "config.json); only state and action encoders plus an action decoder are added; text encoder, image "
                 "encoder and VAE stay frozen; block internals not detailed in the paper (LayerNorm and RoPE named in "
                 "its quantization notes)"),
        ("Attention", "Chunk-causal: the noisy current chunk (K = 2 latent frames + its action chunk) attends to the clean "
                      "previous chunks; frames inside a chunk share one timestep; max context 8 latent frames (4 chunks) = 6.6 s"),
        ("Actions", "Action latents denoised jointly with the video in the same DiT, same timestep; chunks of 48 actions at "
                    "30 Hz (AgiBot) or 24 at 15 Hz (DROID) = 1.6 s; relative joint positions, Savitzky-Golay smoothed; the "
                    "action encoder embeds the noisy actions with the timestep, the state encoder (2-layer MLP) adds one "
                    "state token per chunk to the DiT sequence, and the action decoder (2-layer MLP) maps the action "
                    "tokens to the action velocity at every step (code)"),
        ("Prediction", "Flow matching: 16 steps baseline → 4 effective with velocity caching (cached velocity reused when "
                       "cosine similarity exceeds a threshold) → 1 step with DreamZero-Flash (video timesteps biased to high "
                       "noise, t = 1 − Beta(7,1); action timesteps uniform; applied as a final training stage). Released "
                       "checkpoints: not Flash (decouple_video_action_noise and decouple_inference_noise false in "
                       "experiment_cfg/conf.yaml), num_inference_steps = 16 with the velocity cache in the action head (code)"),
        ("Decoder", "Wan2.1 VAE decoder turns predicted latents into future frames (Fig. 4 inference panel); not needed for "
                    "control: actions come straight from the denoised action chunk, predicted video latents are discarded, "
                    "and the released server decodes them only to save videos"),
        ("Memory", "Closed loop through the robot (Fig. 4, Update with Real Observation): KV cache refreshed with VAE-encoded real observations after every chunk (clean t = 0 pass; predicted "
                   "frames discarded); it holds the first frame plus up to 3 earlier chunks (≤ 7 latent frames [D]), so with "
                   "the chunk being denoised the window is 9 latent frames = 33 raw frames (code: local_attn_size = 4×2 + 1); "
                   "cache reset every 4 chunks (code)"),
        ("Speed", "5.7 s per chunk naive on one GPU; with CFG split across 2 GPUs: 9.6x on H100 (~0.59 s [D]), 16.6x with "
                  "NVFP4 (~350 ms at 4 steps) and 38x with Flash (150 ms at 1 step, ~7 Hz) on GB200 (company claims, "
                  "Tables 1 and 3)"),
        ("Key detail", "Generating only actions gives a minimal speed-up at 14B (diffusion steps and DiT blocks dominate "
                       "latency); the 38x comes from fewer DiT passes (16 → 4 by caching, → 1 with Flash), 2-GPU CFG, "
                       "torch.compile + CUDA graphs, cuDNN attention + GPU-side scheduler, and NVFP4 (E2M1 weights and "
                       "activations, FP8 QKV and softmax)"),
    ],
    "evidence": "read",
    "sources": ["arXiv 2602.15922 Sec. 3 (architecture, inference), Sec. 3.2 (optimizations), Table 1 (speedups), Table 3 "
                "(Flash), Sec. 4 (training), App. C (chunking, context), App. D (CFG parallelism, caching, NVFP4)",
                "Hugging Face Wan-AI/Wan2.1-I2V-14B-480P config.json (40 layers, d 5120, 40 heads, FFN 13824)",
                "github.com/dreamzero0/dreamzero: modules/wan_video_dit_action_casual_chunk.py, "
                "action_head/wan_flow_matching_action_tf.py, socket_test_optimized_AR.py",
                "Hugging Face GEAR-Dreams/DreamZero-DROID and DreamZero-AgiBot config.json, experiment_cfg/conf.yaml"],
    "figure_variant": "DreamZero-Flash (paper only, no released weights): Wan2.1-I2V-14B, one denoising step",
    "flow": {
        "below": [{"text": "Real views per chunk + text, state"}],
        "stack": [
            {"box": "Wan2.1 VAE encoder", "id": "vae", "style": "teal", "basis": "code"},
            {"box": "Real frames → KV cache", "id": "kv", "minor": True, "basis": "stated"},
            {"group": [
                {"box": "Noisy video + actions", "id": "noisy", "style": "soft", "minor": True, "side": "State/action enc.",
                 "basis": "stated", "side_basis": "code"},
                {"group": [
                    {"residual": [{"box": "AdaLN (scale, shift)", "minor": True, "side": "Timestep emb.",
                                   "basis": "code", "side_basis": "code"},
                                  {"box": "Chunk-causal attention", "id": "attn", "style": "dark", "side": "RoPE",
                                   "basis": "stated", "side_basis": "code"},
                                  {"box": "Scale by gate", "minor": True, "basis": "code"}]},
                    {"residual": [{"box": "LayerNorm", "minor": True, "basis": "code"},
                                  {"box": "Cross-attention", "id": "xattn", "side": "Text + image",
                                   "basis": "code", "side_basis": "code"}]},
                    {"residual": [{"box": "AdaLN (scale, shift)", "minor": True, "basis": "code"},
                                  {"box": "Feed forward", "id": "ffn", "basis": "code"},
                                  {"box": "Scale by gate", "minor": True, "basis": "code"}]},
                ], "repeat": "40 ×", "id": "block", "basis": "code"},
                {"fanout": [[{"box": "Video head", "id": "vhead", "basis": "code"}],
                            [{"box": "Action decoder", "id": "adec", "style": "orange", "basis": "code"}]], "minor": True},
                {"box": "Video + action velocity", "id": "vel", "minor": True, "basis": "stated"},
                {"box": "Update latents", "id": "upd", "minor": True, "basis": "stated"},
            ], "loop": "1 step (Flash)", "tint": "grey", "id": "denoise", "basis": "stated"},
            {"fanout": [[{"box": "Next-chunk video latents", "short": "Video latents", "id": "vid", "basis": "stated"}],
                        [{"box": "Action chunk", "id": "act", "style": "orange", "terminal": True, "basis": "stated"}]]},
        ],
        "above": [{"box": "Wan2.1 VAE decoder", "id": "dec", "style": "teal", "basis": "code"},
                  {"text": "Predicted frames (optional)"}],
        "annotations": [
            {"at": "vae", "text": "*880* tokens per latent frame (*3* views)", "side": "left", "key": True},
            {"at": "attn", "text": "*40* heads · width *5,120*", "side": "left"},
            {"at": "block", "text": "*40* layers · *14B* parameters", "side": "left", "key": True},
            {"at": "denoise", "text": "*1* Flash step (base *16*, cached *4*)", "side": "right", "key": True},
            {"at": "kv", "text": "Context ≤ *33* raw frames (*6.6* s)", "side": "right"},
            {"at": "act", "text": "*48* actions in *150* ms (*2* GB200, NVFP4)", "side": "right", "key": True},
        ],
    },
}
