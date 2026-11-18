# Results

All runs: one laptop with RTX 5070 Ti (12 GB VRAM), llama.cpp server, temperature 0, November 2026. "Off" and "on" refer to the model's reasoning ("thinking") mode. Speed is generation tokens per second on this machine. Empty answers mean the model used the whole token budget without answering.

All models were run as quantised GGUF builds (Q4/Q5) on one consumer GPU. The results describe these builds in my use case, not the original models, and are not a general ranking. The model authors have not reviewed them.

## EE1–EE3 (conversational Estonian, /60, reasoning off)

| Model | EE1 /20 | EE2 /20 | EE3 /20 | Total | gen t/s |
|---|---|---|---|---|---|
| Gemma-4-12B-it | 19 | 17 | 18 | **54** | ~37 |
| Qwen3.5-4B | 19 | 17 | 18 | **54** | ~78 |
| Qwen3.5-9B | 18 | 17 | 18 | 53 | ~54 |
| Llama-3.1-EstLLM-8B (TartuNLP) | 18 | 19 | 16 | 53 | ~60 |
| Gemma-2-9B-it | 18 | 15 | 17 | 50 | ~45 |

The scores are too close together to separate the models, which is why the harder suites below exist. Qwen3.5-4B matched the best at twice the speed.

## EE4 "form" (/20, key v1.0)

| Model | Off | On |
|---|---|---|
| Qwen3.6-35B-A3B | – | **14** |
| Gemma-4-12B-it | 12 | 12 |
| Qwen3.5-9B | 11 | 8 |
| Llama-3.1-EstLLM-8B | 11 | – |
| Gemma-2-9B-it | 10 | – |
| Qwen3.5-4B | 9 | 9 |
| gpt-oss-20b (MXFP4) | – | 8 |

Estonian morphology is hard for every local model tested. Key v1.1 later accepted two more correct forms, which can add at most 2 points to a v1.0 score.

## EE5 "extraction" (/20)

| Model | Off | On | Empty answers (on) |
|---|---|---|---|
| Gemma-4-12B-it | **20** | **20** | 0 |
| Qwen3.6-35B-A3B | – | **20** | 0 |
| gpt-oss-20b | – | **20** | 0 |
| Qwen3.5-9B | 17 | 19 | 1 |
| Gemma-2-9B-it | 19 | – | – |
| Qwen3.5-4B | 16 | 16 | 4 |
| Llama-3.1-EstLLM-8B | **5** | – | – |

EstLLM's low score is partly output discipline. Several failures had the right values but wrapped them in a ```json code block, which the prompt forbade and strict scoring counts as a fail. The rest were real errors: wrong decision status, dates left unnormalised (`12.12.2026` instead of `2026-12-12`), and echoing the source text back before the JSON.

## EE6 "editing" (/16)

| Model | Off | On | Empty answers (on) |
|---|---|---|---|
| Qwen3.6-35B-A3B | **15** | **15** | 0 |
| Gemma-4-12B-it | 13 | 9 | 3 |
| Llama-3.1-EstLLM-8B | 11 | – | – |
| Qwen3.5-9B | 9 | 4 | 12 |
| Gemma-2-9B-it | 6 | – | – |

Reasoning did not improve editing for any model. For the smaller ones, most of the drop comes from thinking until the token limit and never giving an answer. The fair conclusion: for an editing role, run these models with reasoning off.

## Choice made from this

For Estonian editing in my own pipeline: Qwen3.6-35B-A3B with reasoning off (15/16, but slow on this GPU: ~23–28 t/s). Gemma-4-12B is the fast fallback (13/16 off, 20/20 on extraction). The final pick waits for a blind A/B comparison on real texts by a native speaker, because 16 items are not enough on their own.
