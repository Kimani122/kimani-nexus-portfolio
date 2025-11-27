# app.py
import os
from flask import Flask, render_template, request, redirect, url_for, jsonify

# Initialize Flask app
app = Flask(__name__)
# Set a secret key for session management and other security features.
# In a production environment, this should be a strong, randomly generated value
# fetched from an environment variable.
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'your_super_secret_key_here')


# Define routes
@app.route('/')
def index():
    """
    Renders the home page of the portfolio.
    Displays an overview of skills, projects, and social links.
    """
    return render_template('index.html')

@app.route('/about')
def about():
    """
    Renders the 'About Me' page.
    Contains information about the user's background and education.
    """
    return render_template('about.html')

@app.route('/request_cv')
def request_cv():
    """
    Renders the CV request form page.
    This page contains a form for visitors to fill out to request a CV.
    The form submission will be handled client-side via JavaScript and Firestore.
    """
    return render_template('request_cv.html')

@app.route('/success')
def success():
    """
    Renders a success page after a CV request has been submitted.
    """
    return render_template('success.html')

@app.errorhandler(404)
def page_not_found(e):
    """
    Custom error handler for 404 Not Found errors.
    Renders a generic 404 page.
    """
    return render_template('404.html'), 404

# Main entry point for running the Flask app
if __name__ == '__main__':
    # Run the Flask development server.
    # In a production environment, use a production-ready WSGI server like Gunicorn or uWSGI.
    app.run(debug=True) # debug=True enables auto-reloading and better error messages

