from flask import Blueprint, render_template, request, session, redirect, url_for, flash, jsonify
from functools import wraps
from . import db
from .models import Member, Workout, AttendanceLog
from datetime import datetime, timedelta
import pytz

userRoutes = Blueprint('userRoutes', __name__)


# ========================================
# ROUTE PROTECTION DECORATOR
# ========================================
def user_login_required(f):
    """Decorator to protect user routes - requires user login."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('userAuth.user_login'))
        return f(*args, **kwargs)
    return decorated_function

# ========================================
# USER DASHBOARD
# ========================================
@userRoutes.route('/user/dashboard')
@user_login_required
def dashboard():
    user_id = session.get('user_id')
    member = Member.query.get(user_id)

    if not member:
        flash('User not found. Please login again.', 'error')
        session.clear()
        return redirect(url_for('userAuth.user_login'))

    # Update status
    member.check_and_update_status()

    tz = pytz.timezone('Asia/Manila')
    today = datetime.now(tz).date()

    # Days remaining
    days_remaining = (member.end_date - today).days if member.end_date > today else 0

    # Workout stats
    total_workouts = Workout.query.filter_by(member_id=user_id).count()
    total_minutes = db.session.query(
        db.func.sum(Workout.duration_minutes)
    ).filter_by(member_id=user_id).scalar() or 0

    total_hours = round(total_minutes / 60, 1)

    # Attendance count
    attendance_count = AttendanceLog.query.filter_by(member_id=user_id).count()

    # Recent workouts
    recent_workouts = Workout.query.filter_by(member_id=user_id) \
        .order_by(Workout.workout_date.desc()) \
        .limit(5).all()

    return render_template(
        'user/user_dashboard.html',
        member=member,
        days_remaining=days_remaining,
        total_workouts=total_workouts,
        total_hours=total_hours,
        recent_workouts=recent_workouts,
        attendance_count=attendance_count
    )

# ========================================
# HELPER: Calculate Workout Streak
# ========================================
def calculate_workout_streak(member_id):
    """Calculate consecutive days with at least one workout."""
    tz = pytz.timezone('Asia/Manila')
    today = datetime.now(tz).date()

    workouts = Workout.query.filter_by(member_id=member_id).order_by(Workout.workout_date.desc()).all()

    if not workouts:
        return 0

    # Get unique workout dates
    workout_dates = set()
    for workout in workouts:
        workout_date = workout.workout_date
        if workout_date.tzinfo is None:
            workout_date = tz.localize(workout_date)
        workout_dates.add(workout_date.date())

    # Calculate streak
    streak = 0
    current_date = today

    while current_date in workout_dates:
        streak += 1
        current_date -= timedelta(days=1)

    return streak

# ========================================
# USER PROFILE (View)
# ========================================
@userRoutes.route('/user/profile')
@user_login_required
def profile():
    user_id = session.get('user_id')
    member = Member.query.get(user_id)

    if not member:
        flash('User not found. Please login again.', 'error')
        session.clear()
        return redirect(url_for('userAuth.user_login'))

    return render_template('user/user_profile.html', member=member)

# ========================================
# USER PROFILE (Update)
# ========================================
@userRoutes.route('/user/profile/update', methods=['POST'])
@user_login_required
def update_profile():
    user_id = session.get('user_id')
    member = Member.query.get(user_id)

    if not member:
        flash('User not found. Please login again.', 'error')
        session.clear()
        return redirect(url_for('userAuth.user_login'))

    # Get form data (only allow editing safe fields)
    contact_number = request.form.get('contact_number', '').strip()
    address = request.form.get('address', '').strip()

    # Update fields
    member.contact_number = contact_number
    member.address = address

    try:
        db.session.commit()
        flash('Profile updated successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Failed to update profile. Please try again.', 'error')
        print(f"Profile update error: {e}")

    return redirect(url_for('userRoutes.profile'))

# ========================================
# MEMBERSHIP DETAILS
# ========================================
@userRoutes.route('/user/membership')
@user_login_required
def membership():
    user_id = session.get('user_id')
    member = Member.query.get(user_id)

    if not member:
        flash('User not found. Please login again.', 'error')
        session.clear()
        return redirect(url_for('userAuth.user_login'))

    # Update status
    member.check_and_update_status()

    # Calculate days remaining
    tz = pytz.timezone('Asia/Manila')
    today = datetime.now(tz).date()
    days_remaining = (member.end_date - today).days if member.end_date > today and member.status == 'Active'  else 0

    return render_template('user/user_membership.html',
                        member=member,
                        days_remaining=days_remaining)

#=========================================
# ATTENDANCE ROUTES
#=========================================
# --- 1. CHECK TODAY'S ATTENDANCE STATUS ---
@userRoutes.route("/user/attendance/status", methods=["GET"])
@user_login_required
def attendance_status():
    user_id = session.get("user_id")
    tz = pytz.timezone("Asia/Manila")
    today = datetime.now(tz).date()

    record = AttendanceLog.query.filter_by(member_id=user_id, date=today).first()

    if not record:
        return jsonify({"time_in": False, "time_out": False})

    return jsonify({
        "time_in": record.time_in is not None,
        "time_out": record.time_out is not None
    })


# --- 2. TIME IN ---
@userRoutes.route("/user/attendance/time_in", methods=["POST"])
@user_login_required
def attendance_time_in():
    user_id = session.get("user_id")
    tz = pytz.timezone("Asia/Manila")
    now = datetime.now(tz)
    today = now.date()

    record = AttendanceLog.query.filter_by(member_id=user_id, date=today).first()

    if record and record.time_in:
        return jsonify({"success": False, "message": "Already timed in today."})

    if not record:
        record = AttendanceLog(member_id=user_id, date=today)

    record.time_in = now
    db.session.add(record)
    db.session.commit()

    return jsonify({"success": True})


# --- 3. TIME OUT ---
@userRoutes.route("/user/attendance/time_out", methods=["POST"])
@user_login_required
def attendance_time_out():
    user_id = session.get("user_id")
    tz = pytz.timezone("Asia/Manila")
    now = datetime.now(tz)
    today = now.date()

    record = AttendanceLog.query.filter_by(member_id=user_id, date=today).first()

    if not record or not record.time_in:
        return jsonify({"success": False, "message": "You must time in first."})

    if record.time_out:
        return jsonify({"success": False, "message": "Already timed out."})

    record.time_out = now
    db.session.commit()

    return jsonify({"success": True})