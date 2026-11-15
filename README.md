# TokoKita support bot + evals

A bilingual (Bahasa / English) customer support bot for a fictional marketplace,
grounded in a written policy, with a pytest eval suite that checks intent,
language, escalation and which policy rules were applied.

## Run
uv sync
echo "ANTHROPIC_API_KEY=your-key" > .env
uv run pytest -v

See NOTES.md for the eval log: what failed, why, and what I changed.