# Model Curation Sources

References for keeping `CURATED_MODELS` in
`config/includes.chroot/usr/lib/neuraldrive/tui/screens/models.py` up to date.

When updating the list, cross-check at least one leaderboard, one opinion
source, and the Ollama library to confirm the model + tag exists and the size
is accurate.

---

## Leaderboards (raw benchmark data, regularly updated)

### Coding

- **Aider LLM Leaderboard** — <https://aider.chat/docs/leaderboards/>
  Code-editing benchmark using Aider's `whole`/`diff` edit formats. Most
  relevant for "which model edits code reliably" — a different question from
  "which model writes code from scratch". Updated when new models drop.
- **EvalPlus (HumanEval+ / MBPP+)** — <https://evalplus.github.io/leaderboard.html>
  Hardened versions of HumanEval and MBPP. The plain HumanEval numbers
  everyone quotes are mostly saturated; EvalPlus is the honest signal.
- **LiveCodeBench** — <https://livecodebench.github.io/leaderboard.html>
  Time-windowed coding benchmark (problems collected after each model's
  training cutoff), so contamination is minimized.
- **BigCodeBench** — <https://bigcode-bench.github.io/>
- **SWE-Bench** — <https://www.swebench.com/>
  Real GitHub issues from real repos. Agentic coding's gold standard.

### General reasoning / chat

- **HuggingFace Open LLM Leaderboard v2** — <https://huggingface.co/spaces/open-llm-leaderboard/open_llm_leaderboard>
  IFEval, BBH, MMLU-Pro, GPQA, MATH, MUSR. Open-source models only.
- **LMSYS / Chatbot Arena** — <https://lmarena.ai/>
  Crowd-sourced Elo from blind A/B preference. Best signal for "which model
  do humans actually like talking to". Covers both open and closed models.
- **Artificial Analysis** — <https://artificialanalysis.ai/leaderboards/models>
  Throughput, latency, and price-per-token for hosted models. Useful for
  context on relative model strengths even though we run locally.

### Embeddings (for RAG)

- **MTEB** — <https://huggingface.co/spaces/mteb/leaderboard>
  Massive Text Embedding Benchmark. Authoritative for picking embedding models
  (e.g., the case for `nomic-embed-text` vs. alternatives).

---

## Registries (what's actually pull-able)

- **Ollama Library** — <https://ollama.com/library>
  Canonical source for tag names, parameter counts, and Q4_K_M sizes. Always
  cross-check `CURATED_MODELS` entries here — a tag we recommend has to exist.
- **Hugging Face Models** — <https://huggingface.co/models>
  Upstream source for original weights. Useful when a model exists on HF but
  isn't on Ollama yet (a sign to wait, not to recommend).

---

## Opinion / analysis sites

- **MorphLLM "Best Ollama Models"** — <https://www.morphllm.com/best-ollama-models>
  Opinion piece with explicit rationale per tier. Currently the basis for our
  `CURATED_MODELS` structure. Re-check whenever they republish.
- **Simon Willison's blog** — <https://simonwillison.net/>
  Highest signal-to-noise coverage of open-model releases. Search for the
  `local-llms` tag. Updated within days of any significant release.
- **r/LocalLLaMA** — <https://www.reddit.com/r/LocalLLaMA/>
  Community wisdom; sort by Top → Week for current consensus. Noisy but the
  fastest place to learn that a heavily-hyped model is actually broken at Q4
  or only works with a specific runner.
- **MLJourney "Best Ollama Models"** — <https://mljourney.com/best-ollama-models-in-2026-a-practical-guide-by-use-case/>
  Use-case-organized list. Cross-reference perspective vs. MorphLLM.
- **Meshworld "Ollama Models Benchmark"** — <https://meshworld.in/blog/ai/ollama-models-benchmark/>
  Includes hardware / VRAM reality checks.

---

## Vendor pages (canonical release info)

Use these to confirm a model's actual size, context length, and license
*before* recommending — third-party articles often round or get details wrong.

- **Qwen (Alibaba)** — <https://qwenlm.github.io/>
- **DeepSeek** — <https://www.deepseek.com/>
- **Meta Llama** — <https://www.llama.com/>
- **Mistral** — <https://mistral.ai/news>
- **Google Gemma** — <https://ai.google.dev/gemma>
- **Microsoft Phi** — <https://azure.microsoft.com/en-us/products/phi> (and `microsoft/Phi-*` on Hugging Face)

---

## Maintenance checklist

When updating `CURATED_MODELS`:

1. Pick a model from at least one leaderboard *or* opinion source above.
2. Verify the tag exists at `https://ollama.com/library/<model>` and copy
   the Q4_K_M size from the tag's metadata.
3. Verify against the vendor page that the model is the version we expect
   (e.g., `qwen2.5-coder:32b` really maps to Qwen2.5-Coder-32B-Instruct, not
   the base model).
4. Cross-reference at least one other source for consensus (e.g., if MorphLLM
   says it's great, check r/LocalLLaMA's last month of posts to make sure
   nobody's reporting it's broken at Q4 or doesn't load correctly via Ollama).
