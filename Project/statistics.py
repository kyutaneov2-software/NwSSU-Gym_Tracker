from flask import Blueprint, jsonify
from . import db
from .models import Member, MembershipLog
from datetime import datetime, timedelta
import pytz

statistics = Blueprint('statistics', __name__)

@statistics.route('/admin/members-statistics', methods=['GET'])
def get_members_statistics():
    tz = pytz.timezone('Asia/Manila')
    now = datetime.now(tz)
    start_of_day = tz.localize(datetime(now.year, now.month, now.day))
    start_of_month = tz.localize(datetime(now.year, now.month, 1))

    members = Member.query.all()
    total_revenue = daily_revenue = monthly_revenue = 0
    total_members = len(members)
    active_members = 0

    # Initialize weekly revenue dictionary (last 7 days)
    # Inside statistics_summary()
    # --- WEEKLY REVENUE ---
    weekly_labels = []
    weekly_values = []
    for i in range(6, -1, -1):  # 6 days ago to today
        day = now - timedelta(days=i)
        weekly_labels.append(day.strftime("%a"))
        weekly_values.append(0)

    members = Member.query.all()
    tz = pytz.timezone("Asia/Manila")
    for m in members:
        price = float(m.price_paid or 0)
        created_at = m.last_payment_date or m.date_registered
        if created_at.tzinfo is None:
            created_at = tz.localize(created_at)
        if m.payment_status == "Paid":
            for idx, label_date in enumerate([(now - timedelta(days=i)).date() for i in range(6, -1, -1)]):
                if created_at.date() == label_date:
                    weekly_values[idx] += price


    member_list = []
    for m in members:
        price = float(m.price_paid or 0)
        created_at = m.last_payment_date or m.date_registered
        payment_status = m.payment_status

        if created_at.tzinfo is None:
            created_at = tz.localize(created_at)

        # Revenue calculations
        if payment_status == 'Paid':
            total_revenue += price
        if created_at >= start_of_month and payment_status == 'Paid':
            monthly_revenue += price
        if created_at >= start_of_day and payment_status == 'Paid':
            daily_revenue += price

        # Weekly revenue
        if payment_status == 'Paid':
            for idx, label_date in enumerate([(now - timedelta(days=i)).date() for i in range(6, -1, -1)]):
                if created_at.date() == label_date:
                    weekly_values[idx] += price

        if m.status.lower() == "active":
            active_members += 1

        member_list.append({
            "id": m.member_id,
            "unique_code": m.unique_code,
            "first_name": m.first_name,
            "last_name": m.last_name,
            "price_paid": m.price_paid,
            "member_type": m.member_type,
            "gym_plan": m.gym_plan,
            "status": m.status,
            "payment_status": m.payment_status,
            "created_at": created_at.strftime("%Y-%m-%d %H:%M:%S")
        })

    return jsonify({
        "members": member_list,
        "stats": {
            "total_revenue": total_revenue,
            "monthly_revenue": monthly_revenue,
            "daily_revenue": daily_revenue,
            "total_members": total_members,
            "active_members": active_members
        },
        "weekly_revenue": {
            "labels": weekly_labels,
            "values": weekly_values
        }
    })

@statistics.route('/admin/membership-logs', methods=['GET'])
def get_membership_logs():
    tz = pytz.timezone('Asia/Manila')
    now = datetime.now(tz)
    one_week_ago = now - timedelta(days=7)

    logs = (
        db.session.query(MembershipLog, Member)
        .join(Member, MembershipLog.member_id == Member.member_id)
        .filter(MembershipLog.action_date >= one_week_ago)
        .order_by(MembershipLog.action_date.desc())
        .all()
    )

    result = []
    for log, member in logs:
        try:
            action_type = str(log.action_type)
        except LookupError:
            action_type = "Unknown"

        result.append({
            "log_id": log.log_id,
            "member_id": member.member_id,
            "member_name": f"{member.first_name} {member.last_name}",
            "action_type": action_type,
            "action_date": log.action_date.strftime("%Y-%m-%d %H:%M:%S"),
            "remarks": log.remarks or ""
        })

    return jsonify(result)

@statistics.route("/admin/statistics-summary", methods=["GET"])
def statistics_summary():
    tz = pytz.timezone("Asia/Manila")
    now = datetime.now(tz)

    # --- LAST 6 MONTHS MEMBERSHIP DATA ---
    labels = []
    students_data = []
    faculty_data = []
    outsiders_data = []

    for i in range(5, -1, -1):
        target = now - timedelta(days=30 * i)
        year, month = target.year, target.month
        labels.append(target.strftime("%Y-%m"))

        start = tz.localize(datetime(year, month, 1))
        end = tz.localize(datetime(year + (month // 12), (month % 12) + 1, 1))

        students_data.append(Member.query.filter(Member.date_registered >= start,
                                                Member.date_registered < end,
                                                Member.member_type == "Student").count())
        faculty_data.append(Member.query.filter(Member.date_registered >= start,
                                                Member.date_registered < end,
                                                Member.member_type == "Faculty").count())
        outsiders_data.append(Member.query.filter(Member.date_registered >= start,
                                                Member.date_registered < end,
                                                Member.member_type == "Outsider").count())

    # --- SUMMARY CARDS ---
    total_members = Member.query.count()
    active_members = Member.query.filter_by(status="Active").count()
    type_counts = {"Students": sum(students_data), "Faculty": sum(faculty_data), "Outsiders": sum(outsiders_data)}
    most_active = max(type_counts, key=type_counts.get)

    # --- STATUS CHARTS ---
    status_overview = {
        "labels": ["Active", "Expired", "Pending"],
        "values": [
            Member.query.filter_by(status="Active").count(),
            Member.query.filter_by(status="Expired").count(),
            Member.query.filter_by(status="Pending").count()
        ]
    }
    status_chart = {
        "labels": ["Students", "Faculty", "Outsiders"],
        "values": [sum(students_data), sum(faculty_data), sum(outsiders_data)]
    }
    payment_status_chart = {
        "labels": ["Paid", "Unpaid", "Overdue"],
        "values": [
            Member.query.filter_by(payment_status="Paid").count(),
            Member.query.filter_by(payment_status="Unpaid").count(),
            Member.query.filter_by(payment_status="Overdue").count()
        ]
    }

    # --- WEEKLY REVENUE (last 7 days) ---
    weekly_labels = []
    weekly_values = [0] * 7
    for i in range(6, -1, -1):
        day = now - timedelta(days=i)
        weekly_labels.append(day.strftime("%a"))

    members = Member.query.filter(Member.payment_status == "Paid").all()
    for m in members:
        price = float(m.price_paid or 0)
        created_at = m.last_payment_date or m.date_registered
        if created_at.tzinfo is None:
            created_at = tz.localize(created_at)

        for idx, label_date in enumerate([(now - timedelta(days=i)).date() for i in range(6, -1, -1)]):
            if created_at.date() == label_date:
                weekly_values[idx] += price

    return jsonify({
        "summary": {"total": total_members, "active": active_members, "most_active": most_active},
        "overview_chart": {"labels": labels, "students": students_data, "faculty": faculty_data, "outsiders": outsiders_data},
        "status_overview": status_overview,
        "status_chart": status_chart,
        "payment_status_chart": payment_status_chart,
        "weekly_revenue": {"labels": weekly_labels, "values": weekly_values}
    })
