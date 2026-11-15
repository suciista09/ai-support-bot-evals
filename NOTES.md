# Notes: TokoKita support bot

Eval log. Each entry: what I saw, why it happened (bot miss or policy gap), what I changed, result.

## 28 Oct 2026: first bot run

**Setup:** `bot.py` returns `BotReply` (language, intent, needs_human, rules_applied, answer) using Claude Haiku with `policy.md` as the system prompt.

| Finding | Type | Fix | Result |
|---|---|---|---|
| Field was `need_human` in code but `needs_human` in the policy | Contract mismatch | Renamed to `needs_human` | ✅ |
| "Paket belum sampai 4 hari" (Surabaya): bot said it was late, but SHP-01 is 3 *working* days | Policy gap | SHP-01 now excludes weekends and holidays, and the bot asks for the order date | ✅ Bot explains working days and asks for the date |
| `rules_applied` listed every related rule, and the answer showed rule IDs to the customer | Spec gap (field never defined) | Prompt: list only the rules that decided the answer; never show rule IDs in the answer | ✅ |

**Lesson:** the bot only knows what's written. Every gap in the spec turns into the model's own guess.

## 29 Oct 2026: first eval run (6 messages with expected results)

Wrote an `# EXPECTED` line for each message *before* running: fields, rules that must be included, what the answer must and must NOT say.

| # | Message | Result | Type | Notes |
|---|---|---|---|---|
| 1 | 4 days late, can I get a refund? (leading question) | ⚠️ Partial | Spec gap | Content correct (no refund promise). Language `id` vs expected `mixed`: "mixed" not defined |
| 2 | Shipping + product voucher together? | ✅ Pass | | |
| 3 | COD not received, courier says delivered | ⚠️ Partial | Spec gap + bot miss | ESC-05 escalation correct, no COD refusal. Replied in both languages (no rule for mixed). Did not explain "refund only if confirmed lost" (bot miss: rule existed) |
| 4 | Expired voucher after cancelled order | ✅ Pass | | TRAP held: escalated, no promise |
| 5 | "I want a human agent" | ✅ Pass | | Earlier it passed through TON-03 (bot's own judgment). Now decided by ESC-04 |
| 6 | Why was my refund rejected? (photo already sent) | ❌ Fail | Policy gap | needs_human false. No rule escalates a disputed decision. Bot also said "I can help you check further", which it can't do (broken promise, TON-02) |

**Score:** 3 pass, 2 partial, 1 fail.

**Policy changes today:** REF-01 = change-of-mind refund (sealed, no shipping fee); REF-03 covers all damaged items; REF-05 applies only to delivered and signed COD; ESC-04 (asks for a human); ESC-05 (delivery dispute).

**Next:** TON-01 reply in the customer's main language; add ESC-06 (disputed decisions the bot can't see); re-run.

**Lessons:**
- If I expect a behaviour, a rule must require it. Otherwise it passes by the model's judgment and may change next run.
- When a rule is silent, the result is undefined, not a default.
- Test what must be true ("must include ESC-03"), not an exact list.
- New rules need a regression check against existing rules (REF-01 "sealed" conflicted with damaged items).

## 15 Nov 2026: promo vs damaged refund, and what rules_applied means

**Test:** `refund-damaged-item`, a damaged item bought in the 12.12 promo. Expected `REF-02` and `REF-03`.

**Result:** ❌ Failed: `missing REF-02, got ['REF-03', 'REF-04']`. The answer itself was correct: refund allowed because the item is damaged, reported within 24 hours with a photo, full refund including shipping, 7 working days.

**Why:** test expectation vs spec. The prompt said "list only the rules that *decided* your answer". REF-02 hands damaged items to REF-03, so REF-02 was checked but did not decide. The bot followed the spec; my test expected something the spec didn't say.

| Finding | Type | Fix |
|---|---|---|
| REF-02 "special promotion" was vague | Policy gap | Defined: flash sale and double dates (10.10, 11.11, ...); exception "unless damaged (see REF-03)" |
| REF-03 didn't say whether promo items count | Policy gap | "Damaged items (including promo items)" |
| Test expected REF-02, spec said "deciding rules only" | Test expectation wrong | Redefined `rules_applied` as "every rule checked, including exceptions", in both the system prompt and the `BotReply` field description |

**Lessons:**
- A failing test is not always a bot bug. First ask: does the test follow the spec I actually wrote?
- Cross-reference exceptions by ID in both rules (REF-02 → REF-03), so the bot doesn't have to infer the link.
- When the spec changes, re-run every test (regression), not just the one that failed.
- Keep the system prompt and the field descriptions saying the same thing; mixed signals cause flaky results.

## Week 1 reflection (15 Nov 2026)

**Where things stand:** 12 test cases, 12/12 passed. All 10 original cases also passed 3 runs in a row (30/30). The `must_not_contain` check runs now and passes.

### What surprised me most
1. **The bot is only as consistent as the policy.** Most "bot problems" disappeared once I wrote clearer rules: defining "mixed" with examples, linking exceptions by ID (REF-02 → REF-03, REF-05), separating "shipped" from "delivered". I have to decide what I expect first, then write it where the model reads it.
2. **Real customers don't write like test cases.** Gaul, typos, the same meaning in different words ("dikirim" vs "terkirim") and mixed Bahasa/English all changed the result. Covering these variations is essential, not a nice-to-have.

### Bot's fault vs my spec or test
| Source | Count | Examples |
|---|---|---|
| Spec, policy or test | 9 logged, plus about 7 more from 4 and 15 Nov | "mixed" and intent undefined, COD refund rules, a test expecting a rule the spec didn't require, ambiguous test message ("dikirim") |
| Bot | 2 logged, plus 2 more | Skipped a rule that existed; promised "I can help check" (TON-02); contradicted VOU-05; guessed the iPhone price |

**About 80% of failures were in the spec, not the model.** As a QA, this is familiar: unclear requirements cause most defects.

### What I'd trust as a release gate
- **Trust now: routing.** `needs_human` and the escalation rules held across 3 runs, including the shipped/delivered boundary pair. A wrong handoff is the most costly mistake, and these checks are reliable.
- **Not yet: answer content.** I only check banned phrases (`must_not_contain`) and my own reading. Nothing automatically checks that an answer is correct and relevant, so I can't gate a release on it.

### What I'd tell a client
"All 12 scenarios pass on routing and policy rules, and they were stable across 3 runs. Answer quality is reviewed by a person and is not automated yet. I recommend human review of replies before launch. Automated answer grading is the next step."

### Next
Measure pass *rates* over more runs instead of pass/fail, and add automated content checks (judge model).
