import tkinter as tk
import serial
import time
import threading
import random

class FakeArduino:
    def __init__(self):
        self.in_waiting = 0
        self.data_to_read = []

    def write(self, message):
        print(f"Message to Arduino: {message}")

    def readline(self):
        if self.data_to_read:
            return self.data_to_read.pop(0).encode()
        else:
            return b''

    def add_fake_data(self, data):
        self.data_to_read.append(data)
        self.in_waiting = len(self.data_to_read)

# Set up serial communication
USE_FAKE_ARDUINO = True  # Set this to False to use real Arduino

if USE_FAKE_ARDUINO:
    arduino = FakeArduino()
    print("Using FakeArduino for testing")
else:
    try:
        arduino = serial.Serial('COM8', 115200)  # Change 'COM8' to your Arduino's serial port
        time.sleep(2)  # Wait for the connection to establish
    except Exception as e:
        print(f"Error connecting to Arduino: {e}")
        arduino = None

# Function to send a specific message to Arduino
def send_message(message):
    if arduino:
        arduino.write(message.encode())

# Function to send a prefixed value to Arduino
def send_prefixed_value(prefix, value):
    if arduino and value:
        arduino.write(f"{prefix}{value}".encode())

# Function to read data from Arduino and update the labels
def read_from_arduino():
    if arduino and arduino.in_waiting > 0:
        data = arduino.readline().decode().strip()
        if data:
            values = data.split(',')
            if len(values) == 7:
                try:
                    temperature1.set(f"Temp Sensor 1: {values[0]}°C")
                    temperature2.set(f"Temp Sensor 2: {values[1]}°C")
                    temperature3.set(f"Temp Sensor 3: {values[2]}°C")
                    temperature4.set(f"Temp Sensor 4: {values[3]}°C")
                    average_temp.set(f"Average Temp: {values[4]}°C")
                    oxygen_sensor.set(f"Oxygen Sensor: {values[5]}%")
                    layers.set(f"Number of Layers: {values[6]}")
                except Exception as e:
                    print(f"Error updating values: {e}")
    root.after(100, read_from_arduino)  # Schedule the function to run again after 100 ms

# Function to add fake Arduino data
def add_fake_arduino_data():
    if isinstance(arduino, FakeArduino):
        fake_data = f"{random.uniform(20, 30):.2f},{random.uniform(20, 30):.2f},{random.uniform(20, 30):.2f},{random.uniform(20, 30):.2f},{random.uniform(20, 30):.2f},{random.uniform(0, 100):.2f},{random.randint(1, 10)}"
        arduino.add_fake_data(fake_data)
    root.after(1000, add_fake_arduino_data)  # Add new fake data every 1 second

# Create the main window
root = tk.Tk()
root.title("Character Sender")

# Create and place other buttons in a single row
button_frame = tk.Frame(root)
button_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

button_labels = ["Dosing 1", "Dosing 2", "Run", "Play/Pause", "Reset", "Lights on", "blower on/off"]
button_characters = "ABGPRLb"

for i, (label, char) in enumerate(zip(button_labels, button_characters)):
    button = tk.Button(button_frame, text=label, command=lambda c=char: send_message(c), width=15, height=2)
    button.grid(row=0, column=i, padx=5, pady=5, sticky="w")

# Create and place control buttons (remote control style)
control_frame = tk.LabelFrame(root, text="Control Buttons", padx=10, pady=10)
control_frame.grid(row=1, column=0, padx=10, pady=10, sticky="n")

control_labels = ["up", "down", "forward", "reverse", "Home"]
control_characters = "udfrH"
control_positions = {
    "up": (0, 1),
    "down": (2, 1),
    "forward": (1, 2),
    "reverse": (1, 0),
    "Home": (1, 1)
}

for label, char in zip(control_labels, control_characters):
    row, col = control_positions[label]
    button = tk.Button(control_frame, text=label, command=lambda c=char: send_message(c), width=10, height=2)
    button.grid(row=row, column=col, padx=5, pady=5)

# Entry fields and buttons for prefixed values
prefix_frame = tk.LabelFrame(root, text="Send Prefixed Values", padx=10, pady=10)
prefix_frame.grid(row=1, column=1, padx=10, pady=10, sticky="n")

prefixes = ["s", "w", "l", "m", "t", "h", "z", "x"]
entries = []

for i, prefix in enumerate(prefixes):
    label_prefix = tk.Label(prefix_frame, text=f"{prefix}:")
    label_prefix.grid(row=i, column=0, padx=5, pady=5, sticky="e")
    
    entry_value = tk.Entry(prefix_frame)
    entry_value.grid(row=i, column=1, padx=5, pady=5)
    entries.append((prefix, entry_value))

    button_send = tk.Button(prefix_frame, text=f"Send {prefix}", command=lambda p=prefix, e=entry_value: send_prefixed_value(p, e.get()), width=20, height=2)
    button_send.grid(row=i, column=2, padx=5, pady=5)

# Labels to display sensor data
sensor_frame = tk.LabelFrame(root, text="Sensor Data", padx=10, pady=10)
sensor_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="n")

temperature1 = tk.StringVar()
temperature2 = tk.StringVar()
temperature3 = tk.StringVar()
temperature4 = tk.StringVar()
average_temp = tk.StringVar()
oxygen_sensor = tk.StringVar()
layers = tk.StringVar()

tk.Label(sensor_frame, textvariable=temperature1).grid(row=0, column=0, padx=5, pady=5, sticky="w")
tk.Label(sensor_frame, textvariable=temperature2).grid(row=1, column=0, padx=5, pady=5, sticky="w")
tk.Label(sensor_frame, textvariable=temperature3).grid(row=2, column=0, padx=5, pady=5, sticky="w")
tk.Label(sensor_frame, textvariable=temperature4).grid(row=3, column=0, padx=5, pady=5, sticky="w")
tk.Label(sensor_frame, textvariable=average_temp).grid(row=4, column=0, padx=5, pady=5, sticky="w")
tk.Label(sensor_frame, textvariable=oxygen_sensor).grid(row=5, column=0, padx=5, pady=5, sticky="w")
tk.Label(sensor_frame, textvariable=layers).grid(row=16, column=0, padx=5, pady=5, sticky="w")

# Start reading from Arduino and adding fake data
root.after(100, read_from_arduino)
root.after(1000, add_fake_arduino_data)

# Run the main event loop
root.mainloop()

# Close the serial connection when the window is closed
if arduino and not isinstance(arduino, FakeArduino):
    arduino.close()