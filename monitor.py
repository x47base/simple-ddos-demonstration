import time
import threading
import requests
import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

class MonitoringApp(ctk.CTk):
    """Class for Server Monitoring with real-time latency plotting"""
    def __init__(self, target_url, interval=1):
        super().__init__()

        self.target_url = target_url
        self.interval = interval
        self.running = False
        self.latency_data = []
        self.time_data = []
        self.max_data_points = 100  # Maximum number of data points to display in the plot

        # Set the appearance of the app
        self.title("Server Monitoring App")
        self.geometry("600x600")

        # Widgets
        self.label_status = ctk.CTkLabel(self, text="Status: Not Started", font=("Arial", 16))
        self.label_status.pack(pady=20)

        self.label_response_time = ctk.CTkLabel(self, text="Response Time: N/A", font=("Arial", 16))
        self.label_response_time.pack(pady=20)

        self.start_button = ctk.CTkButton(self, text="Start Monitoring", command=self.start_monitoring)
        self.start_button.pack(pady=10)

        self.stop_button = ctk.CTkButton(self, text="Stop Monitoring", command=self.stop_monitoring, state="disabled")
        self.stop_button.pack(pady=10)

        # Create the matplotlib figure for real-time plotting
        self.fig, self.ax = plt.subplots()
        self.line, = self.ax.plot([], [], 'b-', label="Latency (s)")
        self.ax.set_xlim(0, self.max_data_points)
        self.ax.set_ylim(0, 1)
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Latency (seconds)")
        self.ax.legend()

        # Add the plot to the Tkinter interface
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(pady=20)

    def check_server(self):
        """Send a request to the server and update the status and response time."""
        try:
            start_time = time.time()
            response = requests.get(self.target_url, timeout=0.1)
            response_time = time.time() - start_time
            if response.status_code == 200:
                self.label_status.configure(text="Status: Server is UP", text_color="green")
                self.label_response_time.configure(text=f"Response Time: {response_time:.4f} seconds")
                self.update_latency_plot(response_time)
            else:
                self.label_status.configure(text=f"Status: Error {response.status_code}", text_color="orange")
        except requests.exceptions.RequestException as e:
            self.label_status.configure(text="Status: Server is DOWN", text_color="red")
            self.label_response_time.configure(text="Response Time: N/A")
            self.update_latency_plot(0)

    def update_latency_plot(self, response_time):
        """Update the latency plot with the new response time."""
        current_time = time.time()

        self.latency_data.append(response_time)
        self.time_data.append(current_time)

        if len(self.latency_data) > self.max_data_points:
            self.latency_data = self.latency_data[-self.max_data_points:]
            self.time_data = self.time_data[-self.max_data_points:]

        self.line.set_xdata(np.arange(len(self.latency_data)))
        self.line.set_ydata(self.latency_data)

        self.ax.set_xlim(0, len(self.latency_data))
        self.ax.set_ylim(0, max(self.latency_data) + 0.1)

        self.canvas.draw()

    def monitor(self):
        """Monitor the server continuously at regular intervals."""
        while self.running:
            self.check_server()
            time.sleep(self.interval)

    def start_monitoring(self):
        """Start the monitoring thread."""
        self.running = True
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        threading.Thread(target=self.monitor, daemon=True).start()

    def stop_monitoring(self):
        """Stop the monitoring thread."""
        self.running = False
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")


if __name__ == "__main__":
    TARGET_URL = "http://localhost:5000/"
    INTERVAL = 1  # Check every 1 second

    app = MonitoringApp(TARGET_URL, INTERVAL)
    app.mainloop()
