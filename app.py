import os
import random
import json
from flask import Flask, render_template, redirect, url_for, flash, request, send_from_directory, jsonify
from datetime import datetime, timedelta
from models import db, User, DailyClaim, AirdropPool

app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = 'metaverse_secret_key'
# Fix the duplicate sslmode parameter
DATABASE_URL = os.environ['DATABASE_URL']
if '?sslmode=' not in DATABASE_URL:
    DATABASE_URL += "?sslmode=require"
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db.init_app(app)

# Create tables
with app.app_context():
    db.create_all()
    # Initialize airdrop pool if it doesn't exist
    if not AirdropPool.query.first():
        db.session.add(AirdropPool(amount=10000))
        db.session.commit()

def get_time_remaining(user):
    last_claim = DailyClaim.query.filter_by(user_id=user.id).order_by(DailyClaim.claim_date.desc()).first()
    if not last_claim:
        return None
    next_claim = last_claim.claim_date + timedelta(days=1)
    remaining = next_claim - datetime.utcnow()
    if remaining.total_seconds() <= 0:
        return None
    hours = int(remaining.total_seconds() // 3600)
    minutes = int((remaining.total_seconds() % 3600) // 60)
    return f"{hours}h {minutes}m"

def can_claim_daily(user):
    last_claim = DailyClaim.query.filter_by(user_id=user.id).order_by(DailyClaim.claim_date.desc()).first()
    if not last_claim:
        return True
    return datetime.utcnow() - last_claim.claim_date > timedelta(days=1)

def get_or_create_user():
    user = User.query.get(1)
    if not user:
        user = User(id=1, username="Player", coins=1500, tokens=0, last_spin=None, last_coinrain=None)  # Welcome bonus, added tokens and last play timestamps
        db.session.add(user)
        db.session.commit()
    return user

@app.route('/')
def index():
    user = get_or_create_user()
    can_claim = can_claim_daily(user)
    time_remaining = None if can_claim else get_time_remaining(user)
    airdrop_pool = AirdropPool.query.first().amount

    return render_template('index.html',
                         user=user,
                         can_claim=can_claim,
                         time_remaining=time_remaining,
                         airdrop_pool=airdrop_pool)

@app.route('/wallet')
def wallet():
    user = get_or_create_user()
    return render_template('wallet.html', user=user)

@app.route('/tasks')
def tasks():
    user = get_or_create_user()
    with open('data/questions.json', 'r') as f:
        questions = json.load(f)
    return render_template('tasks.html', 
                         user=user, 
                         question=random.choice(questions),
                         enumerate=enumerate)

@app.route('/airdrop')
def airdrop():
    user = get_or_create_user()
    airdrop_pool = AirdropPool.query.first()
    return render_template('airdrop.html', user=user, airdrop_pool=airdrop_pool)

@app.route('/leaderboard')
def leaderboard():
    users = User.query.order_by(User.coins.desc()).limit(10).all()
    return render_template('leaderboard.html', users=users)

@app.route('/claim_daily')
def claim_daily():
    user = get_or_create_user()
    if can_claim_daily(user):
        amount = 100  # Fixed daily reward amount
        claim = DailyClaim(user_id=user.id, amount=amount)
        user.coins += amount
        db.session.add(claim)
        db.session.commit()
        flash('🎉 You claimed 100 Metarush Coins!', 'success')
    else:
        flash('⏰ Come back tomorrow for your next reward!', 'error')
    return redirect(url_for('index'))

@app.route('/claim_airdrop')
def claim_airdrop():
    user = get_or_create_user()
    airdrop_pool = AirdropPool.query.first()

    if airdrop_pool.amount <= 0:
        flash('❌ Airdrop pool is empty!', 'error')
        return redirect(url_for('airdrop'))

    amount = random.randint(10, 100)
    if amount > airdrop_pool.amount:
        amount = airdrop_pool.amount

    airdrop_pool.amount -= amount
    user.coins += amount
    db.session.commit()

    flash(f'🎉 You received {amount} coins from the airdrop!', 'success')
    return redirect(url_for('airdrop'))

@app.route('/answer_question', methods=['POST'])
def answer_question():
    user = get_or_create_user()
    answer = request.form.get('answer')
    correct = request.form.get('correct')

    if answer == correct:
        reward = random.randint(50, 200)
        user.coins += reward
        db.session.commit()
        flash(f'✅ Correct! You earned {reward} coins!', 'success')
    else:
        flash('❌ Wrong answer! Try again!', 'error')

    return redirect(url_for('tasks'))

@app.route('/convert_coins', methods=['POST'])
def convert_coins():
    user = get_or_create_user()
    try:
        amount = int(request.form.get('amount', 0))
        if amount < 100 or amount % 100 != 0:
            flash('❌ Amount must be a multiple of 100 coins!', 'error')
            return redirect(url_for('wallet'))

        if user.coins < amount:
            flash('❌ Insufficient coins for conversion!', 'error')
            return redirect(url_for('wallet'))

        tokens = amount // 100
        user.coins -= amount
        user.tokens += tokens
        db.session.commit()

        flash(f'✨ Successfully converted {amount} coins to {tokens} tokens!', 'success')
    except ValueError:
        flash('❌ Invalid amount entered!', 'error')

    return redirect(url_for('wallet'))

@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

def can_play_game(user, game_type):
    if game_type == 'spin':
        last_play = user.last_spin
    else:  # coinrain
        last_play = user.last_coinrain

    if not last_play:
        return True
    return datetime.utcnow() - last_play > timedelta(days=1)

@app.route('/game')
def game():
    user = get_or_create_user()
    can_play = can_play_game(user, 'spin')
    return render_template('game.html', user=user, can_play=can_play)

@app.route('/claim_spin_reward', methods=['POST'])
def claim_spin_reward():
    user = get_or_create_user()
    if not can_play_game(user, 'spin'):
        return jsonify({'success': False, 'message': 'You can only play once per day!'})

    data = request.get_json()
    reward = data.get('reward', 0)

    if reward > 0:
        user.coins += reward
        user.last_spin = datetime.utcnow()
        db.session.commit()
        return jsonify({'success': True, 'message': f'You won {reward} coins!'})

    return jsonify({'success': False, 'message': 'Better luck next time!'})

@app.route('/coinrain')
def coinrain():
    user = get_or_create_user()
    can_play = can_play_game(user, 'coinrain')
    return render_template('coinrain.html', user=user, can_play=can_play)

@app.route('/claim_coinrain_reward', methods=['POST'])
def claim_coinrain_reward():
    user = get_or_create_user()
    if not can_play_game(user, 'coinrain'):
        return jsonify({'success': False, 'message': 'You can only play once per day!'})

    data = request.get_json()
    reward = min(data.get('reward', 0), 10)  # Cap individual coin rewards at 10

    if reward > 0:
        user.coins += reward
        user.last_coinrain = datetime.utcnow()
        db.session.commit()
        return jsonify({'success': True, 'message': f'Collected {reward} coins!'})

    return jsonify({'success': False, 'message': 'No coins collected.'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)