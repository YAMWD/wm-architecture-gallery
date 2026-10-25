# Model card specification

Each `models/<slug>.py` defines one `MODEL` dictionary. Files beginning with `_` are templates and are not loaded. The `slug` must match the filename. The required architecture is `MODEL["flow"]`, described in [FLOW.md](FLOW.md). The obsolete duplicate `diagram` key is rejected.

## Card fields

| Field | Meaning |
|---|---|
| `slug`, `name` | Stable identifier and display name |
| `year`, `month`, `org` | First public release and organization; cite publication metadata |
| `family` | `rl`, `token`, `dit`, `driving`, `jepa`, `wam`, `llm`, `object`, or `ssm` |
| `role` | One of `wmgallery.registry.ROLES` |
| `status` | Publication/report status |
| `params` | Display size, with the counted component and variant made clear; say undisclosed when necessary |
| `params_num` | Numeric sorting value, or `None` when unknown |
| `open` | Availability such as `code + weights`, `code`, `weights`, or `closed` |
| `links` | Original paper/report, official code, weights and project page |
| `tagline`, `summary` | Short description and scope; identify important paper/code differences |
| `facts` | Ordered `(label, text)` pairs: representation, core, attention, actions, prediction, decoder, memory, speed, key detail |
| `evidence` | `read` for primary-source reading; `claim` for an official technical page only |
| `sources` | Human-readable primary-source locators, including relevant sections and files |
| `figure_variant` | Exact configuration drawn; must agree with the source review |
| `flow` | The single canonical figure specification |

The `source_review` field is added during the site build from the review ledger. It is not authored in the model file. Historical `audit` counters are not current evidence.

## Evidence and configuration rules

- Read the original publication and, where available, the official implementation. Inspect constructor/configuration, the executed forward path, sampling and cache updates. A class name or a matching word is insufficient.
- Pick one configuration for the figure. State its variant in the review. Report paper/code disagreement explicitly; do not silently manufacture agreement or combine incompatible variants.
- Trace dimensions, layer/head counts, modulation, residual boundaries, attention masks, action/text input locations, sampler repetitions and output roles to sources.
- Distinguish a total agent size from its dynamics transformer, backbone from added modules, training path from inference, and an external robot loop from a tensor edge.
- Every numeric claim needs a source. Arithmetic is labelled `[D]` in facts and uses an approximate sign where appropriate. Do not assign a paper's runtime to a different released sampler or configuration.
- Do not borrow undisclosed architecture from a familiar transformer. Keep one opaque module box for a named but unexpanded component, and say what is unknown. Add no speculative normalization, FFN, residual, cache or decoder.
- `read` is a description of evidence consulted, not a certificate that the source discloses everything. Official-page-only descriptions remain `claim`.

## Review ledger

[architecture_audit.json](architecture_audit.json) covers exactly the loaded models. Each entry contains:

- `variant`, `architecture`, `checked`, `changes` and `limitations`;
- the complete card/flow's `model_sha256`, produced by `wmgallery.audit.fingerprint`;
- primary `references` with kind, URL, source-byte SHA-256 and a relative `cached_as` path;
- an immutable revision for released code, and a versioned paper link when available.

No-code reviews must state that limit. Updating a fingerprint requires reviewing the actual change; blindly accepting a new hash is not a source check. The site build rejects missing or stale reviews. `python3 -m wmgallery.audit --artifacts` also compares all four SVG exports and the published model data with the reviewed source.
