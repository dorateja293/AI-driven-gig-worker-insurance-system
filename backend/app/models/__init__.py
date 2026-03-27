# Make models easily importable
from app.models.models import User, Wallet, WalletTransaction, Policy, Event, Claim, GPSLog, ActivityLog

__all__ = ['User', 'Wallet', 'WalletTransaction', 'Policy', 'Event', 'Claim', 'GPSLog', 'ActivityLog']
