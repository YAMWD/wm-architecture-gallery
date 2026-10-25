MODEL = {
    "slug": "lingbot_va",
    "name": "LingBot-VA",
    "year": 2026, "month": 1,
    "org": "Robbyant",
    "family": "wam",
    "role": "Diffusion transformer",
    "status": "RSS 2026; arXiv 2601.21998",
    "params": "≈5.1B shared (released)",
    "params_num": 5.089e9,
    "open": "code + weights (shared backbone only)",
    "links": {"arXiv": "https://arxiv.org/abs/2601.21998", "code": "https://github.com/robbyant/lingbot-va",
              "weights": "https://huggingface.co/robbyant/lingbot-va-base", "page": "https://technology.robbyant.com/lingbot-va"},
    "tagline": "Released video and action paths share one Wan DiT",
    "summary": "An autoregressive video-action model with a causal KV cache. The paper describes separate video and narrow "
               "action transformer streams joined by attention. The released implementation instead embeds both modalities "
               "into one 3072-wide, 30-block Wan transformer and selects video or action input/output projections with "
               "action_mode; only this shared-backbone version is released (README: separated version still to come). The figure "
               "follows it with va_demo_cfg.py: 5 video Euler updates, then 10 action updates, each stage ending with a "
               "t=0 pass that caches the predicted chunk. After execution, the server VAE-encodes the real frames, embeds "
               "the executed actions and overwrites those predictions with 2 cache-write passes. The paper's 3-step "
               "partial-video schedule is a different configuration.",
    "facts": [
        ("Representation", "Released demo: two 256x256 camera views encoded separately with the Wan2.2 VAE and concatenated "
                           "in latent width; 4x16x16 VAE and 1x2x2 patching give 128 tokens per latent frame, 512 for the "
                           "4-latent-frame chunk [D]. The paper reports 192 tokens in its experimental setup"),
        ("Core", "Released WanTransformer3DModel: one shared ModuleList of 30 blocks, width 3072, 24 heads of 128, FFN "
                 "14336. Both action_mode branches execute this same block list. Each block has gated adaptive LayerNorm "
                 "self-attention, text cross-attention with LayerNorm, then gated adaptive LayerNorm GELU FFN. "
                 "Separate modality timestep embedders and input/output projections are retained. The released checkpoint "
                 "has 5,089,465,566 transformer parameters [D from safetensors tensor shapes]. The paper instead describes "
                 "a 3072-wide video tower and 768-wide action tower; these are not drawn as released-code architecture"),
        ("Attention", "Chunk-causal attention with RoPE and a shared history cache. Training concatenates noisy and clean "
                      "video/action sequences and applies a structured mask. Inference processes video and actions in "
                      "separate calls to the shared transformer, reading cached history; T5 reaches both modes through "
                      "the same cross-attention layers"),
        ("Actions", "Released demo: action_dim 30, 4 latent frames per chunk and action_per_frame 8 give 32 action vectors "
                    "[D]. Linear action_embedder maps 30 to 3072, action_proj_out maps back. Quantile denormalization and "
                    "selection of used action channels follow generation. Other robot configurations have different horizons"),
        ("Prediction", "Released demo: 5 video Euler updates plus a t=0 pass that caches the predicted video chunk, then 10 "
                       "action Euler updates plus a t=0 pass that caches the predicted actions (is_pred entries). Chunk 0 "
                       "pins its first latent frame to the VAE encoding of the initial observation. Video guidance 5, action guidance 1. The paper reports 3 video steps to "
                       "s=0.6 and 10 action steps to s=1; this is not the demo configuration shown"),
        ("Decoder", "VAE decoding is optional visualization; control reads the action projection directly. Executed "
                    "actions return through the action embedding into the cache write, not into the image encoder"),
        ("Memory", "Per-layer causal KV cache with FIFO eviction; attn_window 30 gives (30//2) x (512 + 32) = 8,160 "
                   "token slots [D]. Every chunk, _compute_kv_cache drops the predicted (is_pred) entries, VAE-encodes "
                   "the real frames, normalizes the executed state/actions and writes both with 2 transformer passes "
                   "(video, then action; update_cache=2). Paper Alg. 1 likewise appends E(o) and executed actions to the cache"),
        ("Speed", "No inference latency is disclosed for the released demo configuration"),
        ("Key detail", "Per chunk, released demo: 6 video + 11 action passes of the 30-block DiT plus 2 cache-write passes, "
                       "all at batch 2 because video guidance 5 enables CFG [D]. Paper/code difference: separate towers in "
                       "the paper versus shared block weights in the released forward_train and forward(action_mode=...) "
                       "paths. Paper: 5.3B total (5B video stream + about 350M for the 768-wide action stream), video at "
                       "12.5 Hz and actions at 50 Hz, noisy-history augmentation to allow partial video denoising"),
    ],
    "evidence": "read",
    "sources": ["arXiv 2601.21998 Sec. 3.3 (paper MoT architecture), Sec. 4.2 (paper sampling and dimensions)",
                "robbyant/lingbot-va commit 7c6ffa9: wan_va/modules/model.py, modules/utils.py, wan_va_server.py, "
                "configs/va_demo_cfg.py, configs/shared_config.py",
                "HF robbyant/lingbot-va-base commit 68b7bc1: transformer/config.json and three safetensors headers"],
    "figure_variant": "Released va_demo_cfg.py: shared 30x3072 DiT, 5 video + 10 action updates",
    "flow": {
        "below": [{"text": "Real 256×256 views ×2 + task text"}],
        "stack": [
            {"box": "Wan2.2 VAE encoder", "id": "vae", "style": "teal", "basis": "code"},
            {"box": "Real-obs K/V write", "id": "write", "basis": "code"},
            {"group": [
                {"box": "Noisy video latents", "style": "soft", "minor": True, "basis": "code"},
                {"box": "Patchify + projection", "id": "patch", "minor": True, "basis": "code"},
                {"box": "Shared Wan DiT", "id": "vdit", "style": "dark", "basis": "code"},
                {"box": "Video velocity head", "minor": True, "basis": "code"},
                {"box": "Euler update", "minor": True, "basis": "code"},
            ], "loop": "5 video steps", "tint": "grey", "basis": "code"},
            {"box": "t=0 pass, cache video", "id": "kv", "minor": True, "basis": "code"},
            {"group": [
                {"box": "Action linear embedding", "minor": True, "side": "Noisy actions", "basis": "code", "side_basis": "code"},
                {"box": "Same shared Wan DiT", "id": "block", "style": "dark", "basis": "code"},
                {"box": "Action velocity head", "minor": True, "basis": "code"},
                {"box": "Euler update", "minor": True, "basis": "code"},
            ], "loop": "10 action steps", "tint": "orange", "basis": "code"},
            {"box": "t=0 pass, cache actions", "minor": True, "basis": "code"},
            {"box": "Denormalize actions", "id": "act", "style": "orange", "basis": "code"},
        ],
        "above": [{"text": "32 actions (demo configuration)"}],
        "insets": [{"for": "block", "label": "shared block ×30", "stack": [
            {"residual": [{"box": "AdaLN", "minor": True, "side": "Modality timestep", "basis": "code", "side_basis": "code"},
                          {"box": "Chunk-causal attention", "side": "RoPE + cached K/V", "style": "dark", "basis": "code", "side_basis": "code"},
                          {"box": "Scale by gate", "minor": True, "basis": "code"}]},
            {"residual": [{"box": "LayerNorm + cross-attn", "side": "T5 text", "basis": "code", "side_basis": "code"}]},
            {"residual": [{"box": "AdaLN-gated GELU FFN", "basis": "code"}]}]}],
        "annotations": [
            {"at": "vae", "text": "*2* views · ≈*512* tokens per *4*-frame chunk", "side": "left", "key": True},
            {"at": "write", "text": "*2* passes · cache ≈*8,160* tokens", "side": "left"},
            {"at": "vdit", "text": "*30* layers · *24* heads · width *3,072*", "side": "left", "key": True},
            {"at": "kv", "text": "Predicted K/V, replaced by real K/V", "side": "left"},
            {"at": "block", "text": "Same weights · ≈*5.1B* parameters", "side": "left", "key": True},
            {"at": "act", "text": "*32* actions · latency not disclosed", "side": "left", "key": True},
        ],
        "feedback": "executed actions",
        "feedback_from": "act",
        "feedback_to": "write",
    },
}
