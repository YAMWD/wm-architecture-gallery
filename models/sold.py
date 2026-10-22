MODEL = {
    "slug": "sold",
    "name": "SOLD",
    "year": 2024, "month": 10,
    "org": "University of Bonn",
    "family": "object",
    "role": "Object-centric model",
    "status": "arXiv preprint (v2 Feb 2025)",
    "params": "12M (all components)",
    "params_num": 12e6,
    "open": "code",
    "links": {"arXiv": "https://arxiv.org/abs/2410.08822", "page": "https://slot-latent-dynamics.github.io/"},
    "tagline": "Dreamer-style RL that imagines in object slots",
    "summary": "Dreamer-style model-based RL on object slots instead of one holistic latent. A SAVi encoder (pretrained, then "
               "fine-tuned) turns each frame into 2-10 slots of 128-d; an OCVP-style dynamics transformer predicts the next "
               "slot set from the slot history and the actions; a second Slot Aggregation Transformer with per-step output "
               "tokens drives the reward, value and actor heads, and the actor-critic trains on 15-step imagined slot "
               "rollouts. Two 4-layer transformers run per imagined step, with cost set by the slot count rather than the "
               "image resolution.",
    "facts": [
        ("Representation", "N = 2-10 object slots of 128-d per frame from SAVi (learned slot init, 3 Slot Attention iterations on "
                           "the first frame, 1 afterwards); slots projected to 256-d tokens; frame size not stated in the text"),
        ("Core", "Dynamics: OCVP-Seq transformer encoder, 4 layers, d 256, 8 heads, FFN 512. Slot Aggregation Transformer (SAT) for "
                 "reward, value and actor: 4 causal layers, d 256, 8 heads, FFN 512, RMSNorm; 12M parameters in total; "
                 "dynamics norm and activation not disclosed"),
        ("Attention", "Dynamics: OCVP sequential pattern, temporal attention (each slot over its own history) then relational "
                      "attention (all slots of one step). SAT: causal over time with ALiBi recency bias; 1 [out] + 4 [reg] "
                      "tokens per step, which cannot attend to earlier [out]/[reg] tokens"),
        ("Actions", "4-D end-effector + gripper commands a_0:t are inputs to the dynamics transformer alongside the slot history "
                    "(the embedding mechanism is not spelled out in the paper)"),
        ("Prediction", "One pass predicts all N next slots (regression): joint-embedding loss to SAVi slots of the real next frame "
                       "plus image reconstruction through the SAVi decoder; no teacher forcing; S seed frames then T = 15 "
                       "imagined steps"),
        ("Decoder", "SAVi CNN spatial-broadcast decoder: per-slot RGB + alpha masks composited by weighted sum; used in the "
                    "dynamics loss and for visualisation, not by the actor"),
        ("Memory", "The dynamics model and SAT re-read the slot history each step (S + imagined steps); no KV cache mentioned"),
        ("Speed", "No inference or wall-clock figure; everything trains on one A100 40 GB (authors)"),
        ("Key detail", "Reward, value and actor are MLP heads on SAT [out] tokens, with symlog two-hot reward/value bins as in "
                       "DreamerV3; per-step cost scales with the number of slots N, not with pixels; the actor head outputs a "
                       "Gaussian (μ, σ)"),
    ],
    "evidence": "read",
    "sources": ["arXiv 2410.08822 Sec. 2 (SAVi, OCVP), Sec. 3.1-3.2 (dynamics, SAT, rewards, imagination), Eq. 3-11",
                "arXiv 2410.08822 App. D Table 2 and D.1-D.4 (SAVi, dynamics, SAT configs; 12M params; one A100 40 GB; horizon 15, λ 0.95)",
                "arXiv 2410.08822 App. F (4-D action vector)"],
    "diagram": {
        "encoder": {"text": "Frame → SAVi (Slot Attention)", "sub": "2–10 slots of 128-d per frame, projected to d 256",
                    "tag": "trained jointly", "short": "SAVi slots, 2–10 × 128-d"},
        "tokens": {"groups": [("slot", 6, "N slots per frame"), ("action", 1, "action (4-D)")],
                   "note": "per step; history of S seed + imagined steps"},
        "core": {"title": "OCVP dynamics ×4 · d 256 · 8 heads",
                 "rows": [("attn", "Temporal attn: each slot over time"),
                          ("attn", "Relational attn: slots within a step"),
                          ("action", "Actions input with the slot history"),
                          ("mlp", "MLP (FFN 512)")],
                 "notes": ["+ Slot Aggregation Transformer ×4 (causal, ALiBi, [out] + 4 [reg] tokens per step) for the heads"]},
        "sampling": {"kind": "regress", "text": "Next slot set, regression", "sub": "1 pass per step; 15-step imagination, no teacher forcing",
                     "short": "Next slots, 1 pass per step"},
        "heads": ["reward", "value", "policy"],
        "decoder": {"text": "SAVi spatial-broadcast decoder → frame", "sub": "per-slot RGB + alpha, for the loss; actor reads slots",
                    "short": "SAVi decoder → frame (loss only)"},
        "loop": "AR rollout",
    },
    "flow": {
        "below": [{"text": "Frame + action a_t (4-D)"}],
        "stack": [
            {"box": "SAVi slot encoder", "id": "enc", "style": "teal"},
            {"box": "Project slots to tokens", "id": "proj", "minor": True},
            {"fanout": [
                [
                    {"box": "Slots + actions", "id": "seq", "side": "Action a_t"},
                    {"group": [
                        {"residual": [{"box": "Norm", "minor": True},
                                      {"box": "Temporal attention", "id": "tattn", "style": "dark"}]},
                        {"residual": [{"box": "Norm", "minor": True},
                                      {"box": "Relational attention", "id": "rattn", "style": "dark"}]},
                        {"residual": [{"box": "Norm", "minor": True}, {"box": "MLP", "id": "mlp"}]},
                    ], "repeat": "4 ×", "id": "dyn"},
                    {"box": "Next slot set", "id": "pred"},
                ],
                [
                    {"group": [
                        {"residual": [{"box": "RMSNorm", "minor": True}, {"box": "Causal self-attention", "id": "sattn", "style": "dark"}]},
                        {"residual": [{"box": "RMSNorm", "minor": True}, {"box": "MLP", "id": "smlp"}]},
                    ], "repeat": "4 ×", "id": "sat"},
                    {"box": "Reward, value, actor", "id": "heads", "terminal": True},
                ],
            ]},
        ],
        "above": [{"box": "SAVi broadcast decoder", "id": "dec", "style": "teal", "minor": True}, {"text": "Next frame (loss only)"}],
        "insets": [
            {"for": "heads", "label": "MLP heads on [out]", "stack": [{"box": "SAT [out] token"},
                                                                     {"fanout": [[{"box": "Reward head"}], [{"box": "Value head"}], [{"box": "Actor head"}]]}]},
        ],
        "annotations": [
            {"at": "enc", "text": "*2–10* slots per frame, *128*-d each", "side": "left", "key": True},
            {"at": "dyn", "text": "*8* heads · width *256*", "side": "left", "key": True},
            {"at": "pred", "text": "*1* pass per step · imagination of *15* steps", "side": "left", "key": True},
            {"at": "sat", "text": "*12M* parameters in all", "side": "right", "key": True},
            {"at": "sattn", "text": "*1* [out] + *4* [reg] tokens per step", "side": "right"},
            {"at": "heads", "text": "Latency not disclosed", "side": "right"},
        ],
        "feedback": "next step",
    },
}
