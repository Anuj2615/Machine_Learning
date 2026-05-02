# Confidence Institue Website (Flask + SQLite)

Dynamic website for **Confidence Institue** (English speaking coaching institute) with:
- Home page with heading, institute image ad, About Us, Contact Us
- Alumni section
- Alumni admin panel to upload alumni name, passing year, and photo
- Admission form with OTP verification flow
- SQLite database integration

## 1) Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 2) Run the app

```bash
python app.py
```

Open: `http://127.0.0.1:5000`

## 3) Database connectivity (step-by-step)

1. **Install Flask-SQLAlchemy** from `requirements.txt`.
2. In `app.py`, configure DB URI:
   ```python
   app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///confidence_institute.db'
   ```
3. Initialize SQLAlchemy:
   ```python
   db = SQLAlchemy(app)
   ```
4. Create models/tables:
   - `Alumni` table: stores name, passing year, photo filename.
   - `AdmissionLead` table: stores admission data and OTP verification status.
5. Call `db.create_all()` inside app context before starting the server.
6. On form submit:
   - Admin panel saves alumni data to DB + photo to `static/uploads/alumni`.
   - Admission form generates OTP, verifies OTP, then inserts verified lead into DB.

## 4) Panels and routes

- `/` → Home + About + Contact + Alumni list
- `/admission` → Admission form (name/email/mobile)
- `/verify-otp` → OTP verification page
- `/admin/alumni` → Admin panel for alumni upload

## 5) Important note on OTP

Current OTP is demo-mode and displayed via flash message for testing.
For production, integrate SMS/email providers like Twilio, MSG91, or SendGrid.
