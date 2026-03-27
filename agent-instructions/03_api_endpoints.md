# InsureX API Endpoints

Claude, please implement these endpoints in Flask matching the exact Request/Response logic described.

## Auth
- `POST /api/auth/register` (Registers user + creates empty wallet)
- `POST /api/auth/login` (Returns JWT token)

## Policies
- `GET /api/policy/quote?user_id=usr_123` (Calculates Risk Score and returns premium quote)
- `POST /api/policy/purchase` (Debits wallet, creates active policy for 7 days)
- `GET /api/policy/status?user_id=usr_123` 

## Claims
- `GET /api/claims?user_id=usr_123` (Returns claims list)
- `GET /api/claims/admin/all`

## Wallet
- `GET /api/wallet?user_id=usr_123` (Returns balance and wallet_transactions)

## Events (Disruptions)
- `GET /api/events?zone=Zone-A`
- `POST /api/events/simulate` (Creates a fake event for testing, e.g. triggers heatwave)

## Fraud
- `GET /api/fraud/flagged` (Returns claims with high fraud scores)
