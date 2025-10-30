import flask_login as fo
from sqlalchemy.sql import func
import decimal as de
from website import db

class Entry(db.Model): # An entry in the journal
    entry_id = db.Column(db.Integer, primary_key = True)
    entry_type = db.Column(db.Integer)
    # 1. Sales – record revenue from goods or services sold.
    # 2. Purchases – record acquisition of goods or services.
    # 3. Expenses - record expenses such as salaries, taxes or utilities.
    # 4. Adjustments - record changes in inventory or cash.
    # 5. Investments & Dividends
    # 6. Product Changes
    time = db.Column(db.DateTime(timezone = False), default = func.now())
    cash = db.Column(db.Numeric(9, 2))
    equity = db.Column(db.Numeric(9, 2))
    message = db.Column(db.String(200))

class Asset(db.Model):
    asset_id = db.Column(db.Integer, primary_key = True)
    asset_name = db.Column(db.String(50))
    quantity = db.Column(db.Integer)
    value = db.Column(db.Numeric(9, 2))
    price = db.Column(db.Numeric(9, 2))
    is_good = db.Column(db.Boolean, default = False) # Will we try to sell this.
    unit = db.Column(db.String(20))

class Bill(db.Model):
    bill_id = db.Column(db.Integer, primary_key = True)
    bill_name = db.Column(db.String(50))
    cost = db.Column(db.Numeric(9, 2))
    message = db.Column(db.String(200))

class Store(db.Model):
    store_id = db.Column(db.Integer, primary_key = True)
    store_name = db.Column(db.String(100))
    cash = db.Column(db.Numeric(9, 2))
    equity = db.Column(db.Numeric(9, 2))