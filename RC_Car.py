import machine
import uasyncio as asyncio
import picoweb
import network
import ujson

SSID = 'Miri'
PASSWORD = '87654321'


def connect_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    print("Connecting to WiFi...")
    while not wlan.isconnected():
        pass
    print('Connected to WiFi. Network config:', wlan.ifconfig())
    return wlan.ifconfig()[0]


ip_address = connect_wifi(SSID, PASSWORD)
print(f"Web server started at http://{ip_address}")

Motor1_pin1 = machine.Pin(12, machine.Pin.OUT)
Motor1_pin2 = machine.Pin(13, machine.Pin.OUT)
Motor2_pin1 = machine.Pin(14, machine.Pin.OUT)
Motor2_pin2 = machine.Pin(15, machine.Pin.OUT)

Motor1_pwm1 = machine.PWM(Motor1_pin1)
Motor1_pwm2 = machine.PWM(Motor1_pin2)
Motor2_pwm1 = machine.PWM(Motor2_pin1)
Motor2_pwm2 = machine.PWM(Motor2_pin2)

Motor1_pwm1.freq(1000)
Motor1_pwm2.freq(1000)
Motor2_pwm1.freq(1000)
Motor2_pwm2.freq(1000)

default = 0
current_speed = 0
max_speed = 200
turn_speed = 500
turn_steps = 6
step_delay = 0.3

command_lock = asyncio.Lock()
current_command = None


def set_pwm_duty(pwm, duty):
    pwm.duty(duty)


def set_motor_speed(speed):
    set_pwm_duty(Motor1_pwm1, speed)
    set_pwm_duty(Motor1_pwm2, speed)
    print(f"Setting motor speed to {speed}")


async def gradual_accelerate(target_speed):
    global current_speed
    while current_speed < target_speed and current_command in ["forward", "backward"]:
        current_speed += 10
        set_motor_speed(current_speed)
        await asyncio.sleep(0.1)


async def gradual_decelerate():
    global current_speed
    while current_speed > 10 and current_command == "stop":
        current_speed -= 10
        set_motor_speed(current_speed)
        await asyncio.sleep(0.05)


async def forward():
    global current_command
    async with command_lock:
        current_command = "forward"
    asyncio.create_task(gradual_accelerate(max_speed))
    Motor1_pin1.value(1)
    Motor1_pin2.value(0)


async def backward():
    global current_command
    async with command_lock:
        current_command = "backward"
    asyncio.create_task(gradual_accelerate(max_speed))
    Motor1_pin1.value(0)
    Motor1_pin2.value(1)


async def move_steps(pwm1, pwm2, steps, speed, direction):
    pwm1.duty(speed if direction else 0)
    pwm2.duty(0 if direction else speed)
    for _ in range(steps):
        await asyncio.sleep(step_delay)
    pwm1.duty(0)
    pwm2.duty(0)


async def left():
    asyncio.create_task(move_steps(Motor2_pwm1, Motor2_pwm2, turn_steps, turn_speed, True))


async def right():
    asyncio.create_task(move_steps(Motor2_pwm1, Motor2_pwm2, turn_steps, turn_speed, False))
    print("Turning right")


async def stop():
    global current_command
    async with command_lock:
        current_command = "stop"
    asyncio.create_task(gradual_decelerate())
    Motor1_pin1.value(0)
    Motor1_pin2.value(0)
    Motor2_pin2.value(0)
    Motor2_pin1.value(0)


def process_command(command):
    if command == "forward":
        if current_command != "forward":
            asyncio.create_task(forward())
    elif command == "backward":
        if current_command != "backward":
            asyncio.create_task(backward())
    elif command == "stop":
        asyncio.create_task(stop())
    elif command == "left":
        asyncio.create_task(left())
    elif command == "right":
        asyncio.create_task(right())
    elif command.isdigit() and 1 <= int(command) <= 5:
        set_gear(int(command))
    return command


def set_gear(gear):
    global max_speed
    max_speed = gear * 200
    print(f"Gear set to {gear}, max speed is now {max_speed}")


app = picoweb.WebApp(__name__)

