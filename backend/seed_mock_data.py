"""
Seed script to populate database with mock GPS and activity logs for testing fraud detection.
Run this script after creating users and policies.
"""

import random
from datetime import datetime, timedelta
from app import create_app, db
from app.models import User, GPSLog, ActivityLog

def seed_gps_and_activity_data():
    """Seed mock GPS and activity logs for all users"""
    app = create_app()

    with app.app_context():
        # Get all users
        users = User.query.all()

        if len(users) == 0:
            print("No users found. Please create users first.")
            return

        print(f"Found {len(users)} users. Seeding GPS and activity logs...")

        # Base coordinates for each zone
        zone_coords = {
            'Zone-A': {'lat': 17.385044, 'lon': 78.486671},  # Hyderabad
            'Zone-B': {'lat': 19.076090, 'lon': 72.877426},  # Mumbai
            'Zone-C': {'lat': 28.704060, 'lon': 77.102493},  # Delhi
            'Zone-D': {'lat': 12.971599, 'lon': 77.594566},  # Bangalore
        }

        for user in users:
            print(f"\nSeeding data for user: {user.name} ({user.zone})")

            # Get base coordinates for user's zone
            base_coords = zone_coords.get(user.zone, {'lat': 17.385044, 'lon': 78.486671})

            # Create realistic GPS logs for the last 24 hours
            now = datetime.utcnow()
            num_logs = random.randint(50, 100)

            for i in range(num_logs):
                # Distribute logs over last 24 hours
                logged_at = now - timedelta(hours=24) + timedelta(minutes=i * (24 * 60 / num_logs))

                # Add realistic movement (within 10km radius)
                lat_offset = random.uniform(-0.05, 0.05)  # ~5km
                lon_offset = random.uniform(-0.05, 0.05)

                # Realistic delivery speed (0-40 km/h)
                speed = random.uniform(0, 40) if random.random() > 0.2 else 0  # 20% idle time

                gps_log = GPSLog(
                    user_id=user.id,
                    latitude=base_coords['lat'] + lat_offset,
                    longitude=base_coords['lon'] + lon_offset,
                    speed_kmh=speed,
                    logged_at=logged_at
                )
                db.session.add(gps_log)

            print(f"  - Created {num_logs} GPS logs")

            # Create activity logs for the last 24 hours
            num_activity_logs = random.randint(20, 40)
            statuses = ['online', 'delivering', 'idle', 'offline']

            for i in range(num_activity_logs):
                logged_at = now - timedelta(hours=24) + timedelta(minutes=i * (24 * 60 / num_activity_logs))

                # More realistic status distribution
                if 8 <= logged_at.hour <= 22:  # Working hours
                    status = random.choices(
                        statuses,
                        weights=[0.3, 0.5, 0.15, 0.05],  # More delivering during work hours
                        k=1
                    )[0]
                else:
                    status = 'offline'  # Offline at night

                orders_count = random.randint(1, 5) if status == 'delivering' else 0

                activity_log = ActivityLog(
                    user_id=user.id,
                    status=status,
                    orders_count=orders_count,
                    logged_at=logged_at
                )
                db.session.add(activity_log)

            print(f"  - Created {num_activity_logs} activity logs")

        # Commit all changes
        db.session.commit()
        print(f"\n✓ Successfully seeded GPS and activity logs for {len(users)} users!")

        # Print summary
        total_gps = GPSLog.query.count()
        total_activity = ActivityLog.query.count()
        print(f"\nTotal GPS logs in database: {total_gps}")
        print(f"Total activity logs in database: {total_activity}")


def create_fraud_scenario_users():
    """
    Create additional users that simulate a fraud ring
    (for testing the DBSCAN cluster detection)
    """
    app = create_app()

    with app.app_context():
        print("\nCreating fraud scenario...")

        # Create 5 fake users (fraud ring)
        fraud_zone = 'Zone-A'
        fraud_coords = {'lat': 17.385044, 'lon': 78.486671}

        for i in range(5):
            # Check if user exists
            existing = User.query.filter_by(phone=f'fake{i:04d}').first()
            if existing:
                print(f"Fraud user {i+1} already exists")
                continue

            fake_user = User(
                name=f'Fake Worker {i+1}',
                phone=f'fake{i:04d}',
                city='Hyderabad',
                zone=fraud_zone,
                platform='Swiggy'
            )
            db.session.add(fake_user)
            db.session.flush()

            # Create wallet
            from app.models import Wallet
            wallet = Wallet(user_id=fake_user.id, balance=0)
            db.session.add(wallet)

            # Create GPS logs at exact same coordinates (spoofing indicator)
            now = datetime.utcnow()
            for j in range(10):
                gps_log = GPSLog(
                    user_id=fake_user.id,
                    latitude=fraud_coords['lat'],  # Exact same coords
                    longitude=fraud_coords['lon'],
                    speed_kmh=0,  # Static
                    logged_at=now - timedelta(minutes=j*10)
                )
                db.session.add(gps_log)

            # Create activity logs showing zero activity
            for j in range(5):
                activity_log = ActivityLog(
                    user_id=fake_user.id,
                    status='offline',
                    orders_count=0,
                    logged_at=now - timedelta(hours=j)
                )
                db.session.add(activity_log)

            print(f"  - Created fraud user: {fake_user.name}")

        db.session.commit()
        print("\n✓ Fraud scenario created successfully!")
        print("  These users will trigger fraud detection due to:")
        print("  - Identical GPS coordinates")
        print("  - Zero movement/speed")
        print("  - Zero delivery activity")


if __name__ == '__main__':
    print("=" * 60)
    print("INSUREX - MOCK DATA SEEDER")
    print("=" * 60)

    # Run automatically for demo without blocking
    seed_gps_and_activity_data()
    create_fraud_scenario_users()
