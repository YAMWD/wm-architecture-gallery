MODEL = {
    "slug": "uva",
    "name": "UVA (Unified Video Action)",
    "year": 2025, "month": 2,
    "org": "Stanford",
    "family": "wam",
    "role": "Diffusion transformer",
    "status": "arXiv preprint (v3 Apr 2025)",
    "params": "not disclosed (MAR-B init)",
    "params_num": None,
    "open": "code + weights",
    "links": {"arXiv": "https://arxiv.org/abs/2503.00200", "page": "https://unified-video-action-model.github.io"},
    "summary": "A masked-autoencoder-style transformer, initialised from MAR-B, that fuses a history of kl-f16 VAE latents and "
               "action chunks into a joint video-action latent, which two lightweight diffusion heads decode into video "
               "patches and actions. Denoising runs only in the small heads, never in the backbone, and at deployment the "
               "video head is skipped entirely, so a 16-action trajectory costs 95 ms on an RTX 3080: 40 ms of VAE encoding, "
               "40 ms of transformer (30 with flash attention) and 15 ms for 16 steps of the action head.",
    "facts": [
        ("Representation", "Pretrained kl-f16 VAE latent map (w x h x c) per frame, flattened and projected by an FC layer into "
                           "N tokens of width d; N and the input resolution are not stated; future frames enter as randomly "
                           "masked tokens concatenated channel-wise with the history tokens"),
        ("Core", "Bidirectional transformer initialised from MAR-B (MAR-B as released: 12 encoder + 12 decoder blocks, d 768, "
                 "12 heads, per the MAR code); UVA's own size is not stated; language as a CLIP text token repeated M times "
                 "plus cross-attention (Libero10)"),
        ("Attention", "Bidirectional over the N x h video-action tokens (+ M language tokens); the same positions are masked "
                      "in every frame to avoid leakage; attention is about half of the transformer time (40 → 30 ms with "
                      "flash attention)"),
        ("Actions", "Each frame pairs with a chunk of L actions sampled faster than frames; history chunks are repeated M "
                    "times, FC-projected to N action tokens and concatenated channel-wise with the visual tokens"),
        ("Prediction", "Video: MAR-style masked generation from an empty sequence in 1 to 8 autoregressive stages; actions: a "
                       "conv + MLP pool the N latents into one action latent that conditions the action diffusion head, "
                       "16 denoising steps on the robot (100 in simulation)"),
        ("Decoder", "Video diffusion head + VAE decoder exist but are skipped at deployment (100 ms at 16 steps, 625 ms at 100)"),
        ("Memory", "History window of h frames and action chunks; no KV cache"),
        ("Speed", "Per 16-action trajectory on an RTX 3080 (authors, Table VI): VAE encoder 40 ms, transformer 40 ms (30 with "
                  "flash attention), action head 15 ms at 16 steps (93 at 100); total 95 ms (85 with flash attention), 173 ms "
                  "at 100 steps; policy + planner 195 ms; simulation timings on L40"),
        ("Key detail", "The clearest train-with-video, deploy-without-it case: the skipped video head would cost more than the "
                       "whole 95 ms policy, and the VAE encoder plus backbone, not the action head, dominate (80 of 95 ms [D])"),
    ],
    "evidence": "read",
    "sources": ["arXiv 2503.00200 Sec. III-A/B/C (encoding, masked transformer, diffusion heads), V-D (16 vs 100 steps, "
                "attention share), App. X-A (autoregressive video stages), X-D and Table VI (timing)",
                "GitHub README (MAR + VAE initialisation, checkpoints, 8 H100 x 4 days)",
                "GitHub LTH14/mar models/mar.py (mar_base: 12 + 12 blocks, d 768, 12 heads; fetched)"],
    "diagram": {
        "encoder": {"text": "Frames → kl-f16 VAE → FC projection", "sub": "N tokens of width d per frame (N not stated)",
                    "tag": "pretrained", "short": "kl-f16 VAE, N tokens per frame"},
        "tokens": {"groups": [("latent", 6, "history tokens"), ("action", 6, "action tokens"), ("noise", 6, "masked future")],
                   "note": "per frame, concatenated channel-wise"},
        "core": {"title": "MAR-B transformer ×24 · d 768 · 12 heads",
                 "rows": [("attn", "Bidirectional self-attention over N × h video-action tokens"),
                          ("xattn", "Language: CLIP text token ×M, cross-attention (Libero10)"),
                          ("mlp", "MLP")],
                 "notes": ["no KV cache; flash attention cuts 40 → 30 ms"]},
        "sampling": {"kind": "diffusion", "text": "Action diffusion head, 16 steps (100 in simulation)",
                     "sub": "video head: MAR masked stages, skipped at deployment", "short": "Action head 16 steps; video head skipped"},
        "heads": ["action chunk"],
        "decoder": {"none": "video diffusion head + VAE decoder skipped at deployment (100 ms at 16 steps)"},
    },
}
