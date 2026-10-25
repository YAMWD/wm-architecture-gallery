MODEL = {
    "slug": "cosmos_predict1_ar",
    "name": "Cosmos-Predict1 (autoregressive)",
    "year": 2025, "month": 1,
    "org": "NVIDIA",
    "family": "token",
    "role": "Discrete-token model",
    "status": "company technical report",
    "params": "4B and 12B (5B/13B with text)",
    "params_num": 4e9,
    "open": "code + weights",
    "links": {"arXiv": "https://arxiv.org/abs/2501.03575", "code": "https://github.com/nvidia-cosmos/cosmos-predict1"},
    "tagline": "Llama-style GPT over discrete video tokens",
    "summary": "NVIDIA's autoregressive world foundation models: Llama3-style GPTs trained from scratch to predict the "
               "next video token, with no language pretraining. A discrete video tokenizer (8x16x16, FSQ, vocabulary "
               "64,000) gives 2,560 tokens per latent frame at 640x1024, and the 4B and 12B base models attend causally "
               "over 12,800 tokens (33 video frames) with 3D RoPE; the figure draws the released 4B base, which generates "
               "32 frames in 31 s on one H100. Not drawn: the Video2World 5B/13B variants add T5 cross-attention, and the "
               "paper's Medusa heads (not in the released code) cut forward passes by up to 4.6x for 4B.",
    "facts": [
        ("Representation", "Cosmos-Tokenize1-DV8x16x16 discrete tokens, FSQ levels (8,8,8,5,5,5) = vocabulary 64,000; at 640x1024 one latent frame (8 video frames; the first holds only frame 1) is 40x64 = 2,560 tokens [D]"),
        ("Core", "Llama3-style decoder with SwiGLU and QK-norm: 4B = 16 layers, d 4096, FFN 14,336, 32 heads, 8 KV heads; 12B = 40 layers, d 5120; the 5B/13B Video2World models add cross-attention layers; RMSNorm (eps 1e-5) before each sub-layer plus a final RMSNorm (official code; the paper names no norm)"),
        ("Attention", "Dense causal over 12,800 tokens = 5 latent frames = 33 video frames, the maximum the AR variants support [D]; 3D RoPE (theta 500,000) plus a sinusoidal 3D absolute positional embedding in every block (Table 14 lists it for all four sizes; the released code adds it only for Video2World); the text says no MQA/GQA, but Table 14 and the code use 8 KV heads"),
        ("Actions", "The base models take only video; the Bridge robot post-train (5B ActionCond) projects the 7-D gripper action with an MLP and injects it by cross-attention; text enters by T5-XXL cross-attention in Video2World"),
        ("Prediction", "Next-token softmax, 2,560 passes per latent frame [D]; Medusa speculative decoding (single-layer FFN heads on the last hidden state that share the output layer, no tree attention; tested on 4B/5B; the released code has no Medusa model): the chosen 9 heads give 2.0x token throughput and 4.2x fewer passes for 4B, 3.2x and 5.7x for 5B [D]; 12 heads give the fewest passes (4.6x, 6.1x) (Table 15, 8 H100)"),
        ("Decoder", "Tokenizer decoder, or an optional 7B diffusion decoder that adds 30-32 s on one H100, doubling the 4B time (31.04 → 61.49 s) [D]"),
        ("Memory", "KV caching is used (Sec. 5.2.4, gpt-fast style); the code keeps a static BF16 self-attention cache over all 12,800 positions, 8 KV heads × 128 dims per layer: ≈0.84 GB per sequence for 4B, ≈2.1 GB for 12B [D]; cross-attention K/V are not cached"),
        ("Speed", "4B on one H100 at 640x1024, 32 frames from 1: 31.04 s (23.52 s with Medusa), 29 GB; 12B 84.78 s; 4B at 320x512 with Medusa on 8 H100: 806.61 tokens/s = 10.08 frames/s (NVIDIA, Tables 16-17)"),
        ("Key detail", "~330 tokens/s for 4B on one H100, averaged over the whole run (10,240 generated tokens in 31.04 s) [D]; 4 → 8 GPUs gains only 3% (18.20 → 17.62 s) [D]; the 10 FPS result used 4x fewer tokens per frame (320x512) [D], Medusa and 8 H100s"),
    ],
    "evidence": "read",
    "sources": ["Cosmos technical report arXiv 2501.03575 Sec. 4 (tokenizer), Sec. 5.2.2-5.2.4 (architecture table, Medusa, Tables 15-17), post-training section (ActionCond)",
                "Official code nvidia-cosmos/cosmos-predict1 (commit 724daa1): cosmos_predict1/autoregressive/networks/transformer.py, modules/attention.py, configs/base/model_config.py, inference/world_generation_pipeline.py, utils/sampling.py"],
    "figure_variant": "Released 4B base: no text cross-attention; paper's per-block 3D APE is off in its code",
    "flow": {
        "below": [{"text": "Video 640×1024 (4B base)"}],
        "stack": [
            {"box": "Cosmos-Tokenize1 encoder", "short": "Video tokenizer (FSQ)", "id": "tok", "style": "teal", "basis": "stated"},
            {"box": "FSQ quantization", "id": "fsq", "minor": True, "basis": "stated"},
            {"box": "Token embedding", "id": "emb", "minor": True, "basis": "stated"},
            {"group": [
                {"residual": [{"box": "RMSNorm", "minor": True, "basis": "code"},
                              {"box": "Masked self-attention", "id": "attn", "style": "dark", "side": "3D RoPE", "basis": "stated", "side_basis": "stated"}]},
                {"residual": [{"box": "RMSNorm", "minor": True, "basis": "code"}, {"box": "SwiGLU feed forward", "short": "SwiGLU FFN", "id": "ffn", "basis": "stated"}]},
            ], "repeat": "16 ×", "id": "block", "basis": "code"},
            {"box": "Final RMSNorm", "minor": True, "basis": "code"},
            {"box": "Output layer", "id": "out", "basis": "stated"},
            {"box": "Sample next token", "id": "sample", "basis": "code"},
        ],
        "above": [{"box": "Tokenizer decoder", "id": "dec", "style": "teal", "basis": "stated"}, {"text": "Frames 640×1024 (33 video frames)"}],
        "insets": [{"for": "ffn", "stack": [{"fanout": [[{"box": "Linear", "basis": "code"}], [{"box": "Linear", "basis": "code"}, {"box": "SiLU", "basis": "code"}]]}, {"merge": "x"}, {"box": "Linear", "basis": "code"}]}],
        "annotations": [
            {"at": "tok", "text": "≈*2,560* tokens per latent frame", "side": "left", "key": True},
            {"at": "fsq", "text": "Vocabulary of *64,000*", "side": "right"},
            {"at": "attn", "text": "*32* heads, context of *12,800* tokens", "side": "left"},
            {"at": "block", "text": "*16* layers, width *4,096*", "side": "right", "key": True},
            {"at": "sample", "text": "≈*2,560* serial passes per latent frame", "side": "left", "key": True},
            {"at": "dec", "text": "*4B*: *32* frames in *31* s", "side": "left", "key": True},
        ],
        "feedback": "next token",
        "feedback_from": "sample",
        "feedback_to": "emb",
    },
}
