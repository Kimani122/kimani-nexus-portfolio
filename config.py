# config.py

import os

class Config:
    # --- Flask Core Configuration ---
    # Retrieve the secret key from environment variables for security
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'A_REALLY_HARD_TO_GUESS_SECRET_KEY'
    
    # Set the current app ID (used for Firestore path construction)
    APP_ID = os.environ.get('APP_ID') or 'default-kimani-nexus-app'

    # --- Firebase Configuration ---
    # Path used for local file fallback in app.py
    FIREBASE_SERVICE_ACCOUNT_PATH = os.environ.get('FIREBASE_SERVICE_ACCOUNT_PATH') or './serviceAccountKey.json'

    # --- Flask-Mail Configuration for CV Request Notification ---
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com' # Use your email provider's SMTP server
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') == 'True'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') # Your email address (the sender)
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') # Your email password or application-specific password
    
    # Recipient of the CV requests (i.e., your email)
    MAIL_RECIPIENT = os.environ.get('MAIL_RECIPIENT') # Your personal email