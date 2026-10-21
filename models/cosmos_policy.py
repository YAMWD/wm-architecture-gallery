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
    "summary": "Cosmos-Predict2-2B Video2World, a latent video diffusion transformer over Wan2.1 VAE latents, fully "
               "fine-tuned into a robot policy with no architectural change. Proprioception, the action chunk and the value "
               "are injected as extra latent frames: blank images are VAE-encoded and their latents overwritten with tiled "
               "copies of the vectors, so the denoising process that predicts future images also predicts actions. As a "
               "direct policy it denoises everything in parallel in 5 steps (0.61 s per chunk on one H100) and discards the "
               "future state and value; planning mode decodes them autoregressively for best-of-N search.",
    "facts": [
        ("Representation", "Wan2.1 VAE latent frames (8x spatial, 4x temporal, 16 channels); one latent frame per modality and "
                           "camera view, e.g. 9 for LIBERO (blank, proprio, 2 views, action chunk, future proprio, 2 future "
                           "views, value) or 11 with 3 cameras; each image is repeated 4x so one latent frame is one timestep; "
                           "LIBERO data at 224 px per the repo config, i.e. ~196 tokens per latent frame with the 2x2 patch [D]"),
        ("Core", "Cosmos-Predict2-2B Video2World DiT, all weights fine-tuned: 28 blocks, d 2048, 16 heads, patch 2x2x1, 3D RoPE, "
                 "AdaLN-LoRA timestep conditioning (repo net config COSMOS_V1_2B); T5 text via cross-attention; no new modules"),
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
        ("Memory", "None: the input is the current observation only, no history; 6.0-8.9 GB VRAM at inference (README)"),
        ("Speed", "Per action chunk on one H100 (authors): 0.61 s at 5 steps, 0.95 s at 10, 0.16 s at 1 step (RoboCasa still "
                  "66.4% success at 1 step); best-of-8 planning 4.9 s on 8 parallel H100s"),
        ("Key detail", "Every step also denoises the future-image and value frames the policy throws away; latency is roughly "
                       "68 ms per step plus 0.27 s fixed [D: from 0.61 s at 5 and 0.95 s at 10 steps]"),
    ],
    "evidence": "read",
    "sources": ["arXiv 2601.16163 Sec. 3 (base model, VAE), 4.1 (latent frame injection), 4.2 (parallel vs AR decoding), "
                "App. A.1 (injection details), A.2 (action chunks, training), A.3.1 and A.4.2 (steps, latency)",
                "GitHub NVlabs/cosmos-policy README (VRAM), net.py (COSMOS_V1_2B: 2048 channels, 28 blocks, 16 heads, patch 2, "
                "rope3d, adaln_lora 256) and cosmos_policy_experiment_configs.py (resolution 224, state_t 9; fetched)"],
    "diagram": {
        "encoder": {"text": "Images + blank placeholders → Wan2.1 VAE",
                    "sub": "9 latent frames (LIBERO); proprio, action chunk and value overwrite the blanks", "tag": "frozen",
                    "short": "Wan2.1 VAE; blanks → action, state, value"},
        "tokens": {"groups": [("latent", 8, "image + proprio frames"), ("action", 1, "action chunk"), ("reward", 1, "value")],
                   "note": "one latent frame per modality and view"},
        "core": {"title": "Cosmos-Predict2 DiT ×28 · d 2048 · 16 heads",
                 "rows": [("attn", "Bidirectional 3D self-attention over all latent frames, 3D RoPE"),
                          ("xattn", "Cross-attention to T5 text"),
                          ("action", "Actions, proprio and value as latent frames (no new modules)"),
                          ("mlp", "MLP")],
                 "notes": ["AdaLN-LoRA timestep conditioning"]},
        "sampling": {"kind": "diffusion", "text": "EDM denoising, 5 steps (10 on ALOHA; 1 works)",
                     "sub": "all frames in parallel; future state and value discarded", "short": "EDM, 5 steps per chunk"},
        "heads": ["action chunk", "future state", "value"],
        "decoder": {"text": "Wan2.1 VAE decoder → future images", "sub": "visualisation only; actions are read from latents",
                    "tag": "frozen", "short": "Wan VAE decoder (not needed for actions)"},
    },
}
