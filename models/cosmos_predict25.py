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
               "base model (an action-conditioned robot variant exists), no KV cache, rCM distillation to 4 steps, and no "
               "inference speed reported.",
    "facts": [
        ("Representation", "Wan2.1 causal VAE (4x8x8) + 1x2x2 patchify; 3,520 tokens per 44x80 latent frame at 1280x704, 84,480 tokens "
                           "per 93-frame clip of 24 latent frames [D]"),
        ("Core", "2B: 32 layers, d 2048, FFN 8192, 16 heads of 128; 14B: 36 layers, d 5120, FFN 20480, 40 heads; AdaLN-LoRA (rank 256) "
                 "timestep modulation, 3D RoPE, GELU; blocks of self-attention, cross-attention and MLP"),
        ("Attention", "Full (bidirectional) self-attention over all tokens of the clip; training at 720p/93 frames needs context "
                      "parallelism 2 (2B) or 8 (14B)"),
        ("Actions", "None in the base model: conditioning is text (Cosmos-Reason1 multi-block activations projected to 1024-d, via "
                    "cross-attention) and 1 or 5 conditioning frames concatenated with a mask-token flag; a 2B robot/action-cond variant "
                    "and 7-camera driving variants exist (mechanism not read)"),
        ("Prediction", "Flow matching; rCM (continuous-time consistency + distribution matching) distillation to 4 steps, 2B overall score "
                       "0.768 → 0.764 (Table 7); teacher step count not located"),
        ("Decoder", "Wan2.1 VAE decoder → 93 frames at up to 1280x704"),
        ("Memory", "None: clip-level generation; longer videos by chaining Video2World with 5 conditioning frames; no KV cache"),
        ("Speed", "Not disclosed; training MFU 36.49% (2B) and 33.08% (14B) on 4,096 H100s at 720p/93 frames (Table 9); ≈3.4e14 dense "
                  "FLOPs per 2B pass over 84,480 tokens, before attention [D]"),
        ("Key detail", "A bidirectional whole-clip DiT with ≈84k-token attention per pass is the template the causal game models in this "
                       "gallery were built to escape; the shipped acceleration lever is 4-step rCM distillation"),
    ],
    "evidence": "read",
    "sources": ["arXiv 2511.00062 Sec. 3.1-3.2 (Table 3 configs, tokenizer, text encoder, Fig. 2), 4.2.1 (frame replacement, mask token), "
                "4.2.3 (rCM, Table 7), 4.3 and Table 9 (MFU, context parallelism)",
                "NVIDIA research page (local src/pred25.txt) for the released-model list",
                "ar_token_and_physical_ai.md Group 2 (derived token counts, assuming 1280x704 for 720p as in Predict1)"],
    "diagram": {
        "encoder": {"text": "Frames → Wan2.1 VAE (4x8x8) + 1x2x2 patchify", "sub": "3,520 latents per 44x80 latent frame at 1280x704 [D]",
                    "tag": "frozen", "short": "Wan2.1 VAE → 3,520 latents"},
        "tokens": {"groups": [("latent", 24, "84,480 latents per clip")],
                   "note": "24 latent frames per 93-frame clip"},
        "core": {"title": "Cosmos DiT ×32 · d 2048 · 16 heads (2B)",
                 "rows": [("attn", "Full self-attention over the clip"),
                          ("xattn", "Cross-attn to Cosmos-Reason1 text"),
                          ("note", "no action input in the base model"),
                          ("mlp", "MLP (FFN 8192), AdaLN-LoRA")],
                 "notes": ["14B: ×36 · d 5120 · 40 heads · FFN 20480",
                           "conditioning frames replaced in the sequence, flagged by a mask token"]},
        "sampling": {"kind": "diffusion", "text": "Flow matching, rCM-distilled to 4 steps", "sub": "per 93-frame clip; teacher steps not located",
                     "short": "rCM, 4 steps per clip"},
        "decoder": {"text": "Wan2.1 VAE decoder → 93 frames at 1280x704", "tag": "frozen", "short": "Wan2.1 VAE decoder → 93 frames"},
    },
    "flow": {
        "below": [{"text": "Text + 1 or 5 frames, no action"}],
        "stack": [
            {"box": "Wan2.1 VAE encoder", "id": "vae", "style": "teal"},
            {"box": "Patchify + mask token", "id": "patch", "minor": True},
            {"group": [
                {"box": "Noisy clip latents", "id": "noisy", "style": "soft", "minor": True},
                {"group": [
                    {"residual": [{"box": "AdaLN-LoRA", "minor": True, "side": "Timestep emb."},
                                  {"box": "Full self-attention", "id": "attn", "style": "dark", "side": "3D RoPE"}]},
                    {"residual": [{"box": "AdaLN-LoRA", "minor": True},
                                  {"box": "Cross-attention", "id": "xattn", "side": "VLM text features"}]},
                    {"residual": [{"box": "AdaLN-LoRA", "minor": True}, {"box": "Feed forward", "id": "ffn"}]},
                ], "repeat": "32 ×", "id": "block"},
                {"box": "Predicted velocity", "id": "vel", "minor": True},
                {"box": "Update latents", "id": "upd", "minor": True},
            ], "loop": "4 rCM steps", "tint": "grey", "id": "denoise"},
        ],
        "above": [{"box": "Wan2.1 VAE decoder", "id": "dec", "style": "teal"}, {"text": "93 frames at 1280×704 (5.8 s)"}],
        "insets": [{"for": "ffn", "stack": [{"box": "Linear"}, {"box": "GELU"}, {"box": "Linear"}]}],
        "annotations": [
            {"at": "vae", "text": "*3,520* tokens per latent frame", "side": "left", "key": True},
            {"at": "patch", "text": "*1* or *5* conditioning frames", "side": "left"},
            {"at": "noisy", "text": "*24* latent frames per clip", "side": "left"},
            {"at": "attn", "text": "*16* heads over *84,480* tokens", "side": "left", "key": True},
            {"at": "block", "text": "*32* layers, width *2,048*", "side": "right", "key": True},
            {"at": "dec", "text": "Speed not disclosed", "side": "right", "key": True},
        ],
    },
}
