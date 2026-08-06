# Preprocessing cases

Every case the text pipeline handles, with real input and real output. All
examples below were produced by running the actual normalizer, not written by
hand — regenerate them by pasting any row into
`VietnameseNormalizer(...).normalize(...)`.

## Order of operations

Order is load-bearing; several rules break if moved.

```
1. strip_reasoning     remove leaked <thinking> / (internal_reasoning) blocks
2. strip_markup        bold, bullets, numbered lists, headings, blockquotes
3. strip_assistant_echo   remove a quoted assistant turn (user turns only)
4. verbalize numbers   digits -> Vietnamese words, per speaker dialect
5. clean_punctuation   reduce punctuation to '.' and ','
```

**Why 4 before 5:** number rules need `-` for ranges (`6-8 tiếng`), `.` for
decimals (`38.5°C`), `/` for fractions (`140/90`) and `>` `<` for comparators.
Cleaning punctuation first destroys all of them.

**Why 3 before 4:** user and assistant get different speakers, so different
dialects — `0.8` verbalizes differently in each. Comparing before verbalization
sidesteps it.

---

## 1. Reasoning leakage

The corpus leaks the generator's private reasoning into utterance text. Seven
distinct shapes, all found in real files:

| shape | input | output |
|---|---|---|
| closed tag | `<thinking> Giai đoạn: Phase 4 </thinking> Không có gì thưa Bác.` | `Không có gì thưa Bác.` |
| literal `think` | `<think>lý luận</think>Chào bác sĩ.` | `Chào bác sĩ.` |
| mismatched brackets | `(internal_reasoning) … </internal_reasoning> Rất vui.` | `Rất vui.` |
| bare fragment, no `<` | `internal_reasoning> Xin chào bác sĩ ạ.` | `Xin chào bác sĩ ạ.` |
| typo'd closing tag | `<think> … </internal_reasony> Chị Hằng chào em.` | `Chị Hằng chào em.` |
| markdown header, no tag | `**Internal Reasoning:** … </internal_reasoning> Tôi hiểu em.` | `Tôi hiểu em.` |
| `external_reasoning` | `<external_reasoning>…</external_reasoning>Chào chị.` | `Chào chị.` |

**Deliberately not stripped:** an unclosed opening tag.
`<think>lý luận chưa đóng Chào bác.` keeps its text. Without a closing tag there
is no way to prove where reasoning ends, and deleting real speech is worse than
keeping some noise.

---

## 2. Markup

| input | output |
|---|---|
| `**Về tình trạng của em**: ổn` | `Về tình trạng của em: ổn` |
| `- Apxe hậu môn\n- Búi trĩ sa` | `Apxe hậu môn Búi trĩ sa` |
| `1. Đầu tiên\n2. Sau đó` | `Đầu tiên Sau đó` |
| `### Lưu ý quan trọng` | `Lưu ý quan trọng` |
| `> **Bác sĩ**: Chào anh.` | `Bác sĩ: Chào anh.` |

> **The corpus contains zero newlines.** Every file is one long line, so
> line-anchored rules (bullets, numbered lists, headings) barely fire in practice
> and stray `-` and `>` survive into the text. This is why `clean_punctuation`
> exists as a backstop and why echo detection matches on a canonical
> letters/digits form rather than verbatim text.

---

## 3. Number verbalization

Rules are ordered; the comments in `textprep.py` record which pairs are
order-sensitive and why.

