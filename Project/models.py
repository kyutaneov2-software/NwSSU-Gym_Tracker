import pytz
from . import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


# ========================================
# ADMIN MODEL
# ========================================
class Admin(db.Model):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# =======================================
# PRICE MODEL   
# =======================================
class GymPricing(db.Model):
    __tablename__ = 'gym_pricing'

    id = db.Column(db.Integer, primary_key=True)
    member_type = db.Column(db.Enum('Student', 'Faculty', 'Outsider'), nullable=False)
    plan_type = db.Column(db.Enum('Daily', 'Monthly', 'Annual'), nullable=False)
    price = db.Column(db.Float, nullable=False)
    effective_date = db.Column(db.Date, default=lambda: datetime.now(pytz.timezone('Asia/Manila')).date())

    def __repr__(self):
        return f"<Pricing {self.member_type} - {self.plan_type}: ₱{self.price}>"
    
    
# =======================================
# PRICE HISTORY MODEL
# =======================================
class PriceHistory(db.Model):
    __tablename__ = 'price_history'
    
    id = db.Column(db.Integer, primary_key=True)
    member_type = db.Column(db.String(50))
    plan_type = db.Column(db.String(50))
    old_price = db.Column(db.Float)
    new_price = db.Column(db.Float)
    change_at = db.Column(db.DateTime, default=lambda: datetime.now(pytz.timezone('Asia/Manila')))

    def __repr__(self):
        return f"<PriceChange {self.member_type} - {self.plan_type}: ₱{self.old_price} → ₱{self.new_price}> "

# ========================================
# MEMBER MODEL
# ========================================
class Member(db.Model):
    __tablename__ = 'members'

    member_id = db.Column(db.Integer, primary_key=True)
    unique_code = db.Column(db.String(10), unique=True, nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer)
    gender = db.Column(db.Enum('Male', 'Female'))
    member_type = db.Column(db.Enum('Faculty', 'Outsider', 'Student'), nullable=False)
    student_number = db.Column(db.String(20))
    gym_plan = db.Column(db.Enum('Daily', 'Monthly', 'Annual'), nullable=False)
    email = db.Column(db.String(150))
    contact_number = db.Column(db.String(20))
    address = db.Column(db.String(255))
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.Enum('Active', 'Inactive', 'Expired'), default='Inactive')
    payment_status = db.Column(db.Enum('Paid', 'Unpaid', 'Overdue'), default='Unpaid')
    date_registered = db.Column(db.DateTime, default=lambda: datetime.now(pytz.timezone('Asia/Manila')))
    price_paid = db.Column(db.Float, nullable=True)
    last_payment_date = db.Column(db.DateTime, nullable=True)

    # User authentication fields (for self-registered members)
    password_hash = db.Column(db.String(200), nullable=True)  # NULL for admin-created members
    is_self_registered = db.Column(db.Boolean, default=False)  # True if user registered themselves

    logs = db.relationship('MembershipLog', backref='member', lazy=True, cascade='all, delete-orphan')
    workouts = db.relationship('Workout', backref='member', lazy=True, cascade='all, delete-orphan')

    # Track original type
    _original_member_type = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Automatically generate the unique code based on member type
        if not self.unique_code:
            self.unique_code = self.generate_unique_code(self.member_type)
        self._original_member_type = self.member_type  # track original type

    def generate_unique_code(self, member_type):
        """Generate a truly unique code like STU-0001, avoiding duplicates even if records were deleted."""
        prefix_map = {
            'Student': 'STU',
            'Faculty': 'FCT',
            'Outsider': 'OTD'
        }
        prefix = prefix_map.get(member_type, 'MBR')

        # Query all codes starting with the prefix
        existing_codes = Member.query.with_entities(Member.unique_code).filter(
            Member.unique_code.like(f"{prefix}-%")
        ).all()

        max_num = 0
        for code_tuple in existing_codes:
            code = code_tuple[0]
            try:
                num = int(code.split('-')[1])
                max_num = max(max_num, num)
            except (ValueError, IndexError):
                pass

        # Always return one higher than the highest found
        return f"{prefix}-{max_num + 1:04d}"

    def update_member_type(self, new_type):
        """Smart update: regenerate unique_code if type changes."""
        if new_type != self.member_type:
            self.member_type = new_type
            self.unique_code = self.generate_unique_code(new_type)

    def get_current_price(self):
        """Fetch the most recent price for this member's type and plan."""
        latest_price = (
            GymPricing.query
            .filter_by(member_type=self.member_type, plan_type=self.gym_plan)
            .order_by(GymPricing.effective_date.desc())
            .first()
        )
        return latest_price.price if latest_price else 0.0

    def set_registration_price(self):
        """Set price_paid when the member registers."""
        self.price_paid = self.get_current_price()

    # ========================================
    # USER AUTHENTICATION METHODS
    # ========================================
    def set_password(self, password):
        """Hash and set password for user authentication."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verify password for user authentication."""
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    # ========================================
    # AUTO STATUS CHECKER
    # ========================================
    def check_and_update_status(self):
        """Automatically update member status based on current date."""
        current_date = datetime.now(pytz.timezone('Asia/Manila')).date()

        if current_date > self.end_date:
            self.status = 'Expired'
        elif self.status == 'Expired' and current_date <= self.end_date:
            # Optional: revive the member if extended manually
            self.status = 'Active'

        db.session.commit()

