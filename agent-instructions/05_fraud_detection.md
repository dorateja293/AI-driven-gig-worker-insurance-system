# InsureX Fraud Detection Pipeline

Claude, this is the most critical logic for the Hackathon Market Crash phase. Please implement this explicitly.

## Multi-Layer Evaluation
Every claim must pass through these 4 checks to generate a final `fraud_score` (0.0 - 1.0).

### 1. GPS Consistency Check
Check `gps_logs` table for sudden coordinate jumps. A user jumping 50km in 2 minutes gets an increased fraud score.

### 2. Activity Validation
Check `activity_logs`. If the user has 0 orders and was 'offline' all day, but suddenly claims a payout, increase fraud score.

### 3. Movement Pattern
If speed is literally 0 km/h or >200 km/h continuously, increase fraud score.

### 4. Cluster Detection (The Market Crash Defense)
**MANDATORY:** You must use Scikit-Learn `DBSCAN` (or similar clustering logic).
Group the GPS coordinates of all claimants for the current Event.
If a distinct cluster contains >= 5 users originating from the exact same location (within 50 meters) at the same time:
- Flag the entire cluster as a Fraud Ring.
- Increase all involved users' `fraud_score` by `+0.6` to guarantee they are held for review.

## False Positives
Do not automatically reject a claim if the phone battery died (no GPS). Instead, increase the score to medium (delayed approval), preserving fairness for genuine offline workers. Only reject/hold if it is a coordinated DBSCAN cluster attack with zero activity.
