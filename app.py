# app.py

from flask import Flask, render_template, redirect, url_for, flash, request, send_file, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer
from functools import wraps
from datetime import datetime
from dotenv import load_dotenv
import os
import smtplib
from email.mime.text import MIMEText
import io
from docx import Document
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# --------------------
# Load environment variables
# --------------------
load_dotenv()

# --------------------
# App Config
# --------------------
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# --------------------
# Database
# --------------------
from models import db, User, Course, Enrollment, Blog, CV
db.init_app(app)

# --------------------
# Flask-Login
# --------------------
login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not getattr(current_user, "is_admin", False):
            flash("🚫 You do not have permission to access this page.", "danger")
            return redirect(url_for("home"))
        return f(*args, **kwargs)
    return decorated_function

# --------------------
# Email Verification
# --------------------
s = URLSafeTimedSerializer(app.config['SECRET_KEY'])

def send_verification_email(user_email, token):
    sender_email = os.getenv('MAIL_USERNAME')
    sender_password = os.getenv('MAIL_PASSWORD')
    base_url = os.getenv('BASE_URL', 'http://127.0.0.1:5000')  # Use BASE_URL or fallback

    verify_link = f"{base_url}/verify/{token}"

    msg = MIMEText(f"Click the link to verify your account: {verify_link}")
    msg["Subject"] = "Verify your EdTech account"
    msg["From"] = sender_email
    msg["To"] = user_email

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, user_email, msg.as_string())
        print(f"✅ Verification email sent to {user_email}")
    except Exception as e:
        print("❌ Email error:", e)

# --------------------
# Routes
# --------------------
@app.route('/')
def home():
    testimonials = [
        {"name": "Aarav", "role": "Student", "feedback": "This platform gave me practical skills at an affordable price!", "avatar": url_for('static', filename='images/user1.jpg')},
        {"name": "Neha", "role": "Data Analyst", "feedback": "Feels like PW Skills but even more tailored to my needs!", "avatar": url_for('static', filename='images/user2.jpg')},
        {"name": "Rohit", "role": "Developer", "feedback": "Instructors are highly experienced, loved the content.", "avatar": url_for('static', filename='images/user3.jpg')}
    ]
    courses = Course.query.limit(4).all()
    return render_template("home.html", courses=courses, testimonials=testimonials, current_year=datetime.now().year)

@app.route("/course/<int:course_id>")
def course_detail(course_id):
    course = Course.query.get_or_404(course_id)
    return render_template("course_detail.html", course=course)

@app.route("/enroll/<int:course_id>")
@login_required
def enroll(course_id):
    course = Course.query.get_or_404(course_id)
    existing_enrollment = Enrollment.query.filter_by(user_id=current_user.id, course_id=course.id).first()
    if existing_enrollment:
        flash("You are already enrolled in this course ✅", "info")
    else:
        enrollment = Enrollment(user_id=current_user.id, course_id=course.id)
        db.session.add(enrollment)
        db.session.commit()
        flash(f"Successfully enrolled in {course.title} 🎉", "success")
    return redirect(url_for("course_detail", course_id=course.id))

@app.route("/my-courses")
@login_required
def my_courses():
    enrollments = Enrollment.query.filter_by(user_id=current_user.id).all()
    courses = [enrollment.course for enrollment in enrollments]
    return render_template("my_courses.html", courses=courses)

# --------------------
# Auth
# --------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already exists!", "danger")
            return redirect(url_for("register"))

        hashed_pw = generate_password_hash(password, method="pbkdf2:sha256", salt_length=8)
        new_user = User(username=username, email=email, password=hashed_pw, is_verified=False)
        db.session.add(new_user)
        db.session.commit()

        token = s.dumps(email, salt="email-confirm")
        send_verification_email(email, token)
        flash("Account created! Please check your email to verify.", "info")
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/verify/<token>")
def verify_email(token):
    try:
        email = s.loads(token, salt="email-confirm", max_age=3600)
        user = User.query.filter_by(email=email).first()
        if user:
            user.is_verified = True
            db.session.commit()
            flash("✅ Email verified! You can now log in.", "success")
            return redirect(url_for("login"))
    except Exception:
        flash("❌ The verification link is invalid or expired.", "danger")
    return redirect(url_for("home"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            if not user.is_verified:
                flash("⚠️ Please verify your email before logging in.", "warning")
                return redirect(url_for("login"))
            login_user(user)
            flash(f"Welcome back, {user.username}!", "success")
            return redirect(url_for("dashboard"))
        flash("Invalid email or password.", "danger")
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("home"))

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", user=current_user)

# --------------------
# Admin Panel
# --------------------
@app.route("/admin", methods=["GET", "POST"])
@login_required
@admin_required
def admin_panel():
    users = User.query.all()
    return render_template("admin.html", users=users)

@app.route("/admin/update_role/<int:user_id>", methods=["POST"])
@login_required
@admin_required
def update_role(user_id):
    user = User.query.get(user_id)
    new_role = request.form.get("role")
    if user and new_role in ["student", "instructor", "admin"]:
        user.role = new_role
        db.session.commit()
        flash(f"Role updated for {user.username} to {new_role}", "success")
    return redirect(url_for("admin_panel"))

# --------------------
# Courses
# --------------------
@app.route("/courses")
def courses():
    search = request.args.get("search", "")
    category = request.args.get("category", "")
    sort = request.args.get("sort", "")

    query = Course.query
    if search:
        query = query.filter(Course.title.ilike(f"%{search}%"))
    if category:
        query = query.filter_by(category=category)
    if sort == "price":
        query = query.order_by(Course.price.asc())
    elif sort == "rating":
        query = query.order_by(Course.rating.desc())

    courses = query.all()
    return render_template("courses.html", courses=courses)

@app.route("/update-progress/<int:enrollment_id>/<int:progress>")
@login_required
def update_progress(enrollment_id, progress):
    enrollment = Enrollment.query.get_or_404(enrollment_id)
    if enrollment.user_id != current_user.id:
        abort(403)
    enrollment.progress = min(progress, 100)
    db.session.commit()
    flash("Progress updated!", "success")
    return redirect(url_for("my_courses"))

# --------------------
# CV Builder
# --------------------
@app.route("/cv-builder", methods=["GET", "POST"])
@login_required
def cv_builder():
    if request.method == "POST":
        cv = CV(
            user_id=current_user.id,
            full_name=request.form["full_name"],
            email=request.form["email"],
            phone=request.form["phone"],
            summary=request.form["summary"],
            skills=request.form["skills"],
            experience=request.form["experience"],
            education=request.form["education"],
            projects=request.form["projects"],
        )
        db.session.add(cv)
        db.session.commit()
        flash("✅ CV Saved! You can now export it.", "success")
        return redirect(url_for("my_cv", cv_id=cv.id))
    return render_template("cv_builder.html")

@app.route("/cv/<int:cv_id>")
@login_required
def my_cv(cv_id):
    cv = CV.query.get_or_404(cv_id)
    return render_template("cv_preview.html", cv=cv)

@app.route("/cv/<int:cv_id>/download/<format>")
@login_required
def download_cv(cv_id, format):
    cv = CV.query.get_or_404(cv_id)
    # PDF/DOCX/TXT generation code (same as your original, unchanged)
    # ...

# --------------------
# Error Handlers
# --------------------
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html"), 500

@app.errorhandler(403)
def forbidden(e):
    return render_template("403.html"), 403

# --------------------
# Run App (serverless friendly)
# --------------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run()
