# Architecture source review — 2026-10-25

All 49 gallery models were compared with their original publication or official technical page. Released implementation files were also checked for 42 models. For the remaining 7, no matching public implementation was found in the consulted sources; their figures show only disclosed details.

The figures are operator-level schematics of the named configuration below. They are not claims that every model variant, training path, or hardware optimization has the same graph. A module box can encapsulate projections and normalization; an expanded residual shows the actual skip boundary. Performance numbers are source reports or labelled arithmetic, not new measurements.

This review corrects the previous audit rather than inheriting its verification labels. Paper/code disagreements and unavailable details are retained as limitations. No architecture is filled in from a related model or a conventional transformer layout.

## Corrections that affect interpretation

- The old audit missed real paper/code disagreements and incompatible variant combinations. Each figure now names one configuration; differences remain explicit rather than being silently reconciled.
- LingBot-VA released video/action forward paths share one transformer; the paper describes separate towers. The pinned checkpoint headers confirm the shared-width action projections and approximately 5.1B parameters.
- Cosmos-Predict1 uses the released 4B base graph. Cosmos-Predict2.5 uses the 35-step base Video2World sampler. NWM uses the released 250-step DDPM. Flash, distilled and base latency/sampler claims are no longer combined in those figures.
- SOLD, SlotFormer, TransDreamer, UniZero and UVA now follow the selected released configuration, with paper differences recorded. Missing final norms, input projections and adaptive residual gates were corrected where code supplies them.
- Rollout arrows now name actual tensor endpoints. Sampled codes, predicted features, latents and cached K/V return to the matching stage; robot actions are not drawn as direct image-encoder inputs.
- All 49 unused legacy diagram specifications and historical verification counters were removed. Default rendering and the website use the same reviewed flow, with current source coverage in each card.
- Undisclosed details stay undisclosed. For seven models no matching official implementation was found in the consulted sources: AAPT, comma.ai, Dreamer 4, GAIA-1, GAIA-2, Genie and the long-context SSM model.
- The source ledger binds each review to the complete card and records immutable code revisions plus source-byte hashes. These are reproducibility/integrity checks, not automated proof of scientific correctness.
- A follow-up independent check of this review found four wrong edits and several removals of source-backed content; they were fixed: SOLD keeps the paper's and checkpoint's 4 slot-aggregation layers, LingBot-VA and the long-context SSM model keep their closed rollout loops, Genie's block count stays the paper's L, and mixed-configuration labels were made consistent with each figure. The former 'verified' evidence level stays retired, because it described a check of an earlier version of the facts.

## Coverage

