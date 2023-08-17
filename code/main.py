"""
Driver code the Core Electronics Random Positioning Machine
Drive the two gimbal motors with random speed setpoints that update periodically

https://github.com/CoreElectronics/CE-Random-Positioning-Machine

Runs on a Raspberry Pi Pico

Requires the micropython-servo library - https://pypi.org/project/micropython-servo/
"""

import time
from servo import Servo
import math
from random import randrange, random

# Create our Servo object, assigning the
# GPIO pin connected the PWM wire of the servo
outer_servo = Servo(pin_id=16)
inner_servo = Servo(pin_id=15)
delay_ms = 100




def modified_sine_wave(amplitude, deadband, t):
    '''removes the dead band from the centre of the sinewave. useful for driving DC motors that stall at low speeds'''
    value = amplitude * math.sin(2 * math.pi * t)
    if abs(value) < deadband:
        value = math.copysign(deadband, value) if value != 0 else deadband
    return value

frequency = 0.05 # Hz
amplitude = 25 # servos accept "speeds" between 0 and 180. most of the speed change is at low amplitudes
dead_band = 12 # dead band around where the servo changes direction. Must be smaller than amplitude

duration = 10000 # time between speed changes
last_update_time = -duration

speed_inner = setpoint_inner = 0.5
speed_outer = setpoint_outer = 0.5

try:
    while True:
        # Periodically update the speed setpoint
        if time.ticks_ms() - duration > last_update_time:
            last_update_time = time.ticks_ms()
            setpoint_inner = random()
            setpoint_outer = random()

        # Update the current speed (-1 -> 1), moving towards the setpoint smoothly 
        speed_inner = speed_inner + 0.01 * (setpoint_inner - speed_inner)
        speed_outer = speed_outer + 0.01 * (setpoint_outer - speed_outer)
        
        # Convert speed (-1 -> 1) to a servo drive signal (angle 0 -> 180), and scale down to the desired amplitude.
        drive_inner = 90 + modified_sine_wave(amplitude, dead_band, speed_inner)
        drive_outer = 90 + modified_sine_wave(amplitude, dead_band, speed_outer)
        
        # Drive the continuous servos
        inner_servo.write(drive_inner)
        outer_servo.write(drive_outer)
        
        time.sleep_ms(delay_ms)

except Exception as e:
    print(e)
finally:
    outer_servo.off()
    inner_servo.off()