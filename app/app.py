from flask import Flask, Response
import time
import threading
import math
import random
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, Gauge


app = Flask(__name__)

TRAFFIC_LEVEL = Gauge("combined_traffic", "Simulated periodic and burst traffic")

PERIODIC_TRAFFIC = Gauge("periodic_traffic", "Simulated periodic traffic")
BURST_TRAFFIC = Gauge("burst_traffic", "Simulated burst traffic")

# Simulate periodic requests using a sinusoidal function
max_requests = 1000
cycle_duration = 3600  # 1 hour cycle (requests increase and decrease in 1 hour)

periodic_request_count = 0
burst_request_count = 0
burst_end_time = 0 

traffic_lock = threading.Lock()

def simulate_periodic_traffic():
    global periodic_request_count, burst_request_count, burst_end_time

    while True:
        current_time = time.time()

        # Use sine wave to simulate periodic traffic: (sin wave between -1 and 1)
        time_in_seconds = time.time() % cycle_duration  # Loop every 1 hour
        traffic_level = (math.sin(2 * math.pi * time_in_seconds / cycle_duration) + 1) / 2  # Normalize to 0-1
        periodic_request_count = int(traffic_level * max_requests)  # Scale to 0-1000 requests
        
        with traffic_lock:
            # Reset burst after time time expires
            if burst_end_time > 0 and current_time > burst_end_time:
                burst_request_count = 0
                burst_end_time = 0
                BURST_TRAFFIC.set(0)
            # Update
            PERIODIC_TRAFFIC.set(periodic_request_count)
            TRAFFIC_LEVEL.set(periodic_request_count + burst_request_count)
        print(f"Request Count: {periodic_request_count}")
        time.sleep(3)  # Simulate periodic traffic every 3 seconds

# Start the periodic traffic simulation in a separate thread
thread = threading.Thread(target=simulate_periodic_traffic)
thread.daemon = True
thread.start()


@app.route('/simulate_burst', methods=['GET'])
def simulate_burst():
    """Simulate bursty traffic for a short time."""
    burst_count = random.randint(50, 150)  # Simulate a burst with random requests
    burst_duration = random.randint(10,20) # Simulate random burst duration
    global burst_request_count, burst_end_time

    with traffic_lock:
        burst_request_count = burst_count
        burst_end_time = time.time() + burst_duration

        BURST_TRAFFIC.set(burst_request_count)
        TRAFFIC_LEVEL.set(periodic_request_count + burst_request_count)

    print(f"Simulated Burst: {burst_count}, New Traffic Level: {periodic_request_count + burst_request_count}")
    return f"Simulated a burst of {burst_count} requests."

@app.route('/metrics', methods=['GET'])
def metrics():
    """Expose metrics for Prometheus."""
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

# @app.route('/metrics', methods=['GET'])
# def metrics():
#     """Expose request counter for monitoring"""
#     global request_counter
#     return f"requests_total {request_counter}"

# @app.route('/status', methods=['GET'])
# def status():
#     """Expose current status for testing locally."""
#     global request_counter
#     return f"Current request count (generated traffic): {request_counter}"
@app.route('/status', methods=['GET'])
def status():
    """Expose current status for testing locally."""
    return {
        "periodic_traffic": periodic_request_count,
        "burst_traffic": burst_request_count,
        "combined_traffic": periodic_request_count + burst_request_count
    }

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
