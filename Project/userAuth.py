from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from . import db
from .models import Member, MembershipLog, GymPricing
from datetime import datetime, timedelta
from werkzeug.security import check_password_hash
import pytz
import re

userAuth = Blueprint('userAuth', __name__)

# ========================================
# HELPER: Email Validation
# ========================================
def is_valid_email(email):
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# ========================================
# HELPER: Calculate End Date
# ========================================
def calculate_end_date(start_date, gym_plan):
    """Calculate membership end date based on plan."""
    if gym_plan == 'Daily':
        return start_date + timedelta(days=1)
    elif gym_plan == 'Monthly':
        return start_date + timedelta(days=30)
    elif gym_plan == 'Annual':
        return start_date + timedelta(days=365)
    return start_date

# ========================================
# USER REGISTRATION
# ========================================
@userAuth.route('/user/register', methods=['GET', 'POST'])
def user_register():
    # If already logged in, redirect to dashboard
    if 'user_id' in session:
        return redirect(url_for('userRoutes.dashboard'))

    if request.method == 'POST':
        # Get form data
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        age = request.form.get('age', type=int)
        gender = request.form.get('gender')
        member_type = request.form.get('member_type')
        student_number = request.form.get('student_number', '').strip()
        gym_plan = request.form.get('gym_plan')
        contact_number = request.form.get('contact_number', '').strip()
        address = request.form.get('address', '').strip()

        # Validation
        errors = []

        if not first_name or not last_name:
            errors.append('First name and last name are required.')

        if not email or not is_valid_email(email):
            errors.append('Valid email is required.')

        if not password or len(password) < 6:
            errors.append('Password must be at least 6 characters.')

        if password != confirm_password:
            errors.append('Passwords do not match.')

        if not age or age < 1 or age > 120:
            errors.append('Valid age is required.')

        if gender not in ['Male', 'Female']:
            errors.append('Gender is required.')

        if member_type not in ['Student', 'Faculty', 'Outsider']:
            errors.append('Member type is required.')

        if member_type == 'Student' and not student_number:
            errors.append('Student number is required for students.')

        if gym_plan not in ['Daily', 'Monthly', 'Annual']:
            errors.append('Gym plan is required.')

        if gym_plan == 'Annual':
            errors.append('Annual plans are not available yet.')

        # Check for existing email
        existing_member = Member.query.filter_by(email=email).first()
        if existing_member:
            if existing_member.password_hash:
                errors.append('Email already registered. Please login instead.')
            else:
                # Allow claiming admin-created account
                errors.append('Email exists in our system. Please contact admin to activate your account.')

        # If validation fails, show errors
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('user/user_register.html')

        # Create new member
        tz = pytz.timezone('Asia/Manila')
        start_date = datetime.now(tz).date()
        end_date = calculate_end_date(start_date, gym_plan)

        new_member = Member(
            first_name=first_name,
            last_name=last_name,
            email=email,
            age=age,
            gender=gender,
            member_type=member_type,
            student_number=student_number if member_type == 'Student' else None,
            gym_plan=gym_plan,
            contact_number=contact_number,
            address=address,
            start_date=start_date,
            end_date=end_date,
            is_self_registered=True
        )

        # Set password
        new_member.set_password(password)

        # Set price
        new_member.set_registration_price()

        # Save to database
        try:
            db.session.add(new_member)
            db.session.commit()

            # Create membership log
            log = MembershipLog(
                member_id=new_member.member_id,
                action_type='User Registration',
                remarks=f'User self-registered with {gym_plan} plan'
            )
            db.session.add(log)
            db.session.commit()

            flash(f'Registration successful! Your Member ID is {new_member.unique_code}. Please login.', 'success')
            return redirect(url_for('userAuth.user_login'))

        except Exception as e:
            db.session.rollback()
            flash('Registration failed. Please try again.', 'error')
            print(f"Registration error: {e}")
            return render_template('user/user_register.html')

    # GET request - show registration form
    return render_template('user/user_register.html')

# ========================================
# USER LOGIN
# ========================================
@userAuth.route('/user/login', methods=['GET', 'POST'])
def user_login():
    # If already logged in, redirect to dashboard
    if 'user_id' in session:
        return redirect(url_for('userRoutes.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        # Validation
        if not email or not password:
            flash('Email and password are required.', 'error')
            return render_template('user/user_login.html')

        # Find user
        member = Member.query.filter_by(email=email).first()

        if not member:
            flash('Invalid email or password.', 'error')
            return render_template('user/user_login.html')

        # Check if user has password (is self-registered)
        if not member.password_hash:
            flash('This account has not been activated yet. Please activate your account first.', 'warning')
            return redirect(url_for('userAuth.activate_account'))

        # Verify password
        if not member.check_password(password):
            flash('Invalid email or password.', 'error')
            return render_template('user/user_login.html')

        # Check membership status
        member.check_and_update_status()

        if member.status == 'Expired':
            flash('Your membership has expired. Please renew to continue.', 'warning')
            # Still allow login to see expired status

        # Login successful - create session
        session['user_id'] = member.member_id
        session['user_name'] = f"{member.first_name} {member.last_name}"
        session['user_email'] = member.email

        flash(f'Welcome back, {member.first_name}!', 'success')
        return redirect(url_for('userRoutes.dashboard'))

    # GET request - show login form
    return render_template('user/user_login.html')

# ========================================
# USER LOGOUT
# ========================================
@userAuth.route('/user/logout')
def user_logout():
    # Clear user session
    session.pop('user_id', None)
    session.pop('user_name', None)
    session.pop('user_email', None)

    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('main.index'))


# ========================================
# ACTIVATE ADMIN REGISTERED USER
# ========================================
@userAuth.route('/user/activate', methods=['GET', 'POST'])
def activate_account():
    # Implement your activation logic here
    return render_template('user/activate_account.html')

# ========================================
# LOGIN ADMIN REGISTERED USER
# ========================================
@userAuth.route('/user/admin-login', methods=['GET', 'POST'])
def admin_member_login():
    """
    Login for admin-created members using unique code (primary) and email (optional).
    """
    # Redirect if already logged in
    if 'user_id' in session:
        return redirect(url_for('userRoutes.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        unique_code = request.form.get('unique_code', '').strip().upper()

        if not unique_code:
            flash('Member ID is required.', 'error')
            return render_template('user/activate_account.html')

        # Try to find member by unique_code first
        member = Member.query.filter_by(unique_code=unique_code).first()

        if not member:
            flash('Invalid Member ID.', 'error')
            return render_template('user/activate_account.html')

        # Only allow admin-created members
        if member.is_self_registered:
            flash('Please login using your regular user login.', 'warning')
            return redirect(url_for('userAuth.user_login'))

        # If email is provided, verify it matches
        if email and member.email and member.email.lower() != email:
            flash('Email does not match the Member ID.', 'error')
            return render_template('user/activate_account.html')

        # Check membership status
        member.check_and_update_status()

        # Successful login
        session['user_id'] = member.member_id
        session['user_name'] = f"{member.first_name} {member.last_name}"
        session['user_email'] = member.email

        flash(f'Welcome back, {member.first_name}!', 'success')
        return redirect(url_for('userRoutes.dashboard'))

    # GET request
    return render_template('user/activate_account.html')