| case | input | output |
|---|---|---|
| integer | `Bệnh nhân 67 tuổi.` | `Bệnh nhân sáu mươi bảy tuổi.` |
| 15 / 21 / 24 forms | `Có 15, 21 và 24 ca.` | `Có mười lăm, hai mươi mốt và hai mươi tư ca.` |
| zero filler | `105` / `1005` | `một trăm linh năm` / `một nghìn không trăm linh năm` |
| decimal (comma) | `Sốt 39,5 độ.` | `Sốt ba mươi chín phẩy năm độ.` |
| decimal (point) | `Sốt 38.5°C.` | `Sốt ba mươi tám phẩy năm độ C.` |
| thousands separator | `1.500.000 đồng` | `một triệu năm trăm nghìn đồng` |
| range | `Kéo dài 10-15 phút.` | `Kéo dài mười đến mười lăm phút.` |
| range + fraction | `Mức độ đau 6-7/10.` | `Mức độ đau sáu đến bảy trên mười.` |
| fraction | `Huyết áp 140/90 mmHg.` | `một trăm bốn mươi trên chín mươi mi-li-mét thuỷ ngân` |
| dose per period | `Metformin 1000mg/ngày.` | `Metformin một nghìn mi-li-gam mỗi ngày.` |
| dosing shorthand | `Uống x2/ngày.` | `Uống hai lần mỗi ngày.` |
| percentage | `Khoảng 20% bệnh nhân.` | `Khoảng hai mươi phần trăm bệnh nhân.` |
| comparators | `Sốt >38.5°C, tiểu cầu <100.` | `Sốt trên …, tiểu cầu dưới một trăm.` |
| unit | `Tiêm 5mg và 250ml.` | `năm mi-li-gam` / `hai trăm năm mươi mi-li-lít` |
| height | `Cao 1m72.` | `Cao một mét bảy hai.` (suffix read digit-by-digit) |
| area | `Diện tích 20m2.` | `Diện tích hai mươi mét vuông.` |
| roman grading | `độ III`, `type I` | `độ ba`, `type một` |
| hotline | `Gọi 115 ngay.` | `Gọi một một năm ngay.` (digit-by-digit) |
| period slash | `30 phút/ngày.` | `ba mươi phút mỗi ngày.` |
| word slash | `Anh/chị ở quận/huyện nào?` | `Anh chị ở quận huyện nào.` |

**Protected, deliberately unverbalized:** identifiers (`vitamin B12` stays `B12`)
and Latin drug names (`Amlodipine 5mg` → `Amlodipine năm mi-li-gam`).

### Dialect varies per speaker

Each speaker is pinned to one dialect derived from their id plus the run salt, so
the corpus carries regional variation instead of one flattened style.

| number | northern | southern |
|---|---|---|
| 105 | một trăm **linh** năm | một trăm **lẻ** năm |
| 1000 | một **nghìn** | một **ngàn** |
| 24 | hai mươi **tư** | hai mươi **bốn** |

`linh`/`nghìn` and `lẻ`/`ngàn` are coupled; `tư`/`bốn` is drawn independently.

### Degenerate input

A **10,433-digit run** exists in the corpus and crashed `int()`, which refuses to
parse beyond 4,300 digits — one bad utterance would abort a whole plan build.
Digit runs longer than 15 are now read digit-by-digit instead.

---

## 4. Punctuation cleanup

Runs last. Reduces punctuation to `.` and `,` — what the model reads reliably.

| rule | input | output |
|---|---|---|
| `? ! …` → `.` | `Có nguy hiểm không? Em lo lắm!` | `Có nguy hiểm không. Em lo lắm.` |
| `:` → `.` | `Chuẩn bị: nhịn ăn sáu tiếng` | `Chuẩn bị. nhịn ăn sáu tiếng` |
| spaced dash → `,` | `viêm nướu - tình trạng nướu bị viêm` | `viêm nướu, tình trạng nướu bị viêm` |
| quotes/brackets dropped | `Bác nói "cần xét nghiệm" đúng không?` | `Bác nói cần xét nghiệm đúng không.` |
| word-internal hyphen kept | `COVID-19 và hậu-COVID` | unchanged |
| runs collapsed | `Nhiều dấu... và  khoảng   trắng .` | `Nhiều dấu. và khoảng trắng.` |

**`:` is mapped, not deleted.** It is the only clause boundary in 3.1% of
oversized sentences, so deleting it would remove split points exactly where the
chunker's clause fallback needs them.

**Known cost:** the model never sees a question mark, so questions lose rising
intonation. `?` was 20.6% of all terminators (5,398 of 26,241). This was accepted
to make period-only sentence splitting viable — revisit if it sounds wrong.

---

## 5. Assistant echo

`user.txt` frequently contains a verbatim copy of an assistant turn before the
patient's reply:

```
(internal_reasoning) … </internal_reasoning>
> **Bác sĩ Meddies**: <an entire assistant turn>
Tôi đi khám ở bệnh viện phụ sản gần nhà, …          ← the real reply
```

