import RPi.GPIO as GPIO
import time
import signal
import sys

from flask import Flask

HOST = "TYPE HOST HERE"

app = Flask(__name__)

pb_pins = (2, 3, 4, 14)
jam_pins = (9, 11, 25, 8)
# door_pins = (9, 11, 25, 8)
door_pins = (15, 18, 17, 27)

sleep_step = 0.002

step_count = 4096

# True for clockwise, False for counter-clockwise
direction = False

step_sequence = [[1,0,0,1],
                 [1,0,0,0],
                 [1,1,0,0],
                 [0,1,0,0],
                 [0,1,1,0],
                 [0,0,1,0],
                 [0,0,1,1],
                 [0,0,0,1]]

# setup
GPIO.setmode(GPIO.BCM)
for i in range(0, 4):
    GPIO.setup(pb_pins[i], GPIO.OUT)
    GPIO.setup(jam_pins[i], GPIO.OUT)
    GPIO.setup(door_pins[i], GPIO.OUT)

#initialization
for i in range(0, 4):
    GPIO.output(pb_pins[i], GPIO.LOW)
    GPIO.output(jam_pins[i], GPIO.LOW)
    GPIO.output(door_pins[i], GPIO.LOW)

pb_step_counter = 0
jam_step_counter = 0
door_step_counter = 0

squeeze_steps = 4096

total_pb_steps = 0
total_jam_steps = 0

def cleanup(sig, frame):
    for i in range(0, 4):
        GPIO.output(pb_pins[i], GPIO.LOW)
        GPIO.output(jam_pins[i], GPIO.LOW)
        GPIO.output(door_pins[i], GPIO.LOW)
    GPIO.cleanup()
    sys.exit(0)

@app.route("/")
def hello():
    return "Hello World!"

@app.route("/open")
def open_door():
    global door_step_counter
    global door_pins
    global step_sequence
    print("Door is being opened...")
    for _ in range(0, 1024):
        for pin in range(0, 4):
            GPIO.output(door_pins[pin], step_sequence[door_step_counter][pin])
        door_step_counter = (door_step_counter - 1) % 8
        time.sleep(sleep_step)
    print("...Door has been opened")
    return("Door Open")

@app.route("/close")
def close_door():
    global door_step_counter
    global door_pins
    global step_sequence
    print("Door is being closed...")
    for _ in range(0, 1024):
        for pin in range(0, 4):
            GPIO.output(door_pins[pin], step_sequence[door_step_counter][pin])
        door_step_counter = (door_step_counter + 1) % 8
        time.sleep(sleep_step)
    print("...Door has been closed")
    return("Door Closed")

@app.route("/squeeze")
def squeeze_contents():
    global pb_step_counter
    global jam_step_counter
    global total_pb_steps
    global pb_pins
    global jam_pins
    global step_sequence
    print("Contents are being squeezed...")
    for _ in range(0, squeeze_steps):
        for pin in range(0, 4):
            GPIO.output(pb_pins[pin], step_sequence[pb_step_counter][pin])
            GPIO.output(jam_pins[pin], step_sequence[jam_step_counter][pin])
        total_pb_steps += 1
        pb_step_counter = (pb_step_counter - 1) % 8
        jam_step_counter = (jam_step_counter - 1) % 8
        time.sleep(sleep_step)
    print("...Contents have been squeezed")
    return("Contents Squeezed")

@app.route("/refill")
def prepare_for_refill():
    global pb_step_counter
    global jam_step_counter
    global total_pb_steps
    global pb_pins
    global jam_pins
    global step_sequence
    print("Preparing containers for refill...")
    for _ in range(total_pb_steps, 0, -1):
        for pin in range(0, 4):
            GPIO.output(pb_pins[pin], step_sequence[pb_step_counter][pin])
            GPIO.output(jam_pins[pin], step_sequence[jam_step_counter][pin])
        pb_step_counter = (pb_step_counter + 1) % 8
        jam_step_counter = (jam_step_counter + 1) % 8
        time.sleep(sleep_step)
    total_pb_steps = 0
    print("...Contents are ready to be refilled")
    return("Refill Ready")

if __name__ == "__main__":
    signal.signal(signal.SIGINT, cleanup)
    signal.pause()
    app.run(host=HOST, port=8000, debug=True)