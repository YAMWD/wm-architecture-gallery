MODEL = {
    "slug": "slotformer",
    "name": "SlotFormer",
    "year": 2022, "month": 10,
    "org": "University of Toronto",
    "family": "object",
    "role": "Object-centric model",
    "status": "ICLR 2023",
    "params": "size not disclosed",
    "params_num": None,
    "open": "code + weights",
    "links": {"arXiv": "https://arxiv.org/abs/2210.05861", "code": "https://github.com/pairlab/SlotFormer"},
    "summary": "The reference object-centric dynamics model. A frozen SAVi (or STEVE) encoder turns each frame into a handful "
               "of object slots, and a small transformer encoder over the slots of the last T frames predicts all of the next "
               "frame's slots in one pass, then rolls out autoregressively. There are no actions; rollouts feed video "
               "prediction, VQA and PHYRE planning. The transformer sees only tens of tokens per step, so the encoder and the "
               "per-slot spatial-broadcast decoder carry most of the compute.",
    "facts": [
        ("Representation", "N object slots per frame from a frozen SAVi (STEVE on Physion): 6-8 slots of 128-d (192-d on Physion) "
                           "at 64×64 or 128×128; a linear layer maps slots to d_e = 128 (OBJ3D) or 256"),
        ("Core", "BERT-style Pre-LN transformer encoder: N_T = 4 layers on OBJ3D and CLEVRER, 8 on Physion and PHYRE; 8 heads; "
                 "FFN 4×d_e; parameter count not disclosed (~3M block weights for 4 layers at d 256 [D])"),
        ("Attention", "Full bidirectional self-attention over the T×N slot tokens of the history; temporal-only sinusoidal "
                      "positional encoding so slots of one frame share it (permutation equivariant); T = 6 burn-in frames on "
                      "OBJ3D and CLEVRER (6 × 7 = 42 tokens on CLEVRER [D]), 15 on Physion, 1 on PHYRE"),
        ("Actions", "None; unconditional video prediction, with VQA and PHYRE task-success readouts on the rollouts"),
        ("Prediction", "One pass predicts all N next-frame slots jointly: the last N outputs go through a linear layer plus a "
                       "residual from the current slots, L2 slot loss (+ image loss); K = 10 rollout frames, predictions fed back"),
        ("Decoder", "Frozen SAVi spatial-broadcast CNN decoder (16×16 broadcast grid) renders each slot as RGB plus alpha mask; "
                    "STEVE's transformer decoder on Physion"),
        ("Memory", "Sliding history of T frames = T×N tokens; no KV cache (bidirectional encoder)"),
        ("Speed", "No inference figure; 'can be trained on servers with 4 modern GPUs in less than 5 days' (authors)"),
        ("Key detail", "~42 tokens per step through a 4-layer encoder: the attention is negligible, the SAVi encoder and "
                       "per-slot decoder dominate"),
    ],
    "evidence": "read",
    "sources": ["arXiv 2210.05861 Sec. 3.2-3.3 (architecture, training), Sec. 4.5 ablations (N_T, T, K, P.E.)",
                "arXiv 2210.05861 App. C Table 8 (per-dataset N, D_slot, D_e, N_T, T, K), App. C text (8 heads, FFN 4×, Pre-LN, 16×16 broadcast)",
                "Reproducibility statement (4 GPUs, < 5 days); github.com/pairlab/SlotFormer (code and weights)"],
    "diagram": {
        "encoder": {"text": "Frame 64×64 → SAVi (Slot Attention)", "sub": "6–8 slots of 128-d per frame, linear → d_e",
                    "tag": "frozen", "short": "SAVi slots, 6–8 × 128-d"},
        "tokens": {"groups": [("slot", 7, "7 slots per frame")],
                   "note": "history 6 frames × 7 slots = 42 tokens (CLEVRER)"},
        "core": {"title": "Transformer enc. ×4 · d 256 · 8 heads",
                 "rows": [("attn", "Bidirectional attention over T×N slots"),
                          ("mlp", "MLP (FFN 4×d)")],
                 "notes": ["temporal-only sinusoidal P.E.: all slots of a frame share it",
                           "4 layers (OBJ3D, CLEVRER), 8 (Physion, PHYRE)"]},
        "sampling": {"kind": "regress", "text": "Next-frame slots, L2 regression", "sub": "1 pass predicts all N slots; residual from current slots",
                     "short": "Next slots, 1 pass per frame"},
        "decoder": {"text": "SAVi spatial-broadcast decoder → 64×64 frame", "sub": "per-slot RGB + alpha masks, composited", "tag": "frozen",
                    "short": "SAVi decoder → 64×64 frame"},
        "loop": "AR rollout",
    },
}
