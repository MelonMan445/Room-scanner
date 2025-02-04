import RPi.GPIO as GPIO
import time
import tkinter as tk
from tkinter import messagebox
import threading
import math
import matplotlib.pyplot as plt

# GPIO pin setup
TRIG_PIN = 22  # GPIO 22 (Pin 15)
ECHO_PIN = 27  # GPIO 27 (Pin 13)
StepPins = [24, 25, 8, 7]

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG_PIN, GPIO.OUT)
GPIO.setup(ECHO_PIN, GPIO.IN)
for pin in StepPins:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, False)

# Stepper motor sequences
StepCount = 8
Seq = [
    [1, 0, 0, 0],
    [1, 1, 0, 0],
    [0, 1, 0, 0],
    [0, 1, 1, 0],
    [0, 0, 1, 0],
    [0, 0, 1, 1],
    [0, 0, 0, 1],
    [1, 0, 0, 1],
]

# Global variables
step_counter = 0
running = False
direction = 1  # 1 = clockwise, -1 = counterclockwise
wait_time = 0.005  # Speed control
sensor_on = False
rotation_count = 0
scanning = False

# Steps per full rotation
STEPS_PER_ROTATION = 4096  # Adjusted to match actual motor steps per rotation

# Scan data storage
scan_data = []

def get_distance():
    if sensor_on:
        GPIO.output(TRIG_PIN, True)
        time.sleep(0.00001)
        GPIO.output(TRIG_PIN, False)
        
        start_time = time.time()
        while GPIO.input(ECHO_PIN) == 0:
            pulse_start = time.time()
            if pulse_start - start_time > 0.1:  # Timeout
                return None
        
        start_time = time.time()
        while GPIO.input(ECHO_PIN) == 1:
            pulse_end = time.time()
            if pulse_end - start_time > 0.1:  # Timeout
                return None
        
        pulse_duration = pulse_end - pulse_start
        distance = (pulse_duration * 34300) / 2
        return round(distance, 2)
    return None

def visualize_scan():
    if not scan_data:
        messagebox.showinfo("Scan Result", "No scan data collected.")
        return
    
    # Polar to Cartesian conversion
    x_points = []
    y_points = []
    for distance, angle in scan_data:
        # Convert polar coordinates to Cartesian
        if distance is not None:
            # Convert angle to radians
            rad_angle = math.radians(angle)
            x = distance * math.cos(rad_angle)
            y = distance * math.sin(rad_angle)
            x_points.append(x)
            y_points.append(y)
    
    # Create visualization
    plt.figure(figsize=(10, 10))
    plt.title("360-Degree Scan Visualization")
    plt.xlabel("Distance (X) in cm")
    plt.ylabel("Distance (Y) in cm")
    
    # Plot points
    plt.scatter(x_points, y_points, color='red', s=50)
    
    # Connect points to form a polygon
    plt.plot(x_points + [x_points[0]], y_points + [y_points[0]], '-b')
    
    # Add grid and center
    plt.grid(True)
    plt.axhline(y=0, color='k', linestyle='--')
    plt.axvline(x=0, color='k', linestyle='--')
    
    # Ensure equal aspect ratio
    plt.axis('equal')
    
    plt.show()

def move_motor():
    global step_counter, running, direction, rotation_count
    steps_moved = 0
    while running:
        for pin in range(4):
            GPIO.output(StepPins[pin], Seq[step_counter][pin])
        step_counter += direction
        steps_moved += 1
        if step_counter >= StepCount:
            step_counter = 0
        if step_counter < 0:
            step_counter = StepCount - 1
        if steps_moved % STEPS_PER_ROTATION == 0:
            rotation_count += direction
            rotation_label.config(text=f"Rotations: {rotation_count}")
        time.sleep(wait_time)

def move_one_rotation(rot_direction):
    global step_counter, rotation_count, scanning
    steps_moved = 0
    for _ in range(STEPS_PER_ROTATION):
        for pin in range(4):
            GPIO.output(StepPins[pin], Seq[step_counter][pin])
        step_counter += rot_direction
        steps_moved += 1
        if step_counter >= StepCount:
            step_counter = 0
        if step_counter < 0:
            step_counter = StepCount - 1
        time.sleep(wait_time)
    rotation_count += rot_direction
    rotation_label.config(text=f"Rotations: {rotation_count}")

