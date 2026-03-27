# InsureX Core Business Logic

Claude, please implement the following strict business logic rules.

## 1. Dynamic Premium Calculation
Base Rate for insurance is ₹25.
Premium should be calculated dynamically.
`Risk Score` (0.0 to 1.0) is based on historical mocked data for that zone (heat days, rain freq).
`Premium = 25 * (1 + risk_score)`

## 2. Claim Trigger Logic (Background Polling)
Use APScheduler to poll every 60 minutes for `extreme_heat` and `heavy_rain`.
**Thresholds:**
- Extreme Heat: >43°C for 2+ hours (Payout: ₹200)
- Heavy Rain: >50mm in 3 hours (Payout: ₹200)
- Platform Outage: 30 mins downtime (Payout: ₹150)

If threshold breached -> Push Event to Redis Queue.

## 3. Claim Async Processor
When Event is popped from Redis Queue:
1. Find all active policies in Event Zone.
2. For each user, run Fraud Detection (`fraud_score`).
3. If `fraud_score < 0.3` -> auto approve.
4. If `0.3 <= fraud_score < 0.6` -> delayed approve.
5. If `fraud_score >= 0.6` -> flag/hold.

## 4. Payout Logic
When Claim is approved:
1. `wallet.balance += claim_amount`
2. Create `wallet_transaction` for ledger history.
3. Update `claim.status = 'paid'`.