index_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <title>RC Car Control</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: Arial, sans-serif;
            background-color: #f0f0f0;
            display: flex;
            flex-direction: column;
            align-items: center;
            height: 100vh;
            justify-content: space-between;
        }

        .camera-container {
            width: 90%;
            max-width: 600px;
            height: auto;
            display: flex;
            justify-content: center;
            align-items: center;
            background-color: #333;
            margin-top: 10px;
            border-radius: 10px;
        }

        .camera-container img {
            width: 100%;
            height: auto;
            border-radius: 10px;
        }

        .joystick-container {
            margin-top: 10px;
            width: 100%;
            max-width: 600px;
            display: flex;
            justify-content: space-evenly;
            align-items: center;
            margin-bottom: 150px;
        }

        .joystick {
            width: 150px;
            height: 150px;
            background-color: #444;
            border-radius: 50%;
            position: relative;
            box-shadow: 0 0 10px rgba(0,0,0,0.5);
        }

        .knob {
            width: 50px;
            height: 50px;
            background-color: #000;
            border-radius: 50%;
            position: absolute;
            left: 50%;
            top: 50%;
            transform: translate(-50%, -50%);
            touch-action: none;
        }

        .stop {
            display: flex;
            justify-content: center;
            align-items: center;
        }

        .stop button {
            width: 130px;
            height: 50px;
            cursor: pointer;
            font-size: 20px;
            border-radius: 30px;
            background-color: #ff0000;
            color: #fff;
            border: none;
            margin: 10px;
            box-shadow: 0 0 10px rgba(0,0,0,0.5);
        }

        .gear-container {
            width: 100px;
            height: 300px;
            background-color: #007bff;
            border-radius: 10px;
            position: absolute;
            right: 20px;
            top: 20px;
            display: flex;
            flex-direction: column;
            justify-content: space-evenly;
            align-items: center;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.5);
        }

        .gear {
            width: 30px;
            height: 30px;
            background-color: #fff;
            border-radius: 50%;
            display: flex;
            justify-content: center;
            align-items: center;
            color: #007bff;
            font-size: 12px;
            font-weight: bold;
            user-select: none;
        }


        .speed-display {
            position: absolute;
            top: 350px;
            right: 20px;
            background-color: #28a745;
            color: white;
            padding: 10px 20px;
            border-radius: 10px;
            font-size: 18px;
            cursor: pointer;
        }

        @media (max-width: 600px) {
            .camera-container {
                width: 100%;
                height: 200px;
            }

            .joystick {
                width: 120px;
                height: 120px;
            }

            .knob {
                width: 40px;
                height: 40px;
            }

            .stop button {
                width: 100px;
                height: 40px;
                font-size: 16px;
            }

            .gear-container {
                width: 250px;
                height: 70px;
                margin-top: 100px;
                align-items: center;
                flex-direction: row;
                right: 80px;
                top: 250px;
            }

            .gear {
                width: 18px;
                height: 18px;
                margin: 0 10px;
            }

            .knob-gear {
                width: 25px;
                height: 25px;
                left: 50px;
            }


            .speed-display {
                top: 280px;
                right: auto;
                left: 50%;
                transform: translateX(-50%);
            }
        }

        .gear1 { top: 220px; }
        .gear2 { top: 70px; }
        .gear3 { top: 120px; }
        .gear4 { top: 170px; }
        .gear5 { top: 100px; }

        .knob-gear {
            width: 30px;
            height: 30px;
            background-color: #000;
            border-radius: 50%;
            position: absolute;
            left: 50px;
            transform: translateX(-38%);
            touch-action: none;
            cursor: pointer;
            box-shadow: 0 0 10px rgba(0,0,0,0.5);
        }

        .gear-selected {
            background-color: #28a745;
            color: white;
        }
    </style>
     <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body>
    <div class="camera-container">
        <img src="car_photo" alt="Car Photo" class="camera-feed">
    </div>

    <!-- Speed display button -->
    <div class="speed-display" id="speed-display">Speed: 0 km/h</div>

    <div class="joystick-container">
        <div class="joystick" id="joystick-fb">
            <div class="knob" id="knob-fb"></div>
        </div>
        <div class="stop">
            <button onclick="sendCommand('stop')">Stop</button>
        </div>
        <div class="joystick" id="joystick-lr">
            <div class="knob" id="knob-lr"></div>
        </div>
    </div>

    <div class="gear-container">
        <div class="gear gear1">1</div>
        <div class="gear gear2">2</div>
        <div class="gear gear3">3</div>
        <div class="gear gear4">4</div>
        <div class="gear gear5">5</div>
        <div class="knob-gear" id="knob-gear"></div>
    </div>
