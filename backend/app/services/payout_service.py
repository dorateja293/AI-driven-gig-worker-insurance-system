from datetime import datetime
from app import db
from app.models import Claim, Wallet, WalletTransaction

def execute_payout(user_id, claim_id, amount):
    """
    Execute payout for an approved claim
    1. Verify claim status = 'approved'
    2. Credit user's wallet
    3. Create wallet transaction record
    4. Update claim status to 'paid'
    """
    try:
        # Get claim
        claim = Claim.query.get(claim_id)
        if not claim:
            return {'success': False, 'error': 'Claim not found'}

        if claim.status != 'approved':
            return {'success': False, 'error': f'Claim status is {claim.status}, not approved'}

        # Get wallet
        wallet = Wallet.query.filter_by(user_id=user_id).first()
        if not wallet:
            return {'success': False, 'error': 'Wallet not found'}

        # Credit wallet
        wallet.balance += amount
        wallet.updated_at = datetime.utcnow()

        # Create transaction record
        transaction = WalletTransaction(
            wallet_id=wallet.id,
            type='claim_payout',
            amount=amount,
            description=f'Claim payout for {claim.id}'
        )
        db.session.add(transaction)

        # Update claim status
        claim.status = 'paid'

        db.session.commit()

        return {
            'success': True,
            'wallet_balance': float(wallet.balance),
            'transaction_id': transaction.id
        }

    except Exception as e:
        db.session.rollback()
        return {'success': False, 'error': str(e)}
