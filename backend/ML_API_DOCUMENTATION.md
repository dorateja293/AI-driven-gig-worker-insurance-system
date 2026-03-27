# InsureX ML API Documentation

Complete API reference for ML-powered endpoints.

---

## 🔥 ML Endpoints

All ML endpoints are prefixed with `/api/ml/`

---

## 1️⃣ Calculate Premium

**Endpoint:** `POST /api/ml/calculate-premium`

**Description:** Calculate insurance premium using ML risk scoring algorithm.

### Request (Option 1: By Zone)

```json
{
  "zone": "Zone-A",
  "season_factor": 1.0
}
```

### Request (Option 2: Custom Parameters)

```json
{
  "heat_days": 15,
  "rain_days": 12,
  "zone_risk": 0.5,
  "season_factor": 1.1
}
```

### Response

```json
{
  "risk_score": 0.45,
  "premium": 42,
  "breakdown": {
    "base_rate": 30,
    "heat_contribution": 0.2,
    "rain_contribution": 0.16,
    "zone_contribution": 0.09,
    "season_multiplier": 1.0
  }
}
```

### CURL Example

```bash
curl -X POST http://localhost:5000/api/ml/calculate-premium \
  -H "Content-Type: application/json" \
  -d '{"zone": "Zone-B", "season_factor": 1.2}'
```

---

## 2️⃣ Check Fraud

**Endpoint:** `POST /api/ml/check-fraud`

**Description:** Detect fraudulent claims using ML anomaly detection.

### Request

```json
{
  "user_id": "usr_abc123",
  "event_id": "evt_xyz789",
  "gps_movement": 12.5,
  "orders_completed": 8,
  "is_online": true,
  "nearby_claims_count": 15
}
```

**Note:** `gps_movement` can be:
- A float representing distance in km
- A list of `[lat, lon]` coordinates

### Response

```json
{
  "fraud_score": 0.1,
  "risk_level": "LOW",
  "action": "APPROVE",
  "reasons": ["Claim submitted instantly after event"],
  "details": {
    "orders_completed": 8,
    "gps_distance_km": 12.5,
    "time_to_claim_minutes": 65.5,
    "nearby_claims": 15,
    "was_online": true
  }
}
```

### Risk Levels

| Fraud Score | Risk Level | Action |
|-------------|------------|--------|
| < 0.3       | LOW        | APPROVE |
| 0.3 - 0.7   | MEDIUM     | REVIEW |
| > 0.7       | HIGH       | FLAG |

### CURL Example

```bash
curl -X POST http://localhost:5000/api/ml/check-fraud \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "usr_test123",
    "event_id": "evt_heat001",
    "gps_movement": 15.0,
    "orders_completed": 10,
    "is_online": true,
    "nearby_claims_count": 8
  }'
```

---

## 3️⃣ Predict Risk

**Endpoint:** `POST /api/ml/predict-risk`

**Description:** Predict disruption risk based on weather patterns.

### Request (With Weather Data)

```json
{
  "last_7_days_weather": {
    "temperatures": [41, 42, 43, 44, 45, 44, 43],
    "rainfall": [0, 0, 2, 1, 0, 0, 3]
  }
}
```

### Request (Auto-Generate Mock Data)

```json
{
  "zone": "Zone-D"
}
```

### Response

```json
{
  "heat_risk": 0.85,
  "rain_risk": 0.05,
  "overall_risk": 0.85,
  "recommendation": "BUY_POLICY",
  "message": "High disruption risk detected. Insurance recommended.",
  "forecast": {
    "avg_temperature": 43.1,
    "max_temperature": 45.0,
    "avg_rainfall": 0.9,
    "max_rainfall": 3.0,
    "temperature_trend": "INCREASING",
    "rainfall_trend": "STABLE"
  }
}
```

### CURL Example