# ========================================
# MEMBERSHIP LOG MODEL
# ========================================
class MembershipLog(db.Model):
    __tablename__ = 'membership_logs'

    log_id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('members.member_id', ondelete='CASCADE'), nullable=False)
    action_type = db.Column(db.String(50), nullable=False)
    action_date = db.Column(db.DateTime, default=lambda: datetime.now(pytz.timezone('Asia/Manila')))
    remarks = db.Column(db.String(255))

    def __repr__(self):
        return f"<Log {self.action_type} for Member {self.member_id}>"

# ========================================
# WORKOUT MODEL
# ========================================
class Workout(db.Model):
    __tablename__ = 'workouts'

    workout_id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('members.member_id', ondelete='CASCADE'), nullable=False)
    workout_date = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(pytz.timezone('Asia/Manila')))
    exercise_type = db.Column(db.String(50), nullable=False)  # Cardio, Strength, Flexibility, etc.
    duration_minutes = db.Column(db.Integer, nullable=False)
    calories_burned = db.Column(db.Integer, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(pytz.timezone('Asia/Manila')))

    def __repr__(self):
        return f"<Workout {self.exercise_type} - {self.duration_minutes} min by Member {self.member_id}>"


# ========================================
# RENEWAL REQUEST MODEL
# ========================================
class RenewalRequest(db.Model):
    __tablename__ = 'renewal_requests'

    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('members.member_id', ondelete='CASCADE'), nullable=False)
    requested_plan = db.Column(db.Enum('Daily', 'Monthly'), nullable=False)
    status = db.Column(db.Enum('Pending', 'Approved', 'Denied'), default='Pending')
    request_date = db.Column(db.DateTime, default=lambda: datetime.now(pytz.timezone('Asia/Manila')))

    member = db.relationship('Member', backref='renewal_requests')


# ========================================
# ATTENDANCE LOG MODEL
# ========================================
class AttendanceLog(db.Model):
    __tablename__ = 'attendance_logs'

    attendance_id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('members.member_id', ondelete='CASCADE'), nullable=False)
    date = db.Column(db.Date, default=lambda: datetime.now(pytz.timezone('Asia/Manila')).date(), nullable=False)
    time_in = db.Column(db.DateTime, nullable=True)
    time_out = db.Column(db.DateTime, nullable=True)

    member = db.relationship('Member', backref='attendance_logs')

    def __repr__(self):
        return f"<Attendance Member {self.member_id}: {self.date} IN:{self.time_in} OUT:{self.time_out}>"