<script>
        let lastLeftRightCommand = 0;
        let speed = 0;
        let activeKeys = {};

        function showSpeed() {
            fetch('/current_speed')
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(data => {
                    if (typeof data.speed === "number") {
                        speed = data.speed;
                        document.getElementById('speed-display').innerText = `Speed: ${speed} km/h`;
                    } else {
                        console.error('Invalid speed data received:', data);
                    }
                })
                .catch(error => console.error('Error fetching speed:', error));
        }

        setTimeout(showSpeed, 1000);

        function sendCommand(command) {
            fetch(`/${command}`).then(response => {
                if (response.ok) {
                    console.log(`${command} command sent successfully`);
                    if (command === 'stop' || command === 'forward' || command === 'backward') {
                        showSpeed();
                    }
                } else {
                    console.log(`Failed to send ${command} command`);
                }
            }).catch(error => {
                console.error('Error:', error);
            });
        }

        // Joystick setup for forward/backward and left/right control
        function setupJoystick(joystickId, knobId, onMove, vertical) {
            const joystick = document.getElementById(joystickId);
            const knob = document.getElementById(knobId);

            let isDragging = false;
            let startX, startY;

            const startDrag = (event) => {
                isDragging = true;
                startX = event.clientX || event.touches[0].clientX;
                startY = event.clientY || event.touches[0].clientY;
            };

            const moveDrag = (event) => {
                if (!isDragging) return;

                const x = event.clientX || event.touches[0].clientX;
                const y = event.clientY || event.touches[0].clientY;
                const dx = x - startX;
                const dy = y - startY;
                const distance = Math.min(50, Math.abs(vertical ? dy : dx));

                if (vertical) {
                    knob.style.transform = `translate(-50%, ${distance * Math.sign(dy) - 25}px)`;
                    onMove(0, dy);
                } else {
                    knob.style.transform = `translate(${distance * Math.sign(dx) - 25}px, -50%)`;
                    onMove(dx, 0);
                }
            };

            const endDrag = () => {
                if (isDragging) {
                    isDragging = false;
                    knob.style.transform = 'translate(-50%, -50%)';
                    onMove(0, 0);
                }
            };

            knob.addEventListener('mousedown', startDrag);
            knob.addEventListener('touchstart', startDrag);
            document.addEventListener('mousemove', moveDrag);
            document.addEventListener('touchmove', moveDrag);
            document.addEventListener('mouseup', endDrag);
            document.addEventListener('touchend', endDrag);
        }

        setupJoystick('joystick-fb', 'knob-fb', (dx, dy) => {
            if (dy < -20) {
                sendCommand('forward');
                speed = Math.min(speed + 10, 100); // Increase speed
            } else if (dy > 20) {
                sendCommand('backward');
                speed = Math.max(speed - 10, 0); // Decrease speed
            } else {
                sendCommand('stop');
            }
            document.querySelector('.speed-display').innerText = `Speed: ${speed} km/h`;
        }, true);

        setupJoystick('joystick-lr', 'knob-lr', (dx, dy) => {
            const now = Date.now();
            if (now - lastLeftRightCommand < 500) return;

            if (dx < -20) {
                sendCommand('left');
            } else if (dx > 20) {
                sendCommand('right');
            } else {
                sendCommand('stop');
            }
            lastLeftRightCommand = now;
        }, false);

        // Gear Shifter
        function setupGearShifter(knobId, onShift) {
            const knob = document.getElementById(knobId);

            knob.addEventListener('mousedown', (event) => {
                const rect = knob.getBoundingClientRect();
                const x = event.clientX - rect.left;
                const gear = Math.ceil(x / (rect.width / 5));
                onShift(gear);
            });

            knob.addEventListener('touchstart', (event) => {
                const rect = knob.getBoundingClientRect();
                const x = event.touches[0].clientX - rect.left;
                const gear = Math.ceil(x / (rect.width / 5));
                onShift(gear);
            });
        }

        setupGearShifter('knob-gear', (gear) => {
            document.querySelectorAll('.gear').forEach(element => element.classList.remove('gear-selected'));
            document.querySelector(`.gear${gear}`).classList.add('gear-selected');
            sendCommand(gear.toString());
        });

        // Key control for directional commands
        document.addEventListener('keydown', (event) => {
            if (activeKeys[event.key]) return;
            activeKeys[event.key] = true;

            switch(event.key) {
                case 'ArrowUp':
                    sendCommand('forward');
                    break;
                case 'ArrowDown':
                    sendCommand('backward');
                    break;
                case 'ArrowLeft':
                    sendCommand('left');
                    break;
                case 'ArrowRight':
                    sendCommand('right');
                    break;
                case ' ':
                    sendCommand('stop');
                    break;
            }
        });

        document.addEventListener('keyup', (event) => {
            delete activeKeys[event.key];
            // Only stop if an arrow key was released
            if (['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(event.key)) {
                sendCommand('stop');
            }
        });
    </script>
</body>
</html>"""

@app.route("/")
async def index(req, resp):
    await picoweb.start_response(resp, content_type="text/html")
    await resp.awrite(index_html)


@app.route("/<command>")
async def handle_command(req, resp, command):
    await process_command(command)
    await picoweb.start_response(resp)
    await resp.awrite(f"Command {command} executed")

@app.route("/current_speed")
async def get_current_speed(req, resp):
    global current_speed
    response = {"speed": current_speed}
    await picoweb.start_response(resp, content_type="application/json")
    await resp.awrite(ujson.dumps(response))


# Run the server
app.run(host="0.0.0.0", port=80)
