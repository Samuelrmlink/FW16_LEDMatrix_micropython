# Copyright (c) Samuel Hedrick <samuel@rml.ink>
# SPDX-License-Identifier: MIT

from machine import Pin
from neopixel import NeoPixel
import time
import random
import array

gpio_starting_pin = 8
led_update_counter = 0
low_power_brightness = 0.01
power_brightness_steps = [low_power_brightness, 0.05, 0.05, 0.045, 0.04, 0.035, 0.03, 0.02, 0.02, 0.02, 0.02, 0.018, 0.018, 0.015, 0.015, 0.015, 0]
loop_counter = 0

# Initialize LED strips
leds_per_strip = 36
leds_num_strips = 8
strip_pins = [Pin(i, Pin.OUT) for i in reversed(range(gpio_starting_pin, gpio_starting_pin + leds_num_strips))]
strips = [NeoPixel(led, 36) for led in strip_pins]

def set_led(index, color):
    # Determine which physical strip and which LED within that strip
    strip_index, led_index = divmod(index, leds_per_strip)
    if strip_index < len(strips):
        strips[strip_index][led_index] = color

def update_leds():
    # Update all LED strips
    for strip in strips:
        strip.write()

def set_led_debug(index, color):
    set_led(index, color)
    update_leds()

def set_all_leds(color):
    for x in range(0, 288):
        set_led(x, color)
    update_leds()

def scale_color(color, factor):
    return tuple(int(c * factor) for c in color)

def wheel(pos):
    # Generate rainbow colors across 0-255 positions.
    if pos < 85:
        return (pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return (255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return (0, pos * 3, 255 - pos * 3)
    
def twinkle_effect():
    twinkle_color = scale_color((255, 255, 255), 0.1)  # White

    # Turn off all LEDs
    set_all_leds((0, 0, 0))
    
    # Create lists for selected LEDs and their colors
    selected_leds = []
    selected_color = []
    
    # Randomly turn on a few groups
    num_twinkles = random.randint(1, 4)
    for j in range(num_twinkles):  # Number of twinkles
        led_index = random.randint(0, 287)  # 288 LEDs total, but indexing starts at 0
        selected_leds.append(led_index)
        selected_color.append(wheel((led_index * 256 // 288) & 255))
    
    for brightness in power_brightness_steps:
        for l in range(num_twinkles):
            scaled_color = scale_color(selected_color[l], brightness)
            set_led(selected_leds[l], scaled_color)
        
        # Update all LED strips
        for strip in strips:
            strip.write()
        
        time.sleep(0.04)
    time.sleep(1)

def twinkle_effect_2(max_lit=5):
    led_states = [(0, (0, 0, 0)) for _ in range(288)]  # (brightness, color) for each LED
    lit_leds = [0] * 288  # Track which LEDs are currently lit

    while True:
        # Count how many LEDs are currently lit
        currently_lit = sum(1 for brightness, _ in led_states if brightness > 0)

        for i in range(288):
            strip_index, led_index = divmod(i, leds_per_strip)

            if strip_index < len(strips):
                current_brightness, current_color = led_states[i]

                if current_brightness > 0:
                    # If the LED is on, proceed with normal behavior
                    if random.random() < 0.05:  # 5% chance to start dimming
                        current_brightness -= 0.01  # Start dimming
                        if current_brightness <= 0:  # If LED just turned off
                            lit_leds[i] = 0
                            currently_lit -= 1
                    else:
                        current_brightness = min(0.1, current_brightness + random.uniform(-0.005, 0.005))

                    # Ensure brightness doesn't go negative
                    current_brightness = max(0, current_brightness)

                    led_states[i] = (current_brightness, current_color)
                else:
                    # If the LED is off and we're under the limit, it might turn on
                    if currently_lit < max_lit and random.random() < 0.01:
                        current_color = wheel(random.randint(0, 255))  # New random color
                        current_brightness = 0.01  # Start brightening
                        lit_leds[i] = 1
                        currently_lit += 1
                        led_states[i] = (current_brightness, current_color)

                # Set the LED color directly on the strip
                strips[strip_index][led_index] = scale_color(current_color, current_brightness)

        # Update all LED strips
        for strip in strips:
            strip.write()
        time.sleep(0.02)  # Update speed, adjust for desired effect


brightness_animation_1 = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.5, 0.4, 0.7, 0.8, 0.9, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0.8, 0.7, 0.5, 0.4, 0.3, 0.2, 0.1, 0.1, 0]
        
def twinkle_effect_3(max_lit=5, brightness_scale = 0.08):
    led_states = [(0, (0, 0, 0)) for _ in range(288)]  # (brightness, color) for each LED
    lit_leds = [0] * 288  # Track which LEDs are currently lit
    animation_states = [0] * 288

    while True:
        # Count how many LEDs are currently lit
        currently_lit = sum(1 for brightness, _ in led_states if brightness > 0)

        for i in range(288):
            strip_index, led_index = divmod(i, leds_per_strip)

            if strip_index < len(strips):
                current_brightness, current_color = led_states[i]

                # Manage animation states
                animation_index = animation_states[i]
                if animation_index == 0:
                    # Consider enabling this LED (if we are under the max_lit limit)
                    if currently_lit < max_lit and random.random() < 0.0005:
                        current_color = wheel(random.randint(0, 255))  # New random color
                        animation_index = 1                    
                else:
                    if len(brightness_animation_1) == animation_index:
                        animation_index = 0
                    else:
                        animation_index += 1
                        
                current_brightness = brightness_animation_1[animation_index - 1]
                        
                # Stash the led_state for the next run
                led_states[i] = (current_brightness, current_color)
                animation_states[i] = animation_index

                # Set the LED color directly on the strip
                strips[strip_index][led_index] = scale_color(current_color, current_brightness * brightness_scale)

        # Update all LED strips
        for strip in strips:
            strip.write()
        time.sleep(0.02)  # Update speed, adjust for desired effect