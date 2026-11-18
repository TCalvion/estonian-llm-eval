# Estonian LLM Eval (EE series)

A small, hand-built benchmark for one question: **can a model do real work in Estonian without quietly changing what the text means?**

I built it to choose local models for my own Estonian-language pipelines (summaries, decision logs, editing). Public leaderboards say little about Estonian, and almost nothing about the failure I care about most: a fluent answer that has drifted from the facts.

> **Lühidalt eesti keeles.** Isiklik eesti keele LLM-testide sari (EE1–EE6), mille ehitasin kohalike mudelite valimiseks oma eestikeelsetele töövoogudele. Mõõdetakse vormi (käänded, verbid, arvsõnad, õigekiri), struktureeritud väljavõtet (otsus, fakt, olek, tekstis peituv juhis) ja toimetamist ilma sisu muutmata. Kõik hindajad on deterministlikud. Täielikud testikomplektid on külmutatud ja hoitakse kinnisena (saastumise vältimiseks); siin on näidised, hindaja ja tulemused.

## What is measured

| Suite | Items | What it tests | Validator |
|---|---|---|---|
| **EE1–EE3** | 60 | Understanding real conversational Estonian: typos, slang, mixed language, humour, irony, how a discussion and its decisions evolve | choice / structured extraction / rubric checks |
| **EE4 "form"** | 20 | Case and agreement, verb forms, numerals written out, spelling and punctuation | `one_of` (exact accepted forms) |
| **EE5 "extraction"** | 20 | Find the decision that is actually in force, extract facts (date, amount, responsible person), detect an instruction hidden inside the text, list unanswered questions | `json_exact` |
| **EE6 "editing"** | 16 | Fix grammar and punctuation **without** changing names, numbers, decision status, negation, uncertainty or who-did-what | rule-based editor check (see below) |

EE1–EE3 are built from privacy-reviewed excerpts of real conversations, so they are not published. EE4–EE6 were written from scratch; a sample of each is in [`samples/`](samples/).

## Design rules

- **Deterministic scoring only.** No LLM-as-judge. Every pass or fail can be traced to a rule.
- **Frozen before the first run.** A suite and its answer key are reviewed by a second reviewer, then frozen and hashed. Any later key fix is a new version with a written reason (EE4 v1.1), never a silent edit.
- **Held out.** Full suites stay private so they do not leak into training data. Each sample file carries the SHA-256 of the frozen full suite.
- **Same conditions for every model.** llama.cpp, temperature 0, same prompts, same token limit; reasoning on and off are run and reported separately.
- **Every failure gets read.** Raw outputs are kept, and a failure is checked by hand to tell a model error from a test error.

The EE6 validator is the most interesting one. Besides "is the error fixed" and "are protected names and numbers unchanged", it has an **alarm bell**: it counts status words (decided, considering, cancelled …), negations and uncertainty markers in the source and in the answer. "Telos *kaalub* plaani kinnitamist" (*is considering approving*) silently becoming "Telos *kinnitas* plaani" (*approved*) reads perfectly and is completely wrong. That is exactly the failure this catches. Details in [METHODOLOGY.md](METHODOLOGY.md).

## Headline results

Local models on one consumer laptop GPU (RTX 5070 Ti, 12 GB), llama.cpp, temperature 0. Full tables in [RESULTS.md](RESULTS.md).

| Model (quant) | EE1–3 /60 | EE4 /20 | EE5 /20 | EE6 /16 |
|---|---|---|---|---|
| Qwen3.6-35B-A3B (Q4_K_M) | – | 14\* | 20\* | **15** |
| Gemma-4-12B-it (Q4_K_M) | **54** | 12 | **20** | 13 |
| Qwen3.5-9B (Q4_K_M) | 53 | 11 | 17 | 9 |
| Llama-3.1-EstLLM-8B (Q4_K_M) | 53 | 11 | **5** | 11 |
| Gemma-2-9B-it (Q5_K_M) | 50 | 10 | 19 | 6 |

\* reasoning on; all other cells reasoning off.

What I learned:
1. **Estonian fluency and instruction-following are different skills.** The Estonian-tuned EstLLM-8B is strong on language form and editing, but scored 5/20 on EE5, where the answer has to be one exact JSON object: code fences it was told not to use, unnormalised dates, wrong decision status.
2. **"Thinking" did not help editing, and it hurt small models.** With reasoning on, Qwen3.5-9B fell from 9/16 to 4/16 on EE6. In 12 of 16 cases it used up the token budget before answering. The largest model scored the same both ways.
3. **Easy suites saturate fast.** On EE1–EE3 the top five models ended up 1–4 points apart. That is why EE4–EE6 exist: harder, narrower, and built around one failure each.

## Repository

```
samples/       4 public items from each of EE4, EE5, EE6 (with the frozen suite's SHA-256)
validators/    validator_ee6.py (editing), basic.py (exact / one_of / json_exact), check.py
RESULTS.md     all runs, reasoning on vs off, speed
METHODOLOGY.md how items are written, reviewed, frozen and scored
```

Check your own model's answers against a sample:

```bash
python validators/check.py samples/ee6_editing_sample.json answers.jsonl
# answers.jsonl: one {"id": "...", "output": "..."} per line
```

Names that appear in items (Telos, Calvion, Sol …) are names of my own projects' agents and roles. In the tests they are just proper nouns that must survive editing unchanged.

## About

Built by Steve, a self-taught builder in Estonia (TCalvion Tech OÜ). Native Estonian, fluent Finnish, working English. I design evaluations and adversarial probes for the AI agents that build my software; see [How I run an AI build operation](https://github.com/TCalvion/How-I-Run-An-AI-Build-Operation).

Code in `validators/` is MIT licensed. The sample items in `samples/` are licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). See [LICENSE](LICENSE).