Measured over 20,000 user utterances, compared against **every** assistant turn in
the conversation:

| | share |
|---|---|
| clean | 96.19% |
| pure echo — no patient speech at all | 3.50% |
| echo + real reply (removable) | 0.30% |

The leak is **one-directional**. An earlier scan appeared to show `assistant.txt`
quoting user content at 2.04%, but those "user" files were themselves
contaminated, so the match was the doctor's own words found twice.

**How it is detected.** Canonical letters/digits form, with the quote's first and
last 60 characters anchored **independently**. A single whole-or-prefix match ends
at the first character where the two copies differ — usually mid-sentence —
leaving the rest of the quote attached to the front of the "reply". Two anchors
tolerate any drift between them.

**Floor is 150 characters, and it matters.** The match-length distribution is
bimodal: a noise spike below 40, a valley from 40–150 holding ~160 files, then the
real population above 150. Sampling the valley found it ~50/50 — half
contaminated, half genuine short patient turns that a *later* assistant turn
quotes back, at 100% coverage, structurally identical. Nothing separates them at
that length, so the band is left alone. Keeping a contaminated utterance is
recoverable; deleting real speech is not.

**Policy: clean, never drop.** Conversations stay whole. When a file is nothing
but the quote, the original text is used — knowingly bad audio rather than a hole
in the dialogue.

---

## 6. Rejection rules

Only these drop an utterance. Everything is logged to `rejects.jsonl` with the
reason and full raw text; nothing is deleted from disk.

| reason | trigger | rate |
|---|---|---|
| `too_long` | over `text.max_chars` (3000) | 0.12% |
| `degenerate` | type-token ratio < 0.35, or an n-gram repeated > 4× | 0.04% |
| `empty_after_normalization` | nothing survives — pure markup or reasoning | 0.01% |

Total ~0.17% of rows. `empty_after_normalization` cannot be relaxed: there is no
text to speak.

---

---

## 7. Edge cases found by full-corpus scan

`scripts/scan_edge_cases.py` normalized **all 712,881 Vietnamese files** (26 min,
0 errors) and collected every token that survives unverbalized — i.e. everything
the TTS model has to guess at. Counts below are whole-corpus, not sampled.

### Reproducible rule gaps

Each row was re-run through the normalizer to confirm; none is theoretical.

| input | current output | should be | corpus count |
|---|---|---|---|
| `Chiếm 5-10% dân số.` | `năm đến mười**%**` | …mười **phần trăm** | `%` survives 1,586× |
| `Góc 45°.` | `bốn mươi lăm**°**` | …lăm **độ** | `°` survives 449× |
| `Sốt ≥ 38°C.` | `**≥** ba mươi tám độ C` | **từ** … **trở lên** | `≥`/`≤` 140× |
| `Thực phẩm giàu omega-3` | unchanged | omega **ba** | ~741× |
| `Ngủ lúc 11h30 tối.` | `mười một **giờ30**` | …giờ **ba mươi** | `giờ<dd>` 180× |
| `Chi phí 500k-1 triệu.` | `**500k-một** triệu` | năm trăm nghìn đến một triệu | `500k-` 31× |

**Why each fails.** The range rule consumes `5-10` before the percent rule sees
it, stranding `%`. The degree rule requires a following `C`, so a bare `°` is
missed. Only `>` and `<` are handled — `≥` and `≤` were never added. `omega-3` is
word-hyphen-digit, which no range rule matches. `11h30` converts `h`→`giờ` but
leaves the minutes. `500k` has no rule at all, and the range rule half-fires
across it.

The last shape is the worst: **partial verbalization produces mixed
digit/word tokens** — `500k-một`, `tục1-hai`, `1chín` (68 occurrences combined) —
which no downstream check catches.

### Residual symbols — 884,982 occurrences

| symbol | count | note |
|---|---|---|
| `(` `)` | **737,684** | never dropped; the model decides what a bracket sounds like |
| `-` | 83,120 | compounds kept deliberately, plus strays |
| `。` `，` `：` | 16,884 | **CJK fullwidth punctuation** |
| `✅ ✓ ❌ ⚠` | 9,058 | checkmarks in summary lists |
| `→` | 6,751 | reads as "leads to" in clinical reasoning |
| `+` | 6,581 | |
| `/` | 5,355 | slashes the word/period rules did not match |
| `😊 💙 🌟 🙏 👋` | 2,852 | emoji |
| `%` `°` `≥` `$` `~` `=` `&` `;` `_` `'` | ~10,000 | see gaps above |
| `�` | 908 | encoding damage in the source |

