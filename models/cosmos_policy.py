MODEL = {
    "slug": "cosmos_policy",
    "name": "Cosmos Policy",
    "year": 2026, "month": 1,
    "org": "NVIDIA",
    "family": "wam",
    "role": "Diffusion transformer",
    "status": "ICLR 2026",
    "params": "2B (Cosmos-Predict2-2B)",
    "params_num": 2e9,
    "open": "code + weights",
    "links": {"arXiv": "https://arxiv.org/abs/2601.16163", "code": "https://github.com/NVlabs/cosmos-policy",
              "weights": "https://huggingface.co/collections/nvidia/cosmos-policy",
              "page": "https://research.nvidia.com/labs/dir/cosmos-policy/"},
    "tagline": "Video DiT predicts actions as extra latent frames",
    "summary": "Cosmos-Predict2-2B Video2World, a latent video diffusion transformer over Wan2.1 VAE latents, fully "
               "fine-tuned into a robot policy with no architectural change. Proprioception, the action chunk and the value "
               "are injected as extra latent frames: blank images are VAE-encoded and their latents overwritten with tiled "
               "copies of the vectors, so the denoising process that predicts future images also predicts actions. As a "
               "direct policy it denoises everything in parallel in 5 steps on LIBERO and RoboCasa (0.61 s per chunk on one "
               "H100; 10 steps and 0.95 s on ALOHA) and discards the future state and value; the figure draws this LIBERO direct policy. Not drawn: on ALOHA a "
               "separately fine-tuned planning model predicts future states and values for best-of-8 search (4.9 s on 8 "
               "H100s).",
    "facts": [
        ("Representation", "Wan2.1 VAE latent frames (8x spatial, 4x temporal, 16 channels); one latent frame per modality and "
                           "camera view, e.g. 9 for LIBERO (blank, proprio, 2 views, action chunk, future proprio, 2 future "
                           "views, value) or 11 with 3 cameras; each image is repeated 4x so one latent frame is one timestep; "
                           "LIBERO data at 224 px per the repo config, i.e. ~196 tokens per latent frame with the 2x2 patch [D]"),
        ("Core", "Cosmos-Predict2-2B Video2World DiT, all weights fine-tuned: 28 blocks, d 2048, 16 heads, patch 2x2x1, 3D RoPE, "
                 "AdaLN-LoRA timestep conditioning (repo net config COSMOS_V1_2B); T5 text via cross-attention; no new modules; "
                 "Predict1 block design with QK RMSNorm"),
        ("Attention", "Bidirectional 3D self-attention over all latent frames; clean conditioning frames (current state) and "
                      "noisy target frames share the sequence"),
        ("Actions", "The action chunk (K x d_act, scaled to [-1, 1], flattened and duplicated to fill H' x W' x C') overwrites "
                    "a placeholder latent frame and is read back by averaging the copies; K = 16 (LIBERO, all executed), "
                    "32 (RoboCasa, 16 executed), 50 at 25 Hz (ALOHA)"),
        ("Prediction", "EDM denoising with sigma_max 80 and sigma_min 4: 5 steps (LIBERO, RoboCasa) or 10 (ALOHA) with action, "
                       "future state and value in parallel, the latter two discarded; planning: autoregressive 10 + 5 + 5 steps, "
                       "ensembles of 3 states and 5 values, best-of-N = 8"),
        ("Decoder", "Wan2.1 VAE decoder only to visualise predicted future images; actions and values are read from the latents "
                    "without any decoding"),
        ("Memory", "None: the input is the current observation only, no history; 6.0-8.9 GB VRAM at inference without "
                   "planning (README)"),
        ("Speed", "Per action chunk on one H100 (authors): 0.61 s at 5 steps, 0.95 s at 10, 0.16 s at 1 step (RoboCasa still "
                  "66.4% success at 1 step); ALOHA planning setup (not drawn; separate refined planning model): best-of-8 "
                  "search with 10-step proposals and 5-step state/value ensembles takes 4.9 s on 8 parallel H100s"),
        ("Key detail", "Every step also denoises the future-state and value frames the policy throws away"),
    ],
    "evidence": "read",
    "sources": ["arXiv 2601.16163 Sec. 3 (base model, VAE), 4.1 (latent frame injection), 4.2 (parallel vs AR decoding), "
                "App. A.1 (injection details), A.2 (action chunks, training), A.3.1 and A.4.2 (steps, latency)",
                "GitHub NVlabs/cosmos-policy README (VRAM), net.py (COSMOS_V1_2B: 2048 channels, 28 blocks, 16 heads, patch 2, "
                "rope3d, adaln_lora 256), minimal_v4_dit.py (block order, AdaLN, no mask, patch embed per step) and "
                "cosmos_policy_experiment_configs.py (resolution 224, state_t 9)"],
    "figure_variant": "Released LIBERO policy: Predict2-2B, 28 blocks, 5 EDM steps",
    "flow": {
        "below": [{"text": "Images + blank frames + text"}],
        "stack": [
            {"box": "Wan2.1 VAE encoder", "id": "vae", "style": "teal", "basis": "stated"},
            {"box": "Latent frame injection", "id": "inject", "style": "orange", "side": "Proprio vector",
             "basis": "stated", "side_basis": "stated"},
            {"group": [
                {"box": "Noisy target frames", "id": "noisy", "style": "soft", "minor": True, "basis": "stated"},
                {"box": "Patchify 1×2×2", "id": "patch", "minor": True, "basis": "code"},
                {"group": [
                    {"residual": [{"box": "AdaLN (scale, shift)", "minor": True, "side": "Noise level σ",
                                   "basis": "code", "side_basis": "stated"},
                                  {"box": "Bidirectional attention", "id": "attn", "style": "dark", "side": "3D RoPE",
                                   "basis": "code", "side_basis": "code"},
                                  {"box": "Scale by gate", "minor": True, "basis": "code"}]},
                    {"residual": [{"box": "AdaLN (scale, shift)", "minor": True, "basis": "code"},
                                  {"box": "Cross-attention", "id": "xattn", "side": "T5-XXL text",
                                   "basis": "stated", "side_basis": "stated"},
                                  {"box": "Scale by gate", "minor": True, "basis": "code"}]},
                    {"residual": [{"box": "AdaLN (scale, shift)", "minor": True, "basis": "code"},
                                  {"box": "Feed forward", "id": "ffn", "basis": "code"},
                                  {"box": "Scale by gate", "minor": True, "basis": "code"}]},
                ], "repeat": "28 ×", "id": "block", "basis": "code"},
                {"box": "Update latent frames", "id": "upd", "minor": True, "basis": "stated"},
            ], "loop": "5 EDM steps", "tint": "grey", "id": "denoise", "basis": "code"},
            {"fanout": [[{"box": "Future-state latents", "short": "Future state", "id": "fut", "basis": "stated"}],
                        [{"box": "Value", "id": "val", "terminal": True, "minor": True, "basis": "stated"}],
                        [{"box": "Action chunk", "id": "act", "style": "orange", "terminal": True, "basis": "stated"}]]},
        ],
        "above": [{"box": "Wan2.1 VAE decoder", "id": "dec", "style": "teal", "minor": True, "basis": "code"},
                  {"text": "Future images (visualisation only)", "minor": True}],
        "insets": [{"for": "ffn", "stack": [{"box": "Linear", "basis": "code"}, {"box": "GELU", "basis": "code"},
                                            {"box": "Linear", "basis": "code"}]}],
        "annotations": [
            {"at": "vae", "text": "*9* frames of ≈*196* tokens", "side": "left", "key": True},
            {"at": "inject", "text": "*1* frame each: proprio, actions, value", "side": "left"},
            {"at": "attn", "text": "*16* heads · width *2,048*", "side": "left", "key": True},
            {"at": "block", "text": "*28* layers · *2B* parameters", "side": "right", "key": True},
            {"at": "fut", "text": "LIBERO: *16* actions per chunk", "side": "left"},
            {"at": "act", "text": "LIBERO: *0.61* s per chunk, *1* H100", "side": "right", "key": True},
        ],
    },
}