```bash
curl -X POST http://localhost:5000/api/ml/predict-risk \
  -H "Content-Type: application/json" \
  -d '{
    "last_7_days_weather": {
      "temperatures": [42, 43, 44, 45, 46, 45, 44],
      "rainfall": [0, 0, 0, 0, 0, 0, 0]
    }
  }'
```

---

## 4️⃣ Insurance Urgency

**Endpoint:** `POST /api/ml/insurance-urgency`

**Description:** Get urgency score (0-10) for buying insurance.

### Request

```json
{
  "zone": "Zone-B",
  "last_7_days_weather": {
    "temperatures": [40, 41, 42, 43, 44, 43, 42],
    "rainfall": [5, 8, 3, 0, 2, 6, 4]
  }
}
```

### Response

```json
{
  "urgency_score": 7,
  "urgency_level": "CRITICAL",
  "action": "Buy insurance immediately - high disruption risk",
  "prediction_details": {
    "heat_risk": 0.75,
    "rain_risk": 0.1,
    "overall_risk": 0.75,
    "recommendation": "BUY_POLICY",
    "message": "High disruption risk detected. Insurance recommended.",
    "forecast": {...}
  }
}
```

### Urgency Levels

| Score | Level    | Action |
|-------|----------|--------|
| 0-2   | LOW      | Insurance optional |
| 3-4   | MODERATE | Consider insurance |
| 5-6   | HIGH     | Strongly recommend |
| 7-10  | CRITICAL | Buy immediately |

---

## 5️⃣ Auto-Claim (Complete Flow)

**Endpoint:** `POST /api/ml/auto-claim`

**Description:** Process automatic claim with ML fraud detection and instant payout.

### Request

```json
{
  "user_id": "usr_ravi123",
  "event_id": "evt_heat456"
}
```

### Response (Approved)

```json
{
  "claim_id": "clm_abc789",
  "status": "paid",
  "payout_amount": 200.0,
  "fraud_analysis": {
    "fraud_score": 0.2,
    "risk_level": "LOW",
    "action": "APPROVE",
    "reasons": ["Claim submitted instantly after event"],
    "details": {
      "orders_completed": 10,
      "gps_distance_km": 14.2,
      "time_to_claim_minutes": 0.5,
      "nearby_claims": 12,
      "was_online": true
    }
  }
}
```

### Response (Flagged)

```json
{
  "claim_id": "clm_xyz123",
  "status": "flagged",
  "payout_amount": 200.0,
  "fraud_analysis": {
    "fraud_score": 0.9,
    "risk_level": "HIGH",
    "action": "FLAG",
    "reasons": [
      "No orders completed before event",
      "GPS shows static position (minimal movement)",
      "User was offline during event period",
      "High nearby claims (75) - potential fraud ring"
    ],
    "details": {...}
  }
}
```

### Flow Diagram

```
1. Check active policy ✓
2. Verify event zone matches user zone ✓
3. Check if claim already exists ✓
4. Run ML fraud detection (4-layer analysis)
   ├─ GPS consistency check
   ├─ Activity validation
   ├─ Movement pattern analysis
   └─ Cluster detection (fraud rings)
5. Determine payout amount
6. Create claim with fraud score & risk level
7. Execute action:
   ├─ APPROVE → Instant payout to wallet
   ├─ REVIEW  → Mark as pending
   └─ FLAG    → Mark as flagged for manual review
```

### CURL Example

```bash
curl -X POST http://localhost:5000/api/ml/auto-claim \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "usr_ravi123",
    "event_id": "evt_heat456"
  }'
```

---

## 🔬 Testing Workflow

### Complete Demo Flow

