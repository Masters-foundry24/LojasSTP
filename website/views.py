# This page has received basic logging.

import os
import flask as fl
import flask_login as fo
import decimal as de
import datetime as dt
from sqlalchemy.sql import func, or_
from sqlalchemy import or_, text
from website.models import Entry, Asset, Store, Bill
from website.util import format_de, compute_results
from website import db

views = fl.Blueprint("views", __name__)

@views.route("/")
def home():
    now = dt.datetime.now()
    start = dt.datetime(now.year, now.month, 1)
    if now.month == 12:
        end = dt.datetime(now.year + 1, 1, 1)
    else:
        end = dt.datetime(now.year, now.month + 1, 1)

    entries = db.session.query(Entry).filter(Entry.time >= start, Entry.time < end).all()

    results = compute_results(entries)
    return fl.render_template("home.html", results = results)

@views.route("/journal")
def journal():
    store = Store.query.first()
    store = {
        "name": store.store_name,
        "cash": format_de(de.Decimal(store.cash)),
        "equity": format_de(de.Decimal(store.equity))
    }
    entries = Entry.query.order_by(Entry.time.desc())
    entries = [
        {
            "entry_type": e.entry_type,
            "time": e.time,
            "message": e.message,
            "cash": format_de(de.Decimal(e.cash)),
            "equity": format_de(de.Decimal(e.equity))
        } for e in entries
    ]
    return fl.render_template("journal.html", store = store, entries = entries)

@views.route("/bills")
def bills():
    store = Store.query.first()
    store = {
        "name": store.store_name,
        "cash": format_de(de.Decimal(store.cash)),
        "equity": format_de(de.Decimal(store.equity))
    }
    bills = Bill.query
    bills = [
        {
            "id": b.bill_id,
            "name": b.bill_name,
            "message": b.message,
            "cost": format_de(de.Decimal(b.cost)),
        } for b in bills
    ]
    return fl.render_template("bills/main.html", store = store, bills = bills)

@views.route("/bills/pay/<int:id>", methods = ["GET", "POST"])
def pay_bill(id):
    b = Bill.query.get_or_404(id)

    if fl.request.method == "POST":
        db.session.add(Entry(
            entry_type = 3, 
            cash = - de.Decimal(b.cost), 
            equity = - de.Decimal(b.cost), 
            message = f"Pagou {b.bill_name}."
        ))
        store = Store.query.first()
        store.cash -= b.cost
        store.equity -= b.cost
        db.session.commit()
        return fl.redirect("/")
    
    b = {
        "id": b.bill_id,
        "name": b.bill_name,
        "message": b.message,
        "cost": format_de(de.Decimal(b.cost)),
    }

    return fl.render_template("bills/pay.html", b = b)

@views.route("/bills/edit/<int:id>", methods = ["GET", "POST"])
def edit_bill(id):
    b = Bill.query.get_or_404(id)

    if fl.request.method == "POST":
        cost = fl.request.form.get("cost")
        b.cost = de.Decimal(cost)
        db.session.add(Entry(
            entry_type = 6, 
            cash = de.Decimal("0.0"), 
            equity = de.Decimal("0.0"), 
            message = f"Despensa de {b.bill_name} mudou para {cost} Db."
        ))
        db.session.commit()
        return fl.redirect("/bills")
    
    b = {
        "id": b.bill_id,
        "name": b.bill_name,
        "message": b.message,
        "cost": format_de(de.Decimal(b.cost)),
    }

    return fl.render_template("bills/edit.html", b = b)

@views.route("/products")
def products():
    store = Store.query.first()
    store = {
        "name": store.store_name,
        "cash": format_de(de.Decimal(store.cash)),
        "equity": format_de(de.Decimal(store.equity))
    }
    goods = Asset.query.filter_by(is_good = True).order_by((Asset.price * Asset.quantity).desc())
    goods = [
        {
            "id": g.asset_id,
            "name": g.asset_name,
            "quantity": int(g.quantity),
            "value": format_de(de.Decimal(g.value)),
            "price": format_de(de.Decimal(g.price)),
            "unit": g.unit
        } for g in goods
    ]
    return fl.render_template("products/main.html", store = store, goods = goods)

@views.route("/products/price/<int:id>", methods = ["GET", "POST"])
def edit_price(id):
    g = Asset.query.get_or_404(id)

    if fl.request.method == "POST":
        price = de.Decimal(fl.request.form.get("price"))
        db.session.add(Entry(
            entry_type = 6, 
            cash = de.Decimal("0.0"), 
            equity = de.Decimal("0.0"), 
            message = f"Preço de {g.asset_name} mudou de {format_de(g.price)} Db para {format_de(price)} Db."
        ))
        g.price = price
        db.session.commit()
        return fl.redirect("/products")
    
    g = {
        "id": g.asset_id,
        "name": g.asset_name,
        "quantity": int(g.quantity),
        "value": format_de(de.Decimal(g.value)),
        "price": format_de(de.Decimal(g.price)),
        "unit": g.unit
    }

    return fl.render_template("products/price.html", g = g)

