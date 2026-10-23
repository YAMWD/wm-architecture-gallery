MODEL = {
    "slug": "genie",
    "name": "Genie",
    "year": 2024, "month": 2,
    "org": "Google DeepMind",
    "family": "token",
    "role": "Discrete-token model",
    "status": "ICML 2024",
    "params": "10.1B dynamics (10.7B total)",
    "params_num": 10.1e9,
    "open": "closed",
    "links": {"arXiv": "https://arxiv.org/abs/2402.15391"},
    "tagline": "MaskGIT over video tokens with latent actions",
    "summary": "A foundation world model trained on 30,000 h of unlabelled 2D-platformer video. An ST-ViViT video "
               "tokenizer (200M) turns 160x90 frames into discrete codes, a latent action model (300M) infers one of 8 "
               "latent actions between frames, and a 10.1B decoder-only MaskGIT dynamics transformer predicts the next "
               "frame's tokens from past frames and actions. Each ST block runs spatial attention over one frame, causal "
               "temporal attention over the 16-frame window, then an FFW; a frame costs 25 MaskGIT steps, and the "
               "authors report about 1 FPS.",
    "facts": [
        ("Representation", "Discrete codes from a 200M ST-ViViT VQ-VAE (patch 4, 1,024 codes x 32-d) on 160x90 frames at 10 FPS; the token grid is not stated, ~920 tokens per frame implied by the stated token counts [D]"),
        ("Core", "MaskGIT dynamics transformer: 48 layers, 36 heads, d 5120, k/q size 128; 10.1B (10.7B with tokenizer and LAM, rounded to '11B' in the abstract)"),
        ("Attention", "ST-transformer block: spatial self-attention over one frame's tokens, causal temporal attention over the same position across 16 frames, then FFW; QK-norm; the spatial term scales linearly with frames; norm type and positional encoding not disclosed. Block norms and residuals are not described, so they are not drawn; Table 12 gives num_layers 48 without saying whether it counts ST blocks"),
        ("Actions", "8 discrete latent actions from a 300M latent action model (patch 16, VQ codebook of 8) learned without action labels; actions enter as additive embeddings on the frame tokens"),
        ("Prediction", "MaskGIT: 25 steps per frame at temperature 2 with random sampling; frames generated autoregressively in token space, decoded by the tokenizer decoder"),
        ("Decoder", "ST-ViViT tokenizer decoder (20 layers, d 1024, 16 heads) → 160x90 frames"),
        ("Memory", "16-frame window, which the authors call a limitation; KV policy not disclosed"),
        ("Speed", "'Genie currently operates around 1FPS', hardware not stated (authors). Training: 125k steps at batch 512 on 256 TPUv5p, 6.6e22 FLOPs over 942B tokens"),
        ("Key detail", "25 sequential passes per frame, each over all ~920 tokens (MaskGIT convention) through 10.1B parameters: 2 x 10.1B x 920 x 25 = 0.46 PFLOP per frame [D]; compute-bound by our roofline reading, unlike GAIA-1's 576 one-token serial steps"),
    ],
    "evidence": "read",
    "sources": ["arXiv 2402.15391 Sec. 2.1-2.2 (ST-transformer, LAM, dynamics), Sec. 3 (training details, 25 MaskGIT steps), Sec. 5 (1 FPS), App. C Tables 5, 7, 10, App. D Table 12 (48 layers, 36 heads, d 5120, 10.1B)",
                "MaskGIT (arXiv 2202.04200) and VQ-VAE (arXiv 1711.00937) for the sampling and codebook conventions; GAIA-1 (arXiv 2309.17080) Sec. 4.1 for the 576-step comparison"],
    "diagram": {
        "encoder": {"text": "Frame 160x90 → ST-ViViT tokenizer (200M)", "sub": "~920 codes per frame, vocab 1,024; LAM (300M) infers 1 of 8 latent actions",
                    "tag": "frozen", "short": "ST-ViViT tokenizer, ~920 codes/frame"},
        "tokens": {"groups": [("frame", 24, "~920 frame codes")],
                   "note": "per frame; window 16 frames at 10 FPS"},
        "core": {"title": "MaskGIT ×48 · d 5120 · 36 heads",
                 "rows": [("attn", "Spatial attention within each frame"),
                          ("attn", "Causal temporal attention across frames"),
                          ("action", "Latent action: additive embedding"),
                          ("mlp", "FFW")],
                 "notes": ["window 16 frames; k/q size 128"]},
        "sampling": {"kind": "parallel", "text": "MaskGIT, 25 steps per frame", "sub": "all tokens of a frame per pass, temperature 2",
                     "short": "MaskGIT, 25 passes per frame"},
        "decoder": {"text": "ST-ViViT decoder → 160x90 frame", "sub": "20 layers, d 1024", "tag": "frozen"},
        "loop": "AR rollout",
    },
    "flow": {
        "below": [{"text": "Frame 160×90 + latent action"}],
        "stack": [
            {"box": "ST-ViViT tokenizer", "id": "tok", "style": "teal", "basis": "stated"},
            {"group": [
                {"box": "Add action embedding", "id": "act", "style": "orange", "side": "Latent action", "basis": "stated", "side_basis": "stated"},
            {"group": [
                {"box": "Masked frame tokens", "id": "masked", "style": "soft", "minor": True, "basis": "stated"},
                {"group": [
                    {"box": "Spatial attention", "id": "sattn", "style": "dark", "basis": "stated"},
                    {"box": "Temporal attention", "id": "tattn", "style": "dark", "basis": "stated"},
                    {"box": "Feed forward", "id": "ffw", "minor": True, "basis": "stated"},
                ], "repeat": "L ×", "id": "block", "basis": "stated"},
                {"box": "Sample (temperature 2)", "id": "sample", "minor": True, "basis": "stated"},
            ], "loop": "25 MaskGIT steps", "tint": "grey", "id": "maskgit"},
            ], "loop": "next-frame tokens", "loop_short": "next frame", "tint": "navy", "id": "rollout"},
        ],
        "above": [{"box": "ST-ViViT decoder", "id": "dec", "style": "teal", "basis": "stated"}, {"text": "Next frame 160×90"}],
        "annotations": [
            {"at": "tok", "text": "≈*920* tokens per frame, vocabulary *1,024*", "side": "left", "key": True},
            {"at": "act", "text": "*8* latent actions, learned without labels", "side": "left", "key": True},
            {"at": "sattn", "text": "*36* heads, width *5,120*", "side": "left"},
            {"at": "tattn", "text": "Causal over a *16*-frame window", "side": "left"},
            {"at": "block", "text": "*48* layers, *10.1B* parameters", "side": "right", "key": True},
            {"at": "maskgit", "text": "~*1* fps; *25* passes per frame", "side": "right", "key": True},
        ],
    },
    "audit": {"date": "2026-10-23", "checked": 44, "stated": 34, "code": 0, "derived": 3, "assumed": 0, "removed": 7, "fixed": 9},
}
