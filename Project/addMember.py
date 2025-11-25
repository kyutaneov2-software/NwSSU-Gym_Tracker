from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from . import db
from .models import Member, MembershipLog, GymPricing, RenewalRequest
from datetime import datetime
from functools import lru_cache
import pytz
import calendar
import time  # for time.time()
from sqlalchemy import and_, func  # for and_ and func
from sqlalchemy.orm import joinedload  # for joinedload used in renewal requests


addMember = Blueprint('addMember', __name__)

# Cache (in-memory)
_cache_data = None
_cache_time = 0

# Automatically mark members as expired if their end_date has passed.
def auto_update_expired_members():
    tz = pytz.timezone("Asia/Manila")
    today = datetime.now(tz).date()

    expired_members = Member.query.filter(
        and_(
            Member.end_date < today,
            Member.status != "Expired"
        )
    ).all()

    count = 0
    for member in expired_members:
        # Skip members manually set to Active (admin override)
        if member.status == "Active":
            continue

        member.status = "Expired"
        count += 1

        log = MembershipLog(
            member_id=member.member_id,
            action_type='Status Update',
            remarks=f"Automatically marked as expired (End date: {member.end_date})."
        )
        db.session.add(log)

    if count > 0:
        db.session.commit()

    return count

# Add Member
@addMember.route('/admin/add-member', methods=['GET', 'POST'])
def add_member():
    if request.method == 'POST':
        try:
            # --- Collect form data ---
            first_name = request.form.get('first_name')
            last_name = request.form.get('last_name')
            age = request.form.get('age')
            gender = request.form.get('gender')
            member_type = request.form.get('member_type')
            student_number = request.form.get('student_number') if member_type == 'Student' else None
            gym_plan = request.form.get('gym_plan')
            email = request.form.get('email')
            contact_number = request.form.get('contact_number')
            address = request.form.get('address')
            start_date = request.form.get('Start_date')
            end_date = request.form.get('End_date')

            # --- Validation ---
            required_fields = [first_name, last_name, member_type, gym_plan, start_date, end_date]
            if not all(required_fields):
                return jsonify({
                    "success": False,
                    "error": "Please fill in all required fields."
                }), 400

            # --- Convert dates ---
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

            # --- Create new member ---
            new_member = Member(
                first_name=first_name,
                last_name=last_name,
                age=age if age else None,
                gender=gender if gender else None,
                member_type=member_type,
                student_number=student_number,
                gym_plan=gym_plan,
                email=email,
                contact_number=contact_number,
                address=address,
                start_date=start_date,
                end_date=end_date
            )

            # --- Fetch price based on type/plan ---
            current_price = GymPricing.query.filter_by(
                member_type=member_type,
                plan_type=gym_plan
            ).first()

            new_member.price_paid = current_price.price if current_price else 0.0

            db.session.add(new_member)
            db.session.commit()

            # --- Log registration ---
            new_log = MembershipLog(
                member_id=new_member.member_id,
                action_type='Registered',
                remarks=f"Member {first_name} {last_name} registered successfully."
            )
            db.session.add(new_log)
            db.session.commit()

            # --- JSON Response (for AJAX/fetch) ---
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({
                    "success": True,
                    "message": f"New member registered successfully! Paid ₱{new_member.price_paid:.2f}",
                    "member": {
                        "id": new_member.member_id,
                        "first_name": new_member.first_name,
                        "last_name": new_member.last_name,
                        "price_paid": new_member.price_paid,
                        "status": new_member.status,
                        "payment_status": new_member.payment_status
                    }
                }), 200

            # --- Normal form submission ---
            flash(f"New member {new_member.first_name} {new_member.last_name} added successfully!", "success")
            return redirect(url_for('addMember.add_member'))

        except Exception as e:
            db.session.rollback()
            return jsonify({
                "success": False,
                "error": f"Error registering member: {str(e)}"
            }), 500

    # ===========================
    # 📋 GET Request - Render Members Page
    # ===========================
    if request.method == 'GET':
        members = Member.query.all()
        auto_update_expired_members()  # check and update expired members
        
        # Fetch renewal requests too
        renewal_requests = (
            RenewalRequest.query
            .options(joinedload(RenewalRequest.member))
            .order_by(RenewalRequest.request_date.desc())
            .all()
        )
        return render_template('admin/members.html', members=members,renewal_requests=renewal_requests)

# View specific member details (AJAX endpoint)
@addMember.route('/admin/member/<int:member_id>', methods=['GET'])
def view_member(member_id):
    member = Member.query.get_or_404(member_id)
    
    member_data = {
        "member_id": member.member_id,
        "unique_code": member.unique_code,
        "first_name": member.first_name,
        "last_name": member.last_name,
        "age": member.age,
        "gender": member.gender,
        "member_type": member.member_type,
        "gym_plan": member.gym_plan,
        "email": member.email,
        "contact_number": member.contact_number,
        "address": member.address,
        "start_date": member.start_date.strftime("%Y-%m-%d"),
        "end_date": member.end_date.strftime("%Y-%m-%d"),
        "status": member.status,
        "payment_status": member.payment_status
    }
    return jsonify(member_data)


