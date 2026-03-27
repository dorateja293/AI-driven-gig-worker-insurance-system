import uuid
from datetime import datetime
from app import db

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.String(36), primary_key=True, default=lambda: f"usr_{uuid.uuid4().hex[:10]}")
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), unique=True, nullable=False)
    city = db.Column(db.String(50), nullable=False)
    zone = db.Column(db.String(20), nullable=False)
    platform = db.Column(db.String(20), nullable=False)  # 'Swiggy' or 'Zomato'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    wallet = db.relationship('Wallet', backref='user', uselist=False, cascade='all, delete-orphan')
    policies = db.relationship('Policy', backref='user', lazy=True, cascade='all, delete-orphan')
    claims = db.relationship('Claim', backref='user', lazy=True, cascade='all, delete-orphan')
    gps_logs = db.relationship('GPSLog', backref='user', lazy=True, cascade='all, delete-orphan')
    activity_logs = db.relationship('ActivityLog', backref='user', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'user_id': self.id,
            'name': self.name,
            'phone': self.phone,
            'city': self.city,
            'zone': self.zone,
            'platform': self.platform,
            'created_at': self.created_at.isoformat()
        }


class Wallet(db.Model):
    __tablename__ = 'wallets'

    id = db.Column(db.String(36), primary_key=True, default=lambda: f"wlt_{uuid.uuid4().hex[:10]}")
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    balance = db.Column(db.Numeric(10, 2), default=0)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    transactions = db.relationship('WalletTransaction', backref='wallet', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'wallet_id': self.id,
            'user_id': self.user_id,
            'balance': float(self.balance),
            'updated_at': self.updated_at.isoformat()
        }


class WalletTransaction(db.Model):
    __tablename__ = 'wallet_transactions'

    id = db.Column(db.String(36), primary_key=True, default=lambda: f"txn_{uuid.uuid4().hex[:10]}")
    wallet_id = db.Column(db.String(36), db.ForeignKey('wallets.id', ondelete='CASCADE'), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # 'premium_paid', 'claim_payout', 'top_up'
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'transaction_id': self.id,
            'type': self.type,
            'amount': float(self.amount),
            'description': self.description,
            'date': self.created_at.isoformat()
        }


class Policy(db.Model):
    __tablename__ = 'policies'

    id = db.Column(db.String(36), primary_key=True, default=lambda: f"pol_{uuid.uuid4().hex[:10]}")
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    risk_score = db.Column(db.Numeric(3, 2), nullable=False)  # 0.00 to 1.00
    premium = db.Column(db.Numeric(10, 2), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(10), default='active')  # 'active', 'expired', 'cancelled'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    claims = db.relationship('Claim', backref='policy', lazy=True)

    def to_dict(self):
        return {
            'policy_id': self.id,
            'user_id': self.user_id,
            'risk_score': float(self.risk_score),
            'premium': float(self.premium),
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }


class Event(db.Model):
    __tablename__ = 'events'

    id = db.Column(db.String(36), primary_key=True, default=lambda: f"evt_{uuid.uuid4().hex[:10]}")
    zone = db.Column(db.String(20), nullable=False)
    event_type = db.Column(db.String(30), nullable=False)  # 'extreme_heat', 'heavy_rain', 'platform_outage'
    trigger_value = db.Column(db.String(50), nullable=False)  # '45.2°C', '62mm', '45 min downtime'
    duration = db.Column(db.Numeric(4, 1))  # hours
    detected_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    claims = db.relationship('Claim', backref='event', lazy=True)

    def to_dict(self):
        return {
            'event_id': self.id,
            'zone': self.zone,
            'type': self.event_type,
            'value': self.trigger_value,
            'duration_hours': float(self.duration) if self.duration else None,
            'timestamp': self.detected_at.isoformat()
        }


class Claim(db.Model):
    __tablename__ = 'claims'

    id = db.Column(db.String(36), primary_key=True, default=lambda: f"clm_{uuid.uuid4().hex[:10]}")
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    policy_id = db.Column(db.String(36), db.ForeignKey('policies.id', ondelete='CASCADE'), nullable=False)
    event_id = db.Column(db.String(36), db.ForeignKey('events.id', ondelete='CASCADE'), nullable=False)
    payout_amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(15), default='pending')  # 'pending','approved','paid','flagged','rejected'
    fraud_score = db.Column(db.Numeric(3, 2), default=0)  # 0.00 to 1.00
    risk_level = db.Column(db.String(10), default='LOW')  # 'LOW', 'MEDIUM', 'HIGH'
    fraud_reason = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'claim_id': self.id,
            'user_id': self.user_id,
            'policy_id': self.policy_id,
            'event_id': self.event_id,
            'payout_amount': float(self.payout_amount),
            'status': self.status,
            'fraud_score': float(self.fraud_score),
            'risk_level': self.risk_level,
            'fraud_reason': self.fraud_reason,
            'timestamp': self.created_at.isoformat()
        }


class GPSLog(db.Model):
    __tablename__ = 'gps_logs'

    id = db.Column(db.String(36), primary_key=True, default=lambda: f"gps_{uuid.uuid4().hex[:10]}")
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    latitude = db.Column(db.Numeric(10, 7), nullable=False)
    longitude = db.Column(db.Numeric(10, 7), nullable=False)
    speed_kmh = db.Column(db.Numeric(5, 1), default=0)
    logged_at = db.Column(db.DateTime, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'latitude': float(self.latitude),
            'longitude': float(self.longitude),
            'speed_kmh': float(self.speed_kmh),
            'logged_at': self.logged_at.isoformat()
        }


class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'

    id = db.Column(db.String(36), primary_key=True, default=lambda: f"act_{uuid.uuid4().hex[:10]}")
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    status = db.Column(db.String(15), nullable=False)  # 'online', 'delivering', 'idle', 'offline'
    orders_count = db.Column(db.Integer, default=0)
    logged_at = db.Column(db.DateTime, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'status': self.status,
            'orders_count': self.orders_count,
            'logged_at': self.logged_at.isoformat()
        }
