#RC Car with ESP32


Overview
This project allows you to control an RC car using an ESP32, providing both forward/backward movement and left/right steering with adjustable speed. The car is controlled through a web interface hosted on the ESP32, accessible over a WiFi network.

Features
WiFi-based control using a web interface.
Forward, backward, left, and right movement.
Adjustable speed via a virtual gear shifter.
Real-time speed display on the interface.
Controlled using a web-based joystick or keyboard input.
Requirements
ESP32 Microcontroller
L298N Motor Driver (or equivalent)
Two DC Motors
MicroPython installed on the ESP32
Libraries:
uasyncio
picoweb
ujson
Hardware Connections
Motor 1 (Left Motor): GPIO 12 and GPIO 13
Motor 2 (Right Motor): GPIO 14 and GPIO 15
Installation
Flash MicroPython onto your ESP32 (if not already done).
Upload required libraries to the ESP32:
uasyncio
picoweb
ujson Upload the libraries using tools like ampy or Thonny.
Upload the project code to your ESP32.
Connect the motors to the correct GPIO pins based on the hardware connections listed above.
Usage
Connect to WiFi:
Set the correct WiFi SSID and password by updating the SSID and PASSWORD variables in the script.
Once connected, the ESP32 will print the assigned IP address.
Access the Web Interface:
Open a web browser and navigate to http://[ESP32-IP-Address].
The web interface will display a control panel with joysticks to control the car and a gear shifter for speed adjustment.
Control the Car:
Forward/Backward: Use the forward/backward joystick or the arrow keys on your keyboard.
Left/Right: Use the left/right joystick or arrow keys.
Stop: Use the "Stop" button or press the spacebar.
Speed Adjustment: Use the gear shifter to change speed levels (1-5).
Key Functions
connect_wifi(ssid, password): Connects the ESP32 to the specified WiFi network.
set_motor_speed(speed): Sets the speed of the motors.
gradual_accelerate(target_speed): Gradually accelerates to the target speed.
forward(), backward(), stop(): Controls the movement of the car.
left(), right(): Controls the steering direction.
set_gear(gear): Adjusts the speed based on the selected gear.
Web Interface
The web interface uses HTML and JavaScript to provide a user-friendly control panel for the car.

Photos of user interface on mobile and laptop:
![image](https://github.com/user-attachments/assets/dcc75bc8-6f3e-4fff-9ea0-a50405486602)
![image](https://github.com/user-attachments/assets/0193cd1b-df1a-4233-88ea-867af268b3a0)

