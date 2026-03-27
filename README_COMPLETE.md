# InsureX: AI-Driven Gig Worker Insurance System

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![React](https://img.shields.io/badge/React-18-blue.svg)](https://reactjs.org)
[![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)](https://flask.palletsprojects.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue.svg)](https://postgresql.org)

Smart, AI-powered insurance platform designed for food delivery gig workers (Swiggy/Zomato). Features dynamic premium calculation, automatic claim processing, and advanced fraud detection with DBSCAN clustering.

## 🌟 Key Features

### For Workers
- **AI-Powered Pricing**: Dynamic premiums based on zone weather risk
- **Automatic Claims**: Claims triggered and processed automatically when weather events occur
- **Instant Payouts**: Low fraud risk claims approved and paid immediately
- **Transparent Tracking**: Real-time wallet balance and transaction history

### For Platform
- **4-Layer Fraud Detection**:
  1. GPS Consistency Check
  2. Activity Validation
  3. Movement Pattern Analysis
  4. DBSCAN Cluster Detection (fraud ring identification)

- **Background Processing**:
  - Weather polling every 60 minutes
  - Automatic event detection and claim creation
  - Redis queue for async claim processing

- **Coverage Events**:
  - Extreme Heat (>43°C for 2+ hours) → ₹200 payout
  - Heavy Rain (>50mm in 3 hours) → ₹200 payout
  - Platform Outage (30+ min downtime) → ₹150 payout

## 🏗️ Architecture

```
┌─────────────────┐
│  React Frontend │
│  (Vite + React) │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────┐
│      Flask Backend (REST API)    │
│  - Auth (JWT)                    │
│  - Policy Management             │
│  - Premium Calculator (AI)       │
│  - Fraud Detection (4 layers)    │
└────────┬────────────────────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌──────┐  ┌───────┐
│ PostgreSQL│  │ Redis  │
│  Database │  │ Queue  │
└──────────┘  └────────┘
         │
         ▼
  ┌────────────────┐
  │ APScheduler     │
  │ - Weather Poll  │
  │ - Claim Process │
  └────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/insurex.git
cd insurex
```

### 2. Backend Setup

```bash
# Navigate to backend
cd backend

# Install dependencies
pip install -r requirements.txt

# Create PostgreSQL database
createdb insurex

# Configure environment
cp .env.example .env
# Edit .env with your database credentials and API keys

# Run backend
python run.py
```

Backend will start on http://localhost:5000

### 3. Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Run frontend
npm run dev
```

Frontend will start on http://localhost:5173

### 4. Seed Mock Data (Optional)

```bash
cd backend
python seed_mock_data.py
# Choose option 3 to seed both realistic and fraud scenario data
```

## 📖 Usage Guide

### Worker Flow

1. **Register Account**
   - Provide name, phone, city, zone, platform
   - Get JWT token for authentication

2. **Top Up Wallet**
   - Add funds to wallet balance
   - Required before purchasing policy

3. **Purchase Policy**
   - View AI-generated quote with risk score
   - Purchase 7-day coverage
   - Premium deducted from wallet

4. **Automatic Claims**
   - System monitors weather conditions
   - Claims auto-created when events occur
   - Fraud detection runs on all claims
   - Low-risk claims paid instantly

5. **Track Progress**
   - View wallet balance
   - Check claim history
   - Review transactions

### Testing with Event Simulation

To test without waiting for real weather events:

```bash
curl -X POST http://localhost:5000/api/events/simulate \
  -H "Content-Type: application/json" \
  -d '{
    "zone": "Zone-A",
    "type": "extreme_heat",
    "value": "45",
    "duration_hours": 2.5
  }'
```

This triggers automatic claim processing for all active policies in Zone-A.

## 🔒 Fraud Detection

### The Market Crash Scenario

**Threat**: A syndicate of 500 workers coordinates via Telegram, using GPS-spoofing to fake their location in a disaster zone while sitting at home, triggering mass false payouts.

**Defense**: 4-Layer Detection Pipeline

#### Layer 1: GPS Consistency
- Detects sudden coordinate jumps (teleportation)
- Identifies exact duplicate coordinates (spoofing)
- Checks for impossible speeds (>200 km/h)

#### Layer 2: Activity Validation
- Verifies platform activity before event
- Checks order count and online status
- Flags zero-activity claims

#### Layer 3: Movement Pattern
- Analyzes speed consistency
- Calculates distance traveled
- Detects static positions

#### Layer 4: Cluster Detection (DBSCAN)
**The Killer Defense**: Uses scikit-learn DBSCAN to identify fraud rings.

```python
# Genuine workers: scattered across delivery routes
# Spoofers: converge on one fake GPS coordinate

DBSCAN(eps=50m, min_samples=5)
→ Identifies clusters of 5+ users at identical location
→ Flags entire cluster as fraud ring
→ Individual fraud_score += 0.6
```

### Fraud Score Thresholds

| Score | Action | User Experience |
|-------|--------|----------------|
| 0.0-0.3 | Auto-approve | Instant payout (1-2 min) |
| 0.3-0.6 | Delayed approve | Paid within 1-2 hours |
| 0.6-0.8 | Manual review | "Under verification" |
| 0.8-1.0 | Auto-reject | "Contact support" |

## 📊 Business Logic

### Premium Calculation

```python
risk_score = (0.3 * rain_freq_norm) +
             (0.3 * heat_days_norm) +
             (0.2 * zone_risk) +
             (0.2 * seasonal_factor)

premium = BASE_RATE * (1 + risk_score)
# BASE_RATE = ₹25
# Premium range: ₹25 - ₹50
```

### Claim Processing Flow

```
Weather Event Detected
    │
    ▼
Create Event Record
    │
    ▼
Push to Redis Queue
    │
    ▼
Claim Processor Picks Event
    │
    ▼
Find Eligible Users (active policies in zone)
    │
    ▼
For Each User:
    ├─ Layer 1-3: Individual fraud checks
    └─ Calculate initial fraud_score
    │
    ▼
Layer 4: Run DBSCAN on all claimants
    │
    ▼
Update fraud_scores for cluster members
    │
    ▼
Process Claims:
    ├─ Score < 0.3 → Auto-approve → Payout
    ├─ Score 0.3-0.6 → Delayed approve
    └─ Score > 0.6 → Flag for review
```

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | React 18 + Vite | Modern UI with fast HMR |
| **Styling** | Tailwind CSS | Utility-first CSS framework |
| **Backend** | Python + Flask | Lightweight REST API |
| **Database** | PostgreSQL | Relational data integrity |
| **ORM** | SQLAlchemy | Clean model definitions |
| **Queue** | Redis (RQ) | Async job processing |
| **Scheduler** | APScheduler | Cron jobs for weather polling |
| **ML** | scikit-learn | DBSCAN clustering |
| **Auth** | JWT (PyJWT) | Stateless authentication |
| **Weather API** | OpenWeather | Real-time weather data |

## 📁 Project Structure

```
insurex/
├── backend/
│   ├── app/
│   │   ├── models/           # SQLAlchemy models
│   │   ├── routes/           # API endpoints
│   │   ├── services/         # Business logic
│   │   │   ├── premium_calculator.py
│   │   │   ├── fraud_detection.py
│   │   │   ├── claim_processor.py
│   │   │   ├── payout_service.py
│   │   │   └── weather_poller.py
│   │   └── utils/            # JWT utilities
│   ├── config/               # App configuration
│   ├── seed_mock_data.py    # Data seeding
│   └── run.py               # Entry point
│
├── frontend/
│   ├── src/
│   │   ├── api/              # API service layer
│   │   ├── components/       # React components
│   │   ├── context/          # React context
│   │   ├── pages/            # Page components
│   │   └── App.jsx          # Main app
│   └── package.json
│
├── agent-instructions/       # Development docs
├── implementation_plan.md
└── README.md
```

## 🧪 Testing

### Manual Testing Flow

1. **Register User**
   - Frontend: Register with phone, zone
   - Backend: Creates user + wallet

2. **Top Up Wallet**
   - Add ₹100 to wallet

3. **Purchase Policy**
   - View quote (e.g., ₹38 for Zone-A)
   - Purchase policy
   - Verify wallet deducted

4. **Simulate Event**
   ```bash
   curl -X POST http://localhost:5000/api/events/simulate \
     -H "Content-Type: application/json" \
     -d '{"zone":"Zone-A","type":"extreme_heat","value":"45","duration_hours":2.5}'
   ```

5. **Check Claim**
   - Wait 1-2 minutes for processing
   - Check History page
   - Verify claim status and payout

### Fraud Detection Testing

Run seed script with fraud scenario:

```bash
python seed_mock_data.py
# Choose option 2 or 3
```

This creates 5 users with:
- Identical GPS coordinates
- Zero movement/activity
- Triggers DBSCAN cluster detection

## 🔐 Security

- **JWT Authentication**: 7-day token expiry
- **Password-less Auth**: Phone-based verification
- **Input Validation**: All API endpoints validate inputs
- **SQL Injection**: Protected via SQLAlchemy ORM
- **CORS**: Configured for frontend origin

## 📈 Future Enhancements

- [ ] Real payment gateway (Razorpay/UPI)
- [ ] Mobile app (React Native)
- [ ] Real GPS tracking from device
- [ ] Integration with Swiggy/Zomato APIs
- [ ] Regulatory compliance module
- [ ] Machine learning premium optimization
- [ ] Push notifications
- [ ] Multi-language support

## 👥 Team

Built for the InsureX Hackathon.

## 📄 License

MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

- OpenWeather API for weather data
- scikit-learn for DBSCAN implementation
- Flask and React communities

---

**Happy Insuring! 🚀**