# Update Member
@addMember.route('/admin/member/<int:member_id>/edit', methods=['POST'])
def edit_member(member_id):
    member = Member.query.get_or_404(member_id)

    try:
        data = request.get_json()   

        # Track original type
        old_type = member.member_type
        new_type = data.get('member_type', member.member_type)

        # Update general info
        member.first_name = data.get('first_name', member.first_name)
        member.last_name = data.get('last_name', member.last_name)
        member.age = data.get('age', member.age)
        member.gender = data.get('gender', member.gender)
        member.gym_plan = data.get('gym_plan', member.gym_plan)
        member.email = data.get('email', member.email)
        member.contact_number = data.get('contact_number', member.contact_number)
        member.address = data.get('address', member.address)
        member.start_date = datetime.strptime(data.get('start_date'), '%Y-%m-%d').date()
        member.end_date = datetime.strptime(data.get('end_date'), '%Y-%m-%d').date()
        member.status = data.get('status', member.status)
        member.payment_status = data.get('payment_status', member.payment_status)

        # Handle type change
        if new_type != old_type:
            member.update_member_type(new_type)

        # Auto-update status based on new end date
        from pytz import timezone
        tz = timezone("Asia/Manila")
        current_date = datetime.now(tz).date()

        member.status = data.get('status', member.status)
        member.payment_status = data.get('payment_status', member.payment_status)

        db.session.commit()

        # Log edit
        log = MembershipLog(
            member_id=member.member_id,
            action_type='Updated',
            remarks=f"Updated information for {member.first_name} {member.last_name}."
        )
        db.session.add(log)
        db.session.commit()

        flash(f"Member {member.first_name} {member.last_name} was updated successfully!", "success")

        # Return success response
        return jsonify({
            "success": True,
            "message": f"{member.first_name} {member.last_name} updated successfully!",
            "member": {
                "id": member.member_id,
                "first_name": member.first_name,
                "last_name": member.last_name,
                "plan": member.gym_plan,
                "status": member.status,
                "payment_status": member.payment_status
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


# Delete Member
@addMember.route('/admin/member/<int:member_id>/delete', methods=['DELETE'])
def delete_member(member_id):
    # Get member ID from database
    member = Member.query.get_or_404(member_id)
    try:
        db.session.delete(member)
        db.session.commit()

        # log membership
        log = MembershipLog(
            member_id=member_id,
            action_type='Updated',
            remarks=f"Deleted member record for {member.first_name} {member.last_name}."
        )
        db.session.add(log)
        db.session.commit()

        return jsonify({"success": True, "message": "Member deleted successfully!"})

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

@addMember.route('/admin/dashboard-summary', methods=['GET'])
def dashboard_summary():
    global _cache_data, _cache_time

    now_time = time.time()

    # Auto-expire members before calculations
    auto_update_expired_members()

    # Cache valid for 10 seconds
    if _cache_data and now_time - _cache_time < 10:
        return jsonify(_cache_data)

    try:
        tz = pytz.timezone("Asia/Manila")
        now = datetime.now(tz)

        # === SUMMARY ===
        status_counts = dict(
            db.session.query(Member.status, func.count(Member.member_id))
            .group_by(Member.status)
            .all()
        )

        active_counts = dict(
            db.session.query(Member.member_type, func.count(Member.member_id))
            .filter(Member.status == "Active")
            .group_by(Member.member_type)
            .all()
        )

        total_members = sum(status_counts.values())
        active_members = status_counts.get("Active", 0)

        type_counts = {
            "Student": active_counts.get("Student", 0),
            "Faculty": active_counts.get("Faculty", 0),
            "Outsider": active_counts.get("Outsider", 0)
        }

        most_active_type = max(type_counts, key=type_counts.get) if active_members > 0 else "N/A"

        # === 6-MONTH CHART ===
        monthly_labels = []
        student_counts = []
        faculty_counts = []
        outsider_counts = []

        for i in range(5, -1, -1):
            month = now.month - i
            year = now.year

            if month <= 0:
                month += 12
                year -= 1

            label = datetime(year, month, 1).strftime("%b")
            monthly_labels.append(label)

            start = tz.localize(datetime(year, month, 1))
            end_day = calendar.monthrange(year, month)[1]
            end = tz.localize(datetime(year, month, end_day, 23, 59, 59))

            # Safely handle NULL start/end
            base_filter = and_(
                Member.status == "Active",
                Member.start_date != None,
                Member.end_date != None,
                Member.start_date <= end,
                Member.end_date >= start
            )

            counts = dict(
                db.session.query(Member.member_type, func.count(Member.member_id))
                .filter(base_filter)
                .group_by(Member.member_type)
                .all()
            )

            student_counts.append(counts.get("Student", 0))
            faculty_counts.append(counts.get("Faculty", 0))
            outsider_counts.append(counts.get("Outsider", 0))

        result = {
            "summary": {
                "total": total_members,
                "active": active_members,
                "most_active": most_active_type
            },
            "overview_chart": {
                "labels": monthly_labels,
                "students": student_counts,
                "faculty": faculty_counts,
                "outsiders": outsider_counts
            },
            "status_chart": {
                "labels": ["Student", "Faculty", "Outsider"],
                "values": [
                    type_counts["Student"],
                    type_counts["Faculty"],
                    type_counts["Outsider"]
                ]
            },
            "status_overview": {
                "labels": ["Active", "Inactive", "Expired"],
                "values": [
                    status_counts.get("Active", 0),
                    status_counts.get("Inactive", 0),
                    status_counts.get("Expired", 0)
                ]
            }
        }

        # Store cache
        _cache_data = result
        _cache_time = now_time

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Get all members as JSON (for members.js use)
@addMember.route('/admin/members-json', methods=['GET'])
def get_members_json():
    members = Member.query.all()
    return jsonify({
        "members": [
            {
                "member_id": m.member_id,
                "unique_code": m.unique_code,
                "first_name": m.first_name,
                "last_name": m.last_name,
                "member_type": m.member_type,
                "gym_plan": m.gym_plan,
                "status": m.status,
                "email": m.email,
                "contact_number": m.contact_number,
                "start_date": m.start_date.strftime("%Y-%m-%d"),
                "end_date": m.end_date.strftime("%Y-%m-%d")
            }
            for m in members
        ]
    })

@addMember.route("/admin/renewals-json")
def renewals_json():
    requests = RenewalRequest.query.all()

    return jsonify({
        "renewals": [
            {
                "id": r.id,
                "first_name": r.member.first_name if r.member else "-",
                "last_name": r.member.last_name if r.member else "",
                "member_type": r.member.member_type if r.member else "-",
                "current_plan": r.member.gym_plan if r.member else "-",
                "requested_plan": r.requested_plan,
                "status": r.status
            }
            for r in requests
        ]
    })


# ADMIN: Handle renewal request
@addMember.route('/admin/renewal/<int:request_id>', methods=['POST'])
def handle_renewal_request(request_id):
    data = request.get_json()
    status = data.get('status')

    if status not in ['Approved', 'Denied']:
        return jsonify({"success": False, "message": "Invalid status"})

    renewal_request = RenewalRequest.query.get(request_id)
    if not renewal_request or not renewal_request.member:
        return jsonify({"success": False, "message": "Request or member not found"})

    try:
        renewal_request.status = status
        member = renewal_request.member

        if status == 'Approved':
            member.gym_plan = renewal_request.requested_plan
            member.status = "Active"
            member.payment_status = "Paid"

            from datetime import timedelta
            tz = pytz.timezone("Asia/Manila")
            today = datetime.now(tz).date()
            member.start_date = today

            # IMPORTANT: This line makes statistics update!
            member.last_payment_date = datetime.now(pytz.timezone('Asia/Manila'))

            # Fetch pricing
            plan_info = GymPricing.query.filter_by(
                member_type=member.member_type,
                plan_type=renewal_request.requested_plan
            ).first()

            requested_plan = renewal_request.requested_plan

            # Duration logic
            if requested_plan == "Daily":
                duration = 1
            elif requested_plan == "Monthly":
                duration = 30
            elif requested_plan == "Annual":
                duration = 365
            else:
                duration = 30

            member.end_date = today + timedelta(days=duration)
            member.price_paid = plan_info.price if plan_info else 0.0

            # Log
            log = MembershipLog(
                member_id=member.member_id,
                action_type='Renewal Approved',
                remarks=f"Renewal approved. Plan updated to {member.gym_plan}, payment status {member.payment_status}."
            )
            db.session.add(log)


        elif status == 'Denied':
            log = MembershipLog(
                member_id=member.member_id,
                action_type='Renewal Denied',
                remarks=f"Renewal request for {renewal_request.requested_plan} plan denied."
            )
            db.session.add(log)

        db.session.commit()
        return jsonify({"success": True, "message": f"Renewal request {status.lower()} successfully."})

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)})

    
@addMember.route('/admin/renewal/delete/<int:request_id>', methods=['DELETE'])
def delete_renewal_request(request_id):
    renewal_request = RenewalRequest.query.get(request_id)
    if not renewal_request:
        return jsonify({"success": False, "message": "Request not found"})

    try:
        db.session.delete(renewal_request)
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)})

