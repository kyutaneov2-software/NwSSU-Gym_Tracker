from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import secrets

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    
    app.config['SECRET_KEY'] = secrets.token_hex(16)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bookings.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # optional but recommended

    db.init_app(app)
    migrate.init_app(app, db)
    
    from .routes import main
    from .adminAuth import admin_Auth
    from .addMember import addMember
    from .statistics import statistics
    from .userAuth import userAuth
    from .userRoutes import userRoutes
    from .userRenewals import userRenewals

    app.register_blueprint(main)
    app.register_blueprint(admin_Auth)
    app.register_blueprint(addMember)
    app.register_blueprint(statistics)
    app.register_blueprint(userAuth)
    app.register_blueprint(userRoutes)
    app.register_blueprint(userRenewals)
    
    with app.app_context():
        from .models import Admin, Member, MembershipLog, GymPricing, Workout
        db.create_all()
        
        if not Admin.query.filter_by(username='admin').first():
            default_admin = Admin(username='admin')
            default_admin.set_password('admin123')
            db.session.add(default_admin)
            db.session.commit()
            
        if GymPricing.query.count() == 0:
            default_prices = [
                # Under suspection cause it shits
                GymPricing(member_type='Student', plan_type='Daily', price=40),
                GymPricing(member_type='Faculty', plan_type='Daily', price=40),
                GymPricing(member_type='Outsider', plan_type='Daily', price=60),
                GymPricing(member_type='Student', plan_type='Monthly', price=500),
                GymPricing(member_type='Faculty', plan_type='Monthly', price=500),
                GymPricing(member_type='Outsider', plan_type='Monthly', price=800)
            ]
            db.session.add_all(default_prices)
            db.session.commit()
        
    return app
