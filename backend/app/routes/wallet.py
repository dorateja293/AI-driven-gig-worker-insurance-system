from flask import Blueprint, request, jsonify
from app import db
from app.models import Wallet, WalletTransaction

bp = Blueprint('wallet', __name__, url_prefix='/api/wallet')

@bp.route('', methods=['GET'])
def get_wallet():
    """
    Get wallet balance and transaction history
    Query params: user_id
    Response: {user_id, balance, transactions[]}
    """
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400

        # Get wallet
        wallet = Wallet.query.filter_by(user_id=user_id).first()
        if not wallet:
            return jsonify({'error': 'Wallet not found'}), 404

        # Get transactions
        transactions = WalletTransaction.query.filter_by(wallet_id=wallet.id).order_by(
            WalletTransaction.created_at.desc()
        ).all()

        return jsonify({
            'user_id': user_id,
            'balance': float(wallet.balance),
            'transactions': [txn.to_dict() for txn in transactions]
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/top-up', methods=['POST'])
def top_up_wallet():
    """
    Top up wallet (for testing purposes)
    Request: {user_id, amount}
    Response: {wallet_id, new_balance, transaction_id}
    """
    try:
        data = request.get_json()

        # Validate required fields
        if 'user_id' not in data or 'amount' not in data:
            return jsonify({'error': 'user_id and amount are required'}), 400

        user_id = data['user_id']
        amount = float(data['amount'])

        if amount <= 0:
            return jsonify({'error': 'Amount must be greater than 0'}), 400

        # Get wallet
        wallet = Wallet.query.filter_by(user_id=user_id).first()
        if not wallet:
            return jsonify({'error': 'Wallet not found'}), 404

        # Add to balance
        wallet.balance += amount

        # Create transaction record
        transaction = WalletTransaction(
            wallet_id=wallet.id,
            type='top_up',
            amount=amount,
            description='Wallet top-up'
        )
        db.session.add(transaction)

        db.session.commit()

        return jsonify({
            'wallet_id': wallet.id,
            'new_balance': float(wallet.balance),
            'transaction_id': transaction.id
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
