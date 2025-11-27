# app.py

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mail import Mail, Message
from dotenv import load_dotenv
import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
from config import Config # Import the configuration class

# Load environment variables from .env file (for local development ONLY)
load_dotenv()

# Initialize Flask app and load configuration
app = Flask(__name__)
# Load configuration from config.py class, which reads all settings from os.environ
app.config.from_object(Config)

# Initialize Flask-Mail
mail = Mail(app)

# --- Firebase Initialization (Server-Side for Firestore) ---
# This block handles secure authentication based on the deployment environment.
try:
    # 1. CHECK FOR RENDER/PAAS ENVIRONMENT VARIABLE (PREFERRED METHOD)
    # This reads the entire JSON key that you pasted into the Render dashboard.
    firebase_credentials_json = os.environ.get('FIREBASE_CREDENTIALS_JSON')

    if firebase_credentials_json:
        # Load credentials from the JSON string provided in the environment variable
        cred_dict = json.loads(firebase_credentials_json)
        cred = credentials.Certificate(cred_dict)
        print("Firebase Admin SDK initialized successfully using JSON environment variable (Production).")
    else:
        # 2. FALLBACK TO LOCAL FILE PATH (FOR DEVELOPMENT)
        service_account_path = os.path.join(os.path.dirname(__file__), app.config['FIREBASE_SERVICE_ACCOUNT_PATH'])
        cred = credentials.Certificate(service_account_path)
        print(f"Firebase Admin SDK initialized successfully using file path: {service_account_path} (Development).")
        
    firebase_app = firebase_admin.initialize_app(cred)
    db = firestore.client()

except Exception as e:
    print(f"CRITICAL ERROR: Failed to initialize Firebase Admin SDK. Check FIREBASE_CREDENTIALS_JSON or service account file path: {e}")
    # Define a dummy client to prevent the app from crashing entirely during initialization
    class DummyFirestoreClient:
        def collection(self, path): return self
        def add(self, data): 
            print(f"ERROR: Firestore not initialized. Cannot add data: {data}")
            raise RuntimeError("Database connection failed.")
        def document(self, path): return self
        def set(self, data): print(f"ERROR: Firestore not initialized. Cannot set data: {data}")
    db = DummyFirestoreClient()


# --- Helper Function for Email Notification ---
def send_notification_email(data):
    try:
        msg = Message(
            subject='NEW CV Request for Kimani Nexus Portfolio',
            sender=app.config['MAIL_USERNAME'],
            recipients=[app.config['MAIL_RECIPIENT']]
        )
        msg.body = f"""
        A new CV request has been submitted on your portfolio.

        Requester Details:
        - Name: {data.get('full_names')}
        - Position: {data.get('position')}
        - Company/Institution: {data.get('company_name')}
        - Company Email: {data.get('company_email')}

        Full Details:
        {json.dumps(data, indent=2)}
        """
        mail.send(msg)
        print("Email notification sent successfully.")
    except Exception as e:
        print(f"WARNING: Failed to send email notification: {e}")

# --- Routes ---

@app.route('/')
def index():
    """Renders the main portfolio page."""
    return render_template('index.html')

@app.route('/about')
def about():
    """Renders the 'About Me' page."""
    return render_template('about.html')

@app.route('/request_cv', methods=['GET', 'POST'])
def request_cv():
    """Handles the CV request form submission and processing."""
    if request.method == 'POST':
        # Collect form data
        form_data = {
            'full_names': request.form['full_names'],
            'phone_number': request.form['phone_number'],
            'contact': request.form.get('contact', ''),
            'company_name': request.form['company_name'],
            'position': request.form['position'],
            'company_email': request.form['company_email'],
            'address': request.form.get('address', ''),
            'company_contact': request.form.get('company_contact', ''),
            'timestamp': firestore.SERVER_TIMESTAMP
        }

        try:
            # 1. Save data to Firestore
            current_app_id = app.config['APP_ID']
            collection_path = f"artifacts/{current_app_id}/public/data/cv_requests"
            db.collection(collection_path).add(form_data)

            # 2. Send email notification 
            send_notification_email(form_data)
            
            flash('Your CV request has been received! Please wait for the CV to be sent to your email.', 'success')

        except Exception as e:
            flash(f'There was an error processing your request. Please check your inputs and try again.', 'error')
            print(f"Error processing CV request: {e}")

        # Redirect to the request CV page to show the flash message
        return redirect(url_for('request_cv'))
    
    return render_template('request_cv.html')

@app.route('/success')
def success():
    """Renders a success page after a CV request has been submitted."""
    return render_template('success.html')

@app.errorhandler(404)
def page_not_found(e):
    """Custom error handler for 404 Not Found errors."""
    return render_template('404.html'), 404

# NOTE: The if __name__ == '__main__': block is removed for Gunicorn deployment,
# as Gunicorn executes `app:app` directly.