Parentheses alone outnumber every other symbol combined. They are not in
`clean_punctuation`'s drop set.

### Acronyms — 135,907 occurrences, 400+ distinct

| category | examples (with counts) |
|---|---|
| dominant | `AI` 67,322 — from "trợ lý AI" in nearly every opening turn |
| imaging / labs | `MRI` 6,860 · `ECG` 2,970 · `CT` 2,299 · `TSH` 1,434 · `CRP` 623 · `EMG` 524 · `CBC` 514 · `BMI` 391 · `LDL` 371 |
| conditions | `GERD` 1,526 · `BPPV` 742 · `COPD` 722 · `IBS` 721 · `HPV` 513 · `HTN` 442 · `AMH` 398 · `UTI` 338 |
| Vietnamese admin | `CCCD` 2,677 · `BHYT` 2,482 · `CMND` 2,462 · `BV` 517 |
| letter+digit | `HbA1c` 743 · `SpO2` 125 · `CoQ10` · `fT4` · `T3`/`T4` |
| **reasoning leakage** | `FIFE` 1,975 · `PHASE` 578 · `OPQRST` 526 · `PMH` 390 · `ROS` 390 |
| **false positives** | `NGAY` 1,879 · `QUAN` 1,357 · `AN` 697 · `KHI` 624 · `NGUY` 595 · `CHO` 486 — Vietnamese words in shouty headers |

**Open question, not a gap.** Nothing currently decides whether `MRI` should be
read letter-by-letter (`em-rờ-i`), as English (`em-ar-eye`), or expanded. VoxCPM2
guesses per occurrence, so the same acronym may differ between utterances. A
lookup table is the fix if consistency matters — this scan is the list to build
it from.

### Reasoning-leak shapes the stripper misses

The scan surfaced tag families not in `_RNAME`:

```
</phase_check> <fife_status>Đã thu thập đủ: Triệu chứng (F), Impact (I)…
Phase: GATHERING INFORMATION (Turn 5) - Moving to PHASE 3: PROVIDING STRUCTURE
**PHASE 3: PROVIDING STRUCTURE** Trước tiên, Tôi muốn xác nhận…
```

`phase_check` and `fife_status` are unknown tag names, and the bare English
scaffolding (`GATHERING INFORMATION`, `PROVIDING STRUCTURE`, `Patient Age`,
`Objective`) has no tag at all. This is the residual leakage measured at ~0.75%
of utterances.

### Corpus degeneracy

```
đi đi đi đi đi đi đi đi.,,,...,,,,,..,.,.,...,,,..,,...,.,,..,,.,.,...,..
......................,......................。... 。。 。。。。 。 。 。。。 。 。 。 。 。，。 ，，，
```

Punctuation-spam utterances exist. The `degenerate` reject rule (TTR < 0.35,
n-gram repeat > 4) is meant to catch these; whether it catches *these particular*
shapes is untested — the type-token ratio of a comma run may pass.

## Open questions

- **No text-fidelity check.** QC measures duration ratio only. A word dropped or
  swapped inside a normal-length utterance is undetectable by anything here.
- **`?` → `.`** costs question intonation across a question-heavy corpus.
- **`EnglishNormalizer` is unfit** for the English config — it verbalizes
  identifiers (`B12` → `Btwelve`).
- **Reference transcripts unused.** VIVOS ships them; they would enable VoxCPM2's
  higher-fidelity transcript-assisted cloning.
- **Six reproducible rule gaps** (§7): `%` after a range, bare `°`, `≥`/`≤`,
  `omega-3`, `11h30`, `500k`. All produce audible wrong output; none is fixed.
- **737,684 parentheses** reach the model unhandled.
- **Acronym pronunciation is undecided** — 135,907 occurrences, no lookup table.
- **`phase_check` / `fife_status` tags and bare English scaffolding** escape the
  reasoning stripper.
