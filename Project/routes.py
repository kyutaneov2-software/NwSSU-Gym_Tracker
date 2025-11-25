from flask import Blueprint, render_template, request, session, redirect, url_for, flash, jsonify
from . import db
from .models import Admin
import pytz

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('admin/index.html')

@main.route('/NwSSU/About/Us')
def aboutUs():
    return render_template('admin/aboutUs.html')

@main.route('/admin/dashboard')
def admin():
    if 'admin_id' not in session:
        flash('Please log in to access admin page.', 'warning')
        return redirect(url_for('adminAuth.admin_login'))
    return render_template('admin/admin.html', page='dashboard')

@main.route('/admin/statistics')
def statistics():
    if 'admin_id' not in session:
        flash('Please log in to access admin page.', 'warning')
        return redirect(url_for('main.admin'))
    return render_template('admin/statistics.html', page='statistics')