```bash
# 1. Register a user
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Ravi Kumar",
    "phone": "9876543210",
    "city": "Hyderabad",
    "zone": "Zone-D",
    "platform": "Swiggy"
  }'

# Save the returned user_id

# 2. Top up wallet
curl -X POST http://localhost:5000/api/wallet/top-up \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "usr_xxx",
    "amount": 100
  }'

# 3. Get premium quote
curl -X POST http://localhost:5000/api/ml/calculate-premium \
  -H "Content-Type: application/json" \
  -d '{
    "zone": "Zone-D",
    "season_factor": 1.2
  }'

# 4. Check disruption risk
curl -X POST http://localhost:5000/api/ml/predict-risk \
  -H "Content-Type: application/json" \
  -d '{
    "zone": "Zone-D"
  }'

# 5. Purchase policy
curl -X POST http://localhost:5000/api/policy/purchase \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "usr_xxx",
    "premium_amount": 48
  }'

# 6. Simulate extreme heat event
curl -X POST http://localhost:5000/api/events/simulate \
  -H "Content-Type: application/json" \
  -d '{
    "zone": "Zone-D",
    "type": "extreme_heat",
    "value": "45",
    "duration_hours": 2.5
  }'

# Save the returned event_id

# 7. Process auto-claim with ML fraud detection
curl -X POST http://localhost:5000/api/ml/auto-claim \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "usr_xxx",
    "event_id": "evt_xxx"
  }'

# 8. Check updated wallet balance
curl -X GET "http://localhost:5000/api/wallet?user_id=usr_xxx"
```

---

## 📊 ML Module Logic

### Module 1: Premium Calculator

**Formula:**
```
risk_score = (0.4 × heat_norm) + (0.4 × rain_norm) + (0.2 × zone_risk)

premium = base_rate × (1 + risk_score) × season_factor

Adjustments:
- Safe zone (risk < 0.3) → -₹2
- High-risk zone (risk > 0.7) → +₹5
- Minimum premium: ₹20
```

### Module 2: Fraud Detector

**Rules:**
```
fraud_score = 0

IF orders_completed == 0         → +0.3
IF gps_distance < 0.5 km         → +0.3
IF time_to_claim < 5 min         → +0.1
IF user offline during event     → +0.2
IF nearby_claims > 50            → +0.4
ELSE IF nearby_claims > 20       → +0.2

Clamp: 0.0 ≤ fraud_score ≤ 1.0

Actions:
- fraud_score < 0.3  → APPROVE
- 0.3 ≤ score < 0.7  → REVIEW
- fraud_score ≥ 0.7  → FLAG
```

### Module 3: Disruption Predictor

**Logic:**
```
heat_risk = 0
IF avg_temp > 40°C     → +0.5
IF max_temp > 43°C     → +0.5
IF avg_temp > 35°C     → +min((avg - 35)/10, 0.3)

rain_risk = 0
IF avg_rain > 30mm     → +0.5
IF max_rain > 50mm     → +0.5
IF avg_rain > 15mm     → +min((avg - 15)/30, 0.3)

overall_risk = max(heat_risk, rain_risk)

Recommendation:
- risk > 0.5  → BUY_POLICY
- risk > 0.3  → CONSIDER_POLICY
- risk ≤ 0.3  → SAFE
```

---

## ⚙️ Error Responses

All endpoints return standard error format:

```json
{
  "error": "Error message description"
}
```

### Common Errors

| Status Code | Meaning |
|-------------|---------|
| 400 | Bad Request (missing parameters) |
| 404 | Resource not found (user, event, policy) |
| 409 | Conflict (duplicate claim) |
| 500 | Internal server error |

---

## 🎯 Quick Reference

### Base URL
```
http://localhost:5000/api/ml
```

### All Endpoints
```
POST /calculate-premium    # Get premium quote
POST /check-fraud          # Run fraud detection
POST /predict-risk         # Weather risk forecast
POST /insurance-urgency    # Urgency score (0-10)
POST /auto-claim           # Complete auto-claim flow
```

### Response Times
- Premium calculation: ~5ms
- Fraud detection: ~10ms
- Risk prediction: ~5ms
- Auto-claim (full): ~50-100ms

---

**Last Updated:** 2026-03-25
**Version:** 1.0
**ML Stack:** Python, Scikit-learn, Pandas
