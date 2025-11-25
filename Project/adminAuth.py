from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from . import db    
from .models import Admin


admin_Auth = Blueprint('adminAuth', __name__)

# ========================================
# ADMIN LOGIN
# ========================================
@admin_Auth.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        #process login credentials
        username = request.form.get('username')
        password = request.form.get('password')
        admin = Admin.query.filter_by(username=username).first()
        
        #Check if admin already exist and password is correct
        if admin and admin.check_password(password):
            session['admin_id'] = admin.id
            flash('Login successful!', 'success')
            return redirect(url_for('main.admin'))
        else:
            flash('Invalid credentials. Please try again.', 'danger')
    return render_template('admin/adminAuth.html')

# ========================================
# ADMIN LOGOUT
# ========================================
@admin_Auth.route('/admin-logout')
def admin_logout():
    session.pop('admin_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('adminAuth.admin_login'))