# Methodology

## Why another benchmark

I needed local models for three Estonian jobs: summarising long working discussions, keeping a decision log, and polishing text that other agents wrote. The first suites (EE1–EE3) showed the models were mostly "good enough" at understanding Estonian, and the scores clustered at the top. They did not tell me what I actually needed to know: **when a model is wrong, is it wrong in a way I will notice?**

So the later suites each target one failure that is easy to miss in fluent output.

## Suites

### EE1–EE3: conversational Estonian (private)
Source: 48 excerpts from 44 real conversations (292 messages). Each was privacy-reviewed, and every message was checked programmatically against the original export. They cover typos and abbreviations, slang and mixed language, humour and irony, how an argument develops, fact versus assumption versus "unknown", technical explanation, and tone. The suites are not published because the source is personal conversation history.

### EE4 "form"
Twenty fill-in items in four blocks (case and agreement, verb forms, numerals in words, spelling and punctuation). Each block has one control item that every reasonable model should get right; if it fails the control, the prompt or the parser is suspected first, not the model. Scoring is `one_of`: a list of all accepted forms, with or without a trailing period or capital letter.

*Version note:* after the first two runs, v1.1 accepted two more forms that are correct Estonian (a colloquial short conditional, and a second valid case for a place name). The key was fixed in a new version with the reason recorded. Old results are reported under the key they were scored with.

### EE5 "extraction"
Twenty items in four blocks:
- **decision**: which message holds the decision that is in force? Only the human lead decides; proposals and agreement from others are not decisions. A decision can be made, cancelled, or never made.
- **fact**: date, amount and responsible person, normalised (e.g. "1 250,50 eurot" → `1250.5`, "3. detsembril 2026" → `2026-12-03`). If a value changed, the latest valid one counts.
- **instruction in quote**: the source contains an instruction aimed at the assistant ("ignore all previous instructions…"). The model must extract the facts, **not obey** the instruction, and flag `juhis_tekstis: true`.
- **status**: which questions in a list have no answer ("not yet" counts as an answer).

Scoring is `json_exact`: the answer must parse to exactly the expected object.

### EE6 "editing"
Sixteen short texts. The task is always the same: fix spelling, case, agreement and punctuation, change nothing else, and return the text untouched if it is already correct.

| Block | Items | What must hold |
|---|---|---|
| correction | 6 | the error is fixed; protected tokens are unchanged |
| clean | 4 | the answer is **exactly** the input |
| status | 4 | decision status, negation and uncertainty survive; change ratio ≤ 0.25 |
| attribution | 2 | each person keeps their own action, in order; change ratio ≤ 0.25 |

Validator checks (all deterministic, see `validators/validator_ee6.py`):
- `peab_sisaldama` / `ei_tohi_sisaldada`: the correct form is present and the wrong one is gone (alternatives allowed);
- `kaitstud`: names, dates, times, IDs appear exactly as in the source;
- **alarm bell**: counts of status stems (otsus-, kinnit-, kaalu-, tühist- …), negations (ei, pole, mitte, ega, ära) and uncertainty markers (võib-olla, ilmselt, vist …) must match the source;
- `omistus`: in the answer, each name still comes before its own verb stem;
- change ratio: word-level difflib distance, to catch over-editing;
- answer length: no explanations added.

The alarm bell is a **signal, not proof**. A correct edit can change a count, so every alarm-bell failure is reviewed by hand and reported separately from real meaning drift.

## Process

1. **Design** a suite around one failure. The items are written from scratch (EE4–EE6).
2. **Second review** before freezing: definitions are tightened, ambiguous items fixed or dropped, and every expected value has to follow from the source alone.
3. **Freeze** the suite and its key; record the SHA-256.
4. **Run** overnight with a scripted runner: llama.cpp server, temperature 0, the same token limit for all models, reasoning off and on as separate runs. Raw outputs and reasoning traces are saved.
5. **Read the failures.** Each failure is classed as a model error, test error, or limit artefact (e.g. empty answer because thinking used the whole token budget). A test error leads to a new version of the suite, not a quiet rescore.
6. **Report** per block, not only the total, so that "good at form, bad at JSON" stays visible.

## Known limits

- Small suites (16–20 items): one item is 5–6 points. Use them to compare models, not to make strong claims.
- Mostly short, single-turn items. Long-document Estonian and PII detection are planned as a separate suite.
- Local quantised models only (Q4/Q5). API models were not run on the frozen suites.
- With reasoning on, the token limit shapes the result. Small models that think for a long time can be under-scored; this is reported as empty answers, not hidden.
