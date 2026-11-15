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
    language: Literal["id", "en", "mixed"] = Field(
        description=(
            "Main language of the customer's message. "
            "Use 'mixed' when it contains an English phrase or clause, in the same "
            "sentence or a separate one. Single English terms common in Indonesian "
            "(refund, voucher, COD, order, policy, request) do not count. "
            "Examples: 'Saya mau refund vouchernya' -> id. "
            "'Barangnya udah sampai tapi the box is damaged' -> mixed. "
            "'I want to use my voucher. Boleh nggak minta reactivate?' -> mixed."
        )
    )
    intent: Literal["refund", "shipping", "voucher", "other"] = Field(
        description="intent is what the customer is asking for (refund) or the topic of the problem (shipping)."
    )
    needs_human: bool
    rules_applied: list[str] = Field(description="Policy rules IDs checked, e.g ['REF-01']")
    answer: str

SYSTEM_PROMPT = f"""You are the customer service assistant for TokoKita, an Indonesian online marketplace.
Answer ONLY from the policy below and follow every rule exactly.
In rules_applied, list every policy rule you checked for this question,
including a rule whose exception sent you to another rule (e.g. REF-02 -> REF-03). 
In the answer, only explain the rules the customer needs for their situation. Do not mention rules you checked that do not apply.
Do not list TON-01 or TON-02. List TON-03 only when the policy did not cover the question. Never mention rule IDs (like REF-01) or internal field names in the answer.
Rule IDs belong only in rules_applied

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
        "Can I use a shipping voucher and a product voucher together?"
    ]

    for sample in samples:
        print("CUSTOMER:", sample)
        print(answer(sample).model_dump_json(indent=2))
        print("-" * 60)