@views.route("/sales", methods = ["GET", "POST"])
def sales():
    if fl.request.method == "POST":
        data = fl.request.form
        product = Asset.query.get_or_404(data.get("product"))
        quantity = int(data.get("quantity"))
        promotion = data.get("promotion")

        product.quantity -= quantity
        if promotion == "worker":
            price = product.value
        else:
            price = product.price
        cash_impact = quantity * price
        equity_impact = quantity * (price - product.value)

        store = Store.query.first()
        store.cash += cash_impact
        store.equity += equity_impact

        db.session.add(Entry(
            entry_type = 1, 
            cash = de.Decimal(cash_impact), 
            equity = de.Decimal(equity_impact), 
            message = f"Vendeu {quantity} {product.unit} de {product.asset_name} por {price}."
        ))

        db.session.commit()
    
    store = Store.query.first()
    store = {
        "name": store.store_name,
        "cash": format_de(de.Decimal(store.cash)),
        "equity": format_de(de.Decimal(store.equity))
    }

    goods = Asset.query.filter_by(is_good = True).order_by((Asset.price * Asset.quantity).desc())
    goods = [
        {
            "id": g.asset_id,
            "name": g.asset_name,
            "quantity": int(g.quantity),
            "value": format_de(de.Decimal(g.value)),
            "price": format_de(de.Decimal(g.price)),
            "unit": g.unit
        } for g in goods
    ]
    return fl.render_template("sales.html", store = store, goods = goods)

@views.route("/purchases", methods = ["GET", "POST"])
def purchases():
    if fl.request.method == "POST":
        data = fl.request.form
        quantity = int(data.get("quantity"))
        cost = de.Decimal(data.get("cost"))
        value = cost / quantity
        is_good = True if data.get("is_good") == "yes" else False
        if data.get("product") == "other":
            product = Asset(
                asset_name = data.get("name"),
                quantity = quantity,
                value = value,
                price = data.get("price") if is_good else 0,
                is_good = is_good,
                unit = data.get("unit")
            )
            db.session.add(product)

            equity_impact = 0
            cash_impact = - cost

        else:
            product = Asset.query.get_or_404(data.get("product"))

            equity_impact = product.quantity * (value - product.value) # revaluation
            product.value = value
            product.quantity += quantity
            cash_impact = - cost

        store = Store.query.first()
        store.cash += cash_impact
        store.equity += equity_impact
        db.session.add(Entry(
            entry_type = 2, 
            cash = de.Decimal(cash_impact), 
            equity = de.Decimal(equity_impact), 
            message = f"Comprou {quantity} {product.unit} de {product.asset_name} por {product.value}."
        ))

        db.session.commit()
    
    store = Store.query.first()
    store = {
        "name": store.store_name,
        "cash": format_de(de.Decimal(store.cash)),
        "equity": format_de(de.Decimal(store.equity))
    }

    assets = Asset.query.order_by(Asset.is_good)
    assets = [
        {
            "id": a.asset_id,
            "name": a.asset_name,
            "quantity": int(a.quantity),
            "value": format_de(de.Decimal(a.value)),
            "price": format_de(de.Decimal(a.price)),
            "unit": a.unit
        } for a in assets
    ]
    return fl.render_template("purchases.html", store = store, assets = assets)

@views.route("/balance")
def balance():
    store = Store.query.first()
    store = {
        "name": store.store_name,
        "cash": format_de(de.Decimal(store.cash)),
        "equity": format_de(de.Decimal(store.equity))
    }

    all_assets = Asset.query.order_by(Asset.is_good)
    goods, assets = {"quantity": 0, "value": de.Decimal("0.0")}, []

    for a in all_assets:
        if a.is_good:
            goods["quantity"] += 1
            goods["value"] += a.value * a.quantity
        else:
            assets.append({
                "id": a.asset_id,
                "name": a.asset_name,
                "quantity": int(a.quantity),
                "value": format_de(de.Decimal(a.value)),
                "price": format_de(de.Decimal(a.price)),
                "unit": a.unit,
                "worth": format_de(de.Decimal(a.value) * int(a.quantity))
            })

    return fl.render_template("balance.html", store = store, assets = assets, goods = goods)

@views.route("/report/<month>")
def report(month):
    year = int("20" + month[3:])     # "25" → 2025
    month = [0, "jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"].index(month[:3])

    start = dt.datetime(year, month, 1)
    if month == 12:
        end = dt.datetime(year + 1, 1, 1)
    else:
        end = dt.datetime(year, month + 1, 1)

    month = [0, "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"][month]

    entries = db.session.query(Entry).filter(Entry.time >= start, Entry.time < end).all()
    results = compute_results(entries)
    return fl.render_template("report.html", entries = entries, results = results, year = year, month = month)

@views.route("/contract")
def contract():
    return fl.render_template("contract.html")