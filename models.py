from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    coins = db.Column(db.Integer, default=1500)  # Welcome bonus
    tokens = db.Column(db.Integer, default=0)
    score = db.Column(db.Integer, default=0)
    consecutive_days = db.Column(db.Integer, default=0)  # Track login streak
    last_played = db.Column(db.DateTime)
    last_spin = db.Column(db.DateTime)  # Track last spin wheel play
    last_coinrain = db.Column(db.DateTime)  # Track last coin rain play
    daily_claims = db.relationship('DailyClaim', backref='user', lazy=True)

class DailyClaim(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    claim_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    amount = db.Column(db.Integer, nullable=False)

class AirdropPool(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Integer, nullable=False, default=10000)