| Model | Figure configuration | Sources |
|---|---|---|
| [AAPT](#aapt) | Paper: 8B, 36-block causal adversarial generator | Publication only |
| [comma.ai world model (openpilot 0.11)](#comma-wm) | Official openpilot 0.11 technical post: 2B, 15 Euler steps | Official page only |
| [Cosmos 3](#cosmos3) | Nano generation (50 FM steps); reasoner text decoding not drawn | Publication + released code |
| [Cosmos Policy](#cosmos-policy) | Released LIBERO policy: Predict2-2B, 28 blocks, 5 EDM steps | Publication + released code |
| [Cosmos-Predict1 (autoregressive)](#cosmos-predict1-ar) | Released 4B base: no text cross-attention; paper's per-block 3D APE is off in its code | Publication + released code |
| [Cosmos-Predict2.5](#cosmos-predict25) | Released 2B base Video2World: 28 blocks, 35 FlowUniPC steps, CFG 7 (2 passes/step) | Publication + released code |
| [CWM (Code World Model)](#cwm) | Released dense 32B code world model | Publication + released code |
| [Δ-IRIS](#delta-iris) | Released Crafter configuration: 3 layers, 4 delta codes per frame | Publication + released code |
| [DINO-WM](#dino-wm) | Released DINO-WM predictor: 6 layers, DINOv2 patch features | Publication + released code |
| [Dreamer 4](#dreamer4) | Paper: 1.6B dynamics, 3 spatial layers per causal temporal layer | Publication only |
| [DreamZero](#dreamzero) | DreamZero-Flash (paper only, no released weights): Wan2.1-I2V-14B, one denoising step | Publication + released code |
| [EMERALD](#emerald) | Released 30M: 4 temporal blocks + 2 spatial MaskGIT blocks | Publication + released code |
| [Fast-WAM](#fast-wam) | Released Fast-WAM policy: cached first-frame video K/V, 10 action steps | Publication + released code |
| [GAIA-1](#gaia1) | Paper: 6.5B autoregressive world model and separate video decoder | Publication only |
| [GAIA-2](#gaia2) | Paper: 8.4B, 22 factorized space-time blocks, 50 flow steps | Publication only |
| [Genie Envisioner (GE-Act)](#ge-act) | Released GE-Base video cache + GE-Act 160M action decoder | Publication + released code |
| [Genie](#genie) | Paper: 10.1B dynamics (num_layers 48), 25 MaskGIT passes | Publication only |
| [Hunyuan-GameCraft](#hunyuan-gamecraft) | Released HunyuanVideo GameCraft: 20 double + 40 single blocks, 8 PCM steps | Publication + released code |
| [IRIS](#iris) | Released Atari IRIS: 10x256 transformer, 16 image codes | Publication + released code |
| [iVideoGPT](#ivideogpt) | Released 138M Llama-style predictor with compressive tokenizer | Publication + released code |
| [JOWA](#jowa) | Released JOWA-150M: 12x768, task-conditioned GPT | Publication + released code |
| [Long-Context SSM World Model](#lc-ssm) | Paper: 200M block-wise SSM/local-attention denoiser | Publication only |
| [LeWorldModel (LeWM)](#lewm) | Released LeWM: ViT-Tiny encoder + 6-layer predictor | Publication + released code |
| [LingBot-VA](#lingbot-va) | Released va_demo_cfg.py: shared 30x3072 DiT, 5 video + 10 action updates | Publication + released code |
| [LingBot-World-Fast](#lingbot-world-fast) | Released dense LingBot-World-Fast: 40x5120, 4 steps | Publication + released code |
| [Matrix-Game 2.0](#matrix-game-2) | Released 1.62B real-time student: 30x1536, 3 DMD steps | Publication + released code |
| [Matrix-Game 3.0](#matrix-game-3) | Released Wan2.2-based 30x3072 student with retrieved memory, 3 steps | Publication + released code |
| [Matrix-Game 3.5](#matrix-game-35) | Released 5B distilled causal rollout with reprojected patch memory | Publication + released code |
| [MineWorld](#mineworld) | 1.2B config: 20x2048 Llama-style decoder, diagonal sampling (weights withdrawn) | Publication + released code |
| [Navigation World Model (CDiT)](#nwm-cdit) | Released CDiT-XL/2: 28x1152, 250-step DDPM | Publication + released code |
| [Oasis](#oasis) | Released Oasis small DiT-S/2: 16 space-time pairs, 10 DDIM steps | Publication + released code |
| [RAP (Reasoning via Planning)](#rap) | Paper BlocksWorld RAP with frozen LLaMA-33B | Publication + released code |
| [REM](#rem) | Released 5x256 RetNet world model with parallel observation prediction | Publication + released code |
| [SANA-WM](#sana-wm) | Released stage-one 2.6B SANA-WM, 20 hybrid blocks, 4 distilled steps | Publication + released code |
| [Self Forcing](#self-forcing) | Released 1.3B Wan student: 30x1536, 4 DMD steps plus cache refresh | Publication + released code |
| [SlotFormer](#slotformer) | Released CLEVRER: 7 slots, width-256, 4-layer predictor | Publication + released code |
| [SOLD](#sold) | Released checkpoint (Reach-Red): 4 dynamics + 4 SAT layers, 0 registers | Publication + released code |
| [STORM](#storm) | Released STORM: 2x512 post-norm transformer, one latent/action token | Publication + released code |
| [Trajectory Transformer](#trajectory-transformer) | Released code defaults: 4-layer GPT; beam plan 128 × 2, horizon 15 | Publication + released code |
| [TransDreamer](#transdreamer) | Released Atari config: 6 layers, width 600, 8 heads of 64, h = all 6 layer outputs | Publication + released code |
| [TWISTER](#twister) | Released TWISTER: 4x512 post-norm temporal transformer | Publication + released code |
| [TWM](#twm) | Released TWM: 10x256 Transformer-XL, three tokens per step | Publication + released code |
| [UniZero](#unizero) | Released 2x768 pre-norm transformer with final LayerNorm | Publication + released code |
| [UVA (Unified Video Action)](#uva) | MAR-B (released code): 12 encoder + 12 decoder blocks; 16 action steps as on the robot (paper) | Publication + released code |
| [UWM (Unified World Models)](#uwm) | Released three-camera DROID configuration: 12x768, 10 DDIM steps | Publication + released code |
| [V-JEPA 2-AC](#vjepa2-ac) | Released 24x1024 action-conditioned predictor with frozen ViT-g | Publication + released code |
| [WHAM (Muse)](#wham) | Released WHAM-1.6B: 24x2304 GPT, 540 image + 16 action tokens | Publication + released code |
| [WorldPlay (HY-World 1.5)](#worldplay) | Released 480P distilled AR model: HY-1.5 8B, 54 blocks, 4 steps | Publication + released code |
| [WorldVLA](#worldvla) | Released Chameleon-based ~7B, 256×256 setting, two-frame input | Publication + released code |

## Per-model findings

### aapt

**AAPT — Paper: 8B, 36-block causal adversarial generator.** The VAE packs four frames per latent step. Noise, conditioning and the previous frame are concatenated by channel; projected text tokens join the sequence, and the diffusion timestep is a stated input whose injection point is undisclosed. The 36-block generator uses block-causal attention with a bounded latent-history cache and predicts one clean latent frame in one evaluation.

Checked: representation and token geometry; core operation order, normalization/modulation and residual boundaries where disclosed; conditioning entry points and attention masks; sampling repetitions, cache/feedback tensor and output/decoder role.

Corrections: Added the text-token join at the actual sequence input. Retained only the disclosed attention and an explicitly undisclosed remainder of the block. Added the stated diffusion-timestep input (Sec. 2.1) to the figure inputs and the Core fact; it is not drawn as a side box because its injection point is not disclosed.

Limits / differences: No matching official generator implementation was found in the consulted sources. Width, heads, patch geometry, internal norms, FFN and residual placement are not disclosed; none are supplied from a conventional DiT.

- [Original paper](https://arxiv.org/html/2506.09350v2)

### comma-wm

**comma.ai world model (openpilot 0.11) — Official openpilot 0.11 technical post: 2B, 15 Euler steps.** A ViT compressor produces a continuous latent per two-camera observation. The 48-layer, width-1600, 25-head DiT uses block-causal attention and AdaLN-single conditioned on pose, noise and frame index. Fifteen guided Euler updates generate the next latent before the ViT decoder.

Checked: representation and token geometry; core operation order, normalization/modulation and residual boundaries where disclosed; conditioning entry points and attention masks; sampling repetitions, cache/feedback tensor and output/decoder role.

Corrections: Added noise and frame-index conditioning. Routed rollout feedback from the updated latent to latent context, bypassing the image encoder.

Limits / differences: No matching public world-model implementation was found in the consulted sources. This is an official-page description, not a research-paper/code verification. The post does not disclose the full block or the cache-write schedule.

- [Original official page](https://blog.comma.ai/011release/)

### cosmos3

**Cosmos 3 — Nano generation (50 FM steps); reasoner text decoding not drawn.** Text and ViT tokens pass once through the reasoner, whose per-layer keys and values are cached. Clean video, audio and action conditioning is encoded by the Wan2.2 VAE, the audio VAE and per-embodiment action projections. In each of the 50 flow-matching steps the noisy DM tokens (plus timestep embedding) are packed with the clean DM tokens and the cached AR context, and pass through 36 generator-tower layers (RMSNorm, own QKV with 3D MRoPE, DM-to-AR+DM attention, own MLP), a final norm and the per-modality out-projections. Video latents go to the Wan2.2 VAE decoder, audio to the audio VAE decoder, and action tokens give the action chunk.

Checked: representation and token geometry; core operation order, normalization/modulation and residual boundaries where disclosed; conditioning entry points and attention masks; sampling repetitions, cache/feedback tensor and output/decoder role.

Corrections: Moved the reasoner and its cache outside the diffusion loop. Added the generator final norm/projection and removed a misleading post-diffusion text-generation head. Restored the clean DM conditioning lane (Wan2.2 VAE, audio VAE, action in-projection), the 'Pack AR + DM tokens' step with the 74,000-token training-context annotation, and audio output; moved all DM out-projections into the loop. Replaced the DROID 4-step annotation and policy output text with Nano-consistent ones, and stated in the variant and facts that reasoner text decoding is not drawn.

Limits / differences: The figure is the Nano 50-step generation path; the reasoner's next-token text decoding is not drawn. The DROID action policy is a separately post-trained checkpoint (4 steps, 32 actions, video decoding skipped) described only in the facts. Super and Edge configurations are outside this figure.

- [Original report](https://research.nvidia.com/labs/cosmos-lab/cosmos3/technical-report.pdf)
- [cosmos_framework/model/vfm/mot/cosmos3_vfm_network.py](https://github.com/NVIDIA/cosmos-framework/blob/300faa14daab3910be9d303c31708a0a1d6e4371/cosmos_framework/model/vfm/mot/cosmos3_vfm_network.py) — revision `300faa14daab3910be9d303c31708a0a1d6e4371`
- [cosmos_framework/model/vfm/mot/unified_mot.py](https://github.com/NVIDIA/cosmos-framework/blob/300faa14daab3910be9d303c31708a0a1d6e4371/cosmos_framework/model/vfm/mot/unified_mot.py) — revision `300faa14daab3910be9d303c31708a0a1d6e4371`
- [cosmos_framework/model/vfm/omni_mot_model.py](https://github.com/NVIDIA/cosmos-framework/blob/300faa14daab3910be9d303c31708a0a1d6e4371/cosmos_framework/model/vfm/omni_mot_model.py) — revision `300faa14daab3910be9d303c31708a0a1d6e4371`

### cosmos-policy

**Cosmos Policy — Released LIBERO policy: Predict2-2B, 28 blocks, 5 EDM steps.** Images, proprioception, actions, future state and value are represented in a common latent-frame layout. The 28-block backbone uses gated AdaLN residual branches for self-attention, text cross-attention and GELU FFN. The five-step policy produces actions directly; pixel decoding is only for visualization.

Checked: representation and token geometry; core operation order, normalization/modulation and residual boundaries where disclosed; conditioning entry points and attention masks; sampling repetitions, cache/feedback tensor and output/decoder role.

Corrections: Made all three modulation gates explicit. Labelled the 4.9 s best-of-8 search as the separate ALOHA planning-model setup (not drawn) in summary and facts, and labelled the 0.61 s annotation as LIBERO on one H100.

Limits / differences: The ten-step ALOHA setup and ensemble planning are separate configurations described in the facts. The diagram is the parallel LIBERO policy path.

- [Original paper](https://arxiv.org/html/2601.16163v1)
- [cosmos_policy/_src/predict2/networks/minimal_v4_dit.py](https://github.com/NVlabs/cosmos-policy/blob/18a2accadf4e7a3531e56754102af5a24d2316da/cosmos_policy/_src/predict2/networks/minimal_v4_dit.py) — revision `18a2accadf4e7a3531e56754102af5a24d2316da`
- [cosmos_policy/config/experiment/cosmos_policy_experiment_configs.py](https://github.com/NVlabs/cosmos-policy/blob/18a2accadf4e7a3531e56754102af5a24d2316da/cosmos_policy/config/experiment/cosmos_policy_experiment_configs.py) — revision `18a2accadf4e7a3531e56754102af5a24d2316da`
- [cosmos_policy/models/policy_video2world_model.py](https://github.com/NVlabs/cosmos-policy/blob/18a2accadf4e7a3531e56754102af5a24d2316da/cosmos_policy/models/policy_video2world_model.py) — revision `18a2accadf4e7a3531e56754102af5a24d2316da`

### cosmos-predict1-ar

**Cosmos-Predict1 (autoregressive) — Released 4B base: no text cross-attention; paper's per-block 3D APE is off in its code.** FSQ video codes enter a 16-layer Llama-style decoder with pre-RMSNorm, 3D RoPE, grouped-query attention, SwiGLU and a final RMSNorm. The released sampler generates one code at a time and feeds codes back into the embedding, then decodes complete latent frames.

Checked: representation and token geometry; core operation order, normalization/modulation and residual boundaries where disclosed; conditioning entry points and attention masks; sampling repetitions, cache/feedback tensor and output/decoder role.

Corrections: Replaced the incompatible 4B/12B/text-conditioned mixture with the 16-layer 4B base. Removed text cross-attention, absolute-position conditioning and the unreleased Medusa branch. Stated the paper/code 3D APE discrepancy in the figure variant and reworded the summary to lead with the drawn 4B base, labelling the Video2World T5 cross-attention and Medusa heads as not drawn.

Limits / differences: The paper also reports 12B, text-conditioned 5B/13B and Medusa experiments. Those are described separately; their speedups and attention paths do not belong to this released base graph.

- [Original paper](https://arxiv.org/html/2501.03575v3)
- [cosmos_predict1/autoregressive/configs/base/model.py](https://github.com/nvidia-cosmos/cosmos-predict1/blob/724daa1b2df5ec96bdf111bb947479d2216b3b08/cosmos_predict1/autoregressive/configs/base/model.py) — revision `724daa1b2df5ec96bdf111bb947479d2216b3b08`
- [cosmos_predict1/autoregressive/configs/base/tokenizer.py](https://github.com/nvidia-cosmos/cosmos-predict1/blob/724daa1b2df5ec96bdf111bb947479d2216b3b08/cosmos_predict1/autoregressive/configs/base/tokenizer.py) — revision `724daa1b2df5ec96bdf111bb947479d2216b3b08`
- [cosmos_predict1/autoregressive/model.py](https://github.com/nvidia-cosmos/cosmos-predict1/blob/724daa1b2df5ec96bdf111bb947479d2216b3b08/cosmos_predict1/autoregressive/model.py) — revision `724daa1b2df5ec96bdf111bb947479d2216b3b08`
- [cosmos_predict1/autoregressive/networks/transformer.py](https://github.com/nvidia-cosmos/cosmos-predict1/blob/724daa1b2df5ec96bdf111bb947479d2216b3b08/cosmos_predict1/autoregressive/networks/transformer.py) — revision `724daa1b2df5ec96bdf111bb947479d2216b3b08`

### cosmos-predict25

**Cosmos-Predict2.5 — Released 2B base Video2World: 28 blocks, 35 FlowUniPC steps, CFG 7 (2 passes/step).** Conditioning video is encoded by the Wan VAE. Every denoising call patchifies the current noisy clip and applies 28 gated AdaLN-LoRA self-attention/cross-attention/FFN blocks. The released base sampler performs 35 FlowUniPC steps with text guidance before decoding the clip.

Checked: representation and token geometry; core operation order, normalization/modulation and residual boundaries where disclosed; conditioning entry points and attention masks; sampling repetitions, cache/feedback tensor and output/decoder role.

Corrections: Used 35 base-model steps rather than mixing the four-step Text2World-only distilled checkpoint with conditioning video and base-model latency. Moved patchification into the denoising loop and exposed residual gates. Loop label and variant now show CFG 7 as two DiT passes per step (70 per clip); the summary marks the 4-step Text2World distilled checkpoint as not drawn.

Limits / differences: Paper Table 3 lists 32 layers, while the released 2B configuration/checkpoint uses 28. The paper calls its distillation rCM; the released four-step checkpoint uses a DMD2/TrigFlow configuration.

- [Original paper](https://arxiv.org/html/2511.00062v2)
- [cosmos_predict2/_src/predict2/configs/video2world/experiment/reason_embeddings/model_2B_reason_1p1_rectified_flow.py](https://github.com/nvidia-cosmos/cosmos-predict2.5/blob/a2c298b0a3df3778b973fe65e9e58877b292d8a7/cosmos_predict2/_src/predict2/configs/video2world/experiment/reason_embeddings/model_2B_reason_1p1_rectified_flow.py) — revision `a2c298b0a3df3778b973fe65e9e58877b292d8a7`
- [cosmos_predict2/_src/predict2/distill/configs/experiment/experiments_dmd2_predict2p5.py](https://github.com/nvidia-cosmos/cosmos-predict2.5/blob/a2c298b0a3df3778b973fe65e9e58877b292d8a7/cosmos_predict2/_src/predict2/distill/configs/experiment/experiments_dmd2_predict2p5.py) — revision `a2c298b0a3df3778b973fe65e9e58877b292d8a7`
- [cosmos_predict2/_src/predict2/networks/minimal_v4_dit.py](https://github.com/nvidia-cosmos/cosmos-predict2.5/blob/a2c298b0a3df3778b973fe65e9e58877b292d8a7/cosmos_predict2/_src/predict2/networks/minimal_v4_dit.py) — revision `a2c298b0a3df3778b973fe65e9e58877b292d8a7`

### cwm

**CWM (Code World Model) — Released dense 32B code world model.** A Llama-tokenized execution trace is processed by 64 pre-RMSNorm decoder blocks with grouped-query attention and SwiGLU. Layers alternate local and global attention windows in a 3:1 pattern; the fanout denotes a layer-type choice, not two attention computations in every layer. Text tokens are generated autoregressively.

Checked: representation and token geometry; core operation order, normalization/modulation and residual boundaries where disclosed; conditioning entry points and attention masks; sampling repetitions, cache/feedback tensor and output/decoder role.

Corrections: Routed generated tokens back to token embeddings.

Limits / differences: Trace text, rather than video or physical-state latents, is this model's observation representation. Window limits are from the released configuration.

- [Original paper](https://arxiv.org/html/2510.02387v1)
- [MODEL_CARD.md](https://github.com/facebookresearch/cwm/blob/7930e0298bf32aae28cc0e35e18a54c772603364/MODEL_CARD.md) — revision `7930e0298bf32aae28cc0e35e18a54c772603364`
- [cwm/fastgen/forward.py](https://github.com/facebookresearch/cwm/blob/7930e0298bf32aae28cc0e35e18a54c772603364/cwm/fastgen/forward.py) — revision `7930e0298bf32aae28cc0e35e18a54c772603364`
- [cwm/model/transformer.py](https://github.com/facebookresearch/cwm/blob/7930e0298bf32aae28cc0e35e18a54c772603364/cwm/model/transformer.py) — revision `7930e0298bf32aae28cc0e35e18a54c772603364`

### delta-iris

**Δ-IRIS — Released Crafter configuration: 3 layers, 4 delta codes per frame.** An action-conditioned delta tokenizer encodes frame changes; an auxiliary CNN supplies the current-frame I-token. The three-layer width-512 causal transformer uses learned positions, pre-LayerNorm residual blocks, GELU and a final LayerNorm. Four dependent delta-code predictions reconstruct the next frame.

Checked: representation and token geometry; core operation order, normalization/modulation and residual boundaries where disclosed; conditioning entry points and attention masks; sampling repetitions, cache/feedback tensor and output/decoder role.

Corrections: Added the learned position input and final LayerNorm. Feedback names the generated frame-to-I-token route rather than sending arbitrary decoder output into the delta encoder.

Limits / differences: Crafter uses a 126-token context; the Atari setup has a different 156-token context. The 25M count is for the agent, not just the transformer.

- [Original paper](https://arxiv.org/html/2406.19320v1)
- [config/params/crafter.yaml](https://github.com/vmicheli/delta-iris/blob/f8d417321717a3d7012488785d7cdc66b62455dd/config/params/crafter.yaml) — revision `f8d417321717a3d7012488785d7cdc66b62455dd`
- [src/envs/world_model_env.py](https://github.com/vmicheli/delta-iris/blob/f8d417321717a3d7012488785d7cdc66b62455dd/src/envs/world_model_env.py) — revision `f8d417321717a3d7012488785d7cdc66b62455dd`
- [src/models/transformer.py](https://github.com/vmicheli/delta-iris/blob/f8d417321717a3d7012488785d7cdc66b62455dd/src/models/transformer.py) — revision `f8d417321717a3d7012488785d7cdc66b62455dd`
- [src/models/world_model.py](https://github.com/vmicheli/delta-iris/blob/f8d417321717a3d7012488785d7cdc66b62455dd/src/models/world_model.py) — revision `f8d417321717a3d7012488785d7cdc66b62455dd`

### dino-wm

**DINO-WM — Released DINO-WM predictor: 6 layers, DINOv2 patch features.** Frozen DINOv2 yields 196 patch embeddings. Action and proprioception embeddings are concatenated to each patch feature; learned positions precede six pre-LayerNorm attention/MLP blocks and a final norm. Frame-causal masking allows within-frame patch attention. Predicted features enter subsequent latent rollout and CEM planning, without a pixel decoder.

Checked: representation and token geometry; core operation order, normalization/modulation and residual boundaries where disclosed; conditioning entry points and attention masks; sampling repetitions, cache/feedback tensor and output/decoder role.

Corrections: Added the learned positions and final norm. Routed predicted features directly into predictor history. The concat annotation and summary now state that the predictor token is 404 wide (384 visual + 10-d action + 10-d proprio), distinguishing it from the 384-wide DINOv2 features.

Limits / differences: Token width is 404 in the released configuration, including action/proprioception, rather than the 384-dimensional visual feature alone. Parameter totals vary with the configured history length.

- [Original paper](https://arxiv.org/html/2411.04983v2)
- [conf/predictor/vit.yaml](https://github.com/gaoyuezhou/dino_wm/blob/0a9492fa12044b852ae9e001cc74604b79c8bb0c/conf/predictor/vit.yaml) — revision `0a9492fa12044b852ae9e001cc74604b79c8bb0c`
- [conf/train.yaml](https://github.com/gaoyuezhou/dino_wm/blob/0a9492fa12044b852ae9e001cc74604b79c8bb0c/conf/train.yaml) — revision `0a9492fa12044b852ae9e001cc74604b79c8bb0c`
- [models/visual_world_model.py](https://github.com/gaoyuezhou/dino_wm/blob/0a9492fa12044b852ae9e001cc74604b79c8bb0c/models/visual_world_model.py) — revision `0a9492fa12044b852ae9e001cc74604b79c8bb0c`
- [models/vit.py](https://github.com/gaoyuezhou/dino_wm/blob/0a9492fa12044b852ae9e001cc74604b79c8bb0c/models/vit.py) — revision `0a9492fa12044b852ae9e001cc74604b79c8bb0c`

### dreamer4

**Dreamer 4 — Paper: 1.6B dynamics, 3 spatial layers per causal temporal layer.** A causal tokenizer provides continuous visual latents. Shortcut dynamics include noisy visual tokens, action/task tokens, learned register tokens and one shortcut token carrying the signal level and step size. The disclosed pre-RMSNorm/RoPE/SwiGLU design repeats three spatial layers and one causal temporal layer. Four shortcut steps generate latents; policy, reward and value heads read task representations.

Checked: representation and token geometry; core operation order, normalization/modulation and residual boundaries where disclosed; conditioning entry points and attention masks; sampling repetitions, cache/feedback tensor and output/decoder role.

Corrections: Added noisy-token and shortcut/register inputs. Kept latent feedback inside dynamics and removed an unsupported expanded FFN inset. Relabelled the shortcut side input from time to signal level + step size, as the paper uses (τ is separate from sequence time; the registers take no input).

Limits / differences: No matching official implementation was found in the consulted sources. Layer count, model width, head count and RoPE axes are not disclosed. The figure leaves the repeat count symbolic and does not borrow those values from another Dreamer.

- [Original paper](https://arxiv.org/html/2509.24527v1)

### dreamzero

**DreamZero — DreamZero-Flash (paper only, no released weights): Wan2.1-I2V-14B, one denoising step.** The 40-block Wan backbone jointly denoises video and actions with state/action projections. Gated AdaLN self-attention is chunk-causal; normalized cross-attention reads frozen text/image features. Real observations refresh the video-history cache. Video and action output projections are distinct, and action generation does not pass through the VAE decoder.

Checked: representation and token geometry; core operation order, normalization/modulation and residual boundaries where disclosed; conditioning entry points and attention masks; sampling repetitions, cache/feedback tensor and output/decoder role.

Corrections: Added self-attention/FFN gates and the released cross-attention norm. Selected the single-step Flash schedule corresponding to the displayed latency and removed an action-to-image-encoder feedback loop. Labelled DreamZero-Flash as a paper-only variant (released DROID/AgiBot checkpoints have the Flash flags off and sample 16 steps with velocity caching) in figure_variant, open, summary and the Prediction fact. The 150 ms annotation now names 2x GB200 + NVFP4. The closed loop through the robot (Fig. 4) is shown in the input text ('Real views per chunk') and the Memory fact, not as an action-to-cache tensor edge.

Limits / differences: The figure draws DreamZero-Flash (1 step), which has no released weights; the released checkpoints use the 16-step schedule with velocity caching (about 4 effective DiT passes). The 150 ms latency also requires NVFP4 and CFG split over 2 GB200. Token geometry (880 per latent frame) comes from the released checkpoint configs and assumes Flash shares the backbone, as the paper describes. The diagram covers tensor inference; executed robot actions and subsequent real observations form an external control loop.

- [Original paper](https://arxiv.org/html/2602.15922v1)
- [groot/vla/configs/model/dreamzero/action_head/wan_flow_matching_action_tf.yaml](https://github.com/dreamzero0/dreamzero/blob/ab790c198fbce33503358efbbd4187ce9a89adf3/groot/vla/configs/model/dreamzero/action_head/wan_flow_matching_action_tf.yaml) — revision `ab790c198fbce33503358efbbd4187ce9a89adf3`
- [groot/vla/model/dreamzero/action_head/wan_flow_matching_action_tf.py](https://github.com/dreamzero0/dreamzero/blob/ab790c198fbce33503358efbbd4187ce9a89adf3/groot/vla/model/dreamzero/action_head/wan_flow_matching_action_tf.py) — revision `ab790c198fbce33503358efbbd4187ce9a89adf3`
- [groot/vla/model/dreamzero/modules/wan_video_dit_action_casual_chunk.py](https://github.com/dreamzero0/dreamzero/blob/ab790c198fbce33503358efbbd4187ce9a89adf3/groot/vla/model/dreamzero/modules/wan_video_dit_action_casual_chunk.py) — revision `ab790c198fbce33503358efbbd4187ce9a89adf3`

### emerald

**EMERALD — Released 30M: 4 temporal blocks + 2 spatial MaskGIT blocks.** A CNN categorical VAE produces a 4x4 latent grid. A temporal action-conditioned transformer computes the history state, then a separate spatial MaskGIT transformer generates the next grid in three passes. Both released transformers use post-LayerNorm residual blocks with ReLU FFNs. Reward and continuation depend on latent/state features.

Checked: representation and token geometry; core operation order, normalization/modulation and residual boundaries where disclosed; conditioning entry points and attention masks; sampling repetitions, cache/feedback tensor and output/decoder role.

Limits / differences: The temporal and spatial stacks have different widths, 512 and 256. The three-pass loop applies only to the spatial predictor, not the temporal history model.

- [Original paper](https://arxiv.org/html/2507.04075v2)
- [nnet/models/emerald.py](https://github.com/burchim/EMERALD/blob/665948d8cd619ccc960abe54ffdfc785ce95f18b/nnet/models/emerald.py) — revision `665948d8cd619ccc960abe54ffdfc785ce95f18b`
- [nnet/modules/emerald/mask_network.py](https://github.com/burchim/EMERALD/blob/665948d8cd619ccc960abe54ffdfc785ce95f18b/nnet/modules/emerald/mask_network.py) — revision `665948d8cd619ccc960abe54ffdfc785ce95f18b`
- [nnet/modules/emerald/tssm.py](https://github.com/burchim/EMERALD/blob/665948d8cd619ccc960abe54ffdfc785ce95f18b/nnet/modules/emerald/tssm.py) — revision `665948d8cd619ccc960abe54ffdfc785ce95f18b`
- [nnet/modules/modules/attention_module.py](https://github.com/burchim/EMERALD/blob/665948d8cd619ccc960abe54ffdfc785ce95f18b/nnet/modules/modules/attention_module.py) — revision `665948d8cd619ccc960abe54ffdfc785ce95f18b`

### fast-wam

**Fast-WAM — Released Fast-WAM policy: cached first-frame video K/V, 10 action steps.** The Wan2.2-5B video branch processes the clean first observation once. Its per-layer keys/values condition a width-1024 action expert over ten denoising steps. Each expert block has gated adaptive self-attention/FFN residuals and normalized T5 cross-attention. The structured attention mask excludes future video from action queries.

Checked: representation and token geometry; core operation order, normalization/modulation and residual boundaries where disclosed; conditioning entry points and attention masks; sampling repetitions, cache/feedback tensor and output/decoder role.

Corrections: Expanded the actual action-expert block, added gates and its velocity head, and kept the video pass outside the action loop. Added the official code link. Drew the video-DiT inset with the same code-level DiTBlock residuals (AdaLN at timestep 0, gates, LayerNorm cross-attention) as the action block, and cited wan_video_dit.py and action_dit.py in the Core fact and sources.

Limits / differences: The paper specifies logit-normal training noise; released training code uses shift-warped uniform noise. The slower imagine-then-execute IDM variant is not this path. Proprioception is included in the text/context representation.

- [Original paper](https://arxiv.org/html/2603.16666v2)
- [configs/model/fastwam.yaml](https://github.com/yuantianyuan01/FastWAM/blob/7faa71108368fbb3b6885649f112af607427a2d4/configs/model/fastwam.yaml) — revision `7faa71108368fbb3b6885649f112af607427a2d4`
- [src/fastwam/models/wan22/fastwam.py](https://github.com/yuantianyuan01/FastWAM/blob/7faa71108368fbb3b6885649f112af607427a2d4/src/fastwam/models/wan22/fastwam.py) — revision `7faa71108368fbb3b6885649f112af607427a2d4`
- [src/fastwam/models/wan22/mot.py](https://github.com/yuantianyuan01/FastWAM/blob/7faa71108368fbb3b6885649f112af607427a2d4/src/fastwam/models/wan22/mot.py) — revision `7faa71108368fbb3b6885649f112af607427a2d4`
- [src/fastwam/models/wan22/wan_video_dit.py](https://github.com/yuantianyuan01/FastWAM/blob/7faa71108368fbb3b6885649f112af607427a2d4/src/fastwam/models/wan22/wan_video_dit.py) — revision `7faa71108368fbb3b6885649f112af607427a2d4`

### gaia1

**GAIA-1 — Paper: 6.5B autoregressive world model and separate video decoder.** A DINO-distilled image tokenizer provides 576 discrete codes per frame. Text, image and action tokens are interleaved with space-time positions, then processed causally. Image codes are sampled serially. The separate video diffusion decoder produces pixels; it is not the autoregressive world-model transformer.

Checked: representation and token geometry; core operation order, normalization/modulation and residual boundaries where disclosed; conditioning entry points and attention masks; sampling repetitions, cache/feedback tensor and output/decoder role.

Limits / differences: No matching official implementation was found in the consulted sources. The report does not specify transformer layer/head counts, internal norms/FFN/residual boundaries or a KV-cache policy. Those details remain undisclosed.

- [Original paper](https://arxiv.org/html/2309.17080v1)

### gaia2

**GAIA-2 — Paper: 8.4B, 22 factorized space-time blocks, 50 flow steps.** The video tokenizer compresses multi-camera footage. Each disclosed block adds positions/camera information, performs spatial/camera attention, temporal attention, cross-attention to agent metadata, then adaptive normalization and an MLP. Fifty flow updates generate a latent window; rollout appends latents and slides context.

Checked: representation and token geometry; core operation order, normalization/modulation and residual boundaries where disclosed; conditioning entry points and attention masks; sampling repetitions, cache/feedback tensor and output/decoder role.

Corrections: Routed rollout feedback between the latent update and latent context.

Limits / differences: No matching official implementation was found in the consulted sources. The report does not locate every normalization or disclose residual wiring, so the figure adds neither. No KV cache is claimed.

- [Original paper](https://arxiv.org/html/2503.20523v1)

### ge-act

**Genie Envisioner (GE-Act) — Released GE-Base video cache + GE-Act 160M action decoder.** A 28-block LTX-derived video model uses per-view attention, selected cross-view attention and text cross-attention. View/timestep modulation gates self-attention and FFN branches. GE-Act caches the video model's per-block states and cross-attends to them during five action steps, enabling asynchronous video and action rates.

Checked: representation and token geometry; core operation order, normalization/modulation and residual boundaries where disclosed; conditioning entry points and attention masks; sampling repetitions, cache/feedback tensor and output/decoder role.

Corrections: Added both video/action modulation gates. Removed a misleading action-output-to-video-encoder loop and added the official code link. The closed loop (Sec. 3.1) is now stated in the input text ('Live views') and in the Prediction fact, with no action-to-encoder tensor edge.

Limits / differences: The paper names 2D RoPE; released code computes 3D latent-frame/height/width RoPE. Released sparse memory contains three earlier observations plus the current frame. The external robot feedback loop is not a direct tensor edge.

- [Original paper](https://arxiv.org/html/2508.05635v3)
- [configs/ltx_model/policy_model.yaml](https://github.com/AgibotTech/Genie-Envisioner-V1/blob/d41358f7548f2cd9fc4b79fcdf7d86d15a8d7b1e/configs/ltx_model/policy_model.yaml) — revision `d41358f7548f2cd9fc4b79fcdf7d86d15a8d7b1e`
- [models/action_patches/patches.py](https://github.com/AgibotTech/Genie-Envisioner-V1/blob/d41358f7548f2cd9fc4b79fcdf7d86d15a8d7b1e/models/action_patches/patches.py) — revision `d41358f7548f2cd9fc4b79fcdf7d86d15a8d7b1e`
- [models/ltx_models/transformer_ltx_multiview.py](https://github.com/AgibotTech/Genie-Envisioner-V1/blob/d41358f7548f2cd9fc4b79fcdf7d86d15a8d7b1e/models/ltx_models/transformer_ltx_multiview.py) — revision `d41358f7548f2cd9fc4b79fcdf7d86d15a8d7b1e`

### genie

**Genie — Paper: 10.1B dynamics (num_layers 48), 25 MaskGIT passes.** The ST tokenizer produces frame codes; a learned latent action is added to the masked target frame-token embeddings. The dynamics stack applies spatial attention, causal temporal attention and FFN. Twenty-five MaskGIT passes complete each next frame before tokenizer decoding. The latent-action model supplies eight discrete actions.

Checked: representation and token geometry; core operation order, normalization/modulation and residual boundaries where disclosed; conditioning entry points and attention masks; sampling repetitions, cache/feedback tensor and output/decoder role.

Corrections: Placed action embedding after construction of the masked target tokens and inside each dynamics evaluation. Set the disclosed 48-layer repeat and causal temporal label. Restored the symbolic 'L ×' block repeat: Table 12's num_layers 48 is not said to count ST blocks, and 48 full ST blocks at d 5120 would far exceed 10.1B. The 48 is kept as a labelled num_layers annotation and in the variant.

Limits / differences: No matching official implementation was found in the consulted sources. Norm/residual internals are not disclosed and are not filled in. Public reproductions are not treated as original code. Table 12 gives num_layers 48 but the paper never says whether this counts ST blocks or attention layers; the figure keeps the block repeat symbolic (L).

- [Original paper](https://arxiv.org/html/2402.15391v1)

### hunyuan-gamecraft

**Hunyuan-GameCraft — Released HunyuanVideo GameCraft: 20 double + 40 single blocks, 8 PCM steps.** Noisy video and history/mask channels are patchified and combined with camera Pluecker features. Twenty double-stream text/video blocks precede forty single-stream blocks, whose attention and MLP branches run in parallel. Eight consistency-model updates produce a chunk, whose latents become subsequent history.

Checked: representation and token geometry; core operation order, normalization/modulation and residual boundaries where disclosed; conditioning entry points and attention masks; sampling repetitions, cache/feedback tensor and output/decoder role.

Corrections: Routed chunk-latent feedback directly to latent history.

Limits / differences: The double-stream boxes encapsulate each modality's normalization, modulation, QKV and output projections; the single-stream residual boundary is expanded. The paper's 13B designation comes from the HunyuanVideo backbone.

- [Original paper](https://arxiv.org/html/2506.17201v1)
- [hymm_sp/config.py](https://github.com/Tencent-Hunyuan/Hunyuan-GameCraft-1.0/blob/9a35ecf495a1b97b4929524fff442481069ecdc2/hymm_sp/config.py) — revision `9a35ecf495a1b97b4929524fff442481069ecdc2`
- [hymm_sp/modules/models.py](https://github.com/Tencent-Hunyuan/Hunyuan-GameCraft-1.0/blob/9a35ecf495a1b97b4929524fff442481069ecdc2/hymm_sp/modules/models.py) — revision `9a35ecf495a1b97b4929524fff442481069ecdc2`
- [hymm_sp/sample_inference.py](https://github.com/Tencent-Hunyuan/Hunyuan-GameCraft-1.0/blob/9a35ecf495a1b97b4929524fff442481069ecdc2/hymm_sp/sample_inference.py) — revision `9a35ecf495a1b97b4929524fff442481069ecdc2`

### iris

**IRIS — Released Atari IRIS: 10x256 transformer, 16 image codes.** A VQ-VAE maps a frame to sixteen codes. Learned positions enter a ten-layer pre-LayerNorm causal decoder with a final LayerNorm. Code, reward and termination heads operate at their assigned sequence positions; sixteen code predictions plus the action-position evaluation advance a frame. Generated codes remain in token context.

Checked: representation and token geometry; core operation order, normalization/modulation and residual boundaries where disclosed; conditioning entry points and attention masks; sampling repetitions, cache/feedback tensor and output/decoder role.

Corrections: Corrected the world-model/whole-agent parameter distinction and made cache precision arithmetic explicit. Fixed code feedback to token embeddings. The params field now gives the drawn world model (≈8.45M) and labels ~30M as the whole-agent total.

Limits / differences: The roughly 30M agent total includes a frozen LPIPS loss network; the world model is about 8.45M. FP16 cache sizes are arithmetic, not evidence that the released FP32 runtime uses FP16.

- [Original paper](https://arxiv.org/html/2209.00588v2)
- [config/world_model/default.yaml](https://github.com/eloialonso/iris/blob/24326aaaa283c527f42b89b44cfdecf2665a7a16/config/world_model/default.yaml) — revision `24326aaaa283c527f42b89b44cfdecf2665a7a16`
- [src/envs/world_model_env.py](https://github.com/eloialonso/iris/blob/24326aaaa283c527f42b89b44cfdecf2665a7a16/src/envs/world_model_env.py) — revision `24326aaaa283c527f42b89b44cfdecf2665a7a16`
- [src/models/transformer.py](https://github.com/eloialonso/iris/blob/24326aaaa283c527f42b89b44cfdecf2665a7a16/src/models/transformer.py) — revision `24326aaaa283c527f42b89b44cfdecf2665a7a16`
- [src/models/world_model.py](https://github.com/eloialonso/iris/blob/24326aaaa283c527f42b89b44cfdecf2665a7a16/src/models/world_model.py) — revision `24326aaaa283c527f42b89b44cfdecf2665a7a16`

### ivideogpt

**iVideoGPT — Released 138M Llama-style predictor with compressive tokenizer.** Two context frames retain 256 codes each; predicted frames use sixteen compressed codes conditioned on context features. The twelve-layer width-768 Llama-style transformer has RoPE, RMSNorm, SwiGLU and a final RMSNorm. Slot/action tokens and the next-code head support seventeen calls per predicted frame; a reward head supports control.

Checked: representation and token geometry; core operation order, normalization/modulation and residual boundaries where disclosed; conditioning entry points and attention masks; sampling repetitions, cache/feedback tensor and output/decoder role.

Corrections: Added the final RMSNorm and routed sampled codes back into the token sequence.

Limits / differences: The 436M scaling run has a different 24-layer configuration. Context compression belongs to the tokenizer, not to a shrinking transformer KV head.

- [Original paper](https://arxiv.org/html/2405.15223v3)
- [dependencies/modeling_llama.py](https://github.com/huggingface/transformers/blob/092f1fdaa4224fdd88c616dc9678e6fcb37bfffd/src/transformers/models/llama/modeling_llama.py) — revision `092f1fdaa4224fdd88c616dc9678e6fcb37bfffd`
- [ivideogpt/transformer/action_model.py](https://github.com/thuml/iVideoGPT/blob/d601d5cac9e96c6aa0c17cb37ed6a7c7ca1fb210/ivideogpt/transformer/action_model.py) — revision `d601d5cac9e96c6aa0c17cb37ed6a7c7ca1fb210`
- [mbrl/video_predictor.py](https://github.com/thuml/iVideoGPT/blob/d601d5cac9e96c6aa0c17cb37ed6a7c7ca1fb210/mbrl/video_predictor.py) — revision `d601d5cac9e96c6aa0c17cb37ed6a7c7ca1fb210`
- [train_gpt.py](https://github.com/thuml/iVideoGPT/blob/d601d5cac9e96c6aa0c17cb37ed6a7c7ca1fb210/train_gpt.py) — revision `d601d5cac9e96c6aa0c17cb37ed6a7c7ca1fb210`

### jowa

**JOWA — Released JOWA-150M: 12x768, task-conditioned GPT.** VQ codes receive token, position and task embeddings. Twelve pre-LayerNorm causal GPT blocks plus a final LayerNorm produce next-code, reward, termination and Q heads. The released world-model environment samples the next code from the categorical by default (mode only when sampling is disabled); Q-based planning uses the learned world model without turning the Q head into an image decoder.

Checked: representation and token geometry; core operation order, normalization/modulation and residual boundaries where disclosed; conditioning entry points and attention masks; sampling repetitions, cache/feedback tensor and output/decoder role.

Corrections: Added the final LayerNorm and fixed token feedback. Replaced the 'argmax' code-selection box with sampling, matching the released world_model_env default (should_sample=True; mode only otherwise).

Limits / differences: The 70M and 40M models use different layer/width counts. The figure is specifically the 150M variant.

- [Original paper](https://arxiv.org/html/2410.00564v4)
- [config/transformer/JOWA_150M.yaml](https://github.com/CJReinforce/JOWA/blob/8cb02c5e6768a948c566a9012ac8a4fc420c6970/config/transformer/JOWA_150M.yaml) — revision `8cb02c5e6768a948c566a9012ac8a4fc420c6970`
- [src/envs/world_model_env.py](https://github.com/CJReinforce/JOWA/blob/8cb02c5e6768a948c566a9012ac8a4fc420c6970/src/envs/world_model_env.py) — revision `8cb02c5e6768a948c566a9012ac8a4fc420c6970`
- [src/models/jowa_model.py](https://github.com/CJReinforce/JOWA/blob/8cb02c5e6768a948c566a9012ac8a4fc420c6970/src/models/jowa_model.py) — revision `8cb02c5e6768a948c566a9012ac8a4fc420c6970`
- [src/models/transformer.py](https://github.com/CJReinforce/JOWA/blob/8cb02c5e6768a948c566a9012ac8a4fc420c6970/src/models/transformer.py) — revision `8cb02c5e6768a948c566a9012ac8a4fc420c6970`

### lc-ssm

**Long-Context SSM World Model — Paper: 200M block-wise SSM/local-attention denoiser.** Spatial-major latent tokens pass through an AdaLN-conditioned Mamba scan, frame-local attention, and FFN, each with its own gated residual. Recurrent state is maintained per spatial scan block and frame-local attention keeps a KV cache of the previous k = 10 frames. Frames are generated autoregressively one at a time: each denoised latent frame re-enters the token sequence as clean context. The original block figure, rather than a generic transformer template, determines this order.

Checked: representation and token geometry; core operation order, normalization/modulation and residual boundaries where disclosed; conditioning entry points and attention masks; sampling repetitions, cache/feedback tensor and output/decoder role.

Corrections: Removed an invented serial KV/state-output operation and an unsupported final-frame decoder path. The endpoint now identifies a denoiser output with an unspecified sampler. Restored the stated one-frame-at-a-time autoregressive loop in latent space (denoised frame back to the token sequence as clean context) and the 'next frame; decoder not described' output. Moved the 10-frame KV cache annotation to frame-local attention and kept the per-scan-block SSM state on the scan.

Limits / differences: No matching official implementation was found in the consulted sources. Layer count, width, detailed VAE and sampling algorithm are undisclosed; no complete deployed frame-generation pipeline can be verified. A spatial scan block is not a transformer layer.

- [Original paper](https://arxiv.org/html/2505.20171v1)

### lewm

**LeWorldModel (LeWM) — Released LeWM: ViT-Tiny encoder + 6-layer predictor.** A projected ViT-Tiny CLS embedding gives one token per frame. Action-conditioned, zero-initialized AdaLN and internal LayerNorms precede causal attention/MLP operations, whose outputs are gated before addition. Six predictor layers, a final LayerNorm and a projector predict the next embedding. Planning uses embeddings without decoding pixels.

Checked: representation and token geometry; core operation order, normalization/modulation and residual boundaries where disclosed; conditioning entry points and attention masks; sampling repetitions, cache/feedback tensor and output/decoder role.

Corrections: Added the internal attention/FFN norms, gates and final norm. Routed predicted embeddings directly to predictor history. Dropped the unsourced word 'small' from the figure variant.

Limits / differences: The paper's 15M and released roughly 18M totals differ. The released TwoRoom configuration uses three history tokens, while the paper describes one. Sixteen 64-wide attention heads do not imply the residual token width is 1024; it remains 192.

- [Original paper](https://arxiv.org/html/2603.19312v3)
- [config/train/model/lewm.yaml](https://github.com/lucas-maes/le-wm/blob/8edfeb336732b5f3ce7b8b210d0ba370a09e2cac/config/train/model/lewm.yaml) — revision `8edfeb336732b5f3ce7b8b210d0ba370a09e2cac`
- [jepa.py](https://github.com/lucas-maes/le-wm/blob/8edfeb336732b5f3ce7b8b210d0ba370a09e2cac/jepa.py) — revision `8edfeb336732b5f3ce7b8b210d0ba370a09e2cac`
- [module.py](https://github.com/lucas-maes/le-wm/blob/8edfeb336732b5f3ce7b8b210d0ba370a09e2cac/module.py) — revision `8edfeb336732b5f3ce7b8b210d0ba370a09e2cac`

### lingbot-va

**LingBot-VA — Released va_demo_cfg.py: shared 30x3072 DiT, 5 video + 10 action updates.** The released video and action modes use one shared 30-block Wan list (width 3072) with separate modality input/output projections and timestep embedders; each block has gated AdaLN self-attention over a chunk-causal KV cache, LayerNorm text cross-attention and a gated AdaLN GELU FFN. Per chunk the demo runs 5 video Euler steps and 10 action Euler steps, each stage ending with a t=0 pass that caches the predicted chunk; after execution, the server VAE-encodes the real frames, embeds the executed state/actions, discards the predicted entries and writes real K/V with two more passes.

Checked: representation and token geometry; core operation order, normalization/modulation and residual boundaries where disclosed; conditioning entry points and attention masks; sampling repetitions, cache/feedback tensor and output/decoder role.

Corrections: Replaced the paper-only dual-tower graph with the released shared-weight graph. Corrected demo token geometry, 32-action horizon and sampling schedule; removed direct action-to-image feedback. Three freshly downloaded checkpoint headers confirm 841 tensors totaling 5,089,465,566 parameters. Replaced the 'clean cache pass' wording with t=0 passes that cache predicted chunks, and restored the per-chunk real-observation cache write (2 passes, update_cache=2) as a main-flow box with an 'executed actions' feedback route; the VAE no longer feeds the noisy-latent path. Restored the per-chunk pass count, the shared-backbone-only release qualifier and the paper's 5.3B/12.5 Hz/noisy-history facts as labelled contrasts.

Limits / differences: The paper specifies separate 3072-wide video and 768-wide action towers (5.3B), 192 video tokens and a three-step partial-video schedule. The demo instead uses one 3072-wide backbone, 128 tokens per latent frame, five video steps and ten action steps. Paper latency is not assigned to this configuration. The real-observation cache write runs only in server mode when the client sends compute_kv_cache; the offline generate() demo never receives real frames and keeps the predicted cache entries.

- [Original paper](https://arxiv.org/html/2601.21998v2)
- [hf_transformer_config.json](https://huggingface.co/robbyant/lingbot-va-base/blob/68b7bc1b35da6ddc67ea94c4ceb58d768fbb3f9c/transformer/config.json) — revision `68b7bc1b35da6ddc67ea94c4ceb58d768fbb3f9c`
- [wan_va/configs/shared_config.py](https://github.com/robbyant/lingbot-va/blob/7c6ffa9bfc4b83582cafc860fab4c82cc7deeeeb/wan_va/configs/shared_config.py) — revision `7c6ffa9bfc4b83582cafc860fab4c82cc7deeeeb`
- [wan_va/configs/va_demo_cfg.py](https://github.com/robbyant/lingbot-va/blob/7c6ffa9bfc4b83582cafc860fab4c82cc7deeeeb/wan_va/configs/va_demo_cfg.py) — revision `7c6ffa9bfc4b83582cafc860fab4c82cc7deeeeb`
- [wan_va/modules/model.py](https://github.com/robbyant/lingbot-va/blob/7c6ffa9bfc4b83582cafc860fab4c82cc7deeeeb/wan_va/modules/model.py) — revision `7c6ffa9bfc4b83582cafc860fab4c82cc7deeeeb`
- [wan_va/modules/utils.py](https://github.com/robbyant/lingbot-va/blob/7c6ffa9bfc4b83582cafc860fab4c82cc7deeeeb/wan_va/modules/utils.py) — revision `7c6ffa9bfc4b83582cafc860fab4c82cc7deeeeb`
- [wan_va/wan_va_server.py](https://github.com/robbyant/lingbot-va/blob/7c6ffa9bfc4b83582cafc860fab4c82cc7deeeeb/wan_va/wan_va_server.py) — revision `7c6ffa9bfc4b83582cafc860fab4c82cc7deeeeb`
- [checkpoint_header_1.json](https://huggingface.co/robbyant/lingbot-va-base/blob/68b7bc1b35da6ddc67ea94c4ceb58d768fbb3f9c/transformer/diffusion_pytorch_model-00001-of-00003.safetensors) — revision `68b7bc1b35da6ddc67ea94c4ceb58d768fbb3f9c`
- [checkpoint_header_2.json](https://huggingface.co/robbyant/lingbot-va-base/blob/68b7bc1b35da6ddc67ea94c4ceb58d768fbb3f9c/transformer/diffusion_pytorch_model-00002-of-00003.safetensors) — revision `68b7bc1b35da6ddc67ea94c4ceb58d768fbb3f9c`
- [checkpoint_header_3.json](https://huggingface.co/robbyant/lingbot-va-base/blob/68b7bc1b35da6ddc67ea94c4ceb58d768fbb3f9c/transformer/diffusion_pytorch_model-00003-of-00003.safetensors) — revision `68b7bc1b35da6ddc67ea94c4ceb58d768fbb3f9c`

### lingbot-world-fast

**LingBot-World-Fast — Released dense LingBot-World-Fast: 40x5120, 4 steps.** A dense Wan2.2-derived backbone uses chunk-causal self-attention, per-block camera scale/shift, normalized text cross-attention and a gated FFN. Four distilled updates generate a chunk, then a separate cache-write pass makes its keys/values available to later chunks. The released camera modules increase the parameter count beyond the nominal 14B backbone.

Checked: representation and token geometry; core operation order, normalization/modulation and residual boundaries where disclosed; conditioning entry points and attention masks; sampling repetitions, cache/feedback tensor and output/decoder role.

Corrections: Added gates/cross-attention norm and routed cache feedback to attention. Recomputed the displayed per-chunk BF16 cache as 3.83 GB from this model's dimensions. Restored WorldKV's stated figures (3.4 GB per chunk, >200 GB per minute, Sec. 4.3) in the KV annotation and summary. Our BF16 count (≈3.83 GB) is kept as a labelled [D] contrast in the summary and Memory fact.

Limits / differences: The 3.4 GB per chunk and >200 GB per minute are WorldKV's stated figures for this model; our BF16 count (≈3.83 GB per chunk) differs and is labelled [D], not a runtime measurement. The figure covers the dense fast student, not the two-expert middle-training model.

- [Original paper](https://arxiv.org/html/2601.20540v1)
- [README.md](https://github.com/robbyant/lingbot-world/blob/a43bec7f8091c83e9b30b16b912f6fc906236fa6/README.md) — revision `a43bec7f8091c83e9b30b16b912f6fc906236fa6`
- [wan/configs/wan_i2v_A14B.py](https://github.com/robbyant/lingbot-world/blob/a43bec7f8091c83e9b30b16b912f6fc906236fa6/wan/configs/wan_i2v_A14B.py) — revision `a43bec7f8091c83e9b30b16b912f6fc906236fa6`
- [wan/modules/model.py](https://github.com/robbyant/lingbot-world/blob/a43bec7f8091c83e9b30b16b912f6fc906236fa6/wan/modules/model.py) — revision `a43bec7f8091c83e9b30b16b912f6fc906236fa6`

### matrix-game-2

**Matrix-Game 2.0 — Released 1.62B real-time student: 30x1536, 3 DMD steps.** Reference latents/mask condition patchification; gated chunk-causal self-attention is followed by normalized first-frame CLIP cross-attention, an action module in the first fifteen blocks, and a gated FFN. Three denoising steps precede a cache-write pass. The action module implements its own residual additions.

Checked: representation and token geometry; core operation order, normalization/modulation and residual boundaries where disclosed; conditioning entry points and attention masks; sampling repetitions, cache/feedback tensor and output/decoder role.

Corrections: Added explicit modulation gates and the cross-attention norm. Removed the extra outer action-module residual, which duplicated the residual already implemented inside that module. Fixed cache feedback. Evidence 'verified' could not be restored: the current wmgallery/registry.py EVIDENCE accepts only 'read' and 'claim', so the card stays 'read' until the registry is changed. The facts are unchanged since the 2026-10-23 three-vote check.

Limits / differences: The nominal foundation-model size and the real-time checkpoint size differ. The action-module box is active only in the first fifteen of thirty blocks, as stated in the annotation/facts.

- [Original paper](https://arxiv.org/html/2508.13009v5)
- [Matrix-Game-2/README.md](https://github.com/SkyworkAI/Matrix-Game/blob/c7a88bfc039cd97695082484986e95b962390676/Matrix-Game-2/README.md) — revision `c7a88bfc039cd97695082484986e95b962390676`
- [Matrix-Game-2/wan/modules/action_module.py](https://github.com/SkyworkAI/Matrix-Game/blob/c7a88bfc039cd97695082484986e95b962390676/Matrix-Game-2/wan/modules/action_module.py) — revision `c7a88bfc039cd97695082484986e95b962390676`
- [Matrix-Game-2/wan/modules/causal_model.py](https://github.com/SkyworkAI/Matrix-Game/blob/c7a88bfc039cd97695082484986e95b962390676/Matrix-Game-2/wan/modules/causal_model.py) — revision `c7a88bfc039cd97695082484986e95b962390676`

### matrix-game-3

**Matrix-Game 3.0 — Released Wan2.2-based 30x3072 student with retrieved memory, 3 steps.** Camera-aware retrieval supplies memory to bidirectional video attention with perturbed positions. Camera scale/shift, text cross-attention and first-fifteen-block action modules supplement the Wan backbone. The released cross-attention path normalizes the tensor before saving its residual input; action modules retain their own residuals.

Checked: representation and token geometry; core operation order, normalization/modulation and residual boundaries where disclosed; conditioning entry points and attention masks; sampling repetitions, cache/feedback tensor and output/decoder role.

Corrections: Moved the cross-attention LayerNorm outside its residual boundary to match the actual forward expression. Removed an extra action-module residual, exposed modulation gates and routed latents to memory context.

Limits / differences: The nominal 5B label excludes added camera/action modules; the released checkpoint is roughly 6.5B. The separate 28B MoE scale-up is not drawn.

- [Original paper](https://arxiv.org/html/2604.08995v3)
- [Matrix-Game-3/README.md](https://github.com/SkyworkAI/Matrix-Game/blob/c7a88bfc039cd97695082484986e95b962390676/Matrix-Game-3/README.md) — revision `c7a88bfc039cd97695082484986e95b962390676`
- [Matrix-Game-3/wan/modules/action_module.py](https://github.com/SkyworkAI/Matrix-Game/blob/c7a88bfc039cd97695082484986e95b962390676/Matrix-Game-3/wan/modules/action_module.py) — revision `c7a88bfc039cd97695082484986e95b962390676`
- [Matrix-Game-3/wan/modules/model.py](https://github.com/SkyworkAI/Matrix-Game/blob/c7a88bfc039cd97695082484986e95b962390676/Matrix-Game-3/wan/modules/model.py) — revision `c7a88bfc039cd97695082484986e95b962390676`

### matrix-game-35

**Matrix-Game 3.5 — Released 5B distilled causal rollout with reprojected patch memory.** Depth/pose reprojects selected historical patches into reference memory. The 30-block Wan model applies gated causal self-attention using RoPE plus tiled PRoPE, normalized text cross-attention and a gated FFN. Three DMD steps update each chunk; a clean t = 0 cache-fill pass then writes the chunk's keys/values into the rolling KV window that later chunks attend to, and decoded frames feed the patch memory.

Checked: representation and token geometry; core operation order, normalization/modulation and residual boundaries where disclosed; conditioning entry points and attention masks; sampling repetitions, cache/feedback tensor and output/decoder role.

Corrections: Added gates and the released cross-attention norm. Fixed latent feedback to the sequence rather than the image encoder. Replaced the 'chunk context' feedback into the token sequence with a 'Write chunk to KV cache' box and a 'rolling K/V' feedback into attention, matching the released cache-fill pass (causal_rollout.py L2120-2170). Moved the tiled-PRoPE inset to the block and merged the layer/head annotations so the route crosses nothing.

Limits / differences: Chunk/window settings refer to the released distilled six-block rollout configuration. First-chunk temporal padding and special cache handling are implementation details beyond this steady-state schematic.

- [Original paper](https://arxiv.org/html/2608.29910v1)
- [configs/infer_distilled_6blocks.yaml](https://github.com/Riemann-Dynamics/Matrix-Game-3.5/blob/fbf7def0693ae14f745ba35bf2a26215d4ef991d/configs/infer_distilled_6blocks.yaml) — revision `fbf7def0693ae14f745ba35bf2a26215d4ef991d`
- [diffsynth/models/wan_video_dit.py](https://github.com/Riemann-Dynamics/Matrix-Game-3.5/blob/fbf7def0693ae14f745ba35bf2a26215d4ef991d/diffsynth/models/wan_video_dit.py) — revision `fbf7def0693ae14f745ba35bf2a26215d4ef991d`
- [examples/wanvideo/pipeline/mosaic/causal_rollout.py](https://github.com/Riemann-Dynamics/Matrix-Game-3.5/blob/fbf7def0693ae14f745ba35bf2a26215d4ef991d/examples/wanvideo/pipeline/mosaic/causal_rollout.py) — revision `fbf7def0693ae14f745ba35bf2a26215d4ef991d`

### mineworld

**MineWorld — 1.2B config: 20x2048 Llama-style decoder, diagonal sampling (weights withdrawn).** A VQ-VAE maps each image to 336 codes, interleaved with eleven action tokens. The twenty-layer predictor uses pre-RMSNorm, RoPE, grouped-query attention and SwiGLU. A final norm and output logits support anti-diagonal parallel image sampling, reducing a frame to 37 dependent sampling rounds at k = 1 (50 at the released code's default k = 2).

Checked: representation and token geometry; core operation order, normalization/modulation and residual boundaries where disclosed; conditioning entry points and attention masks; sampling repetitions, cache/feedback tensor and output/decoder role.

Corrections: Corrected the FFN label to SwiGLU and added final RMSNorm/output logits. Routed generated codes back to embeddings. The variant now says the 1.2B configuration with weights withdrawn, not 'released'; the sampling annotation labels 37 passes as k = 1 and gives the code-default k = 2 count (50).

Limits / differences: The 300M and 700M variants use different widths/FFNs. Anti-diagonal token independence is a trained attention-mask property, not unrestricted parallel next-token generation.

- [Original paper](https://arxiv.org/html/2504.08388v1)
- [README.md](https://github.com/microsoft/MineWorld/blob/9f49efbcc68a5f0cf60e78f0abc566eac409282f/README.md) — revision `9f49efbcc68a5f0cf60e78f0abc566eac409282f`
- [diagonal_decoding.py](https://github.com/microsoft/MineWorld/blob/9f49efbcc68a5f0cf60e78f0abc566eac409282f/diagonal_decoding.py) — revision `9f49efbcc68a5f0cf60e78f0abc566eac409282f`
- [inference.py](https://github.com/microsoft/MineWorld/blob/9f49efbcc68a5f0cf60e78f0abc566eac409282f/inference.py) — revision `9f49efbcc68a5f0cf60e78f0abc566eac409282f`
- [lvm.py](https://github.com/microsoft/MineWorld/blob/9f49efbcc68a5f0cf60e78f0abc566eac409282f/lvm.py) — revision `9f49efbcc68a5f0cf60e78f0abc566eac409282f`

### nwm-cdit

**Navigation World Model (CDiT) — Released CDiT-XL/2: 28x1152, 250-step DDPM.** Stable-Diffusion VAE latents are patchified for a conditional DiT. Each block uses gated AdaLN target self-attention, context cross-attention and MLP. Action, prediction offset and diffusion time condition the denoiser. The released 250-step DDPM predicts noise/covariance; rollout decodes and re-encodes context as in the code.

Checked: representation and token geometry; core operation order, normalization/modulation and residual boundaries where disclosed; conditioning entry points and attention masks; sampling repetitions, cache/feedback tensor and output/decoder role.

Corrections: Removed the unsupported mixture of six distilled steps and a DDPM update. Selected 250 released steps and corresponding base-model latency, moved patchification into the loop and exposed gates. Output label now names the LPIPS cost used by CEM planning; summary and the Key detail fact now describe the released 250-step sampler (4,000 passes, 30.3 s), and label the 0.4 s / 48-pass numbers as the paper's unreleased distilled + Time Skip setting.

Limits / differences: The paper reports a six-step distilled model, but its weights and sampler are not supplied by the consulted release. The 30.3-second base-model rollout is not the distilled speed.

- [Original paper](https://arxiv.org/html/2412.03572v2)
- [config/nwm_cdit_xl.yaml](https://github.com/facebookresearch/nwm/blob/3f6cd8e70d6f2d1e2b9684acff510710135f0f41/config/nwm_cdit_xl.yaml) — revision `3f6cd8e70d6f2d1e2b9684acff510710135f0f41`
- [diffusion/__init__.py](https://github.com/facebookresearch/nwm/blob/3f6cd8e70d6f2d1e2b9684acff510710135f0f41/diffusion/__init__.py) — revision `3f6cd8e70d6f2d1e2b9684acff510710135f0f41`
- [models.py](https://github.com/facebookresearch/nwm/blob/3f6cd8e70d6f2d1e2b9684acff510710135f0f41/models.py) — revision `3f6cd8e70d6f2d1e2b9684acff510710135f0f41`

### oasis

**Oasis — Released Oasis small DiT-S/2: 16 space-time pairs, 10 DDIM steps.** The released VAE gives continuous visual latents; 2x2 patchification yields 144 tokens per latent frame. Each repeated block contains separate gated spatial attention/MLP and causal temporal attention/MLP pairs. Action and noise modulate the blocks. Ten DDIM updates generate the next latent with context retained in latent space.

Checked: representation and token geometry; core operation order, normalization/modulation and residual boundaries where disclosed; conditioning entry points and attention masks; sampling repetitions, cache/feedback tensor and output/decoder role.

Corrections: Added explicit gates to all four adaptive residual branches and routed latent feedback correctly.

Limits / differences: The released model's tensor dimensions give roughly 608M DiT parameters despite its Oasis 500M name. The larger hosted demo is not the released small configuration.

- [Original official page](https://oasis-model.github.io/)
- [dit.py](https://github.com/etched-ai/open-oasis/blob/f59deef2c019c212bd0c5a3a5b986a51f3701847/dit.py) — revision `f59deef2c019c212bd0c5a3a5b986a51f3701847`
- [generate.py](https://github.com/etched-ai/open-oasis/blob/f59deef2c019c212bd0c5a3a5b986a51f3701847/generate.py) — revision `f59deef2c019c212bd0c5a3a5b986a51f3701847`
- [vae.py](https://github.com/etched-ai/open-oasis/blob/f59deef2c019c212bd0c5a3a5b986a51f3701847/vae.py) — revision `f59deef2c019c212bd0c5a3a5b986a51f3701847`

### rap

**RAP (Reasoning via Planning) — Paper BlocksWorld RAP with frozen LLaMA-33B.** A frozen LLaMA decoder is prompted as policy, world model and reward evaluator. Standard RMSNorm/RoPE/SwiGLU decoder blocks generate text transitions token by token. A separate Monte Carlo tree-search procedure selects actions and evaluates imagined states using calls to the same model; no learned video encoder or dynamics head is added.

Checked: representation and token geometry; core operation order, normalization/modulation and residual boundaries where disclosed; conditioning entry points and attention masks; sampling repetitions, cache/feedback tensor and output/decoder role.

Corrections: Made feedback a prompt/token route for MCTS rather than a visual-encoder loop.

Limits / differences: The LLaMA-33B backbone dimensions are from the original LLaMA model and released compatible implementation. RAP's full-BlocksWorld Llama-2-70B experiment is a separate variant.

- [Original paper](https://arxiv.org/html/2305.14992v2)
- [dependencies/llama_model.py](https://github.com/meta-llama/llama/blob/57b0eb62de0636e75af471e49e2f1862d908d9d8/llama/model.py) — revision `57b0eb62de0636e75af471e49e2f1862d908d9d8`
- [examples/rap_blocksworld/search_config.py](https://github.com/maitrix-org/llm-reasoners/blob/195048c40e8985a09dd0c2e0268d59f39ab6919c/examples/rap_blocksworld/search_config.py) — revision `195048c40e8985a09dd0c2e0268d59f39ab6919c`
- [examples/rap_blocksworld/world_model.py](https://github.com/maitrix-org/llm-reasoners/blob/195048c40e8985a09dd0c2e0268d59f39ab6919c/examples/rap_blocksworld/world_model.py) — revision `195048c40e8985a09dd0c2e0268d59f39ab6919c`
- [reasoners/lm/llama_model.py](https://github.com/maitrix-org/llm-reasoners/blob/195048c40e8985a09dd0c2e0268d59f39ab6919c/reasoners/lm/llama_model.py) — revision `195048c40e8985a09dd0c2e0268d59f39ab6919c`

### rem

**REM — Released 5x256 RetNet world model with parallel observation prediction.** VQ codes and placeholder u-tokens enter five pre-LayerNorm retention/FFN blocks. Multi-scale retention maintains fixed recurrent state rather than a growing softmax KV cache. Parallel observation prediction uses one call for all next-frame codes plus a separate action/context call; reward and termination have dedicated heads.

Checked: representation and token geometry; core operation order, normalization/modulation and residual boundaries where disclosed; conditioning entry points and attention masks; sampling repetitions, cache/feedback tensor and output/decoder role.

Corrections: Routed predicted codes back to code/u-token embeddings.

Limits / differences: The paper lists GELU while released code uses SiLU. The roughly 4.8M total is arithmetic rather than a published parameter count. POP is a two-call frame transition, not a one-call generic autoregressive image model.

- [Original paper](https://arxiv.org/html/2402.05643v5)
- [config/world_model/default.yaml](https://github.com/leor-c/REM/blob/b8bcef56ee3dde382d2e201fcf189dcd4ec33859/config/world_model/default.yaml) — revision `b8bcef56ee3dde382d2e201fcf189dcd4ec33859`
- [dependencies/retnet.py](https://github.com/fkodom/yet-another-retnet/blob/fdd1c0e85a5ee64d4556c731879ee5efab9a968a/yet_another_retnet/retnet.py) — revision `fdd1c0e85a5ee64d4556c731879ee5efab9a968a`
- [requirements.txt](https://github.com/leor-c/REM/blob/b8bcef56ee3dde382d2e201fcf189dcd4ec33859/requirements.txt) — revision `b8bcef56ee3dde382d2e201fcf189dcd4ec33859`
- [src/envs/world_model_env.py](https://github.com/leor-c/REM/blob/b8bcef56ee3dde382d2e201fcf189dcd4ec33859/src/envs/world_model_env.py) — revision `b8bcef56ee3dde382d2e201fcf189dcd4ec33859`
- [src/models/pop_retnet.py](https://github.com/leor-c/REM/blob/b8bcef56ee3dde382d2e201fcf189dcd4ec33859/src/models/pop_retnet.py) — revision `b8bcef56ee3dde382d2e201fcf189dcd4ec33859`
- [src/models/world_model.py](https://github.com/leor-c/REM/blob/b8bcef56ee3dde382d2e201fcf189dcd4ec33859/src/models/world_model.py) — revision `b8bcef56ee3dde382d2e201fcf189dcd4ec33859`

### sana-wm

**SANA-WM — Released stage-one 2.6B SANA-WM, 20 hybrid blocks, 4 distilled steps.** LTX2 VAE latents pass through fifteen Gated DeltaNet layers and five softmax layers. Each block combines a parallel UCPE camera branch with the selected attention type, adds Pluecker mixing, then uses text cross-attention and a Mix-FFN. Attention and FFN are adaptively normalized and gated; streaming keeps recurrent state or sink/window KV.

Checked: representation and token geometry; core operation order, normalization/modulation and residual boundaries where disclosed; conditioning entry points and attention masks; sampling repetitions, cache/feedback tensor and output/decoder role.

Corrections: Moved patchification into the denoising loop, preserved the parallel camera branch, and exposed AdaLN/output gates. Added the official code link. The outer feedback now returns clean-chunk context to the block stack as GDN state plus sink/window KV cache rather than to the noisy latent input; the 34 s speed annotation and summary now cite the one-H100 attention-sink run, with the NVFP4 RTX 5090 numbers labelled separately.

Limits / differences: The optional 17B second-stage refiner is not part of this figure or its 2.6B backbone. GDN and softmax boxes are alternative layer types, not simultaneous main branches. State/cache sizes are arithmetic; the source does not disclose all spatial token geometry.

- [Original paper](https://arxiv.org/html/2605.15178v1)
- [README.md](https://github.com/NVlabs/Sana/blob/25adaaf02ad501c27be2c376b6b49b349cbcbe52/README.md) — revision `25adaaf02ad501c27be2c376b6b49b349cbcbe52`
- [configs/sana_wm/sana_wm_streaming_1600m_720p.yaml](https://github.com/NVlabs/Sana/blob/25adaaf02ad501c27be2c376b6b49b349cbcbe52/configs/sana_wm/sana_wm_streaming_1600m_720p.yaml) — revision `25adaaf02ad501c27be2c376b6b49b349cbcbe52`
- [diffusion/model/nets/sana_gdn_camctrl_blocks.py](https://github.com/NVlabs/Sana/blob/25adaaf02ad501c27be2c376b6b49b349cbcbe52/diffusion/model/nets/sana_gdn_camctrl_blocks.py) — revision `25adaaf02ad501c27be2c376b6b49b349cbcbe52`
- [diffusion/model/nets/sana_multi_scale_video_camctrl.py](https://github.com/NVlabs/Sana/blob/25adaaf02ad501c27be2c376b6b49b349cbcbe52/diffusion/model/nets/sana_multi_scale_video_camctrl.py) — revision `25adaaf02ad501c27be2c376b6b49b349cbcbe52`
- [inference_video_scripts/wm/inference_sana_wm_streaming.py](https://github.com/NVlabs/Sana/blob/25adaaf02ad501c27be2c376b6b49b349cbcbe52/inference_video_scripts/wm/inference_sana_wm_streaming.py) — revision `25adaaf02ad501c27be2c376b6b49b349cbcbe52`

### self-forcing

**Self Forcing — Released 1.3B Wan student: 30x1536, 4 DMD steps plus cache refresh.** The causal Wan student patchifies noisy latent chunks and applies gated self-attention/FFN with normalized text cross-attention. Four distilled updates are followed by a separate refresh pass on the generated chunk. Attention reads a bounded history cache, with sink/local-window handling for long rollout.

Checked: representation and token geometry; core operation order, normalization/modulation and residual boundaries where disclosed; conditioning entry points and attention masks; sampling repetitions, cache/feedback tensor and output/decoder role.

Corrections: Added residual gates and the cross-attention norm. Routed refreshed K/V to attention rather than feeding decoded pixels through an encoder.

Limits / differences: The 14B DMD teacher is not the deployed student. The figure shows steady-state chunks; first-frame/chunk special handling and the refresh pass matter when counting actual model calls.

- [Original paper](https://arxiv.org/html/2506.08009v2)
- [configs/self_forcing_dmd.yaml](https://github.com/guandeh17/Self-Forcing/blob/33593df3e81fa3ec10239271dd2c100facac6de1/configs/self_forcing_dmd.yaml) — revision `33593df3e81fa3ec10239271dd2c100facac6de1`
- [pipeline/causal_inference.py](https://github.com/guandeh17/Self-Forcing/blob/33593df3e81fa3ec10239271dd2c100facac6de1/pipeline/causal_inference.py) — revision `33593df3e81fa3ec10239271dd2c100facac6de1`
- [wan/modules/causal_model.py](https://github.com/guandeh17/Self-Forcing/blob/33593df3e81fa3ec10239271dd2c100facac6de1/wan/modules/causal_model.py) — revision `33593df3e81fa3ec10239271dd2c100facac6de1`

### slotformer

**SlotFormer — Released CLEVRER: 7 slots, width-256, 4-layer predictor.** Frozen SAVi extracts seven 128-dimensional slots per frame. Projected slots receive temporal positions and enter four pre-LayerNorm bidirectional transformer layers. The last frame's slot outputs are linearly projected back and rolled forward. A frozen SAVi spatial-broadcast decoder can render the predicted slots.

Checked: representation and token geometry; core operation order, normalization/modulation and residual boundaries where disclosed; conditioning entry points and attention masks; sampling repetitions, cache/feedback tensor and output/decoder role.

Corrections: Selected a single CLEVRER configuration. Removed the paper-only current-slot output residual: the released rollout projects the last N outputs directly.

Limits / differences: The paper's residual equation and released forward path differ. Physion/PHYRE use eight layers, while the displayed CLEVRER decoder uses an 8x8 initial grid. No total parameter count is published.

- [Original paper](https://arxiv.org/html/2210.05861v2)
- [slotformer/video_prediction/configs/slotformer_clevrer_params.py](https://github.com/pairlab/SlotFormer/blob/10a6d9b7bc05ef2397ce2586da3fc0212f8c47aa/slotformer/video_prediction/configs/slotformer_clevrer_params.py) — revision `10a6d9b7bc05ef2397ce2586da3fc0212f8c47aa`
- [slotformer/video_prediction/models/slotformer.py](https://github.com/pairlab/SlotFormer/blob/10a6d9b7bc05ef2397ce2586da3fc0212f8c47aa/slotformer/video_prediction/models/slotformer.py) — revision `10a6d9b7bc05ef2397ce2586da3fc0212f8c47aa`

### sold

**SOLD — Released checkpoint (Reach-Red): 4 dynamics + 4 SAT layers, 0 registers.** SAVi slots (7 in the released Reach-Red run) feed a 4-layer OCVP sequential relational/temporal transformer with pre-normalized ReLU FFNs. The projected next-slot output adds the current-slot residual. Separate 4-layer slot-aggregation transformers compute reward, critic and actor with RMSNorm/SiLU and one output token (0 registers in the release); generated slot state feeds future dynamics.

Checked: representation and token geometry; core operation order, normalization/modulation and residual boundaries where disclosed; conditioning entry points and attention masks; sampling repetitions, cache/feedback tensor and output/decoder role.

Corrections: Matched the released three-layer, zero-register SAT configuration instead of the paper's four-layer/four-register setup. Added the dynamics output projection/residual and explicit slot-state feedback. Added the official code link. Restored 4 SAT layers (paper D.3 and the released checkpoint's blocks 0-3; the 3 in train_sold.yaml is an unweighted default), relabelled the variant to the released Reach-Red checkpoint, restored the 12M total (checkpoint ≈11.9M), and labelled registers, slot count and SAVi fine-tuning as paper vs release.

Limits / differences: The paper reports 12M parameters; the released Reach-Red checkpoint sums to ≈11.9M. The unweighted train_sold.yaml default lists 3 SAT layers, but the paper and the released checkpoint use 4; the release has 0 register tokens against the paper's 4, uses 7 slots, and does not fine-tune SAVi (finetune_autoencoder False). The diagram distinguishes dynamics from parallel actor/critic/reward branches rather than putting all SATs in series.

- [Original paper](https://arxiv.org/html/2410.08822v2)
- [configs/train_sold.yaml](https://github.com/maltemosbach/sold/blob/54617b6f8a4c199d5ba116945541b45d27e2491b/configs/train_sold.yaml) — revision `54617b6f8a4c199d5ba116945541b45d27e2491b`
- [sold/modeling/sold/dynamics.py](https://github.com/maltemosbach/sold/blob/54617b6f8a4c199d5ba116945541b45d27e2491b/sold/modeling/sold/dynamics.py) — revision `54617b6f8a4c199d5ba116945541b45d27e2491b`
- [sold/modeling/sold/prediction.py](https://github.com/maltemosbach/sold/blob/54617b6f8a4c199d5ba116945541b45d27e2491b/sold/modeling/sold/prediction.py) — revision `54617b6f8a4c199d5ba116945541b45d27e2491b`
- [sold/modeling/sold/slot_aggregation_transformer.py](https://github.com/maltemosbach/sold/blob/54617b6f8a4c199d5ba116945541b45d27e2491b/sold/modeling/sold/slot_aggregation_transformer.py) — revision `54617b6f8a4c199d5ba116945541b45d27e2491b`

### storm

**STORM — Released STORM: 2x512 post-norm transformer, one latent/action token.** A categorical VAE encodes observations. An MLP mixes latent and action into one temporal token; learned positions and an input norm precede two post-LayerNorm causal attention/FFN blocks. A linear dynamics head samples the next latent; reward and continuation heads support actor-critic imagination without pixel decoding.

Checked: representation and token geometry; core operation order, normalization/modulation and residual boundaries where disclosed; conditioning entry points and attention masks; sampling repetitions, cache/feedback tensor and output/decoder role.

Corrections: Routed sampled latent feedback to the latent/action mixer.

Limits / differences: The approximately 16.5M whole world-model count and 4.2M block count are separate arithmetic estimates. Reconstruction decoding is a training path, not part of every imagined transition.

- [Original paper](https://arxiv.org/html/2310.09615v1)
- [config_files/STORM.yaml](https://github.com/weipu-zhang/STORM/blob/e8be598643b4fc0d54e68d870810f05cda5551ec/config_files/STORM.yaml) — revision `e8be598643b4fc0d54e68d870810f05cda5551ec`
- [sub_models/attention_blocks.py](https://github.com/weipu-zhang/STORM/blob/e8be598643b4fc0d54e68d870810f05cda5551ec/sub_models/attention_blocks.py) — revision `e8be598643b4fc0d54e68d870810f05cda5551ec`
- [sub_models/transformer_model.py](https://github.com/weipu-zhang/STORM/blob/e8be598643b4fc0d54e68d870810f05cda5551ec/sub_models/transformer_model.py) — revision `e8be598643b4fc0d54e68d870810f05cda5551ec`
- [sub_models/world_models.py](https://github.com/weipu-zhang/STORM/blob/e8be598643b4fc0d54e68d870810f05cda5551ec/sub_models/world_models.py) — revision `e8be598643b4fc0d54e68d870810f05cda5551ec`

### trajectory-transformer

**Trajectory Transformer — Released code defaults: 4-layer GPT; beam plan 128 × 2, horizon 15.** State/action/reward/return dimensions become separate discretized scalar tokens. Four pre-LayerNorm GPT blocks and a final norm predict one scalar token at a time. Return tokens are excluded as attention keys. Beam search ranks imagined transitions with reward/return rather than treating the model as a pixel generator.

Checked: representation and token geometry; core operation order, normalization/modulation and residual boundaries where disclosed; conditioning entry points and attention masks; sampling repetitions, cache/feedback tensor and output/decoder role.

Corrections: Added the final LayerNorm and routed beam tokens back to embeddings. Matched the planning inset to released 128-beam/two-expansion CDF sampling instead of mixing in paper planning defaults. Split the beam inset into CDF-filtered action sampling and greedy state decoding as in search/core.py, relabelled the beam annotation and variant as the released base defaults (128 × 2, horizon 15), and stated the released HalfCheetah overrides (32 beams, horizon 5, 108 passes) in the facts.

Limits / differences: Paper planning uses width 256/top-20 actions; released defaults use 128 beams with two expansions, a cumulative-probability action filter and greedy state tokens, and the released HalfCheetah configs override them to 32 beams (horizon 5 for medium and medium-replay). The schematic keeps the planning inset distinct from the learned autoregressive graph.

- [Original paper](https://arxiv.org/html/2106.02039v4)
- [config/offline.py](https://github.com/jannerm/trajectory-transformer/blob/8834a6ed04ceeab8fdb9465e145c6e041c05d71b/config/offline.py) — revision `8834a6ed04ceeab8fdb9465e145c6e041c05d71b`
- [trajectory/models/transformers.py](https://github.com/jannerm/trajectory-transformer/blob/8834a6ed04ceeab8fdb9465e145c6e041c05d71b/trajectory/models/transformers.py) — revision `8834a6ed04ceeab8fdb9465e145c6e041c05d71b`
- [trajectory/search/core.py](https://github.com/jannerm/trajectory-transformer/blob/8834a6ed04ceeab8fdb9465e145c6e041c05d71b/trajectory/search/core.py) — revision `8834a6ed04ceeab8fdb9465e145c6e041c05d71b`

### transdreamer

**TransDreamer — Released Atari config: 6 layers, width 600, 8 heads of 64, h = all 6 layer outputs.** A myopic observation posterior produces categorical latent z. Concatenated latent/action tokens pass through a Linear/ELU/sinusoidal-position input and six pre-LayerNorm transformer layers. The outputs of all six layers are concatenated (deter_type concat_o, 3600-d) into the deterministic state, which conditions the stochastic prior; h and the sampled z feed reward, discount and reconstruction heads. Imagination re-runs the history window without KV caching.

Checked: representation and token geometry; core operation order, normalization/modulation and residual boundaries where disclosed; conditioning entry points and attention masks; sampling repetitions, cache/feedback tensor and output/decoder role.

Corrections: Replaced a mixed paper/code block with the released six-layer Atari configuration. Added the input transform/positions and made current versus next-state indices consistent. Drew the released concat_o deterministic state (all six layer outputs concatenated, 3600-d) and corrected the Attention fact to the config's absolute sinusoidal ('temporal') positions; clarified the figure's 'next' indexing against the paper's p(z_t|h_t).

Limits / differences: The paper's DMC/Atari experiments use two layers and ten heads; the released Atari config differs in heads, depth, FFN and normalization mode. The three-trajectory training claim is not assigned to the released rollout.

- [Original paper](https://arxiv.org/html/2202.09481v2)
- [config_files/configs_atari.py](https://github.com/changchencc/TransDreamer/blob/393007a1528acdfb70a2a813e09ab7b2e236bd4f/config_files/configs_atari.py) — revision `393007a1528acdfb70a2a813e09ab7b2e236bd4f`
- [configs.py](https://github.com/changchencc/TransDreamer/blob/393007a1528acdfb70a2a813e09ab7b2e236bd4f/configs.py) — revision `393007a1528acdfb70a2a813e09ab7b2e236bd4f`
- [model/modules_transformer.py](https://github.com/changchencc/TransDreamer/blob/393007a1528acdfb70a2a813e09ab7b2e236bd4f/model/modules_transformer.py) — revision `393007a1528acdfb70a2a813e09ab7b2e236bd4f`
- [model/transformer.py](https://github.com/changchencc/TransDreamer/blob/393007a1528acdfb70a2a813e09ab7b2e236bd4f/model/transformer.py) — revision `393007a1528acdfb70a2a813e09ab7b2e236bd4f`

### twister

**TWISTER — Released TWISTER: 4x512 post-norm temporal transformer.** A categorical VAE provides stochastic latents; a latent/action MLP forms one token per step. Four post-LayerNorm causal transformer blocks use relative positions. The prior samples a next latent for actor-critic imagination, while reward and continuation heads read the dynamics representation. Contrastive temporal prediction is a training objective.

Checked: representation and token geometry; core operation order, normalization/modulation and residual boundaries where disclosed; conditioning entry points and attention masks; sampling repetitions, cache/feedback tensor and output/decoder role.

Corrections: Routed sampled latent feedback to the latent/action mixer.

Limits / differences: The contrastive head is not an extra inference-time world-model transition. The fixed history window is distinct from Transformer-XL-style positional encoding.

- [Original paper](https://arxiv.org/html/2503.04416v2)
- [nnet/models/twister.py](https://github.com/burchim/TWISTER/blob/e6d8cde8dfe486d47ffb3e6ac7e061de03a380ca/nnet/models/twister.py) — revision `e6d8cde8dfe486d47ffb3e6ac7e061de03a380ca`
- [nnet/modules/blocks/transformer_block.py](https://github.com/burchim/TWISTER/blob/e6d8cde8dfe486d47ffb3e6ac7e061de03a380ca/nnet/modules/blocks/transformer_block.py) — revision `e6d8cde8dfe486d47ffb3e6ac7e061de03a380ca`
- [nnet/modules/twister/tssm.py](https://github.com/burchim/TWISTER/blob/e6d8cde8dfe486d47ffb3e6ac7e061de03a380ca/nnet/modules/twister/tssm.py) — revision `e6d8cde8dfe486d47ffb3e6ac7e061de03a380ca`

### twm

**TWM — Released TWM: 10x256 Transformer-XL, three tokens per step.** Categorical latent, action and reward embeddings are interleaved. Ten post-LayerNorm causal Transformer-XL blocks use relative positions; the action-token representation drives next-latent, reward and discount predictions. One cached model evaluation per step supplies a sampled latent to actor-critic imagination without decoding pixels.

Checked: representation and token geometry; core operation order, normalization/modulation and residual boundaries where disclosed; conditioning entry points and attention masks; sampling repetitions, cache/feedback tensor and output/decoder role.

Corrections: Routed next-latent feedback to the interleaved sequence.

Limits / differences: Three input tokens per environment step do not mean three independent dynamics samples. Throughput is the authors' batch measurement, not a new latency result.

- [Original paper](https://arxiv.org/html/2303.07109v1)
- [twm/config.py](https://github.com/jrobine/twm/blob/e6a8e599864f5539b166ee9a8d173ece8f3fba84/twm/config.py) — revision `e6a8e599864f5539b166ee9a8d173ece8f3fba84`
- [twm/nets.py](https://github.com/jrobine/twm/blob/e6a8e599864f5539b166ee9a8d173ece8f3fba84/twm/nets.py) — revision `e6a8e599864f5539b166ee9a8d173ece8f3fba84`
- [twm/world_model.py](https://github.com/jrobine/twm/blob/e6a8e599864f5539b166ee9a8d173ece8f3fba84/twm/world_model.py) — revision `e6a8e599864f5539b166ee9a8d173ece8f3fba84`

### unizero

**UniZero — Released 2x768 pre-norm transformer with final LayerNorm.** A convolutional encoder supplies SimNorm latent tokens interleaved with actions and learned positions. Two released pre-LayerNorm causal blocks and a final LayerNorm feed dynamics and policy/value heads. During imagined planning, an action-token call predicts latent/reward, then a latent-token call predicts policy/value.

Checked: representation and token geometry; core operation order, normalization/modulation and residual boundaries where disclosed; conditioning entry points and attention masks; sampling repetitions, cache/feedback tensor and output/decoder role.

Corrections: Replaced the paper's post-norm drawing with released pre-norm blocks and a final norm. Matched the code's 4D FFN and corrected latent feedback. Re-based the FFN inset on the released code (Linear 768→3072, tanh-GELU, Linear 3072→768) so it matches the drawn 4D-wide pre-norm variant instead of Table 6.

Limits / differences: Paper Table 6 specifies post-norm and FFN width D; the release uses pre-norm and width 4D. Smaller long-memory-task settings differ from the displayed Atari/DMC width.

- [Original paper](https://arxiv.org/html/2406.10667v2)
- [lzero/model/unizero_world_models/transformer.py](https://github.com/opendilab/LightZero/blob/fdd414c603a842260e05b40d078f585b63a40bd6/lzero/model/unizero_world_models/transformer.py) — revision `fdd414c603a842260e05b40d078f585b63a40bd6`
- [lzero/model/unizero_world_models/world_model.py](https://github.com/opendilab/LightZero/blob/fdd414c603a842260e05b40d078f585b63a40bd6/lzero/model/unizero_world_models/world_model.py) — revision `fdd414c603a842260e05b40d078f585b63a40bd6`
- [zoo/atari/config/atari_unizero_config.py](https://github.com/opendilab/LightZero/blob/fdd414c603a842260e05b40d078f585b63a40bd6/zoo/atari/config/atari_unizero_config.py) — revision `fdd414c603a842260e05b40d078f585b63a40bd6`

### uva

**UVA (Unified Video Action) — MAR-B (released code): 12 encoder + 12 decoder blocks; 16 action steps as on the robot (paper).** VAE image tokens, action chunks and repeated CLIP text tokens enter a joint masked transformer. Twelve encoder blocks and twelve decoder blocks (released mar_base) are separated by final encoder norm and decoder projection/positions. The resulting latent is pooled once to condition an action diffusion head; only that head repeats, for the paper's sixteen real-robot denoising steps (the released config uses 100).

Checked: representation and token geometry; core operation order, normalization/modulation and residual boundaries where disclosed; conditioning entry points and attention masks; sampling repetitions, cache/feedback tensor and output/decoder role.

Corrections: Split the incorrect undifferentiated 24-block stack into the actual encoder and decoder stages. Added their final norms and projection/positions, and restricted the 16-step loop to the action head. Labelled the 16 action denoising steps as the paper's real-robot setting (loop, annotation, figure_variant) and noted in the Prediction fact that the released uva.yaml uses act_diff_testing_steps 100.

Limits / differences: The paper describes language cross-attention, but released language tokens are concatenated into self-attention. The code retains masked token positions, so no invented MAE token-restoration stage is drawn. Video generation and 100-step simulation sampling are separate paths. The drawn 16 action steps (and the 15 ms / 95 ms timings) are the paper's real-robot setting; the released uva.yaml samples the action head with 100 steps.

- [Original paper](https://arxiv.org/html/2503.00200v3)
- [unified_video_action/config/model/uva.yaml](https://github.com/ShuangLI59/unified_video_action/blob/fe3dec81af565fbb2d686072722f12340be31293/unified_video_action/config/model/uva.yaml) — revision `fe3dec81af565fbb2d686072722f12340be31293`
- [unified_video_action/model/autoregressive/mar_con_unified.py](https://github.com/ShuangLI59/unified_video_action/blob/fe3dec81af565fbb2d686072722f12340be31293/unified_video_action/model/autoregressive/mar_con_unified.py) — revision `fe3dec81af565fbb2d686072722f12340be31293`
- [unified_video_action/policy/unified_video_action_policy.py](https://github.com/ShuangLI59/unified_video_action/blob/fe3dec81af565fbb2d686072722f12340be31293/unified_video_action/policy/unified_video_action_policy.py) — revision `fe3dec81af565fbb2d686072722f12340be31293`

### uwm

**UWM (Unified World Models) — Released three-camera DROID configuration: 12x768, 10 DDIM steps.** Image latents, action embeddings and register tokens form a joint denoising sequence. A ResNet observation embedding plus modality timesteps conditions the gated AdaLN attention/MLP blocks. Ten DDIM updates predict action and image outputs; policy mode keeps image tokens at a noisy timestep and does not decode them.

Checked: representation and token geometry; core operation order, normalization/modulation and residual boundaries where disclosed; conditioning entry points and attention masks; sampling repetitions, cache/feedback tensor and output/decoder role.

Corrections: Moved noisy-image patchification inside each denoising evaluation and exposed attention/MLP gates.

Limits / differences: The approximately 385M denoiser size is computed from the released three-camera condition width, not a published universal count. Paper policy mode fixes image time at T; the code uses its first DDIM timestep, 90.

- [Original paper](https://arxiv.org/html/2504.02792v3)
- [configs/model/uwm.yaml](https://github.com/WEIRDLabUW/unified-world-model/blob/b7d4067c8859775e5b08f681e76d538015cdd445/configs/model/uwm.yaml) — revision `b7d4067c8859775e5b08f681e76d538015cdd445`
- [models/common/adaln_attention.py](https://github.com/WEIRDLabUW/unified-world-model/blob/b7d4067c8859775e5b08f681e76d538015cdd445/models/common/adaln_attention.py) — revision `b7d4067c8859775e5b08f681e76d538015cdd445`
- [models/uwm/uwm.py](https://github.com/WEIRDLabUW/unified-world-model/blob/b7d4067c8859775e5b08f681e76d538015cdd445/models/uwm/uwm.py) — revision `b7d4067c8859775e5b08f681e76d538015cdd445`

### vjepa2-ac

**V-JEPA 2-AC — Released 24x1024 action-conditioned predictor with frozen ViT-g.** Frozen V-JEPA 2 yields 256 visual features of width 1408. A projection maps them to predictor width; interleaved state/action tokens give 258 tokens per step. Twenty-four pre-LayerNorm block-causal layers with 3D RoPE and a final norm/projection regress next features. Goal-distance planning rolls out features without a pixel decoder.

Checked: representation and token geometry; core operation order, normalization/modulation and residual boundaries where disclosed; conditioning entry points and attention masks; sampling repetitions, cache/feedback tensor and output/decoder role.

Corrections: Added the input feature projection and final norm/output projection. Routed predicted features back to the predictor sequence. The rollout feedback now returns the predicted 1,408-d features to the input projection box instead of the interleaved 1,024-d sequence, and the Prediction fact notes the layer norm and re-projection applied in the released planning wrapper.

Limits / differences: The 1B encoder and 300M predictor are distinct components. Planning runtime includes many candidate sequences; it is not the latency of one predictor pass.

- [Original paper](https://arxiv.org/html/2506.09985v1)
- [configs/train/vitg16/droid-256px-8f.yaml](https://github.com/facebookresearch/vjepa2/blob/204698b45b3712590f06245fbfba32d3be539812/configs/train/vitg16/droid-256px-8f.yaml) — revision `204698b45b3712590f06245fbfba32d3be539812`
- [src/hub/backbones.py](https://github.com/facebookresearch/vjepa2/blob/204698b45b3712590f06245fbfba32d3be539812/src/hub/backbones.py) — revision `204698b45b3712590f06245fbfba32d3be539812`
- [src/models/ac_predictor.py](https://github.com/facebookresearch/vjepa2/blob/204698b45b3712590f06245fbfba32d3be539812/src/models/ac_predictor.py) — revision `204698b45b3712590f06245fbfba32d3be539812`
- [src/models/utils/modules.py](https://github.com/facebookresearch/vjepa2/blob/204698b45b3712590f06245fbfba32d3be539812/src/models/utils/modules.py) — revision `204698b45b3712590f06245fbfba32d3be539812`

### wham

**WHAM (Muse) — Released WHAM-1.6B: 24x2304 GPT, 540 image + 16 action tokens.** A ViT-VQGAN produces 540 frame codes. Controller tokens join the learned-position sequence; 24 pre-LayerNorm nanoGPT blocks with GELU and a final norm predict tokens serially. Image and action modes rebuild their sliding-window cache as implemented. The VQGAN decoder reconstructs generated frame codes.

Checked: representation and token geometry; core operation order, normalization/modulation and residual boundaries where disclosed; conditioning entry points and attention masks; sampling repetitions, cache/feedback tensor and output/decoder role.

Corrections: Replaced the symbolic block count with the released 24 layers and width/head configuration. Added the official Hugging Face code link and fixed token feedback.

Limits / differences: WHAMM is a later MaskGIT model, not the autoregressive graph shown here. The smaller WHAM models use a different tokenizer/resolution. No runtime benchmark was executed.

- [Original paper](https://www.nature.com/articles/s41586-025-08600-3?error=cookies_not_supported&code=554be077-5f2d-4bbe-b6e8-30f4a956262d)
- [wham/models/nn/nanoGPT.py](https://huggingface.co/microsoft/wham/blob/963399322b737416569ab62e269b1d6d02b00e8f/wham/models/nn/nanoGPT.py) — revision `963399322b737416569ab62e269b1d6d02b00e8f`
- [wham/models/wham_token_model/gpt_token_transformer_predictor.py](https://huggingface.co/microsoft/wham/blob/963399322b737416569ab62e269b1d6d02b00e8f/wham/models/wham_token_model/gpt_token_transformer_predictor.py) — revision `963399322b737416569ab62e269b1d6d02b00e8f`

### worldplay

**WorldPlay (HY-World 1.5) — Released 480P distilled AR model: HY-1.5 8B, 54 blocks, 4 steps.** Camera-aware memory is retrieved and its K/V recomputed before denoising. The 54 double-stream blocks jointly attend video and refined text using parallel RoPE and PRoPE attention, whose projected results are summed. Keyboard/timestep AdaLN gates residual attention and FFN outputs. Four updates generate a latent chunk for later memory.

Checked: representation and token geometry; core operation order, normalization/modulation and residual boundaries where disclosed; conditioning entry points and attention masks; sampling repetitions, cache/feedback tensor and output/decoder role.

Corrections: Added the parallel RoPE/PRoPE inset and gates, and labelled the text/memory attention input. Routed latent feedback through memory reconstruction. The attention box is again named with the paper's term 'Block-causal attention'; the figure variant is now the released 480P distilled AR checkpoint, so token, memory and KV annotations are recomputed for 480×832 (6,240 tokens per chunk, ≈31k context, ≈27.6 GB KV), and the 24 fps / 720p numbers are labelled as the paper setting.

Limits / differences: The paper drawing includes cross-attention, while the released double-stream block joins text K/V into joint attention instead. The roughly 27.6 GB cache (≈63.7 GB at the paper's 720p) is a full BF16 arithmetic estimate for both attention paths at 480×832, not a measured allocation. The 24 FPS figure is the company's 720p result on 8 H800s; the released checkpoints are 480P, and the paper does not name the 720p model's backbone size (54 blocks × 2048 come from the released HunyuanVideo-1.5 config).

- [Original paper](https://arxiv.org/html/2512.14614v2)
- [hyvideo/models/transformers/modules/mlp_layers.py](https://github.com/Tencent-Hunyuan/HY-WorldPlay/blob/1588e1336e842b03b0a7860c654ebd7c46bb065e/hyvideo/models/transformers/modules/mlp_layers.py) — revision `1588e1336e842b03b0a7860c654ebd7c46bb065e`
- [hyvideo/models/transformers/worldplay_1_5_transformer.py](https://github.com/Tencent-Hunyuan/HY-WorldPlay/blob/1588e1336e842b03b0a7860c654ebd7c46bb065e/hyvideo/models/transformers/worldplay_1_5_transformer.py) — revision `1588e1336e842b03b0a7860c654ebd7c46bb065e`
- [hyvideo/pipelines/worldplay_video_pipeline.py](https://github.com/Tencent-Hunyuan/HY-WorldPlay/blob/1588e1336e842b03b0a7860c654ebd7c46bb065e/hyvideo/pipelines/worldplay_video_pipeline.py) — revision `1588e1336e842b03b0a7860c654ebd7c46bb065e`

### worldvla

**WorldVLA — Released Chameleon-based ~7B, 256×256 setting, two-frame input.** Text, VQ image codes and quantized actions share one vocabulary. The released 32-layer Chameleon decoder applies pre-normalized causal attention/FFN blocks and a final norm; action chunk masking is a trained attention-mask modification. The released generator is greedy and serial. Image codes may be decoded; action tokens go directly to control.

Checked: representation and token geometry; core operation order, normalization/modulation and residual boundaries where disclosed; conditioning entry points and attention masks; sampling repetitions, cache/feedback tensor and output/decoder role.

Corrections: Routed generated tokens to token embeddings, preserving the separate image/action output roles. The figure is now consistently the 256×256 setting: the per-frame pass count is ≈277 only, and the 512×512 figure (≈1,061) is labelled as that setting in the summary and facts.

Limits / differences: The paper's claim of parallel action-chunk generation is distinct from the released greedy serial generation path. Token counts differ for 256-code and 1024-code image settings. The figure uses the default two-frame context.

- [Original paper](https://arxiv.org/html/2506.21539v1)
- [worldvla/libero_util/run_libero_eval.py](https://github.com/alibaba-damo-academy/WorldVLA/blob/ebdc36dc5cfdc3288e19a7b117b2ff07b135c8be/worldvla/libero_util/run_libero_eval.py) — revision `ebdc36dc5cfdc3288e19a7b117b2ff07b135c8be`
- [worldvla/model/chameleon/modeling_chameleon.py](https://github.com/alibaba-damo-academy/WorldVLA/blob/ebdc36dc5cfdc3288e19a7b117b2ff07b135c8be/worldvla/model/chameleon/modeling_chameleon.py) — revision `ebdc36dc5cfdc3288e19a7b117b2ff07b135c8be`
- [worldvla/model/modeling_xllmx_chameleon_ck.py](https://github.com/alibaba-damo-academy/WorldVLA/blob/ebdc36dc5cfdc3288e19a7b117b2ff07b135c8be/worldvla/model/modeling_xllmx_chameleon_ck.py) — revision `ebdc36dc5cfdc3288e19a7b117b2ff07b135c8be`

## Reproduce the integrity checks

```bash
python3 -m wmgallery.audit
python3 -m wmgallery.audit --sources '/home/yaoz0b/wm_accel/research_notes/Architecture audit/2026-10-25'
python3 -m wmgallery.audit --artifacts
```

The JSON ledger records SHA-256 hashes of the reviewed card and every downloaded primary source. The checks detect stale cards, missing reviews, invalid feedback ports, source-byte changes, and stale SVG/data exports. They do not prove scientific correctness by searching for names in code. No downloaded model code or weights were executed.
