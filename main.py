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

RED_PIN = 27  # red led

YELLOW_PIN = 24  # blue led

GREEN_PIN = 18  # green led


# output
alarm_led = LED(ALARM_PIN, active_high=True, initial_value=False)
ok_led = LED(OK_PIN, active_high=True, initial_value=False)
deco_led = LED(DECO_PIN, active_high=True, initial_value=False)
timer_led = LED(TIMER_PIN, active_high=True, initial_value=False)

# input
temp = TemperatureSensor(
    sensor_file="/sys/bus/w1/devices/28-01145f1e90df/w1_slave", threshold=20)


# write data to json file
with io.open('/home/code/shower-power/status.json', 'w') as file:
    json.dump(data, file)

# custom constant value generators
def constant_true():
    while True:
        yield True

def constant_false():
    while True:
        yield False


# start it
assign_sources()

# temperature alarms
ok_led.source = booleanized(temp, MIN_TEMP/100, MAX_TEMP/100)
alarm_led.source = negated(booleanized(temp, MIN_TEMP/100, MAX_TEMP/100))


# schedule status write to file
def writeStatus():
    global scheduler
    writeStatusToFile()
    scheduler.enter(1, 1, writeStatus)

# start scheduler
# scheduler.enter(2, 1, writeStatus) ?
scheduler.run()

# wait until program gets killed
def sigterm_handler(_signo, _stack_frame):
    # Raises SystemExit(0):
    sys.exit(0)


signal.signal(signal.SIGTERM, sigterm_handler)

signal.pause()

