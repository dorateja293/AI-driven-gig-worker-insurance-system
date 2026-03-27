# InsureX Backend

AI-driven gig worker insurance system with fraud detection and automatic claim processing.

## Features

- **User Authentication** (JWT-based)
- **Dynamic Premium Calculation** (AI-powered risk scoring)
- **Automatic Weather Monitoring** (OpenWeather API integration)
- **4-Layer Fraud Detection** (GPS, Activity, Movement, DBSCAN clustering)
- **Async Claim Processing** (Redis Queue)
- **Wallet System** (Transaction ledger)

## Tech Stack

- **Backend**: Python 3.9+ with Flask
- **Database**: PostgreSQL
- **Queue**: Redis
- **Scheduler**: APScheduler
- **ML**: scikit-learn (DBSCAN clustering)

## Setup Instructions

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Set Up PostgreSQL

Create a PostgreSQL database:

```sql
CREATE DATABASE insurex;
```

### 3. Set Up Redis

Make sure Redis is installed and running:

```bash
# On Windows (with Redis for Windows)
redis-server

# On Linux/Mac
redis-server
```

### 4. Configure Environment

Copy the example environment file and configure it:

```bash
cp .env.example .env
```

Edit `.env` and set your values:

```
DATABASE_URL=postgresql://postgres:password@localhost:5432/insurex
REDIS_URL=redis://localhost:6379/0
OPENWEATHER_API_KEY=your_api_key_here
SECRET_KEY=your_secret_key_here
JWT_SECRET_KEY=your_jwt_secret_here
```

### 5. Initialize Database

The database tables will be created automatically when you first run the app.

### 6. Seed Mock Data (Optional)

For testing fraud detection, seed mock GPS and activity logs:

```bash
python seed_mock_data.py
```

Choose option 3 to seed both realistic data and fraud scenario.

### 7. Run the Application

```bash
python run.py
```

The backend will start on `http://localhost:5000`

## API Endpoints

### Auth
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/me` - Get current user

### Policy
- `GET /api/policy/quote?user_id=xxx` - Get policy quote
- `POST /api/policy/purchase` - Purchase policy
- `GET /api/policy/status?user_id=xxx` - Get policy status

### Claims
- `GET /api/claims?user_id=xxx` - Get user claims
- `GET /api/claims/admin/all` - Get all claims (admin)

### Wallet
- `GET /api/wallet?user_id=xxx` - Get wallet balance and transactions
- `POST /api/wallet/top-up` - Top up wallet

### Events
- `GET /api/events?zone=Zone-A` - Get events
- `POST /api/events/simulate` - Simulate event (testing)

### Fraud
- `GET /api/fraud/flagged` - Get flagged claims

## Background Jobs

The system runs two background jobs:

1. **Weather Poller**: Runs every 60 minutes
   - Fetches weather data from OpenWeather API
   - Checks against thresholds (extreme heat, heavy rain)
   - Creates events and pushes to queue

2. **Claim Processor**: Runs every 5 minutes
   - Processes events from Redis queue
   - Runs fraud detection on eligible users
   - Auto-approves or flags claims based on fraud score

## Testing Event Simulation

To test the system without waiting for real weather events:

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

This will create an event and trigger claim processing for all users in Zone-A with active policies.

## Project Structure

```
backend/
├── app/
│   ├── models/          # Database models
│   ├── routes/          # API endpoints
│   ├── services/        # Business logic
│   │   ├── premium_calculator.py
│   │   ├── fraud_detection.py
│   │   ├── claim_processor.py
│   │   ├── payout_service.py
│   │   ├── weather_poller.py
│   │   ├── queue_service.py
│   │   └── scheduler.py
│   └── utils/           # Utilities (JWT, etc.)
├── config/              # Configuration
├── seed_mock_data.py    # Data seeding script
├── run.py              # Application entry point
└── requirements.txt
```

## Fraud Detection System

The system uses a 4-layer fraud detection pipeline:

1. **GPS Consistency Check**
   - Detects sudden coordinate jumps (teleportation)
   - Identifies static positions (spoofing)

2. **Activity Validation**
   - Checks platform activity before event
   - Verifies order count and online status

3. **Movement Pattern Analysis**
   - Analyzes speed consistency
   - Calculates distance traveled

4. **Cluster Detection (DBSCAN)**
   - Identifies fraud rings (coordinated attacks)
   - Flags users with identical GPS at same location

### Fraud Score Thresholds

- **0.0 - 0.3** (Low): Auto-approve, instant payout
- **0.3 - 0.6** (Medium): Approve with delay
- **0.6 - 1.0** (High/Critical): Flag for manual review

## Support

For issues or questions, please check the main project README.
