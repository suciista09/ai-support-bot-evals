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
        #EXPECTED: intent=['shipping'], mixed, needs_human=False, rules_applied must include 'SHP-01', 'SHP-02', 'SHP-03'.
        # Must NOT agree refund is possible yet; should explain working days / ask order date.
        "Halo kak, paket saya belum sampai udah 4 hari, saya di Surabaya, based on policy, harusnya saya sudah bisa ajukan request refund kan?",
        #EXPECTED: intent=['voucher'], en, needs_human=False, rules_applied=['VOU-02'].
        # explain the policy about combining different voucher categories is possible.
        "Can I use a shipping voucher and a product voucher together?",
        #EXPECTED: intent= shipping or refund (either OK), language= mixed, needs_human=True, rules_applied must include: ESC-05
        #answer must: explain a refund is possible only if the parcel is confirmed lost (SHP-02/SHP-03),
        #            and say the case is being passed to the team to investigate
        #answer must NOT: promise a refund, or refuse it because it's COD
        "Hello, saya mau refund barang COD karena sampai hari ini belum saya terima. Saya sudah menghubungi kurir tapi katanya barangnya sudah dikirim. Apa yang harus saya lakukan?",
        #EXPECTED: intent=['voucher'], mixed, needs_human=True, rules_applied=['VOU-04','VOU-05', 'ESC-03'].
        # Must explain the policy about expired vouchers and the escalation process.
        "Hi, I want to use my voucher but it is expired. Dan nggak fair dong ini lewat expired karena order yang pakai voucher ini cancel. Boleh nggak minta reactivate vouchernya?",
        #EXPECTED: intent=['other'], en, needs_human=True, rules_applied=['ESC-04'].
        "I feel frustrated talking with bot like you. I want to talk to a human agent.",
        #EXPECTED: intent=['refund'], en, needs_human=True, rules_applied=['REF-03'].
        # Must explain the refund process REF-03 and escalate to human agent (ESC-04)
        "Hi, why my refund requuest is rejected? The item is damaged and I have sent the photo in attactment.",
    ]

    for sample in samples:
        print("CUSTOMER:", sample)
        print(answer(sample).model_dump_json(indent=2))
        print("-" * 60)