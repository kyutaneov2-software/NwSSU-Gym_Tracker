# NwSSU Gym Tracker System

A comprehensive gym management system built with Flask for Northwest Samar State University. This system provides both administrative and member-facing features for managing gym memberships, tracking workouts, and monitoring gym statistics.

## Table of Contents
- [Technology Stack](#technology-stack)
- [How to Run the Website](#how-to-run-the-website)
- [Current Implementation Overview](#current-implementation-overview)
- [User Features Implementation Details](#user-features-implementation-details)
- [Troubleshooting](#troubleshooting)
---

## Technology Stack

- **Backend**: Flask 3.1.2 (Python web framework)
- **Database**: SQLite with SQLAlchemy 2.0.44 ORM
- **Authentication**: Werkzeug password hashing
- **Frontend**: HTML5, CSS3, JavaScript
- **Template Engine**: Jinja2
- **Timezone**: Asia/Manila (Philippine Time)

---

## How to Run the Website

### Prerequisites
- Python 3.13 or higher installed
- pip package manager

### Installation & Setup

#### 1. Clone the Repository
```bash
git clone https://github.com/tormis-neil/GTS-System-.git
cd GTS-System-
```

#### 2. Install Dependencies

**Option A: Using `python` command** (Linux/Mac/Some Windows)
```bash
python -m pip install -r requirements.txt
```

**Option B: Using `py` command** (Windows with Python Launcher)
```bash
py -m pip install -r requirements.txt
```

**Option C: Using `python3` command** (Linux/Mac explicit Python 3)
```bash
python3 -m pip install -r requirements.txt
```

**Option D: Direct `pip` command** (if pip is in PATH)
```bash
pip install -r requirements.txt
```

> **Note**: If you get "pip is not recognized" error on Windows, use **Option B** (`py -m pip`). This is the most reliable method on Windows.

#### 3. Run the Application

**Option A: Using `python` command**
```bash
python run.py or python main.py
```

**Option B: Using `py` command** (Windows)
```bash
py run. or py main.py
```

**Option C: Using `python3` command** (Linux/Mac)
```bash
python3 run.py or python3 main.py
```

**Option D: Using Flask CLI**
```bash
flask run or flask main
```

#### 4. Access the Website

Once the server is running, open your browser and navigate to:
```
http://127.0.0.1:5000/ or similar link
```

### Default Admin Credentials
- **Username**: `admin`
- **Password**: `admin123`

---

## Current Implementation Overview

### Admin Features (Existing)
- **Dashboard**: Real-time statistics and analytics
- **Member Management**: Add, edit, delete, and view member details
- **Membership Tracking**: Monitor active memberships and expirations
- **Statistics**: Visual analytics with charts and graphs
- **Gym Pricing**: Configure membership plans and pricing

### User/Member Features (Phase 1 - Implemented)

#### 1. Account Management
- **Self-Registration**: New members can create accounts independently
  - Auto-generated member codes (STU-XXX for students, FCT-XXX for faculty, OTD-XXX for others)
  - Email and password authentication
  - Member type selection (Student, Faculty, Other)
  - Gym plan selection (1 Month, 3 Months, 6 Months, 1 Year)

- **Account Activation Portal**: Admin-created members can activate their accounts
  - Step 1: Verify email and Member ID
  - Step 2: Set personal password
  - Secure two-step verification process

- **Login/Logout**: Secure session-based authentication
  - Separate session management from admin
  - Password verification with Werkzeug hashing

#### 2. User Dashboard
- **Welcome Card**: Displays member information (name, member code, type)
- **Membership Overview**:
  - Current membership status (Active/Expired/Inactive)
  - Days remaining in membership
  - Membership expiration date
- **Workout Statistics**:
  - Total workouts logged
  - Current workout streak (consecutive days)
  - Recent workout history
- **Flash Messages**: Real-time feedback for user actions

#### 3. Profile Management
- **View Profile**: Complete member information display
  - Personal info (name, age, gender, member type)
  - Contact information (email, phone, address)
  - Membership details (member code, join date)
  - Emergency contact information
- **Edit Contact Info**: Update phone number and address
  - Form validation
  - Success/error feedback

#### 4. Membership Details
- **Comprehensive Membership View**:
  - Member code and type
  - Current plan (duration and pricing)
  - Start and end dates
  - Days remaining calculation
  - Status badges (Active/Expired/Inactive)
- **Alerts**:
  - Expiring soon warning (less than 7 days)
  - Expired membership notice
  - Active membership confirmation
- **Help Section**: Instructions for membership renewal

#### 5. UI/UX Design
- **Consistent Theme**: Matches admin panel color scheme
  - Dark background (#0a0e27)
  - Cyan accent color (#00d9ff)
  - Card-based layout with borders
- **Responsive Design**: Works on desktop and mobile devices
- **Horizontal Navigation**: Website-style navbar (not mobile hamburger menu)
  - Logo and branding
  - Navigation links (Dashboard, Profile, Membership)
  - User greeting and logout button
- **Accessibility**: Clear typography, proper contrast, intuitive navigation

---

## User Features Implementation Details

### Files Changed/Created for User Features

#### Backend Files

##### 1. `Project/models.py` - Database Models
**Changes Made**: Extended Member model and created Workout model

**New Fields in Member Model**:
```python
password_hash = db.Column(db.String(200), nullable=True)  # For user authentication
is_self_registered = db.Column(db.Boolean, default=False)  # Track registration source
```

**New Methods in Member Model**:
```python
def set_password(self, password):
    """Hash and set password for user authentication."""
    self.password_hash = generate_password_hash(password)

def check_password(self, password):
    """Verify password for user authentication."""
    if not self.password_hash:
        return False
    return check_password_hash(self.password_hash, password)
```

**New Workout Model**:
```python
class Workout(db.Model):
    __tablename__ = 'workouts'
    workout_id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('members.member_id', ondelete='CASCADE'))
    workout_date = db.Column(db.DateTime, nullable=False)
    exercise_type = db.Column(db.String(50), nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    calories_burned = db.Column(db.Integer, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
```

**Purpose**: Enables user authentication and prepares database for future workout tracking features.

---

##### 2. `Project/userAuth.py` - User Authentication Routes
**Status**: NEW FILE

**Routes Implemented**:
- `GET/POST /user/register` - Self-registration for new members
- `GET/POST /user/login` - User login with email/password
- `GET /user/logout` - User logout and session cleanup
- `GET/POST /activate-account` - Two-step account activation for admin-created members

**Key Features**:
- Auto-generates unique member codes with prefixes (STU/FCT/OTD)
- Validates email format and password strength (minimum 6 characters)
- Creates membership logs automatically upon registration
- Separate session management using `session['user_id']`
- Redirects to activation portal if account needs password setup

**Blueprint Registration**: `app.register_blueprint(userAuth)`

---

##### 3. `Project/userRoutes.py` - User Dashboard & Profile Routes
**Status**: NEW FILE

**Route Protection Decorator**:
```python
def user_login_required(f):
    """Decorator to protect user routes - requires user login."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('userAuth.user_login'))
        return f(*args, **kwargs)
    return decorated_function
```

**Routes Implemented**:
- `GET /user/dashboard` - User dashboard with stats and recent workouts
- `GET /user/profile` - View complete profile information
- `POST /user/profile/update` - Update contact information (phone, address)
- `GET /user/membership` - View detailed membership information

**Key Features**:
- Calculates membership days remaining
- Determines membership status (Active/Expired/Inactive)
- Fetches workout statistics (total workouts, streak)
- Form validation for profile updates
- Flash messages for user feedback

**Blueprint Registration**: `app.register_blueprint(userRoutes)`

---

##### 4. `Project/__init__.py` - Application Factory
**Changes Made**: Registered new blueprints and imported Workout model

**New Imports**:
```python
from .userAuth import userAuth
from .userRoutes import userRoutes
from .models import Admin, Member, MembershipLog, GymPricing, Workout
```

**New Blueprint Registrations**:
```python
app.register_blueprint(userAuth)
app.register_blueprint(userRoutes)
```

**Purpose**: Integrates user features into the main Flask application.

---

#### Frontend Files

##### 5. `Project/templates/user_base.html` - User Base Template
**Status**: NEW FILE

**Key Features**:
- Extends `base.html` for consistent styling
- Implements horizontal navigation bar (website-style, not mobile hamburger)
- Navigation sections:
  - Left: Logo, branding, navigation links (Dashboard, Profile, Membership)
  - Right: User greeting, logout button
- Conditional rendering based on `session.user_id`
- Links user_navbar.css stylesheet

**CSS Import**:
```html
<link rel="stylesheet" href="{{ url_for('static', filename='css/layout/user_navbar.css') }}">
```

---

##### 6. `Project/templates/user_login.html` - User Login Page
**Status**: NEW FILE (replaces old mobile-style login)

**Key Features**:
- Dark theme with cyan accents (matches admin)
- Centered login card with logo
- Email and password input fields
- "Activate Account" link for admin-created members
- "Create Account" link for new users
- Flash message display area
- Responsive design

**Form Fields**:
- Email (required, email validation)
- Password (required, type="password")
- Submit button with hover effects

---

##### 7. `Project/templates/user_register.html` - User Registration Page
**Status**: NEW FILE (replaces old mobile-style registration)

**Key Features**:
- Organized into 4 sections with clear headings:
  1. Personal Information (first name, last name, age, gender)
  2. Account Information (email, password, confirm password)
  3. Membership Details (member type, gym plan)
  4. Contact Information (phone, address, emergency contact)
- Form validation indicators
- Password strength requirements (minimum 6 characters)
- Dropdown selectors for member type and gym plan
- Link to login page for existing users

**Design**: Card-based layout with dark background and cyan accents

---

##### 8. `Project/templates/activate_account.html` - Account Activation Page
**Status**: NEW FILE

**Two-Step Process**:

**Step 1 - Verification**:
- Email input field
- Member ID input field
- Verify button

**Step 2 - Set Password**:
- New password input field
- Confirm password input field
- Activate button

**Key Features**:
- Hidden member_id field passed between steps
- Password strength validation (minimum 6 characters)
- Clear instructions for each step
- Link to login page
- Dark theme with cyan accents

---

##### 9. `Project/templates/user_dashboard.html` - User Dashboard
**Status**: NEW FILE (replaces old mobile-style dashboard)

**Layout Sections**:

**Welcome Card**:
- Displays user name, member code, and member type
- Personalized greeting

**Statistics Grid (4 Cards)**:
1. **Membership Status**: Active/Expired/Inactive badge
2. **Days Remaining**: Countdown to membership expiration
3. **Total Workouts**: Count of logged workouts
4. **Workout Streak**: Consecutive days with workouts

**Recent Workouts Section**:
- Table with columns: Date, Exercise Type, Duration, Calories, Notes
- Shows last 5 workouts
- Empty state message if no workouts logged

**Design**: Card-based layout with dark background, cyan accents, responsive grid

---

##### 10. `Project/templates/user_profile.html` - User Profile Page
**Status**: NEW FILE (replaces old mobile-style profile)

**Layout Sections**:

**Profile Information Grid** (Read-Only):
- Member ID
- Email
- Full Name
- Age
- Gender
- Member Type
- Join Date

**Update Contact Information Form** (Editable):
- Contact Number input field
- Address textarea field
- Update button

**Info Notice**:
- Instructions on how to request changes to read-only fields

**Design**: Two-column grid layout with cards, dark theme with cyan accents

---

##### 11. `Project/templates/user_membership.html` - Membership Details Page
**Status**: NEW FILE (replaces old mobile-style membership)

**Layout Sections**:

**Membership Details Grid (6 Cards)**:
1. **Member Code**: Unique member identifier
2. **Member Type**: Student/Faculty/Other
3. **Current Plan**: Gym plan duration
4. **Plan Price**: Membership cost
5. **Start Date**: Membership start date
6. **End Date**: Membership expiration date

**Days Remaining Card**:
- Large display of days left
- Visual prominence

**Status Alerts** (Conditional):
- **Expired Alert** (red): Shown if membership ended
- **Expiring Soon Alert** (yellow): Shown if less than 7 days remaining
- **Active Alert** (green): Shown if membership is active

**Need Help? Section**:
- Instructions for membership renewal
- Contact information placeholder

**Design**: Card-based grid layout, color-coded status badges, responsive

---

##### 12. `Project/templates/index.html` - Landing Page
**Changes Made**: Updated call-to-action buttons

**Old Buttons**:
```html
<button class="cta-btn primary">=====></button>
<a href="{{ url_for('main.admin') }}" class="cta-btn admin">Admin Portal</a>
```

**New Buttons**:
```html
<a href="{{ url_for('userAuth.user_register') }}" class="cta-btn primary">Get Started</a>
<a href="{{ url_for('userAuth.user_login') }}" class="cta-btn secondary">Member Login</a>
<a href="{{ url_for('main.admin') }}" class="cta-btn admin">Admin Portal</a>
```

**Purpose**: Provides clear entry points for new users, existing members, and administrators.

---

##### 13. `Project/templates/base.html` - Base Template
**Changes Made**: Added user_navbar.css to CSS imports

**New Line**:
```html
<link rel="stylesheet" href="{{ url_for('static', filename='css/layout/user_navbar.css') }}">
```

**Purpose**: Ensures user navbar styling is available across all templates.

---

#### CSS Files

##### 14. `Project/static/css/layout/user_navbar.css` - User Navigation Bar Styles
**Status**: NEW FILE

**Key Styles**:

**Navbar Container**:
```css
.user-navbar {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    background: var(--bg-secondary);
    border-bottom: 1px solid var(--card-border);
    padding: 0.8rem 2rem;
    z-index: 1000;
    backdrop-filter: blur(10px);
}
```

**Navigation Links**:
```css
.user-navbar-links a {
    padding: 0.6rem 1.2rem;
    border-radius: 8px;
    transition: all 0.3s ease;
}

.user-navbar-links a.active {
    background: var(--card-bg);
    color: var(--accent-primary);
    border: 1px solid var(--card-border);
}
```

**Design Features**:
- Fixed position at top of viewport
- Flexbox layout for responsive alignment
- Hover effects on navigation links
- Active state highlighting
- Uses CSS variables from admin theme (--bg-secondary, --accent-primary, --card-border)
- Backdrop blur effect for modern appearance

---

#### Configuration Files

##### 15. `.gitignore` - Git Ignore Configuration
**Status**: CREATED

**Excluded Patterns**:
```
# Flask
instance/
*.db
*.sqlite
*.sqlite3

# Python
__pycache__/
*.py[cod]
*$py.class

# Virtual Environment
venv/
env/

# IDE
.vscode/
.idea/

# OS
.DS_Store

# Logs
*.log

# Environment variables
.env
.flaskenv
```

**Purpose**: Prevents database files, cache files, and environment-specific files from being tracked in git. This eliminates the need to commit database changes every time the website is used.

---

### Database Schema Changes

**Extended Members Table**:
| Column | Type | Description |
|--------|------|-------------|
| `password_hash` | String(200) | Hashed password for user authentication |
| `is_self_registered` | Boolean | True if user registered themselves, False if admin-created |

**New Workouts Table**:
| Column | Type | Description |
|--------|------|-------------|
| `workout_id` | Integer | Primary key |
| `member_id` | Integer | Foreign key to members table |
| `workout_date` | DateTime | Date and time of workout |
| `exercise_type` | String(50) | Type of exercise performed |
| `duration_minutes` | Integer | Duration in minutes |
| `calories_burned` | Integer | Estimated calories burned (optional) |
| `notes` | Text | Additional workout notes (optional) |
| `created_at` | DateTime | Record creation timestamp |

---

## Troubleshooting

### Common Errors and Solutions

#### 1. "pip is not recognized as the name of a cmdlet"

**Error Message**:
```
pip : The term 'pip' is not recognized as the name of a cmdlet, function, script file, or operable program.
```

**Solution**: Use Python's `-m` flag to run pip as a module:
```bash
py -m pip install -r requirements.txt
```

**Alternative**: Add Python Scripts to PATH, or use `python -m pip` instead.

---

#### 2. "ModuleNotFoundError: No module named 'flask_migrate'"

**Error Message**:
```
ModuleNotFoundError: No module named 'flask_migrate'
```

**Solution**: Install Flask-Migrate manually:
```bash
py -m pip install Flask-Migrate
```

Or add to requirements.txt and reinstall:
```bash
echo Flask-Migrate==4.0.5 >> requirements.txt
py -m pip install -r requirements.txt
```

---

#### 3. "OperationalError: no such column: members.password_hash"

**Error Message**:
```
sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) no such column: members.password_hash
```

**Cause**: Database schema doesn't match updated models (old database doesn't have new columns).

**Solution**: Delete the database and let Flask recreate it with the new schema:

```bash
# Stop the Flask server (Ctrl+C)

# Delete the database file
rm instance/bookings.db         # Linux/Mac
del instance\bookings.db        # Windows CMD
Remove-Item instance\bookings.db # Windows PowerShell

# Restart the Flask server
py run.py
```

**Note**: This will delete all existing data. In production, use Flask-Migrate for database migrations.

---

#### 4. "Address already in use" or "Port 5000 is already in use"

**Error Message**:
```
OSError: [Errno 48] Address already in use
```

**Cause**: Another process is using port 5000, or Flask server is already running.

**Solution A - Use a different port**:
```bash
flask run --port 5001
```

**Solution B - Kill the process using port 5000**:

**On Windows**:
```bash
netstat -ano | findstr :5000
taskkill /PID <PID_NUMBER> /F
```

**On Linux/Mac**:
```bash
lsof -ti:5000 | xargs kill -9
```

---

#### 5. "Failed to push some refs" (Git Error)

**Error Message**:
```
error: failed to push some refs to 'https://github.com/...'
hint: Updates were rejected because the remote contains work that you do not have locally.
```

**Solution**: Fetch and rebase before pushing:
```bash
git fetch origin
git pull --rebase origin <branch-name>
git push -u origin <branch-name>
```

---

#### 6. "TemplateNotFound: user_base.html"

**Error Message**:
```
jinja2.exceptions.TemplateNotFound: user_base.html
```

**Cause**: Template file is missing or in wrong directory.

**Solution**: Verify file structure:
```bash
ls Project/templates/user_*.html
```

Expected files:
- `Project/templates/user_base.html`
- `Project/templates/user_login.html`
- `Project/templates/user_register.html`
- `Project/templates/user_dashboard.html`
- `Project/templates/user_profile.html`
- `Project/templates/user_membership.html`

If files are missing, restore from git or recreate them.

---

#### 7. Database locked error

**Error Message**:
```
sqlite3.OperationalError: database is locked
```

**Cause**: Another process is accessing the database, or SQLite is in use.

**Solution**:
```bash
# Stop Flask server
# Wait 5 seconds
# Restart Flask server
py run.py
```

**Alternative**: Check if multiple Flask instances are running:
```bash
# Windows
tasklist | findstr python

# Linux/Mac
ps aux | grep python
```

Kill extra Python processes if found.

---

#### 8. CSS not loading / Styles not applying

**Symptoms**: Website loads but looks unstyled or broken.

**Solution A - Clear browser cache**:
- Press `Ctrl + Shift + R` (Windows/Linux) or `Cmd + Shift + R` (Mac)
- Or use hard refresh in browser

**Solution B - Check static files path**:
```bash
ls Project/static/css/layout/user_navbar.css
```

**Solution C - Verify Flask static folder configuration**:
```python
# In Project/__init__.py, verify:
app = Flask(__name__, static_folder='static', template_folder='templates')
```

---

#### 9. Session not persisting / Auto-logout

**Symptoms**: User gets logged out immediately after login.

**Cause**: Missing or invalid `SECRET_KEY` in Flask app.

**Solution**: Check `Project/__init__.py` has SECRET_KEY configured:
```python
app.config['SECRET_KEY'] = 'your-secret-key-here'
```

If missing, add it before registering blueprints.

---

#### 10. "ImportError: cannot import name 'userAuth'"

**Error Message**:
```
ImportError: cannot import name 'userAuth' from 'Project'
```

**Cause**: Blueprint not properly defined or file missing.

**Solution**: Verify blueprint definition in `Project/userAuth.py`:
```python
from flask import Blueprint

userAuth = Blueprint('userAuth', __name__)
```

And verify import in `Project/__init__.py`:
```python
from .userAuth import userAuth
app.register_blueprint(userAuth)
```

---

### Debug Mode

To enable debug mode for better error messages during development:

**Method 1 - Flask CLI**:
```bash
export FLASK_ENV=development  # Linux/Mac
set FLASK_ENV=development     # Windows CMD
$env:FLASK_ENV="development"  # Windows PowerShell

flask run
```

**Method 2 - In run.py**:
```python
if __name__ == "__main__":
    app.run(debug=True)
```

**Warning**: Never enable debug mode in production environments.

---

### Getting Help

If you encounter issues not covered here:

1. **Check Flask Logs**: Read the terminal output for detailed error messages
2. **Verify File Structure**: Ensure all files are in correct directories
3. **Check Dependencies**: Run `py -m pip list` to verify installed packages
4. **Review Git Status**: Run `git status` to check for uncommitted changes
5. **Database Issues**: When in doubt, delete `instance/bookings.db` and restart

---

## Project Structure

```
GTS-System-/
├── Project/
│   ├── __init__.py              # App factory and configuration
│   ├── models.py                # Database models (Member, Workout, etc.)
│   ├── routes.py                # Admin routes
│   ├── adminAuth.py             # Admin authentication
│   ├── userAuth.py              # User authentication (NEW)
│   ├── userRoutes.py            # User dashboard routes (NEW)
│   ├── addMember.py             # Member management
│   ├── statistics.py            # Statistics and analytics
│   ├── templates/
│   │   ├── base.html            # Base template
│   │   ├── index.html           # Landing page (UPDATED)
│   │   ├── user_base.html       # User base template (NEW)
│   │   ├── user_login.html      # User login page (NEW)
│   │   ├── user_register.html   # User registration page (NEW)
│   │   ├── activate_account.html # Account activation (NEW)
│   │   ├── user_dashboard.html  # User dashboard (NEW)
│   │   ├── user_profile.html    # User profile (NEW)
│   │   ├── user_membership.html # Membership details (NEW)
│   │   └── [admin templates...]
│   └── static/
│       ├── css/
│       │   ├── layout/
│       │   │   ├── user_navbar.css  # User navbar styles (NEW)
│       │   │   └── [other css files...]
│       │   └── [other css directories...]
│       ├── images/
│       └── js/
├── instance/
│   └── bookings.db              # SQLite database (gitignored)
├── run.py                       # Application entry point
├── requirements.txt             # Python dependencies
├── .gitignore                   # Git ignore rules (NEW)
└── README.md                    # This file (NEW)
```

---

## Future Features (Phase 2+)

Planned features for future development:

- **Workout Tracking**: Log exercises, sets, reps, and duration
- **Fitness Goals**: Set and track personal fitness goals
- **Progress Analytics**: Charts and graphs for workout progress
- **Workout Programs**: Predefined workout routines
- **Social Features**: Share achievements and compete with friends
- **Payment Integration**: Online membership payment processing
- **Email Notifications**: Membership expiration reminders
- **Password Reset**: Forgot password functionality
- **Mobile App**: Native mobile application

---

## License

This project is developed for Northwest Samar State University.

---

## Contributors

Developed by the NwSSU Gym Tracker Development Team.

For questions or support, contact the development team.
