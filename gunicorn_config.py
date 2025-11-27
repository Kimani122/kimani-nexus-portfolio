# gunicorn_config.py

# --- Core Configuration ---

# CRITICAL for Render/Cloud deployment: Bind to all interfaces (0.0.0.0) 
# to allow the platform's reverse proxy to connect.
bind = '0.0.0.0:8000'

# Number of worker processes (Render provides CPU core information)
# We set a good default value, which is usually sufficient.
workers = 4 

# Timeout for workers (in seconds)
timeout = 30

# Process naming (Optional)
proc_name = 'kimani_nexus_gunicorn'

# --- Logging ---
# CRITICAL for Render: Set access and error logs to standard output ('-') 
# Render captures these logs and displays them in the service dashboard.
errorlog = '-'
accesslog = '-'
loglevel = 'info' 

# Set the process name
proc_name = 'kimani_nexus_gunicorn'