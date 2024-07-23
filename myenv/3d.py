import tkinter as tk
from PIL import Image, ImageTk
import serial
import time
import threading
import random

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

class FakeArduino:
    def __init__(self):
        self.in_waiting = 0
        self.data_to_read = []

    def write(self, message):
        print(f"Message to Arduino: {message.decode()}")

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

# Function to generate fake data for testing
def generate_fake_data():
    if isinstance(arduino, FakeArduino):
        fake_data = f"{random.uniform(20, 30):.2f},{random.uniform(20, 30):.2f},{random.uniform(20, 30):.2f},{random.uniform(20, 30):.2f},{random.uniform(20, 30):.2f},{random.uniform(0, 100):.2f},{random.randint(1, 10)}"
        arduino.add_fake_data(fake_data)
    root.after(1000, generate_fake_data)  # Generate new fake data every 1 second

# Create the main window
root = tk.Tk()
root.title("Character Sender")
root.geometry("800x800")

# Load and set the background image using Canvas
background_image_path = r"C:/Users/amala/Downloads/3dlaser/myenv/images/bg.png"  # Change to your image path
background_image = Image.open(background_image_path)
background_photo = ImageTk.PhotoImage(background_image)

canvas = tk.Canvas(root, width=800, height=900)
canvas.grid(row=0, column=0, rowspan=3, columnspan=4, sticky='nsew')
canvas.create_image(0, 0, anchor='nw', image=background_photo)

# Function to update the background image size
def update_background_image(event):
    new_width = event.width
    new_height = event.height
    resized_image = background_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    resized_photo = ImageTk.PhotoImage(resized_image)
    canvas.create_image(0, 0, anchor='nw', image=resized_photo)
    canvas.image = resized_photo  # Keep a reference to the image

root.bind("<Configure>", update_background_image)

# Configure grid weights for responsiveness
root.grid_rowconfigure(0, weight=0)
root.grid_rowconfigure(1, weight=10)
root.grid_rowconfigure(2, weight=0)
root.grid_rowconfigure(3, weight=0)

root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_columnconfigure(2, weight=1)
root.grid_columnconfigure(3, weight=1)

# Button style configuration
button_style = {
    'bg': '#4CAF50',  # Green background
    'fg': 'white',    # White text
    'font': ('Helvetica', 12, 'bold'),
    'relief': 'raised',
    'bd': 2
}

# Create and place other buttons in a single row
button_frame = tk.Frame(root, bg='yellow')
button_frame.grid(row=0, column=0, columnspan=3, padx=0, pady=0, sticky='n')

button_labels = ["Dosing 1", "Dosing 2", "Run", "Play/Pause", "Reset", "Lights on", "blower on/off"]
button_characters = "ABGPRLb"

for i, (label, char) in enumerate(zip(button_labels, button_characters)):
    button = tk.Button(button_frame, text=label, command=lambda c=char: send_message(c), width=10, height=2, **button_style)
    button.grid(row=0, column=i, padx=4, pady=0, sticky="nw")

# Create and place control buttons (remote control style)
control_frame = tk.LabelFrame(root, text="Control Buttons", padx=2, pady=5, bg='red',width=15)
control_frame.grid(row=1, column=0, padx=2, pady=2, sticky='nw')

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
    button = tk.Button(control_frame, text=label, command=lambda c=char: send_message(c), width=6, height=2, **button_style)
    button.grid(row=row, column=col, padx=2, pady=2)

# Entry fields and buttons for prefixed values
prefix_frame = tk.LabelFrame(root, text="Send Prefixed Values", padx=10, pady=10, bg='white')
prefix_frame.grid(row=0, column=3, rowspan=2, padx=10, pady=10, sticky='nsew')

prefixes = ["s", "w", "l", "m", "t", "h", "z", "x"]
entries = []

for i, prefix in enumerate(prefixes):
    label_prefix = tk.Label(prefix_frame, text=f"{prefix}:", bg='white')
    label_prefix.grid(row=i, column=0, padx=5, pady=5, sticky="w")
    
    entry_value = tk.Entry(prefix_frame)
    entry_value.grid(row=i, column=1, padx=5, pady=5)
    entries.append((prefix, entry_value))

    button_send = tk.Button(prefix_frame, text=f"Send {prefix}", command=lambda p=prefix, e=entry_value: send_prefixed_value(p, e.get()), width=20, height=2, **button_style)
    button_send.grid(row=i, column=2, padx=5, pady=5)

# Labels to display sensor data
sensor_frame = tk.LabelFrame(root, text="Sensor Data", padx=0, pady=0, bg='white')
sensor_frame.grid(row=2, column=3, padx=0, pady=0, sticky='nwe')

temperature1 = tk.StringVar()
temperature2 = tk.StringVar()
temperature3 = tk.StringVar()
temperature4 = tk.StringVar()
average_temp = tk.StringVar()
oxygen_sensor = tk.StringVar()
layers = tk.StringVar()

tk.Label(sensor_frame, textvariable=temperature1, bg='white').grid(row=0, column=0, padx=2, pady=5, sticky="nwes")
tk.Label(sensor_frame, textvariable=temperature2, bg='white').grid(row=1, column=0, padx=2, pady=5, sticky="w")
tk.Label(sensor_frame, textvariable=temperature3, bg='white').grid(row=2, column=0, padx=2, pady=5, sticky="w")
tk.Label(sensor_frame, textvariable=temperature4, bg='white').grid(row=3, column=0, padx=2, pady=5, sticky="w")
tk.Label(sensor_frame, textvariable=average_temp, bg='white').grid(row=4, column=0, padx=2, pady=5, sticky="w")
tk.Label(sensor_frame, textvariable=oxygen_sensor, bg='white').grid(row=5, column=0, padx=2, pady=5, sticky="w")
tk.Label(sensor_frame, textvariable=layers, bg='white').grid(row=6, column=0, padx=2, pady=5, sticky="w")

#3d model
model_frame = tk.LabelFrame(root, text="3D Model", padx=10, pady=10, bg='white')
model_frame.grid(row=1, column=4, rowspan=2, padx=10, pady=10, sticky='nsew')

# PyOpenGL setup
def init_gl():
    glEnable(GL_DEPTH_TEST)
    glClearColor(0.1, 0.1, 0.1, 1.0)

def draw_teapot():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    gluLookAt(0, 0, 5, 0, 0, 0, 0, 1, 0)
    glColor3f(1.0, 0.0, 0.0)
    glutSolidTeapot(1)
    glFlush()
    # glXSwapBuffers()

def opengl_frame(frame):
    frame.update_idletasks()
    frame.update()

    frame_width = frame.winfo_width()
    frame_height = frame.winfo_height()

    # Set up the OpenGL context and frame buffer
    glViewport(0, 0, frame_width, frame_height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, frame_width / frame_height, 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    draw_teapot()

def create_opengl_context(frame):
    frame.bind("<Configure>", lambda event: opengl_frame(frame))

    init_gl()
    glutInit()
    glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB | GLUT_DEPTH)
    glutCreateWindow(b"OpenGL Window")
    glutDisplayFunc(draw_teapot)

create_opengl_context(model_frame)

root.after(100, read_from_arduino)

# Start generating fake data if using FakeArduino
if USE_FAKE_ARDUINO:
    root.after(1000, generate_fake_data)

# Run the main event loop
root.mainloop()

# Close the serial connection when the window is closed
if arduino and not isinstance(arduino, FakeArduino):
    arduino.close()
