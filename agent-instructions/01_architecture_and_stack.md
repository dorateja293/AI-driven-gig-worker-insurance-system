# InsureX Architecture and Tech Stack for Claude Code

## 1. High-Level Architecture
The system consists of a Frontend (React), a Python Flask Backend, a PostgreSQL Database, a Redis Queue, a Background Scheduler (APScheduler), and External APIs.

### Components
- **Auth Service:** Register/login workers
- **Policy Service:** Create weekly policies, calculate premium
- **AI Premium Calculator:** Risk scoring + dynamic pricing
- **Weather Poller:** Cron job, fetches weather every 60 min (via OpenWeather)
- **Claim Processor:** Picks events from queue, runs eligibility
- **Fraud Detection:** Multi-layer validation (GPS, activity)
- **Payout Simulator:** Credits wallet, logs transaction
- **Redis Queue:** Async event processing

## 2. Tech Stack
- **Backend:** Python + Flask
- **Database:** PostgreSQL with SQLAlchemy ORM
- **Queue:** Redis (RQ)
- **Scheduler:** APScheduler
- **Auth:** JWT (PyJWT)

### MVP Scope for Claude
- **MUST BUILD:** User registration + login, Weekly policy endpoints, Automatic claim trigger, Fraud detection (4 layers), Wallet simulation.
- **MOCKED:** Payment gateway, push notifications, GPS logs, platform outage detection.
