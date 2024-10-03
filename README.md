# RC_Car
This project allows you to control an RC car using an ESP32, providing both forward/backward movement and left/right steering, with speed adjustments and a web-based control interface. The project uses a web server hosted on the ESP32 that can be accessed over a WiFi network.

Features:
WiFi-based control using a web interface.
Forward, backward, left, and right movement.
Adjustable speed using a virtual gear shifter.
Real-time speed display.
Controlled using a web-based joystick or keyboard input.
Requirements:
ESP32 Microcontroller
L298N Motor Driver (or equivalent)
Two DC Motors
Micropython installed on the ESP32
uasyncio, picoweb, and ujson libraries installed on the ESP32.
Hardware Connections:
Motor1 (Left Motor): GPIO 12 and GPIO 13
Motor2 (Right Motor): GPIO 14 and GPIO 15
Installation:
Flash Micropython onto your ESP32 if not already done.
Upload the required libraries:
uasyncio
picoweb
ujson
Upload this code to your ESP32 using tools like ampy or Thonny.
Connect the motors to the correct GPIO pins as per the pin assignment.
Usage:
Connect to WiFi:

Set the correct WiFi SSID and password by updating the SSID and PASSWORD variables in the script.
Once connected, the ESP32 will print the assigned IP address.
Access the Web Interface:

Open a web browser and navigate to http://<ESP32-IP-Address>.
You will see a control interface with joysticks to control the car and a gear shifter for speed adjustment.
Control the Car:

Forward/Backward: Use the forward/backward joystick or arrow keys on your keyboard.
Left/Right: Use the left/right joystick or arrow keys.
Stop: Use the "Stop" button or press the spacebar.
Speed Adjustment: Use the gear shifter to change speed levels (1-5).
Key Functions:
connect_wifi(ssid, password): Connects the ESP32 to the specified WiFi network.
set_motor_speed(speed): Sets the speed of the motors.
gradual_accelerate(target_speed): Gradually accelerates to the target speed.
forward() / backward() / stop(): Controls the movement of the car.
left() / right(): Controls the steering direction.
set_gear(gear): Adjusts the speed based on the selected gear.
Web Interface: HTML and JavaScript to provide a user-friendly control panel for the car.
