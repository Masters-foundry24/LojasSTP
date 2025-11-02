# A file with the specific __init__.py name turns our website into a python package.

import flask as fl
import flask_sqlalchemy as fs
import os
import flask_login as fo
import decimal as de
import time

from website.util import format_de

db = fs.SQLAlchemy()
db_name = "database.db"


def create_app():
    """
    This function initialises our app to run a website, it was mostly copied
    from this tutorial: https://www.youtube.com/watch?v=dam0GPOAvVI&t=4228s
    """
    app = fl.Flask(__name__)
    app.config["SECRET_KEY"] = "keyyy"

    # This tells flask the location where the database is stored 
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_name}"
    db.init_app(app)

    from website.views import views

    app.register_blueprint(views, url_prefix = "/")

    from website.models import Entry, Asset, Store, Bill

    create_database(app)

    @app.route("/increase_price/<int:id>")
    def increase_price(id):
        a = Asset.query.get_or_404(id)
        a.price += 1
        db.session.add(Entry(
            entry_type = 6, 
            cash = de.Decimal("0.00"), 
            equity = de.Decimal("0.00"), 
            message = f"O preço do {a.asset_name} aumentou para {format_de(a.price)}."
        ))
        db.session.commit()
        return fl.redirect("/products")
    
    @app.route("/decrease_price/<int:id>")
    def decrease_price(id):
        a = Asset.query.get_or_404(id)
        a.price -= 1
        db.session.add(Entry(
            entry_type = 6, 
            cash = de.Decimal("0.00"), 
            equity = de.Decimal("0.00"), 
            message = f"O preço do {a.asset_name} caiu para {format_de(a.price)}."
        ))
        db.session.commit()
        return fl.redirect("/products")
    
    return app

def create_database(app):
    if os.path.exists(f"instance/{db_name}") or os.path.exists(f"/home/PortalSTP/Portal/instance/{db_name}"):
        pass # database already exists
    else:
        from website.models import Entry, Asset, Store, Bill
        with app.app_context():
            db.create_all() # database created

            db.session.add(Store(
                store_name = "Loja Quaresma",
                cash = de.Decimal("25000.00"), 
                equity = de.Decimal("25000.00"), 
            ))
            
            db.session.add(Entry(
                entry_type = 5, 
                cash = de.Decimal("25000.00"), 
                equity = de.Decimal("25000.00"), 
                message = "Investimento de capital inicial."
            ))
            db.session.commit()

            db.session.add(Bill(
                bill_name = "Alugel", 
                cost = de.Decimal("500.00"), 
                message = "Pagar alugel no inicio de cada mês."
            ))
            db.session.add(Bill(
                bill_name = "Sálario de Pascoal", 
                cost = de.Decimal("800.00"), 
                message = "Pagar no fim de cada sexta-feira."
            ))
            db.session.add(Bill(
                bill_name = "Saldo de Celular", 
                cost = de.Decimal("180.00"), 
                message = "Pagar no inicio de cada mês."
            ))
            db.session.add(Bill(
                bill_name = "Marketing", 
                cost = de.Decimal("300.00"), 
                message = "Pagar no inicio de cada mês."
            ))
            db.session.add(Bill(
                bill_name = "Transporte", 
                cost = de.Decimal("100.00"), 
                message = "Pagar cada vez trazer mais produtos."
            ))
            db.session.commit()

            db.session.add(Asset(
                asset_name = "Arroz", 
                quantity = 0,
                value = de.Decimal("10.00"), 
                price = de.Decimal("15.00"), 
                is_good = True,
                unit = "kg"
            ))
            db.session.commit()