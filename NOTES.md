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
