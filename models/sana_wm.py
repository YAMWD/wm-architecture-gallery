MODEL = {
    "slug": "sana_wm",
    "name": "SANA-WM",
    "year": 2026, "month": 5,
    "org": "NVIDIA",
    "family": "ssm",
    "role": "SSM hybrid",
    "status": "arXiv preprint",
    "params": "2.6B (+17B optional refiner)",
    "params_num": 2.6e9,
    "open": "code + weights",
    "links": {"arXiv": "https://arxiv.org/abs/2605.15178"},
    "summary": "A minute-scale camera-controlled world model whose DiT replaces most softmax attention with frame-wise "
               "Gated DeltaNet: 15 of 20 blocks keep a D×D recurrent state per head, updated once per latent frame, and "
               "only 5 blocks use softmax attention, run at deployment with an attention sink plus a local window. The "
               "LTX2 VAE packs 8 raw frames into one 128-channel latent frame, so 60 s of 720p fits one GPU. Self Forcing "
               "distillation gives a 4-step chunk-causal generator; with NVFP4 on one RTX 5090 it denoises 60 s of 720p "
               "in 34 s (authors).",
    "facts": [
        ("Representation", "LTX2 VAE, 128 latent channels, one latent frame per 8 raw frames; spatial stride and tokens per "
                           "latent frame at 720p are not stated in the paper, which calls the representation 8x smaller than Wan2.1-VAE's"),
        ("Core", "Hybrid linear DiT from SANA-Video: 20 blocks, d 2240, 20 heads of 112; 15 frame-wise Gated DeltaNet blocks "
                 "+ softmax attention at layers {3, 7, 11, 15, 19}, keeping the original QKV and output projections; text, "
                 "video and pose tokens pass through the alternating blocks"),
        ("Attention", "GDN blocks: a D×D recurrent state per head updated once per latent frame from all S spatial tokens "
                      "(forward scan global, reversed scan reset at chunk boundaries in the chunk-causal variant); softmax blocks: "
                      "first latent frame as sink + local temporal window at deployment; chunk size not stated"),
        ("Actions", "6-DoF camera trajectory only, no keyboard: UCPE relative camera encoding on the geometric channels of a "
                    "camera attention branch at latent-frame rate, plus the 8 raw-frame Plücker raymaps of one VAE stride packed "
                    "into a 48-channel tensor through a zero-initialized 3D patch embedder; applied in every block"),
        ("Prediction", "Flow matching; 60-step chunk-causal AR generator distilled with Self Forcing to 4 steps; bidirectional, "
                       "chunk-causal and distilled variants each run on one GPU"),
        ("Decoder", "LTX2 VAE decoder → 720p at 16 fps (961 frames = 60 s [D]); optional second stage: LTX-2 17B refiner with a "
                    "rank-384 LoRA, 3 Euler steps"),
        ("Memory", "15 GDN layers hold 20 × 112² ≈ 0.25M values each, ≈7.5 MB in BF16 for all 15 [D]; the 5 softmax layers keep "
                   "a sink + window KV, so memory is constant in rollout length (all-softmax runs out of memory at 60 s on an H100, "
                   "Fig. 7b); no explicit 3D scene memory"),
        ("Speed", "60 s of 720p: DiT time on one H100 21.7 min at 60 steps → 43 s at 4 steps → 29 s with the sink; 34 s end to end "
                  "on one RTX 5090 with NVFP4 (authors, Fig. 7a); 433 ms per denoising step at 720p on one H100, 5.68 GiB (Table 3, 5 s clips); "
                  "24.1 one-minute videos per hour on 8 H100s (Table 2)"),
        ("Key detail", "The only model in this gallery whose per-frame cost is constant in rollout length in 3/4 of its layers; the "
                       "high-compression VAE is the bigger lever per step (3.4x latency, 8.9 → 5.4 GiB) and the softmax layers cost 1.17x per step [D]"),
    ],
    "evidence": "read",
    "sources": ["arXiv 2605.15178 abstract, Sec. 1, 3.1 (stages), 3.2 (frame-wise GDN, hybrid), 3.3 (UCPE + Plücker mixing), "
                "5.1 (backbone), 5.4 and Fig. 7 (speed path), Tables 2-3, App. C.1 (head dim 112)",
                "abstract and title page state open-source with a GitHub link (weight release not verified here)"],
    "diagram": {
        "encoder": {"text": "Frames → LTX2 VAE (128 ch, 8 frames per latent)", "sub": "spatial stride and tokens per frame not stated",
                    "tag": "pretrained", "short": "LTX2 VAE, 8 frames per latent"},
        "tokens": {"groups": [("latent", 8, "S latents per frame"), ("text", 2, "text tokens")],
                   "note": "tokens per frame not stated"},
        "core": {"title": "GDN/softmax DiT ×20 · d 2240 · 20 heads",
                 "rows": [("ssm", "Frame-wise GDN in 15 of 20 blocks"),
                          ("attn", "Softmax attention in 5 of 20 blocks"),
                          ("action", "Camera: UCPE attention + Plücker"),
                          ("mlp", "MLP")],
                 "notes": ["GDN: D×D state per head, updated once per latent frame",
                           "softmax layers: first latent frame as sink + local window"]},
        "sampling": {"kind": "diffusion", "text": "Self Forcing distilled flow, 4 denoising steps",
                     "sub": "per chunk (size not stated); 60 steps before distillation", "short": "4 steps per chunk"},
        "decoder": {"text": "LTX2 VAE decoder → 720p at 16 fps", "sub": "optional LTX-2 17B refiner (LoRA), 3 Euler steps",
                    "tag": "pretrained", "short": "LTX2 VAE decoder → 720p"},
        "loop": "AR rollout",
    },
    "flow": {
        "below": [{"text": "First frame + text + 6-DoF camera trajectory"}],
        "stack": [
            {"box": "LTX2 VAE encoder (8 frames per latent)", "short": "LTX2 VAE encoder", "id": "vae", "style": "teal"},
            {"box": "Patchify", "id": "patch", "minor": True},
            {"group": [
                {"box": "Noisy latent chunk", "id": "noisy", "style": "soft", "minor": True},
                {"group": [
                    {"residual": [{"box": "Norm", "minor": True, "side": "Timestep emb."},
                                  {"fanout": [[{"box": "Frame-wise Gated DeltaNet", "short": "Gated DeltaNet", "id": "gdn", "style": "dark"}],
                                              [{"box": "Softmax attention (sink + window)", "short": "Softmax attention", "id": "sattn", "style": "dark"}]]},
                                  {"box": "Add Plücker mixing", "id": "pl", "style": "orange", "minor": True, "side": "Raw-frame Plücker rays"}]},
                    {"residual": [{"box": "UCPE camera attention", "id": "ucpe", "style": "orange", "side": "6-DoF poses"}]},
                    {"residual": [{"box": "Cross-attention", "id": "xattn", "minor": True, "side": "Text tokens"}]},
                    {"residual": [{"box": "Norm", "minor": True}, {"box": "Mix-FFN", "id": "ffn"}]},
                ], "repeat": "20 ×", "id": "block"},
                {"box": "Predicted velocity", "id": "vel", "minor": True},
                {"box": "Update latents", "id": "upd", "minor": True},
            ], "loop": "4 denoising steps (Self Forcing)", "tint": "grey", "id": "denoise"},
        ],
        "above": [{"box": "LTX2 VAE decoder", "id": "dec", "style": "teal"}, {"text": "720p at 16 fps, up to 60 s"}],
        "annotations": [
            {"at": "vae", "text": "*128* latent channels, one latent frame per *8* raw frames (*8*× smaller than Wan2.1-VAE); spatial stride and tokens per frame not stated", "short": "one latent frame per *8* raw frames", "side": "left", "key": True},
            {"at": "gdn", "text": "in *15* of *20* blocks: a D×D recurrent state per head (D = *112*), updated once per latent frame from all spatial tokens; ≈*7.5 MB* for all 15 layers [D]", "short": "*15* of *20* blocks; fixed state ≈ *7.5 MB* [D]", "side": "left", "key": True},
            {"at": "sattn", "text": "in *5* of *20* blocks (layers *3, 7, 11, 15, 19*); first latent frame as sink + local temporal window at deployment", "short": "*5* of *20* blocks; sink + local window", "side": "right", "key": True},
            {"at": "pl", "text": "*8* raw-frame raymaps per VAE stride packed into *48* channels → zero-init 3D patch embedder, added after each attention output", "side": "left"},
            {"at": "ucpe", "text": "relative camera encoding on the geometric channels of the camera-branch heads, RoPE on the rest; in every block", "side": "left"},
            {"at": "block", "text": "*20* blocks, width *2,240*, *20* heads, *2.6B* parameters; text via cross-attention; norm and modulation type not disclosed", "short": "*20* blocks, width *2,240*, *2.6B*", "side": "right", "key": True},
            {"at": "upd", "text": "*60*-step chunk-causal generator distilled with Self Forcing to *4* steps: DiT time per minute of 720p *43* s, *29* s with the sink (one H100); chunk size not stated", "side": "right"},
            {"at": "dec", "text": "*60* s of 720p in *34* s on one RTX 5090 with NVFP4 (authors); optional *17B* refiner, *3* Euler steps", "short": "*60* s of 720p in *34* s on one RTX 5090", "side": "right", "key": True},
        ],
        "feedback": "next chunk",
    },
}
