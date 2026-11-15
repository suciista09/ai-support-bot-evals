import pytest

from bot import answer


CASES = [
    {
        "id": "shipping-4-days-not-arrived",
        "message": "Halo kak, paket saya belum sampai udah 4 hari, saya di Surabaya, based on policy, harusnya saya sudah bisa ajukan request refund kan?",
        "intent": ["shipping", "refund"],
        "language": "id",
        "needs_human": False,
        "must_include_rules": ["SHP-01", "SHP-02"],
    },
    {
        "id": "voucher-combine-shipping-product",
        "message": "Can I use a shipping voucher and a product voucher together?",
        "intent": "voucher",
        "language": "en",
        "needs_human": False,
        "must_include_rules": ["VOU-02"],
    },
    {
        # Boundary pair 1/2: courier says SHIPPED (in transit) -> not a dispute, follow SHP-01
        "id": "cod-shipped-not-arrived",
        "message": "Hello, saya mau refund barang COD karena sampai hari ini belum saya terima. Saya sudah menghubungi kurir tapi katanya barangnya sudah dikirim. Apa yang harus saya lakukan?",
        "intent": ["shipping", "refund"],
        "language": "id",
        "needs_human": False,
        "must_include_rules": ["SHP-01", "REF-05"],
        "must_not_contain": ["agen manusia", "human agent"],
    },
    {
        # Boundary pair 2/2: courier says DELIVERED but customer didn't receive -> dispute, ESC-05
        "id": "cod-delivered-not-received",
        "message": "Hello, saya mau refund barang COD karena sampai hari ini belum saya terima. Saya sudah menghubungi kurir tapi katanya barangnya sudah terkirim. Apa yang harus saya lakukan?",
        "intent": ["shipping", "refund"],
        "language": "id",
        "needs_human": True,
        "must_include_rules": ["ESC-05"],
    },
    {
        "id": "extended-voucher-expired",
        "message": "Hi, I want to use my voucher but it is expired. Dan nggak fair dong ini lewat expired karena order yang pakai voucher ini cancel. Boleh nggak minta reactivate vouchernya?",
        "intent": "voucher",
        "language": "mixed",
        "needs_human": True,
        "must_include_rules": ["VOU-04", "VOU-05", "ESC-03"],
    },
    {
        "id": "escalation-request",
        "message": "I feel frustrated talking with bot like you. I want to talk to a human agent.",
        "intent": "other",
        "language": "en",
        "needs_human": True,
        "must_include_rules": ["ESC-04"],
    },
    {
        "id": "request-refund-rejected-evidence-sent",
        "message": "Hi, why my refund requuest is rejected? The item is damaged and I have sent the photo in attactment.",
        "intent": "refund",
        "language": "en",  
        "needs_human": True,
        "must_include_rules": ["ESC-06"],
    },
    # TRAP: no price given; bot must infer iPhone 18 Pro Max > Rp 10 juta
    {
        "id": "refund-over-10-juta",
        "message": "Hello, tolong bantu untuk refund iphone 18 pro max baru. Barangnya sudah saya terima tapi rusak.",
        "intent": "refund",
        "language": "id",
        "needs_human": True,
        "must_include_rules": ["ESC-01"],
    }, 
    {
        "id": "refund-changed-mind",
        "message": "Hello kak, saya mw refund soalnya udah nggak butuh lagi. Barangnya masih blum dibuka apakah bisa dikembalikan?",
        "intent": "refund",
        "language": "id",
        "needs_human": False,
        "must_include_rules": ["REF-01", "REF-02", "REF-05"],
    },
    {
        
        "id": "refund-damaged-item",
        "message": "Kak, kemarin saya beli barang pas promo 12.12, tapi sayang sekali barangnya rusak. Tolong bantu refundnya ya",
        "intent": "refund",
        "language": "id",
        "needs_human": False,
        "must_include_rules": ["REF-02","REF-03"],
        "must_not_contain": ["tidak bisa refund", "non-refundable"]
    },
    {
        "id": "voucher-not-working",
        "message": "kak voucher gw kok ga bisa dipake sih?? udh belanja 80rb loh",
        "intent": "voucher",
        "language": "id",
        "needs_human": False,
        "must_include_rules": ["VOU-01"],
    },
    {
        # Out of scope: unrelated to TokoKita -> decline politely, no human
        "id": "out-of-scope-itinerary",
        "message": "Kak, bantu buat itinerary liburan ke Bali dong, aku mau ke pantai dan ke gunung",
        "intent": "other",
        "language": "id",
        "needs_human": False,
        "must_include_rules": ["TON-04"],
        "must_not_contain": ["agen manusia", "human agent"],
    },

]

@pytest.mark.parametrize("case", CASES, ids=[case["id"] for case in CASES])
def test_bot(case):
    reply = answer(case["message"])
    print(f"Test case {case['id']}. Reply: {reply.answer}")  
    
    allowed = case["intent"] if isinstance(case["intent"], list) else [case["intent"]]
    assert reply.intent in allowed, f"intent {reply.intent} not in {allowed}"
    
    assert reply.language == case["language"], f"expected {case['language']}, got {reply.language}"
    assert reply.needs_human == case["needs_human"]
    
    for rule in case["must_include_rules"]:
        assert rule in reply.rules_applied, f"missing {rule}, got {reply.rules_applied}"
      