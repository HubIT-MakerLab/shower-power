# Is using gpiozero library for communication with the GPIO(Gerneral purpose input output) ports
# https://gpiozero.readthedocs.io/en/stable/index.html

# RASPI4 GPIO PINOUT
# 3V3  (1) (2)  5V
#  GPIO2  (3) (4)  5V
#  GPIO3  (5) (6)  GND
#  GPIO4  (7) (8)  GPIO14
#    GND  (9) (10) GPIO15
# GPIO17 (11) (12) GPIO18
# GPIO27 (13) (14) GND
# GPIO22 (15) (16) GPIO23
#    3V3 (17) (18) GPIO24
# GPIO10 (19) (20) GND
#  GPIO9 (21) (22) GPIO25
# GPIO11 (23) (24) GPIO8
#    GND (25) (26) GPIO7
#  GPIO0 (27) (28) GPIO1
#  GPIO5 (29) (30) GND
#  GPIO6 (31) (32) GPIO12
# GPIO13 (33) (34) GND
# GPIO19 (35) (36) GPIO16
# GPIO26 (37) (38) GPIO20
#    GND (39) (40) GPIO21

# Temp sensor
# red wire -> 3.3V
# black wire -> GND
# yellow -> data

#light mappings
# light circle   relay        
# mode1_lights = [r1]
# mode2_lights = [r1, r2]
# mode3_lights = [w2, r1, r2]
# day1_lights =  [w2, w3, r2]
# mode4_lights = [w2, w3]
# mode5_lights = [w2]
# sleep1_lights = []
# mode6_lights = [w2]
# mode7_lights = [w2, w3]
# day2_lights =  [w2, w3, r2]
# mode8_lights = [w2, r1, r2]
# mode9_lights = [r1, r2]
# mode10_lights = [r1]
# night_lights = [b1]
# sleep2_lights = []
# deco_lights = [b2, b1, r2]
# all_lights = [w2, w3, b2, b1, r1, r2]

# to run at raspberry start
# https://www.raspberrypi.org/documentation/linux/usage/systemd.md

import sys
import io
import signal
import sched
import json
import time as timelib
from datetime import time
from gpiozero import TimeOfDay, LED, OutputDevice, Button, CPUTemperature
from gpiozero.tools import any_values, booleanized, negated

# For writing data to file in an intervall
scheduler = sched.scheduler(timelib.time, timelib.sleep)

# Read temperature from sensor file
class TemperatureSensor(CPUTemperature):
    @property
    def temperature(self):
        with io.open(self.sensor_file, 'r') as f:
            return float(f.readlines()[1].split("=")[1]) / 1000

W2_PIN = 12
W3_PIN = 13
B2_PIN = 16
B1_PIN = 19
R1_PIN = 20
R2_PIN = 21

ALARM_PIN = 27  # red led
OK_PIN = 22  # green led

TIMER_PIN = 24  # blue led
DECO_PIN = 23  # yellow led

BUTTON_PIN = 18

MIN_TEMP = 24
MAX_TEMP = 27

# timer thresholds
NIGHT_START = time(20,15)
NIGHT_END = time(22,15,59)
SLEEP2_START = time(22,16)
SLEEP2_END = time(7,44,59)
MODE1_START = time(7,45)
MODE1_END = time(7,49,59)
MODE2_START = time(7,50)
MODE2_END = time(7,54,59)
MODE3_START = time(7,55)
MODE3_END = time(7,59,59)
DAY1_START = time(8,00)
DAY1_END = time(11,59,59)
MODE4_START = time(12,00)
MODE4_END = time(12,4,59)
MODE5_START = time(12,5)
MODE5_END = time(12,9,59)
SLEEP1_START = time(12,10)
SLEEP1_END = time(15,59,59)
MODE6_START = time(16,0)
MODE6_END = time(16,4,59)
MODE7_START = time(16,5)
MODE7_END = time(16,9,59)
DAY2_START = time(16,10)
DAY2_END = time(19,59,59)
MODE8_START = time(20,00)
MODE8_END = time(20,4,59)
MODE9_START = time(20,5)
MODE9_END = time(20,9,59)
MODE10_START = time(20,10)
MODE10_END = time(20,14,59)


# output
w2 = OutputDevice(W2_PIN, active_high=False)
w3 = OutputDevice(W3_PIN, active_high=False)
b2 = OutputDevice(B2_PIN, active_high=False)
b1 = OutputDevice(B1_PIN, active_high=False)
r1 = OutputDevice(R1_PIN, active_high=False)
r2 = OutputDevice(R2_PIN, active_high=False)
alarm_led = LED(ALARM_PIN, active_high=True, initial_value=False)
ok_led = LED(OK_PIN, active_high=True, initial_value=False)
deco_led = LED(DECO_PIN, active_high=True, initial_value=False)
timer_led = LED(TIMER_PIN, active_high=True, initial_value=False)

# input
button = Button(BUTTON_PIN)
temp = TemperatureSensor(
    sensor_file="/sys/bus/w1/devices/28-01145f1e90df/w1_slave", threshold=20)

# either timer or deco

active_mode = "timer"

day1 = day2 = night = mode1 = mode2 = mode3 = mode4 = mode5 = mode6 = mode7 = mode8 = mode9 = mode10 = sleep1 = sleep2 = None

