MODEL = {
    "slug": "cosmos_predict25",
    "name": "Cosmos-Predict2.5",
    "year": 2025, "month": 11,
    "org": "NVIDIA",
    "family": "driving",
    "role": "Diffusion transformer",
    "status": "company technical report (arXiv 2511.00062, v2 Feb 2026)",
    "params": "2B and 14B",
    "params_num": 2e9,
    "open": "code + weights",
    "links": {"arXiv": "https://arxiv.org/abs/2511.00062", "code": "https://github.com/nvidia-cosmos/cosmos-predict2.5"},
    "tagline": "Bidirectional DiT that generates whole video clips",
    "summary": "NVIDIA's physical-AI world foundation model: a flow-matching DiT that generates a whole 93-frame clip (24 latent "
               "frames, 5.8 s at 16 fps) with full self-attention, unifying Text2World, Image2World and Video2World by "
               "replacing conditioning frames in the sequence and flagging them with a mask token. The Cosmos-Reason1 VLM "
               "replaces T5 as the text encoder. It is a clip generator, not an interactive model: no action input in the "
               "base model (an action-conditioned robot variant exists), no KV cache. The figure draws the released 2B base "
               "Video2World sampler: 35 FlowUniPC steps with CFG 7, two DiT passes per step (70 per clip); the 2B model "
               "card reports 228.8 s per 720p Video2World clip on H100 SXM. Not drawn: a 4-step distilled checkpoint (rCM "
               "in the paper; the released one is Text2World only and configured as DMD2).",
    "facts": [
        ("Representation", "Wan2.1 causal VAE (4x8x8) + 1x2x2 patchify; at 1280x704 each latent frame is 88x160, patchified to a 44x80 "
                           "grid of 3,520 tokens; 84,480 tokens per 93-frame clip of 24 latent frames [D]"),
        ("Core", "2B: 28 layers in the released config and checkpoint (matches the model card's 2,059,174,912 parameters; paper "
                 "Table 3 lists 32), d 2048, FFN 8192, 16 heads of 128; 14B: 36 layers, d 5120, FFN 20480, 40 heads; AdaLN-LoRA "
                 "(rank 256) timestep modulation, 3D RoPE, GELU; blocks of self-attention, cross-attention and MLP"),
        ("Attention", "Full (bidirectional) self-attention over all tokens of the clip; training at 720p/93 frames uses context "
                      "parallelism 2 (2B) or 8 (14B) (Table 9)"),
        ("Actions", "None in the base model: conditioning is text (Cosmos-Reason1 multi-block activations projected to 1024-d, via "
                    "cross-attention) and 1 or 5 conditioning frames concatenated with a mask-token flag; the 2B robot/action-cond "
                    "variant adds an action-embedder MLP to the timestep embeddings (Sec. 6.6), and the 7-camera driving variant "
                    "concatenates views along the latent time axis (Sec. 6.3.1)"),
        ("Prediction", "Flow matching; the paper distills with rCM (continuous-time consistency + distribution matching) to 4 steps, "
                       "2B overall score 0.768 → 0.764 (Table 7); the released 4-step 2B checkpoint (Text2World only) is configured "
                       "as DMD2 in TrigFlow form; the released base sampler defaults to 35 FlowUniPC steps with CFG 7 (two passes "
                       "per step)"),
        ("Decoder", "Wan2.1 VAE decoder → 93 frames at up to 1280x704"),
        ("Memory", "None: clip-level generation; longer videos via the released autoregressive sliding-window mode, each new "
                   "chunk conditioned on the last chunk_overlap generated frames (default 1); no KV cache"),
        ("Speed", "2B model card: 228.8 s per 720p Video2World generation on H100 SXM (123.9 s on B200), 32.54 GB VRAM; 14B timing "
                  "not yet published; training MFU 36.49% (2B) and 33.08% (14B) on 4,096 H100s at 720p/93 frames (Table 9); "
                  "≈2.8e14 dense FLOPs per 2B pass over 84,480 tokens before attention, which adds ≈1.6e15 [D]"),
        ("Key detail", "A bidirectional whole-clip DiT with ≈84k-token attention per pass [D]; the shipped acceleration levers are "
                       "the 4-step distilled 2B checkpoint (Text2World only, CFG distilled into the student) and multi-GPU "
                       "context parallelism at inference"),
    ],
    "evidence": "read",
    "sources": ["arXiv 2511.00062 Sec. 3.1-3.2 (Table 3, Fig. 2), 4.1 (conditioning frames, mask token), 4.2.3 (rCM, Table 7), "
                "4.3 and Table 9 (MFU, context parallelism), 6.3.1 (multiview), 6.6 (action conditioning)",
                "github.com/nvidia-cosmos/cosmos-predict2.5 @a2c298b: configs/video2world/defaults/net.py, networks/minimal_v4_dit.py, "
                "cosmos_predict2/config.py, distill/configs/experiment/experiments_dmd2_predict2p5.py, docs/inference.md, docs/distillation.md",
                "Hugging Face model cards nvidia/Cosmos-Predict2.5-2B and -14B (parameters, VRAM, inference time)"],
    "figure_variant": "Released 2B base Video2World: 28 blocks, 35 FlowUniPC steps, CFG 7 (2 passes/step)",
    "flow": {
        "below": [{"text": "Text + 1 or 5 frames, no action"}],
        "stack": [
            {"box": "Wan2.1 VAE encoder", "id": "vae", "style": "teal", "basis": "stated"},
            {"group": [
                {"box": "Noisy clip latents", "id": "noisy", "style": "soft", "minor": True, "basis": "stated"},
                {"box": "Patchify + mask token", "id": "patch", "minor": True, "basis": "stated"},
                {"group": [
                    {"residual": [{"box": "AdaLN-LoRA", "minor": True, "side": "Timestep emb.", "basis": "stated",
                                   "side_basis": "stated"},
                                  {"box": "Full self-attention", "id": "attn", "style": "dark", "side": "3D RoPE",
                                   "basis": "code", "side_basis": "code"},
                                  {"box": "Scale by gate", "minor": True, "basis": "code"}]},
                    {"residual": [{"box": "AdaLN-LoRA", "minor": True, "basis": "stated"},
                                  {"box": "Cross-attention", "id": "xattn", "side": "VLM text features", "basis": "stated",
                                   "side_basis": "stated"},
                                  {"box": "Scale by gate", "minor": True, "basis": "code"}]},
                    {"residual": [{"box": "AdaLN-LoRA", "minor": True, "basis": "stated"},
                                  {"box": "Feed forward", "id": "ffn", "basis": "stated"},
                                  {"box": "Scale by gate", "minor": True, "basis": "code"}]},
                ], "repeat": "28 ×", "id": "block", "basis": "code"},
                {"box": "Predicted velocity", "id": "vel", "minor": True, "basis": "stated"},
                {"box": "Update latents", "id": "upd", "minor": True, "basis": "code"},
            ], "loop": "35 steps × 2 (CFG 7)", "loop_short": "35 steps", "tint": "grey", "id": "denoise", "basis": "code"},
        ],
        "above": [{"box": "Wan2.1 VAE decoder", "id": "dec", "style": "teal", "basis": "stated"},
                  {"text": "93 frames at 1280×704 (5.8 s)"}],
        "insets": [{"for": "ffn", "stack": [{"box": "Linear", "basis": "code"}, {"box": "GELU", "basis": "stated"},
                                            {"box": "Linear", "basis": "code"}]}],
        "annotations": [
            {"at": "vae", "text": "≈*3,520* tokens per latent frame", "side": "left", "key": True},
            {"at": "patch", "text": "*1* or *5* conditioning frames", "side": "left"},
            {"at": "noisy", "text": "*24* latent frames per clip", "side": "left"},
            {"at": "attn", "text": "*16* heads over ≈*84,480* tokens", "side": "left", "key": True},
            {"at": "block", "text": "*28* layers, width *2,048*", "side": "right", "key": True},
            {"at": "dec", "text": "2B: *228.8* s per *720p* clip, H100 SXM", "side": "right", "key": True},
        ],
    },
}
