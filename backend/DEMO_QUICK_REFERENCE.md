# 🎯 InsureX Demo - Quick Reference Card

## 📍 THE ONE COMMAND YOU NEED

```bash
curl -X POST http://localhost:5000/api/demo/run \
  -H "Content-Type: application/json" \
  -d '{
    "worker_name": "Ravi Kumar",
    "zone": "Zone-D",
    "event_type": "HEAT"
  }'
```

---

## 🎬 2-Minute Demo Script

### Setup (30 seconds)
```bash
cd backend
python run.py
# Wait for: "🚀 Starting InsureX Backend Server"
```

### Demo (60 seconds)

#### Part 1: Show the Problem (10 seconds)
> "Delivery workers face extreme heat, rain, and platform outages daily.
> Traditional insurance is too slow - claims take days.
> What if we could pay them **instantly** using AI?"

#### Part 2: Run the Demo (10 seconds)
```bash
# Run in separate terminal or use test_demo.py
curl -X POST http://localhost:5000/api/demo/run \
  -d '{"worker_name": "Ravi Kumar", "zone": "Zone-D", "event_type": "HEAT"}'
```

#### Part 3: Explain What Happened (40 seconds)
> "Watch what our system just did in under 2 seconds:
>
> 1. **Registered Ravi** - Swiggy partner in Zone-D
> 2. **Calculated Premium** - AI analyzed risk: ₹57 for 7 days
> 3. **Triggered Event** - Extreme heat: 45°C
> 4. **Ran Fraud Detection** - ML checked GPS, orders, activity
>    - Fraud score: 0.00 (legitimate worker)
> 5. **Instant Payout** - ₹200 credited to wallet immediately
>
> **Result:** Ravi paid ₹57, received ₹200. Net gain: ₹143.
> **Processing time:** 85 milliseconds."

---

## 📊 Key Numbers to Mention

| Metric | Value | Impact |
|--------|-------|--------|
| Processing Time | <100ms | Real-time |
| Fraud Score | 0.00 | Legitimate |
| Payout | ₹200 | Instant |
| Premium | ₹57 | Risk-based |
| ROI | 3.5x | High value |
| Approval Rate | 95%+ | Efficient |

---

## 🎯 Response Fields to Show

```json
{
  "demo_summary": "Extreme heat wave strikes...",

  "narration": {
    "step_1": "✅ Ravi Kumar registered in Zone-D",
    "step_2": "✅ Purchased ₹57 policy",
    "step_3": "⚡ Extreme heat → 1 approved → ₹200 paid",
    "step_4": "💰 Final balance: ₹243.00"
  },

  "claim_automation": {
    "processing_time_ms": 85,
    "approved": 1,
    "total_payout": 200.0
  },

  "user_claim": {
    "status": "paid",
    "fraud_score": 0.0,
    "risk_level": "LOW"
  }
}
```

---

## 🔥 Talking Points (Pick 3-5)

1. ✅ **Fully Automated** - Zero manual intervention
2. ✅ **Real-Time** - Claims processed in <100ms
3. ✅ **AI-Powered** - ML fraud detection & risk scoring
4. ✅ **Instant Payouts** - Money in wallet immediately
5. ✅ **Fraud-Resistant** - 5-layer detection system
6. ✅ **Scalable** - Handles 50+ workers per event
7. ✅ **Parametric** - Auto-triggers on weather data

---

## 💡 If Asked Questions

**Q: How do you prevent fraud?**
> "5-layer ML fraud detection: GPS movement, order activity, claim timing,
> online status, and cluster detection for fraud rings. Workers get fraud
> scores 0-1, and only low scores (<0.3) get instant payouts."

**Q: How do you calculate premiums?**
> "AI analyzes: heat days (40%), rain days (40%), zone risk (20%).
> Zone-D is high-risk → ₹57. Zone-C is safe → ₹34."

**Q: What triggers payouts?**
> "Parametric triggers: Temp >43°C, Rain >50mm, Platform downtime >30min.
> When met, system auto-detects affected workers and processes claims."

**Q: How fast is it?**
> "Complete claim processing in <100ms. From event detection to wallet
> credit takes under 2 seconds."

**Q: Can it scale?**
> "Yes! One event can process 50+ workers simultaneously. Each claim is
> evaluated independently with ML fraud detection."

---

## 🎭 Alternative Demo Scenarios

### Scenario A: Multiple Workers
```bash
# Show claim automation for many workers
curl -X POST http://localhost:5000/api/demo/trigger-event \
  -d '{"event_type": "RAIN", "zone": "Zone-B"}'

# Show: "15 workers affected, 12 approved, ₹2400 paid out"
```

### Scenario B: Different Events
```bash
# Show variety
curl -X POST http://localhost:5000/api/demo/run -d '{"event_type": "RAIN"}'
curl -X POST http://localhost:5000/api/demo/run -d '{"event_type": "OUTAGE"}'
curl -X POST http://localhost:5000/api/demo/run -d '{"event_type": "SMOG"}'
```

### Scenario C: Stats Dashboard
```bash
# Show system stats
curl -X GET http://localhost:5000/api/demo/stats

# Show: total events, approval rate, total payout
```

---

## 🚨 Troubleshooting

**Server not running?**
```bash
cd backend
python run.py
```

**Test before demo?**
```bash
python test_demo.py
```

**Need to reset?**
```bash
curl -X POST http://localhost:5000/api/demo/reset
```

**Want to see logs?**
Look at terminal where `python run.py` is running - you'll see emoji logs!

---

## 🎯 Success Indicators

After demo, you should be able to show:

- ✅ Processing speed: <100ms
- ✅ Fraud score: 0.00 (legitimate)
- ✅ Status: "paid" (instant)
- ✅ Payout: ₹200 (credited)
- ✅ Net gain: ₹143 (ROI)

---

## 🎉 Closing Statement

> "This is parametric insurance reimagined. No paperwork, no waiting,
> no fraud. Just instant protection for India's 10 million gig workers.
>
> From event detection to payout: **Under 100 milliseconds.**
>
> That's InsureX."

---

**Pro Tip:** Practice the demo once before presenting. The endpoint is idempotent - you can run it multiple times!

**Last Updated:** 2026-03-25
**Status:** ✅ READY TO WOW JUDGES
