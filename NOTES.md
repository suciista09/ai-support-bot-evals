# Notes: TokoKita support bot

## 28 Oct: Surabaya late-parcel case
- **Before:** customer said "4 hari". Bot assumed the parcel was late (3-day estimate),
  but 4 calendar days may be under 3 working days.
- **Root cause:** SHP-01 didn't say how to handle calendar vs working days.
- **Fix:** clarified SHP-01 (exclude weekends and holidays, ask for the order date).
- **After:** bot explains working days and asks for the order date. ✅

## 28 Oct: other findings
- Field name mismatch: `need_human` in the code vs `needs_human` in the policy. Renamed.
- `rules_applied` was undefined, so the bot listed every related rule. Defined it in the prompt.

## 1 Nov: Week 1 reflection
(fill in on Sunday)