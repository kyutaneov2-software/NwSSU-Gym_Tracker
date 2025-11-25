from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from . import db
from .models import Member, RenewalRequest
import pytz
from datetime import datetime

userRenewals = Blueprint('userRenewals', __name__)

# ========================================
# USER RENEWAL REQUEST
# ========================================
@userRenewals.route('/user/request-renewal', methods=['POST'])
def user_request_renewal():
    # Get user_id from session
    user_id = session.get('user_id')
    if not user_id:
        flash("You must be logged in to request a renewal.", "warning")
        return redirect(url_for('userAuth.user_login'))

    member = Member.query.get(user_id)
    if not member:
        flash("Member record not found.", "danger")
        return redirect(url_for('userRoutes.dashboard'))

    # Prevent multiple pending requests
    existing = RenewalRequest.query.filter_by(member_id=user_id, status="Pending").first()
    if existing:
        flash("You already have a pending renewal request.", "info")
        return redirect(url_for('userRoutes.membership'))

    # Get plan from form
    requested_plan = request.form.get('requested_plan')
    if requested_plan not in ['Daily', 'Monthly']:
        flash("Invalid plan selected.", "danger")
        return redirect(url_for('userRoutes.membership'))

    # Create new renewal request
    new_request = RenewalRequest(member_id=user_id, requested_plan=requested_plan)
    db.session.add(new_request)
    db.session.commit()

    flash(f"Renewal request submitted for {requested_plan} plan.", "success")
    return redirect(url_for('userRoutes.membership'))

