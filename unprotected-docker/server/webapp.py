import time
from flask import Flask, jsonify, request, abort
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.exceptions import HTTPException

app = Flask(__name__)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["100000 per day", "20000 per hour"]
)

request_log = {}
blacklist = {}
BLACKLIST_THRESHOLD = 5  # Number of DDoS detections before blacklisting
BLACKLIST_DURATION = 3600  # Blacklist duration in seconds (1 hour)
MAX_REQUESTS_PER_MINUTE = 100
REQUEST_TIME_WINDOW = 60  # In seconds (1 minute)

def is_ddos_attack(ip_address):
    """Check if the IP address is exceeding the allowed request rate."""
    current_time = time.time()
    if ip_address not in request_log:
        request_log[ip_address] = {'timestamps': [current_time], 'ddos_count': 0}
        return False
    else:
        recent_requests = [req_time for req_time in request_log[ip_address]['timestamps'] if current_time - req_time < REQUEST_TIME_WINDOW]
        request_log[ip_address]['timestamps'] = recent_requests
        request_log[ip_address]['timestamps'].append(current_time)
        if len(request_log[ip_address]['timestamps']) > MAX_REQUESTS_PER_MINUTE:
            request_log[ip_address]['ddos_count'] += 1
            return True
        return False

def is_blacklisted(ip_address):
    """Check if the IP is blacklisted, and remove it if the blacklist duration has expired."""
    current_time = time.time()
    if ip_address in blacklist:
        if current_time - blacklist[ip_address] > BLACKLIST_DURATION:
            del blacklist[ip_address]
            print(f"IP {ip_address} removed from blacklist after {BLACKLIST_DURATION} seconds.")
            return False
        return True
    return False

def drop_request():
    """Drop the connection by shutting down the server-side connection without sending a response."""
    shutdown_func = request.environ.get('werkzeug.server.shutdown')
    if shutdown_func:
        shutdown_func()  # This simulates dropping the request by shutting down the connection
    return "", 500  # Return a dummy empty response to prevent further handling

@app.before_request
def check_ddos():
    """Check every request for signs of DDoS attack and block IP if blacklisted."""
    ip_address = get_remote_address()

    # Check if the IP is blacklisted
    if is_blacklisted(ip_address):
        print(f"Blacklisted IP tried to access: {ip_address}")
        return drop_request()

    # Check for DDoS attack
    if is_ddos_attack(ip_address):
        print(f"Potential DDoS attack detected from IP: {ip_address}")

        # If the IP exceeds the blacklist threshold, blacklist it
        if request_log[ip_address]['ddos_count'] >= BLACKLIST_THRESHOLD:
            blacklist[ip_address] = time.time()  # Add to blacklist
            print(f"IP {ip_address} added to blacklist for {BLACKLIST_DURATION} seconds.")
            return drop_request()  # Simulate dropped request without response

        # Drop the connection for now but don't blacklist yet
        return drop_request()

@app.route('/')
def index():
    """Homepage route."""
    return "Welcome to the Flask app!"

@app.route('/blacklist')
def get_blacklist():
    """Return the list of blacklisted IPs."""
    return jsonify(list(blacklist.keys()))

@app.errorhandler(HTTPException)
def handle_exception(e):
    """Handle all HTTP exceptions by returning nothing."""
    # Here we return nothing but shut down the request
    return drop_request()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
