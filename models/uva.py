MODEL = {
    "slug": "uva",
    "name": "UVA (Unified Video Action)",
    "year": 2025, "month": 2,
    "org": "Stanford",
    "family": "wam",
    "role": "Diffusion transformer",
    "status": "RSS 2025 (arXiv v3, 24 Apr 2025)",
    "params": "0.5B (MAR-B init)",
    "params_num": 0.5e9,
    "open": "code + weights",
    "links": {"code": "https://github.com/ShuangLI59/unified_video_action", "arXiv": "https://arxiv.org/abs/2503.00200", "page": "https://unified-video-action-model.github.io"},
    "tagline": "Video and action heads on one masked transformer",
    "summary": "A masked-autoencoder-style transformer, initialised from MAR-B, that fuses a history of kl-f16 VAE latents and "
               "action chunks into a joint video-action latent, which two lightweight diffusion heads decode into video "
               "patches and actions. Denoising runs only in the small heads, never in the backbone, and at deployment the "
               "video head is skipped entirely, so a 16-action trajectory costs 95 ms on an RTX 3080: 40 ms of VAE encoding, "
               "40 ms of transformer (30 with flash attention) and 15 ms for 16 steps of the action head.",
    "facts": [
        ("Representation", "Pretrained kl-f16 VAE latent map (w x h x c) per frame, flattened and projected by an FC layer into "
                           "N tokens of width d; official config: 256×256 frames, 16×16×16 latents, so N = 256 tokens per frame "
                           "and h = 4 frames (the paper gives neither); future frames enter as randomly "
                           "masked tokens concatenated channel-wise with the history tokens"),
        ("Core", "MAE-style transformer initialised from MAR-B and itself mar_base (official code: 12 encoder + 12 decoder "
                 "timm ViT blocks, pre-LN, d 768, 12 heads, MLP ratio 4); 0.5B parameters in total (paper, no breakdown); "
                 "language (Libero10, UMI multi-task) is a CLIP ViT-B/32 text token projected 512 → 768, repeated M times "
                 "(64 in code) and concatenated into the token sequence; the paper calls this cross-attention, but the code "
                 "has no cross-attention layer"),
        ("Attention", "Bidirectional (no attention mask in code) over the N x h video-action tokens + M language tokens; the "
                      "same positions are masked in every frame to avoid leakage; the paper says attention takes half of the "
                      "inference time; Table VI: transformer 40 of 95 ms, 30 with flash attention"),
        ("Actions", "Each frame pairs with a chunk of L actions sampled faster than frames; history chunks are repeated M "
                    "times, FC-projected to N action tokens and concatenated channel-wise with the visual tokens"),
        ("Prediction", "Video: MAR-style masked generation from an empty sequence in 1 to 8 autoregressive stages; actions: a "
                       "conv + MLP pool the N latents into one action latent that conditions the action diffusion head, "
                       "16 denoising steps on the robot (paper; 100 in simulation); the released config/model/uva.yaml sets "
                       "act_diff_testing_steps 100, and no released task config overrides it"),
        ("Decoder", "Video diffusion head + VAE decoder exist but are skipped at deployment (100 ms at 16 steps, 625 ms at 100)"),
        ("Memory", "History window of h frames and action chunks; no KV cache"),
        ("Speed", "Per 16-action trajectory on an RTX 3080 (authors, Table VI): VAE encoder 40 ms, transformer 40 ms (30 with "
                  "flash attention), action head 15 ms at 16 steps (93 at 100); total 95 ms (85 with flash attention), 173 ms "
                  "at 100 steps; policy + planner 195 ms; simulation timings on L40"),
        ("Key detail", "Trained with video, deployed without it: the skipped video head (100 ms) would cost more than the "
                       "whole 95 ms policy, and the VAE encoder plus backbone, not the action head, dominate (80 of 95 ms [D])"),
    ],
    "evidence": "read",
    "sources": ["arXiv 2503.00200 Sec. III-A/B/C (encoding, masked transformer, diffusion heads), V-D (0.5B, 16 vs 100 "
                "steps, attention share), App. X-A (autoregressive video stages), X-D and Table VI (timing)",
                "Official code: model/autoregressive/mar_con_unified.py (mar_base 12 + 12 blocks, CLIP text tokens "
                "concatenated), config/model/uva.yaml (256x256, vae_stride 16, 4 frames), timm 0.9.7 ViT Block",
                "GitHub README (MAR + VAE initialisation, checkpoints, 8 H100 x 4 days); LTH14/mar models/mar.py",
                "Project page (RSS 2025)"],
    "figure_variant": "MAR-B (released code): 12 encoder + 12 decoder blocks; 16 action steps as on the robot (paper)",
    "flow": {
        "below": [{"text": "History frames + actions + text"}],
        "stack": [
            {"box": "kl-f16 VAE encoder", "id": "vae", "style": "teal", "basis": "stated"},
            {"box": "FC projection to tokens", "id": "fc", "minor": True, "basis": "stated"},
            {"box": "Concat + masked future", "short": "Concat tokens", "id": "cat", "side": "Action chunks",
             "basis": "stated", "side_basis": "stated"},
            {"box": "Concat text tokens", "id": "txt", "side": "CLIP text ×M", "minor": True,
             "basis": "stated", "side_basis": "stated"},
            {"group": [
                {"residual": [{"box": "LayerNorm", "minor": True, "basis": "code"},
                              {"box": "Bidirectional attention", "id": "attn", "style": "dark", "basis": "code"}]},
                {"residual": [{"box": "LayerNorm", "minor": True, "basis": "code"},
                              {"box": "Feed forward", "id": "ffn", "basis": "code"}]},
            ], "repeat": "12 ×", "label": "encoder", "id": "encoder", "basis": "code", "condensed_box": "Attention + FFN"},
            {"box": "Final encoder LayerNorm", "minor": True, "basis": "code"},
            {"box": "Projection + positions", "minor": True, "basis": "code"},
            {"group": [
                {"residual": [{"box": "LayerNorm", "minor": True, "basis": "code"},
                              {"box": "Bidirectional attention", "style": "dark", "basis": "code"}]},
                {"residual": [{"box": "LayerNorm", "minor": True, "basis": "code"},
                              {"box": "Feed forward", "basis": "code"}]},
            ], "repeat": "12 ×", "label": "decoder", "id": "block", "basis": "code", "condensed_box": "Attention + FFN"},
            {"box": "Final decoder LayerNorm", "minor": True, "basis": "code"},
            {"box": "Video-action latents", "short": "Joint latents", "id": "z", "minor": True, "basis": "stated"},
            {"fanout": [[{"box": "Video diffusion head", "short": "Video head (skipped)", "id": "vhead", "terminal": True, "minor": True,
                          "basis": "stated"}],
                        [{"box": "Conv + MLP pool", "id": "pool", "minor": True, "basis": "stated"},
                         {"group": [{"box": "Action diffusion head", "id": "ahead", "style": "orange", "basis": "stated"}],
                          "loop": "16 steps (paper)", "tint": "grey", "basis": "stated"}]]},
        ],
        "above": [{"text": "16-action trajectory", "id": "out"}],
        "annotations": [
            {"at": "vae", "text": "*40* ms · *256* tokens per frame", "side": "left", "key": True},
            {"at": "attn", "text": "*12* heads · width *768* (MAR-B)", "side": "left"},
            {"at": "block", "text": "*40* ms (*30* flash) · *12* enc + *12* dec", "side": "right", "key": True},
            {"at": "vhead", "text": "Skipped at deployment (*100* ms)", "side": "left"},
            {"at": "ahead", "text": "*16* steps in *15* ms (paper, robot)", "side": "right", "key": True},
            {"at": "out", "text": "*95* ms per trajectory", "side": "right", "key": True},
        ],
    },
}