def writeStatusToFile():
    data = {
        'mode': active_mode,
        'temp': temp.value * 100,
        'status': {
            'day1': day1.value,
            'day2': day2.value,
            'night': night.value,
            'mode1': mode1.value,
            'mode2': mode2.value,
            'mode3': mode3.value,
            'mode4': mode4.value,
            'mode5': mode5.value,
            'mode6': mode6.value,
            'mode7': mode7.value,
            'mode8': mode8.value,
            'mode9': mode9.value,
            'mode10': mode10.value,
            'sleep1': sleep1.value,
            'sleep2': sleep2.value,
        }
    }

    with io.open('/home/pi/piquarium/status.json', 'w') as file:
        json.dump(data, file)

# custom constant value generators
def constant_true():
    while True:
        yield True


def constant_false():
    while True:
        yield False

# setup the time trackers
def assign_timers():
    global day1, day2, night, mode1, mode2, mode3, mode4, mode5, mode6, mode7, mode8, mode9, mode10, sleep1, sleep2, timer, DAY1_START, DAY1_END, DAY2_START, DAY2_END, NIGHT_START, NIGHT_END, MODE1_START, MODE1_END, MODE2_START, MODE2_END, MODE3_START, MODE3_END, MODE4_START, MODE4_END, MODE5_START, MODE5_END, MODE6_START, MODE6_END, MODE7_START, MODE7_END, MODE8_START, MODE8_END, MODE9_START, MODE9_END, MODE10_START, MODE10_END, SLEEP1_END, SLEEP1_START, SLEEP2_END, SLEEP2_START
    day1 = TimeOfDay(start_time=DAY1_START, end_time=DAY1_END, utc=False)
    day2 = TimeOfDay(start_time=DAY2_START, end_time=DAY2_END, utc=False)
    night = TimeOfDay(start_time=NIGHT_START, end_time=NIGHT_END, utc=False)
    sleep1 = TimeOfDay(start_time=SLEEP1_START, end_time=SLEEP1_END, utc=False)
    sleep2 = TimeOfDay(start_time=SLEEP2_START, end_time=SLEEP2_END, utc=False)
    mode1 = TimeOfDay(start_time=MODE1_START, end_time=MODE1_END, utc=False)
    mode2 = TimeOfDay(start_time=MODE2_START, end_time=MODE2_END, utc=False)
    mode3 = TimeOfDay(start_time=MODE3_START, end_time=MODE3_END, utc=False)
    mode4 = TimeOfDay(start_time=MODE4_START, end_time=MODE4_END, utc=False)
    mode5 = TimeOfDay(start_time=MODE5_START, end_time=MODE5_END, utc=False)
    mode6 = TimeOfDay(start_time=MODE6_START, end_time=MODE6_END, utc=False)
    mode7 = TimeOfDay(start_time=MODE7_START, end_time=MODE7_END, utc=False)
    mode8 = TimeOfDay(start_time=MODE8_START, end_time=MODE8_END, utc=False)
    mode9 = TimeOfDay(start_time=MODE9_START, end_time=MODE9_END, utc=False)
    mode10 = TimeOfDay(start_time=MODE10_START, end_time=MODE10_END, utc=False)
    timer = constant_true()

def reset_modes():
    global day1, day2, night, sleep1, sleep2, mode1, mode2, mode3, mode4, mode5, mode6, mode7, mode8, mode9, mode10

    def null_timer():
        return TimeOfDay(start_time=time(0), end_time=time(0,0,1), utc=False)

    day1 = null_timer()
    day2 = null_timer()
    night = null_timer()
    sleep1 = null_timer()
    sleep2 = null_timer()
    mode1 = null_timer()
    mode2 = null_timer()
    mode3 = null_timer()
    mode4 = null_timer()
    mode5 = null_timer()
    mode6 = null_timer()
    mode7 = null_timer()
    mode8 = null_timer()
    mode9 = null_timer()
    mode10 = null_timer()

# wire timers and other states to outputs
def assign_sources():
    global w2, w3, b2, b1, r1, r2, ok_led, deco, timer
    w2.source = any_values(day1, mode3, mode4, mode5, mode6, day2, mode8, mode7)
    w3.source = any_values(day1, mode4, mode7, day2)
    b2.source = any_values(deco)
    b1.source = any_values(night, deco)
    r1.source = any_values(mode1, mode2, mode3, mode8, mode9, mode10)
    r2.source = any_values(mode2, mode3, day1, day2, mode8, mode9,deco)
    deco_led.source = deco
    timer_led.source = timer

# runs after button is pressed
def button_callback():
    global deco, active_mode, ok_led, timer
    print("button pressed")
    if active_mode is "timer":
        active_mode = "deco"
        reset_modes()
        deco = constant_true()
        timer = constant_false()
    else:
        active_mode = "timer"
        assign_timers()
        deco = constant_false()
    assign_sources()
    print(temp.value)
    print(active_mode)
    writeStatusToFile()

# default status of the modes
deco = constant_false()
timer = constant_false()
reset_modes()

# start it
assign_timers()
assign_sources()

# temperature alarms
ok_led.source = booleanized(temp, MIN_TEMP/100, MAX_TEMP/100)
alarm_led.source = negated(booleanized(temp, MIN_TEMP/100, MAX_TEMP/100))

# button
button.when_released = button_callback

# schedule status write to file
def writeStatus():
    global scheduler
    writeStatusToFile()
    scheduler.enter(60, 1, writeStatus)

# start scheduler
scheduler.enter(2, 1, writeStatus)
scheduler.run()

# wait until program gets killed
def sigterm_handler(_signo, _stack_frame):
    # Raises SystemExit(0):
    sys.exit(0)


signal.signal(signal.SIGTERM, sigterm_handler)

signal.pause()

