# InsureX Database Schema (PostgreSQL/SQLAlchemy)

## Tables to Create

1. **users**
   - `id` (UUID, Primary Key)
   - `name` (String)
   - `phone` (String, Unique)
   - `city` (String)
   - `zone` (String)
   - `platform` (String, e.g., 'Swiggy', 'Zomato')
   - `created_at` (DateTime)

2. **wallets**
   - `id` (UUID, Primary Key)
   - `user_id` (UUID, Unique, Foreign Key to users)
   - `balance` (Decimal)
   - `updated_at` (DateTime)

3. **wallet_transactions**
   - `id` (UUID, Primary Key)
   - `wallet_id` (UUID, Foreign Key to wallets)
   - `type` (String, e.g., 'premium_paid', 'claim_payout')
   - `amount` (Decimal)
   - `description` (Text)
   - `created_at` (DateTime)

4. **policies**
   - `id` (UUID, Primary Key)
   - `user_id` (UUID, Foreign Key to users)
   - `risk_score` (Decimal 0.00-1.00)
   - `premium` (Decimal)
   - `start_date` (Date)
   - `end_date` (Date)
   - `status` (String, default 'active')
   - `created_at` (DateTime)

5. **events** (disruptions only — threshold-breached events)
   - `id` (UUID, Primary Key)
   - `zone` (String)
   - `event_type` (String, 'extreme_heat', 'heavy_rain')
   - `trigger_value` (String)
   - `duration` (Decimal, hours)
   - `detected_at` (DateTime)
   - `created_at` (DateTime)

6. **claims**
   - `id` (UUID, Primary Key)
   - `user_id` (UUID, Foreign Key to users)
   - `policy_id` (UUID, Foreign Key to policies)
   - `event_id` (UUID, Foreign Key to events)
   - `payout_amount` (Decimal)
   - `status` (String, default 'pending' / 'approved' / 'paid' / 'flagged')
   - `fraud_score` (Decimal 0.00-1.00)
   - `fraud_reason` (Text)
   - `created_at` (DateTime)

7. **gps_logs** (mocked logs for fraud detection)
   - `user_id` (FK to users)
   - `latitude`, `longitude`, `speed_kmh`, `logged_at`

8. **activity_logs** (mocked platform activity)
   - `user_id` (FK to users)
   - `status` ('online', 'delivering', 'idle', 'offline')
   - `orders_count`
   - `logged_at`
