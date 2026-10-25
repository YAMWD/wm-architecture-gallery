MODEL = {
    "slug": "worldvla",
    "name": "WorldVLA",
    "year": 2025, "month": 6,
    "org": "Alibaba DAMO Academy",
    "family": "wam",
    "role": "Discrete-token model",
    "status": "arXiv preprint",
    "params": "~7B (Chameleon backbone)",
    "params_num": 7e9,
    "open": "code + weights",
    "links": {"arXiv": "https://arxiv.org/abs/2506.21539", "code": "https://github.com/alibaba-damo-academy/WorldVLA",
              "weights": "https://huggingface.co/Alibaba-DAMO-Academy/WorldVLA"},
    "tagline": "One LLM writes next-frame and action tokens",
    "summary": "A single autoregressive transformer, initialised from Chameleon, that treats images, text and actions as one "
               "token vocabulary: it predicts the next frame's VQ-GAN codes as a world model and the next action's 7 tokens "
               "as a VLA, and the authors report that training both together helps both. There are no diffusion steps; "
               "everything is next-token decoding, so an action costs 9 serial passes ([BOA], 7 action tokens, [EOA]) and "
               "an imagined frame about 277 at the drawn 256×256 setting (512×512 setting: about 1,061). A custom mask hides the earlier actions of a "
               "chunk so that each action depends only on text and images, which, the authors say, lets the chunk be "
               "generated in parallel; the released code still decodes it token by token.",
    "facts": [
        ("Representation", "VQ-GAN image tokenizer (compression 16, codebook 8192): 256 tokens per 256x256 frame or 1,024 per "
                           "512x512; BPE text; one shared vocabulary of 65,536 including the 8192 image and 256 action tokens"),
        ("Core", "Chameleon-initialised decoder-only LLM; the paper gives no size, the released base_model config.json has "
                 "32 layers, d 4096, 32 heads, FFN 11,008 (~7B; 14 GB of bf16 safetensors [D]); block details not disclosed "
                 "in the paper"),
        ("Attention", "Causal over text, image and action tokens in world-model mode; in action mode a mask lets each action "
                      "attend to text and images but not to earlier actions of the chunk; default M = 2 input frames"),
        ("Actions", "7 discrete tokens per action (3 relative positions, 3 relative angles, 1 gripper), 256 bins per dimension; "
                    "chunks of K = 5 (K = 10 on LIBERO-Long)"),
        ("Prediction", "Next-token softmax, greedy in the released code; 9 passes per action ([BOA], 7 tokens, [EOA]) [D]; "
                       "the masked chunk can be generated in parallel (authors); about 277 serial passes per generated frame at "
                       "256×256 (256 VQ codes plus row-end, size, [BOI], [EOI] and end tokens) [D]; 512×512 setting: about "
                       "1,061 (1,024 codes) [D]"),
        ("Decoder", "VQ-GAN decoder for predicted image tokens (world-model mode); actions need only a de-binning lookup "
                    "(token → bin centre → min-max un-normalisation), no neural decoder"),
        ("Memory", "LLM KV cache over the prompt (history frames + text); 1, 2 or 4 history frames evaluated, 2 by default"),
        ("Speed", "LIBERO, GPU not stated (authors, Table 5): 2.27 / 1.77 / 1.22 FPS with 1 / 2 / 4 history frames without "
                  "chunking, 3.67 / 3.13 / 2.78 FPS with chunking"),
        ("Key detail", "An LLM-style decode workload, token-serial; each imagined frame is about 277 (256×256) to 1,061 "
                       "(512×512) decode steps [D]; 'memory-bandwidth-bound' is our estimate for batch-1 decode of a 7B "
                       "model, not an author measurement"),
    ],
    "evidence": "read",
    "sources": ["arXiv 2506.21539 Sec. 3.2 (tokenizers, Chameleon init), 3.3 (attention mask), 4.1 (M = 2, K), 4.3 and "
                "Table 5 (history length, FPS)",
                "Hugging Face Alibaba-DAMO-Academy/WorldVLA config.json (32 layers, hidden 4096, 32 heads, FFN 11008, "
                "vocab 65536) and safetensors headers (7.01B params, BF16)",
                "GitHub alibaba-damo-academy/WorldVLA: README; item_processor.py (process_image, process_action); "
                "libero_util/Chameleon_utils.py (GenerationConfig, greedy); modeling_xllmx_chameleon_ck.py "
                "(decode_token_ids_to_actions)"],
    "figure_variant": "Released Chameleon-based ~7B, 256×256 setting, two-frame input",
    "flow": {
        "below": [{"text": "Text + 2 frames (current + 1 past)"}],
        "stack": [
            {"box": "VQ-GAN image tokenizer", "short": "VQ-GAN tokenizer", "id": "tok", "style": "teal", "basis": "stated"},
            {"box": "One shared vocabulary", "id": "seq", "side": "Text, action bins", "minor": True, "basis": "stated", "side_basis": "stated"},
            {"box": "Token embedding", "id": "emb", "minor": True, "basis": "code"},
            {"group": [
                {"residual": [{"box": "Norm", "minor": True, "basis": "code"}, {"box": "Masked self-attention", "id": "attn", "style": "dark", "basis": "stated"}]},
                {"residual": [{"box": "Norm", "minor": True, "basis": "code"}, {"box": "Feed forward", "id": "ffn", "basis": "code"}]},
            ], "repeat": "32 ×", "id": "block", "basis": "code"},
            {"box": "Final norm", "id": "fnorm", "minor": True, "basis": "code"},
            {"box": "Linear output layer", "id": "out", "minor": True, "basis": "code"},
            {"box": "Greedy next token", "id": "sample", "basis": "code"},
            {"fanout": [[{"box": "Image tokens", "id": "img", "basis": "stated"}],
                        [{"box": "Action tokens", "id": "act", "style": "orange", "terminal": True, "basis": "stated"}]]},
        ],
        "above": [{"box": "VQ-GAN decoder", "id": "dec", "style": "teal", "basis": "code"}, {"text": "Next frame (world-model mode)"}],
        "annotations": [
            {"at": "tok", "text": "*256* codes per frame · codebook *8,192*", "side": "left", "key": True},
            {"at": "seq", "text": "Vocabulary of *65,536*", "side": "left"},
            {"at": "attn", "text": "*32* heads · width *4,096*", "side": "left"},
            {"at": "block", "text": "*32* layers · ≈*7B* parameters", "side": "right", "key": True},
            {"at": "sample", "text": "*9* passes per action · ≈*277* per frame", "side": "right", "key": True},
            {"at": "act", "text": "*3.13* FPS with chunking (*1.77* without)", "side": "right", "key": True},
        ],
        "feedback": "next token",
        "feedback_from": "sample",
        "feedback_to": "emb",
    },
}
