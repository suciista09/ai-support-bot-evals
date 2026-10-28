from pathlib import Path
import re
from typing import Literal

import anthropic
from dotenv import load_dotenv
from pydantic import BaseModel, Field


load_dotenv()
client = anthropic.Anthropic()

MODEL = "claude-haiku-5-5"
POLICY_FILE = Path(__file__).parent / "policy.md"

def load_policy()->str:
    text = POLICY_FILE.read_text(encoding="utf-8")
    return re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)

class BotReply(BaseModel):
    language: Literal["id", "en", "mixed"]
    intent: Literal["refund", "shipping", "voucher", "other"]
    needs_human: bool
    rules_applied: list[str] = Field(description="Policy rules IDs used, e.g ['REF-01']")
    answer: str

SYSTEM_PROMPT = f"""You are the customer service assistant for TokoKita, an Indonesian online marketplace.
Answer ONLY from the policy below and follow every rule exactly. In rules_applied, list only the rules that decided your answer.
Do not list TON-01 or TON-02. List TON-03 only when the policy did not cover the question.

<policy>
{load_policy()}
</policy>"""

def answer(message: str) -> BotReply:
    response = client.messages.parse(
        model=MODEL,
        max_tokens=4000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": message}],
        output_format=BotReply,
    )

    return response.parsed_output

if __name__ == "__main__":
    samples = [
        "Halo kak, paket saya belum sampai udah 4 hari, saya di Surabaya",
        "Can I use a shipping voucher and a product voucher together?",
    ]

    for sample in samples:
        print("CUSTOMER:", sample)
        print(answer(sample).model_dump_json(indent=2))
        print("-" * 60)