def start_motor():
    global running
    if not running:
        running = True
        threading.Thread(target=move_motor, daemon=True).start()

def stop_motor():
    global running, scanning
    running = False
    scanning = False
    for pin in StepPins:
        GPIO.output(pin, False)

def increase_speed():
    global wait_time
    if wait_time > 0.001:
        wait_time -= 0.001

def decrease_speed():
    global wait_time
    wait_time += 0.001

def clockwise():
    global direction
    direction = 1

def counterclockwise():
    global direction
    direction = -1

def toggle_sensor():
    global sensor_on
    sensor_on = not sensor_on
    sensor_status_label.config(text=f"Sensor: {'ON' if sensor_on else 'OFF'}")

def scan_360():
    global scanning, sensor_on, scan_data, step_counter
    
    # Reduce wait time for faster rotation
    global wait_time
    original_wait_time = wait_time
    wait_time = 0.001  # Speed up rotation
    
    scan_data = []
    
    # Ensure sensor is on
    if not sensor_on:
        toggle_sensor()
    
    scanning = True
    scan_result_label.config(text="Fast Scanning...")
    
    # Sample every 8th step to speed up scan
    for i in range(0, STEPS_PER_ROTATION, 8):
        # Calculate current angle
        current_angle = (i / STEPS_PER_ROTATION) * 360
        
        # Get distance
        dist = get_distance()
        
        # Store valid measurements
        if dist is not None and dist != "Timeout":
            scan_data.append((dist, current_angle))
        
        # Move multiple steps
        for _ in range(8):
            for pin in range(4):
                GPIO.output(StepPins[pin], Seq[step_counter][pin])
            
            step_counter += 1
            if step_counter >= StepCount:
                step_counter = 0
            
            time.sleep(wait_time)
    
    # Restore original wait time
    wait_time = original_wait_time
    
    scanning = False
    scan_result_label.config(text=f"Fast Scan Complete: {len(scan_data)} points")
    
    # Visualize the scan
    
    visualize_scan()
    


def update_distance():
    while True:
        dist = get_distance()
        distance_label.config(text=f"Distance: {dist} cm")
        time.sleep(0.1)

root = tk.Tk()
root.title("Stepper Motor & Ultrasonic Sensor")

frame1 = tk.Frame(root, bg="lightblue")
frame1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
frame2 = tk.Frame(root, bg="lightgreen")
frame2.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

tk.Button(frame1, text="Start", command=start_motor, width=15).pack()
tk.Button(frame1, text="Stop", command=stop_motor, width=15).pack()
tk.Button(frame1, text="Faster", command=increase_speed, width=15).pack()
tk.Button(frame1, text="Slower", command=decrease_speed, width=15).pack()
tk.Button(frame1, text="Left", command=counterclockwise, width=15).pack()
tk.Button(frame1, text="Right", command=clockwise, width=15).pack()

# New buttons for +1 and -1 full rotation
tk.Button(frame1, text="+1", command=lambda: threading.Thread(target=move_one_rotation, args=(1,), daemon=True).start(), width=15).pack()
tk.Button(frame1, text="-1", command=lambda: threading.Thread(target=move_one_rotation, args=(-1,), daemon=True).start(), width=15).pack()

rotation_label = tk.Label(frame1, text="Rotations: 0", bg="lightblue")
rotation_label.pack()

tk.Button(frame2, text="Toggle Sensor", command=toggle_sensor, width=15).pack()
sensor_status_label = tk.Label(frame2, text="Sensor: OFF", bg="lightgreen")
sensor_status_label.pack()

distance_label = tk.Label(frame2, text="Distance: -- cm", bg="lightgreen")
distance_label.pack()

# Scan button and results label
tk.Button(frame2, text="Scan", command=scan_360, width=15).pack()
scan_result_label = tk.Label(frame2, text="", bg="lightgreen", wraplength=200)
scan_result_label.pack()

distance_thread = threading.Thread(target=update_distance, daemon=True)
distance_thread.start()

root.mainloop()
GPIO.cleanup()


