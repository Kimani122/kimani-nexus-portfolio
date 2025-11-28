from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mail import Mail, Message
import firebase_admin
from firebase_admin import credentials, firestore
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables from .env
load_dotenv()

# --- Configuration and Initialization ---
app = Flask(__name__)
# Uses SECRET_KEY from .env for session management and flashing messages
app.secret_key = os.environ.get('SECRET_KEY', 'default_secret_key') 

# Flask-Mail configuration (using environment variables from .env)
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT'))
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS').lower() == 'true'
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
mail = Mail(app)

# Firebase Admin SDK Initialization
db = None
APP_ID = os.environ.get('APP_ID')
MAIL_RECIPIENT = os.environ.get('MAIL_RECIPIENT')

try:
    # Path to your Firebase Admin SDK service account JSON file (from .env)
    cred_path = os.environ.get('FIREBASE_SERVICE_ACCOUNT_PATH')
    
    if not firebase_admin._apps:
        if not os.path.exists(cred_path):
            print(f"CRITICAL ERROR: Firebase Service Account Key not found at {cred_path}")
        else:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            db = firestore.client()
            print("Firebase Admin SDK initialized successfully.")
    elif 'firebase_admin' in firebase_admin._apps:
        db = firestore.client()
except Exception as e:
    print(f"Error initializing Firebase Admin SDK: {e}")

# --- Routes ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/request_cv')
def request_cv():
    return render_template('request_cv.html')

@app.route('/submit_cv', methods=['POST'])
def submit_cv():
    """
    Handles server-side submission of CV requests.
    Saves the request for manual review and sends a notification email.
    The CV is NOT sent to the requester automatically.
    """
    
    if not db:
        flash('Internal Server Error: Database is unavailable. Please check server logs.', 'error')
        return redirect(url_for('request_cv'))

    try:
        # 1. Collect Form Data and Add Review Status
        form_data = {
            'fullName': request.form.get('fullName'),
            'phoneNumber': request.form.get('phoneNumber'),
            'requesterEmail': request.form.get('requesterEmail'),
            'companyName': request.form.get('companyName'),
            'position': request.form.get('position'),
            'companyEmail': request.form.get('companyEmail'),
            'companyAddress': request.form.get('companyAddress'),
            'companyContact': request.form.get('companyContact'),
            'timestamp': datetime.utcnow(),
            'status': 'Pending Review' # CRITICAL: New field for vetting
        }

        # 2. Save Data to Firestore (Public Collection)
        collection_path = f'artifacts/{APP_ID}/public/data/cv_requests'
        db.collection(collection_path).add(form_data)
        print("CV request saved to Firestore for review.")
        
        # 3. Send Notification Email to You (Kimani Nexus)
        if MAIL_RECIPIENT:
            notification_msg = Message(
                f'ACTION REQUIRED: New CV Request from {form_data["companyName"]}',
                sender=app.config['MAIL_USERNAME'],
                recipients=[MAIL_RECIPIENT]
            )
            notification_msg.body = (
                f"A new CV request has been submitted by {form_data['fullName']} ({form_data['requesterEmail']}).\n\n"
                f"Company: {form_data['companyName']} - Position: {form_data['position']}\n"
                f"Time: {form_data['timestamp'].strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n"
                f"Please review the request in Firestore (Collection: {collection_path}) before sending the CV manually."
            )
            mail.send(notification_msg)
            flash('Your request has been successfully submitted for review. We will verify the details and send the CV to your email shortly.', 'success')
        else:
            flash('Your request has been saved, but the system notification failed. I will review it manually.', 'error')


    except Exception as e:
        print(f"Server-side submission or email error: {e}")
        flash('An internal error occurred during submission. Please try again.', 'error')

    # Redirect back to the form page to display flash messages
    return redirect(url_for('request_cv'))

if __name__ == '__main__':
    app.run(debug=True)