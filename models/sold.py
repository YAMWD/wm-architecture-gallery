MODEL = {
    "slug": "sold",
    "name": "SOLD",
    "year": 2024, "month": 10,
    "org": "University of Bonn",
    "family": "object",
    "role": "Object-centric model",
    "status": "ICML 2025 (PMLR 267); arXiv v1 Oct 2024",
    "params": "12M (paper; released checkpoint ≈11.9M)",
    "params_num": 12e6,
    "open": "code + weights",
    "links": {"code": "https://github.com/maltemosbach/sold", "arXiv": "https://arxiv.org/abs/2410.08822", "page": "https://slot-latent-dynamics.github.io/"},
    "tagline": "Dreamer-style RL that imagines in object slots",
    "summary": "Dreamer-style model-based RL on object slots instead of one holistic latent. A SAVi encoder (pretrained; fine-tuned in "
               "the paper, not in the released Reach-Red run) turns each frame into 2-10 slots of 128-d (7 in Reach-Red); an OCVP-Seq dynamics transformer predicts the next "
               "slot set from the slot history and the actions; three separate Slot Aggregation Transformers (reward, value, "
               "actor), each with per-step output tokens and its own MLP head, read the slot history, and the actor-critic "
               "trains on 15-step imagined slot rollouts. Each imagined step runs the dynamics model and the actor's SAT in "
               "sequence, with cost set by the slot count rather than the image resolution.",
    "facts": [
        ("Representation", "N = 2-10 object slots of 128-d per frame from SAVi (paper range; released Reach-Red checkpoint: 7, from its SAT mask 50 × 8) (learned slot init, 3 Slot Attention iterations on "
                           "the first frame, 1 afterwards); slots projected to 256-d tokens; frame size not stated in the text"),
        ("Core", "Dynamics: OCVP-Seq transformer encoder, 4 layers, d 256, 8 heads, FFN 512; in code each layer is a "
                 "relational and a temporal pre-LayerNorm sub-layer, each with its own ReLU FFN. One Slot Aggregation "
                 "Transformer (SAT) each for reward, value and actor: 4 causal layers (paper D.3 and released checkpoint, "
                 "blocks 0-3; the unweighted train_sold.yaml default says 3), d 256, 8 heads, FFN 512, RMSNorm, SiLU FFN; "
                 "4 [reg] tokens in the paper, 0 in the release; 12M parameters (paper), ≈11.9M in the checkpoint [D]"),
        ("Attention", "Dynamics (OCVP-Seq order, as in code): relational attention (the N slots plus the action token of one "
                      "step) then temporal attention (each token over its own history). SAT: causal over time with ALiBi "
                      "recency bias; 1 [out] + 4 [reg] tokens per step (paper; the released config uses 0 [reg]); no "
                      "token can attend to earlier steps' [out]/[reg] tokens"),
        ("Actions", "4-D end-effector + gripper commands a_0:t are inputs to the dynamics transformer alongside the slot history "
                    "(the embedding mechanism is not spelled out in the paper)"),
        ("Prediction", "One pass predicts all N next slots (regression): joint-embedding loss to SAVi slots of the real next frame "
                       "plus image reconstruction through the SAVi decoder; no teacher forcing; S seed frames then T = 15 "
                       "imagined steps"),
        ("Decoder", "SAVi CNN spatial-broadcast decoder: per-slot RGB + alpha masks composited by weighted sum; used in the "
                    "dynamics loss and for visualisation, not by the actor"),
        ("Memory", "The dynamics model and SAT re-read the slot history each step (S + imagined steps); no KV cache mentioned"),
        ("Speed", "No inference or wall-clock figure; everything trains on one A100 40 GB (authors)"),
        ("Key detail", "Reward, value and actor are MLP heads on SAT [out] tokens, with symlog two-hot reward/value bins (255 "
                       "over [−20, 20] in code); [D] per-step cost scales with the number of slots N, not with pixels; the actor head outputs a "
                       "Gaussian (μ, σ)"),
    ],
    "evidence": "read",
    "sources": ["arXiv 2410.08822 Sec. 2 (SAVi, OCVP), Sec. 3.1-3.2 (dynamics, SAT, rewards, imagination), Eq. 3-11",
                "arXiv 2410.08822 App. D Table 2 and D.1-D.4 (SAVi, dynamics, SAT configs; 12M params; one A100 40 GB; horizon 15, λ 0.95)",
                "arXiv 2410.08822 App. F (4-D action vector); ICML 2025, PMLR 267 (mosbach25a)",
                "github.com/maltemosbach/sold: modeling/sold/dynamics.py, slot_aggregation_transformer.py, prediction.py; README (checkpoints)"],
    "figure_variant": "Released checkpoint (Reach-Red): 4 dynamics + 4 SAT layers, 0 registers",
    "flow": {
        "below": [{"text": "Frame + action a_t (4-D)"}],
        "stack": [
            {"box": "SAVi slot encoder", "id": "enc", "style": "teal", "basis": "stated"},
            {"box": "Slot state", "id": "slots", "minor": True, "basis": "stated"},
            {"fanout": [
                [
                    {"box": "Project slots to tokens", "id": "dproj", "minor": True, "basis": "code"},
                    {"box": "Slots + actions", "id": "seq", "side": "Action a_t", "basis": "stated", "side_basis": "stated"},
                    {"group": [
                        {"residual": [{"box": "Norm", "minor": True, "basis": "code"},
                                      {"box": "Relational attention", "id": "rattn", "style": "dark", "basis": "stated"}]},
                        {"residual": [{"box": "Norm", "minor": True, "basis": "code"}, {"box": "MLP", "id": "mlp", "basis": "stated"}]},
                        {"residual": [{"box": "Norm", "minor": True, "basis": "code"},
                                      {"box": "Temporal attention", "id": "tattn", "style": "dark", "basis": "stated"}]},
                        {"residual": [{"box": "Norm", "minor": True, "basis": "code"}, {"box": "MLP", "id": "mlp2", "minor": True, "basis": "code"}]},
                    ], "repeat": "4 ×", "id": "dyn", "basis": "code"},
                    {"box": "Linear + slot residual", "short": "Next slot set", "id": "pred",
                     "side": "Current slots", "basis": "code", "side_basis": "code"},
                ],
                [
                    {"box": "Project slots to tokens", "id": "proj", "minor": True, "basis": "code"},
                    {"group": [
                        {"residual": [{"box": "RMSNorm", "minor": True, "basis": "stated"},
                                      {"box": "Causal self-attention", "id": "sattn", "style": "dark", "basis": "stated"}]},
                        {"residual": [{"box": "RMSNorm", "minor": True, "basis": "stated"}, {"box": "MLP", "id": "smlp", "basis": "stated"}]},
                    ], "repeat": "4 ×", "label": "One SAT per head", "id": "sat", "basis": "stated"},
                    {"box": "Reward, value, actor", "id": "heads", "terminal": True, "basis": "stated"},
                ],
            ]},
        ],
        "above": [{"box": "SAVi broadcast decoder", "id": "dec", "style": "teal", "minor": True, "basis": "code"}, {"text": "Next frame (loss only)"}],
        "insets": [
            {"for": "heads", "label": "Own SAT [out] per head", "stack": [
                {"fanout": [[{"box": "Reward SAT [out]", "basis": "code"}, {"box": "Reward head", "basis": "stated"}],
                            [{"box": "Value SAT [out]", "basis": "code"}, {"box": "Value head", "basis": "stated"}],
                            [{"box": "Actor SAT [out]", "basis": "code"}, {"box": "Actor head", "basis": "stated"}]]}]},
        ],
        "annotations": [
            {"at": "enc", "text": "*7* slots (Reach-Red; paper *2–10*) · *128*-d", "side": "left", "key": True},
            {"at": "dyn", "text": "*8* heads · width *256*", "side": "left", "key": True},
            {"at": "pred", "text": "*1* pass per step · imagination of *15* steps", "side": "left", "key": True},
            {"at": "sat", "text": "*4* dynamics + *4* SAT layers · *12M* total", "side": "right", "key": True},
            {"at": "sattn", "text": "*1* [out] · *0* [reg] (release; paper *4*)", "side": "right"},
            {"at": "heads", "text": "Latency not disclosed", "side": "right"},
        ],
        "feedback": "predicted slots",
        "feedback_from": "pred",
        "feedback_to": "slots",
    },
}
