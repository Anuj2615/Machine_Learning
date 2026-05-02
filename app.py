from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'change-this-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///confidence_institute.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads', 'alumni')
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)


class Alumni(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    passing_year = db.Column(db.Integer, nullable=False)
    photo_filename = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class AdmissionLead(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    mobile = db.Column(db.String(20), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


@app.route('/')
def home():
    alumni = Alumni.query.order_by(Alumni.passing_year.desc()).all()
    return render_template('index.html', alumni=alumni)


@app.route('/admission', methods=['GET', 'POST'])
def admission():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        mobile = request.form.get('mobile', '').strip()

        if not name or not email or not mobile:
            flash('All fields are required.', 'danger')
            return redirect(url_for('admission'))

        otp = random.randint(100000, 999999)
        session['pending_admission'] = {'name': name, 'email': email, 'mobile': mobile}
        session['admission_otp'] = str(otp)

        flash(f'OTP generated for demo: {otp}', 'info')
        return redirect(url_for('verify_otp'))

    return render_template('admission.html')


@app.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    pending = session.get('pending_admission')
    if not pending:
        flash('No admission request found. Please submit form first.', 'warning')
        return redirect(url_for('admission'))

    if request.method == 'POST':
        entered_otp = request.form.get('otp', '').strip()
        saved_otp = session.get('admission_otp')

        if entered_otp == saved_otp:
            lead = AdmissionLead(
                name=pending['name'],
                email=pending['email'],
                mobile=pending['mobile'],
                is_verified=True
            )
            db.session.add(lead)
            db.session.commit()

            session.pop('pending_admission', None)
            session.pop('admission_otp', None)
            flash('Admission form verified and submitted successfully!', 'success')
            return redirect(url_for('home'))

        flash('Invalid OTP. Please try again.', 'danger')

    return render_template('verify_otp.html', pending=pending)


@app.route('/admin/alumni', methods=['GET', 'POST'])
def admin_alumni():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        passing_year = request.form.get('passing_year', '').strip()
        photo = request.files.get('photo')

        if not name or not passing_year or not photo:
            flash('Name, passing year, and photo are required.', 'danger')
            return redirect(url_for('admin_alumni'))

        if not passing_year.isdigit():
            flash('Passing year must be a number.', 'danger')
            return redirect(url_for('admin_alumni'))

        filename = secure_filename(photo.filename)
        timestamped_filename = f"{int(datetime.utcnow().timestamp())}_{filename}"
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], timestamped_filename)
        photo.save(save_path)

        alumni = Alumni(name=name, passing_year=int(passing_year), photo_filename=timestamped_filename)
        db.session.add(alumni)
        db.session.commit()

        flash('Alumni record added successfully.', 'success')
        return redirect(url_for('admin_alumni'))

    alumni_list = Alumni.query.order_by(Alumni.created_at.desc()).all()
    return render_template('admin_alumni.html', alumni_list=alumni_list)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
