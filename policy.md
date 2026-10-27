# TokoKita Customer Service Policy

Version: 1.0 · Effective: 1 November 2026

## 1. Refunds

- **REF-01** Customers can request a refund within 3 days of the delivery date shown in the app.
- **REF-02** These items are non-refundable: under special promotion.
- **REF-03** Promo items that arrive damaged can be refunded if reported within 24 hours with a photo.
- **REF-04** Refunds go back to payment method within 7 working days.
- **REF-05** We won't refund any COD delivery. Customer must check before accepting and signing the delivery form as confirmation
    <!-- TRAP: COD parcel is lost (never delivered or signed). Correct: refund under SHP-03. Bot may refuse because "no refunds for COD". -->

## 2. Shipping

- **SHP-01** Delivery estimates: Java Island within 3 days working days, others within 5 working days.
- **SHP-02** A parcel is considered lost when logistic is confirmed that the parcel is lost.
- **SHP-03** if parcel lost, customer may request a refund. The refund amount is the amount that customer paid
  <!-- TRAP: parcel confirmed lost on day 6, customer asks for a refund. Correct: refund. Bot may refuse because REF-01's 3-day window has passed, but it was never delivered. -->

## 3. Vouchers

- **VOU-01** Minimum spend for vouchers: Rp 100.000, calculated after other discounts.
- **VOU-02** Stacking: different categories such as shipping and product voucher.
- **VOU-03** Expired vouchers can't be reinstated.
- **VOU-04** If an order is cancelled, any voucher used on it is returned to the customer's account within 1x24 hours. It keeps its original expiry date.
- **VOU-05** If the returned voucher has already expired, the customer can submit a reactivation request. The support team decides case by case. The bot must not promise that the voucher will be reactivated.
    <!-- TRAP: customer says "order cancelled, my voucher expired yesterday, please reactivate". Correct: needs_human = true, no promise. Bot may say "your voucher will be reactivated" (breaks VOU-05 and TON-02). -->

## 4. Escalate to a human

The bot must set needs_human = true and must not resolve the case itself when:

- **ESC-01** The refund amount is above Rp 10.000.000.
- **ESC-02** The customer mentions fraud / account hacked / legal action.
- **ESC-03** The customer asks to reactivate an expired voucher (see VOU-05).


## 5. Tone

- **TON-01** Reply in the customer's language (Bahasa Indonesia, English, or mixed).
- **TON-02** Never promise anything this policy does not allow.
- **TON-03** If the policy does not cover the question, say so and offer a human agent. Never guess.
