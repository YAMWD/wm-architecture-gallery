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
    "links": {"report": "https://research.nvidia.com/labs/cosmos-lab/cosmos3/technical-report.pdf", "code": "https://github.com/NVIDIA/cosmos-framework",
              "weights": "https://huggingface.co/collections/nvidia/cosmos3"},
    "tagline": "Reasoner and generator towers share one attention",
    "summary": "An omnimodal world model built as a mixture of transformers: a reasoner tower (initialized from Qwen3-VL, "
               "then further pre-trained and fine-tuned) runs autoregressively over text and ViT tokens, and a generator "
               "tower denoises video latents, audio and action tokens with flow matching. The towers keep their own norms, "
               "attention projections and MLPs but share one self-attention operator, so every diffusion token can read "
               "the AR context. One set of weights serves generation, forward and inverse dynamics and a policy, selected "
               "by which tokens are clean and which are noisy (Nano: 50 flow-matching steps); a separately post-trained DROID "
               "policy checkpoint runs 4 steps with CFG split across 2 RTX Pro 6000 GPUs and skips video decoding.",
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
                       "projection, with no AdaLN in the layers (code); the reasoner decodes text by next-token "
                       "prediction (not drawn); Nano forward/inverse dynamics also use 50 steps (guidance 1)"),
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
    "sources": ["Cosmos 3 technical report (22 Jun 2026) Sec. 2.1 (encoders, action tokenization), Sec. 2.3 (MoT, attention), "
                "Table 2 (variants), Sec. 4.2 (74K context), Sec. 5 (reasoner caching, CFG parallelism, Fig. 16 timings), "
                "Sec. 4.2.5 (DROID policy: 4 steps, 2 RTX Pro 6000, decoding skipped), Table 21 (sampler settings)",
                "NVIDIA/cosmos-framework (commit 300faa14): cosmos_framework/model/vfm/mot/unified_mot.py (RMSNorm, "
                "per-tower layers), cosmos3_vfm_network.py (patch padding, timestep embedding)",
                "Hugging Face model cards and configs: nvidia/Cosmos3-Nano, Cosmos3-Edge, Cosmos3-Nano-Policy-DROID"],
    "figure_variant": "Nano generation (50 FM steps); reasoner text decoding not drawn",
    "flow": {
        "below": [{"fanout": [[{"text": "Text + image context (AR)"}], [{"text": "Video / audio / action (DM)"}]]}],
        "stack": [
            {"fanout": [[{"box": "Text / ViT encoder", "id": "enc", "style": "teal", "basis": "stated"},
                         {"box": "Reasoner pass", "id": "reasoner", "basis": "stated"},
                         {"box": "Cache AR keys / values", "id": "cache", "minor": True, "basis": "stated"}],
                        [{"box": "VAEs + action in-proj.", "short": "DM encoders", "id": "denc", "style": "teal",
                          "basis": "stated"},
                         {"box": "Clean DM tokens", "id": "clean", "style": "soft", "minor": True, "basis": "stated"}]]},
            {"group": [
                {"box": "Noisy DM tokens", "id": "noisy", "style": "soft", "minor": True,
                 "side": "Timestep embedding", "basis": "stated", "side_basis": "code"},
                {"box": "Pack AR + DM tokens", "id": "seq", "minor": True, "basis": "stated"},
                {"group": [
                    {"residual": [{"box": "RMSNorm", "minor": True, "basis": "code"},
                                  {"box": "Generator QKV", "id": "gqkv", "minor": True,
                                   "side": "3D MRoPE", "basis": "code", "side_basis": "stated"},
                                  {"box": "DM → AR + DM attention", "id": "attn", "style": "dark",
                                   "side": "Cached AR K/V", "basis": "code", "side_basis": "stated"}]},
                    {"residual": [{"box": "RMSNorm", "minor": True, "basis": "code"},
                                  {"box": "Generator MLP", "id": "gmlp", "minor": True, "basis": "stated"}]},
                ], "repeat": "36 ×", "id": "block", "basis": "stated"},
                {"box": "Final generator RMSNorm", "minor": True, "basis": "code"},
                {"box": "DM out-projections", "id": "outp", "minor": True, "basis": "code"},
                {"box": "Update noisy DM tokens", "short": "Update DM tokens", "id": "upd", "minor": True,
                 "basis": "stated"},
            ], "loop": "50 FM steps", "tint": "grey", "id": "denoise", "basis": "stated"},
            {"fanout": [[{"box": "Video latents", "id": "vid", "basis": "stated"}],
                        [{"box": "Audio VAE decoder", "id": "aud", "style": "teal", "terminal": True, "minor": True,
                          "basis": "code"}],
                        [{"box": "Action chunk", "id": "act", "style": "orange", "terminal": True, "basis": "stated"}]]},
        ],
        "above": [{"box": "Wan2.2 VAE decoder", "id": "dec", "style": "teal", "basis": "code"},
                  {"text": "Video frames"}],
        "annotations": [
            {"at": "vid", "text": "*32×32* pixels × *4* frames per video token", "side": "left", "key": True},
            {"at": "seq", "text": "Training packs *74,000* AR + DM tokens", "side": "left"},
            {"at": "attn", "text": "*32* query, *8* KV heads · width *4,096*", "side": "left", "key": True},
            {"at": "block", "text": "*36* layers · *16B* on a dense *8B* base", "side": "right", "key": True},
            {"at": "gmlp", "text": "FFN *12,288* in each tower", "side": "right"},
            {"at": "act", "text": "Per-embodiment proj. · *10*–*57*-D actions", "side": "right", "key": True},
        ],
    },
}
