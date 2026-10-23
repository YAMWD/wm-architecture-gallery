MODEL = {
    "slug": "cosmos3",
    "name": "Cosmos 3",
    "year": 2026, "month": 6,
    "org": "NVIDIA",
    "family": "wam",
    "role": "LLM or mixture of transformers",
    "status": "company technical report",
    "params": "16B Nano (dense 8B base), 64B Super (dense 32B base)",
    "params_num": 16e9,
    "open": "code + weights",
    "links": {"report": "https://research.nvidia.com/labs/cosmos-lab", "code": "https://github.com/nvidia/cosmos",
              "weights": "https://huggingface.co/collections/nvidia/cosmos3"},
    "tagline": "Reasoner and generator towers share one attention",
    "summary": "An omnimodal world model built as a mixture of transformers: a reasoner tower (initialized from Qwen3-VL, "
               "then further pre-trained and fine-tuned) runs autoregressively over text and ViT tokens, and a generator "
               "tower denoises video latents, audio and action tokens with flow matching. The towers keep their own norms, "
               "attention projections and MLPs but share one self-attention operator, so every diffusion token can read "
               "the AR context. One set of weights serves generation, forward and inverse dynamics and a policy, selected "
               "by which tokens are clean and which are noisy; the post-trained DROID policy runs 4 steps with CFG split "
               "across 2 RTX Pro 6000 GPUs and skips video decoding.",
    "facts": [
        ("Representation", "Generation: Wan2.2-TI2V-5B VAE latents, 4x temporal and 32x32 spatial (16x16 VAE + 2x2 patch "
                           "merge), linearly projected to the hidden size, so ⌈H/32⌉ x ⌈W/32⌉ tokens per latent frame, "
                           "e.g. 23 x 40 = 920 at 720p 16:9, because an odd latent side is zero-padded before the merge [D]; "
                           "understanding: ViT tokens (patch 16, 2x2 merge); audio 25 tokens/s (48 kHz, hop 1920)"),
        ("Core", "Nano: 36 layers, hidden 4096, 32 heads / 8 KV heads of 128, FFN 12,288 in each of two towers = 16B "
                 "(from Qwen3-VL-8B); Super: 64 layers, hidden 5120, 64 / 8 heads, FFN 25,600 = 64B; Edge 4B (28 layers, "
                 "hidden 2048) released 20 Jul 2026"),
        ("Attention", "Shared self-attention: AR tokens attend causally to AR tokens only; DM tokens attend bidirectionally "
                      "over all AR + DM tokens; AR tokens never read DM tokens; training packs a fixed 74,000-token context"),
        ("Actions", "Action vectors (relative ego pose 9-D, effector pose 9-D, grasp state; 10-D single arm up to 57-D "
                    "egocentric human) enter as DM tokens through per-embodiment input and output projections; the MoT "
                    "backbone is shared; the DROID policy re-initializes the action encoder, decoding MLP and action "
                    "embedding tokens"),
        ("Prediction", "Flow matching: 50 steps for generation (guidance 6, shift 10), 4 steps for the DROID policy "
                       "(guidance 3, shift 5) predicting 32 absolute joint-position actions at 15 Hz; the reasoner pass is "
                       "computed once and cached across all steps; σ enters as a sinusoidal timestep embedding (256 → "
                       "Linear-SiLU-Linear) added to every noisy video, audio and action token after its input "
                       "projection, with no AdaLN in the layers (code)"),
        ("Decoder", "Wan2.2 VAE decoder for video; skipped in policy serving, where only the action tokens are read"),
        ("Memory", "The report describes no streaming rollout; the Nano model card chains 16-frame forward-dynamics "
                   "chunks, each re-conditioned on the previous chunk's last generated frame. Within each sample the "
                   "generator attends bidirectionally over its AR + DM tokens; paged KV caching only for reasoner "
                   "serving (TensorRT-LLM / vLLM)"),
        ("Speed", "Nano 720p text-to-video on one GPU: 297 s on H100 NVL vs 115 s on B200 (PyTorch; frames and steps not "
                  "stated); policy served on 2 RTX Pro 6000 with CFG parallelism, per-chunk latency not disclosed "
                  "(company claims)"),
        ("Key detail", "Each token passes through one tower, so per-token compute stays near the dense 8B backbone while "
                       "total parameters grow ≈1.8x (15.75B vs 8.77B) [D]; the DROID policy runs 4 steps x a 540x640 "
                       "three-view canvas and skips decoding the video latents"),
    ],
    "evidence": "read",
    "audit": {"date": "2026-10-22", "checked": 50, "stated": 41, "code": 7, "derived": 2, "assumed": 0, "fixed": 16},
    "sources": ["Cosmos 3 technical report (22 Jun 2026) Sec. 2.1 (encoders, action tokenization), Sec. 2.3 (MoT, attention), "
                "Table 2 (variants), Sec. 4.2 (74K context), Sec. 5 (reasoner caching, CFG parallelism, Fig. 16 timings), "
                "Sec. 4.2.5 (DROID policy: 4 steps, 2 RTX Pro 6000, decoding skipped), Table 21 (sampler settings)",
                "NVIDIA/cosmos-framework (commit 300faa14): cosmos_framework/model/vfm/mot/unified_mot.py (RMSNorm, "
                "per-tower layers), cosmos3_vfm_network.py (patch padding, timestep embedding)",
                "Hugging Face model cards and configs: nvidia/Cosmos3-Nano, Cosmos3-Edge, Cosmos3-Nano-Policy-DROID"],
    "diagram": {
        "encoder": {"text": "Video → Wan2.2 VAE · text + ViT → AR tokens",
                    "sub": "4x temporal, 32x32 spatial; (H/32)×(W/32) tokens per latent frame",
                    "tag": "frozen", "short": "Wan2.2 VAE + ViT/text tokens"},
        "tokens": {"groups": [("text", 4, "AR text/ViT"), ("latent", 16, "DM video latents"),
                              ("action", 4, "DM actions")],
                   "note": "packed training context of 74,000 tokens"},
        "core": {"title": "MoT ×36 · d 4096 · 32 heads (Nano)",
                 "rows": [("attn", "Shared self-attention: AR causal; DM bidirectional over AR + DM", "Shared attention: AR causal, DM full"),
                          ("mlp", "Reasoner tower: own norms + MLP (FFN 12,288) for AR tokens", "Reasoner tower: norms + MLP (AR)"),
                          ("moe", "Generator tower: own norms + MLP (FFN 12,288) for DM tokens", "Generator tower: norms + MLP (DM)"),
                          ("action", "Action tokens via per-embodiment in/out projections", "Actions: per-embodiment projections")],
                 "notes": ["8 KV heads; Super ×64 · d 5120 · 64 heads"]},
        "sampling": {"kind": "diffusion", "text": "Flow matching: 50 steps generation, 4 steps policy",
                     "sub": "reasoner pass cached across steps; CFG on 2 GPUs", "short": "Flow matching, 50 steps (4 policy)"},
        "heads": ["action chunk"],
        "decoder": {"text": "Wan2.2 VAE decoder → video (+ audio)", "sub": "skipped when serving the policy", "tag": "frozen",
                    "short": "Wan2.2 VAE decoder (policy skips it)"},
    },
    "flow": {
        "below": [{"fanout": [[{"text": "Text + images (AR)"}], [{"text": "Video, audio, actions (DM)"}]]}],
        "stack": [
            {"box": "Modality encoders", "id": "enc", "style": "teal", "basis": "stated"},
            {"box": "Pack AR + DM tokens", "id": "seq", "minor": True, "basis": "stated"},
            {"group": [
                {"box": "Noisy DM tokens", "id": "noisy", "style": "soft", "minor": True, "basis": "stated"},
                {"group": [
                    {"fanout": [[{"box": "RMSNorm", "minor": True, "basis": "code"},
                                 {"box": "Reasoner QKV", "id": "rqkv", "minor": True, "basis": "stated"}],
                                [{"box": "RMSNorm", "minor": True, "basis": "code"},
                                 {"box": "Generator QKV", "id": "gqkv", "minor": True, "basis": "stated"}]]},
                    {"box": "Shared self-attention", "id": "attn", "style": "dark", "side": "3D MRoPE",
                     "basis": "stated", "side_basis": "stated"},
                    {"fanout": [[{"box": "RMSNorm", "minor": True, "basis": "code"},
                                 {"box": "Reasoner MLP", "id": "rmlp", "basis": "stated"}],
                                [{"box": "RMSNorm", "minor": True, "basis": "code"},
                                 {"box": "Generator MLP", "id": "gmlp", "basis": "stated"}]]},
                ], "repeat": "36 ×", "id": "block", "basis": "stated"},
                {"box": "Update DM tokens", "id": "upd", "minor": True, "basis": "stated"},
            ], "loop": "50 steps (policy 4)", "tint": "grey", "id": "denoise", "basis": "stated"},
            {"fanout": [[{"box": "Video latents", "id": "vid", "basis": "stated"}],
                        [{"box": "Next text token", "id": "txt", "terminal": True, "minor": True, "basis": "stated"}],
                        [{"box": "Action out-projection", "short": "Action chunk", "id": "act", "style": "orange",
                          "terminal": True, "basis": "stated"}]]},
        ],
        "above": [{"box": "Wan2.2 VAE decoder", "id": "dec", "style": "teal", "basis": "code"},
                  {"text": "Video (policy skips decoding)"}],
        "annotations": [
            {"at": "enc", "text": "*32×32* pixels × *4* frames per token", "side": "left", "key": True},
            {"at": "seq", "text": "Context of *74,000* tokens", "side": "left"},
            {"at": "attn", "text": "*32* query, *8* KV heads · width *4,096*", "side": "left", "key": True},
            {"at": "block", "text": "*36* layers · *16B* on a dense *8B* base", "side": "right", "key": True},
            {"at": "gmlp", "text": "FFN *12,288* in each tower", "side": "right"},
            {"at": "act", "text": "DROID: *32* actions · latency not disclosed", "side": "right", "key": True},
        ],
    },
}
