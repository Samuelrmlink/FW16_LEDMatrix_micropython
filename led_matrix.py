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

def set_all_leds(color):
    for x in range(0, 288):
        set_led(x, color)
    update_leds()

def scale_color(color, factor):
    return tuple(int(c * factor) for c in color)

def interpolate_color(start_color, end_color, factor):
    return tuple(int(start_color[i] + factor * (end_color[i] - start_color[i])) for i in range(3))

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
    
def rainbow_cycle(wait=0.01):
    global loop_counter

    loop_counter %= 256

    for i in range(0, 288):
        pixel_index = (i * 256 // 288) + loop_counter
        color = wheel(pixel_index & 255)
        scaled_color = scale_color(color, low_power_brightness)
        set_led(i, scaled_color)
    update_leds()
    print("w")
    time.sleep(wait)
    loop_counter += 1
    print(loop_counter)

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
        update_leds()
        time.sleep(0.04)
    time.sleep(1)


def twinkle_effect_async_randomtimeframe():
    led_states = [(0, (0, 0, 0)) for _ in range(288)]  # (brightness, color) for each LED
    while True:
        for i in range(288):
            # Determine which strip and LED
            strip_index, led_index = divmod(i, leds_per_strip)
            if strip_index < len(strips):
                current_brightness, current_color = led_states[i]
                if random.random() < 0.002:  # 1% chance to start twinkling
                    if current_brightness == 0:  # If LED is off
                        current_color = wheel(random.randint(0, 255))  # New random color
                        current_brightness = 0.01  # Start brightening
                    elif current_brightness >= 0.1:  # If LED is on
                        current_brightness = 0  # Turn off
                    else:
                        current_brightness += 0.01  # Continue brightening
                elif current_brightness > 0:
                    if random.random() < 0.15:  # 5% chance to start dimming
                        current_brightness -= 0.01  # Start dimming
                    else:
                        # Keep the same brightness or very slightly adjust for natural flicker
                        current_brightness = min(0.1, current_brightness + random.uniform(-0.005, 0.005))
                # Ensure brightness doesn't go negative
                current_brightness = max(0, current_brightness)
                led_states[i] = (current_brightness, current_color)
                # Set the LED color directly on the strip
                strips[strip_index][led_index] = scale_color(current_color, current_brightness)
        # Update all LED strips
        for strip in strips:
            strip.write()
        time.sleep(0.1)  # Update speed, adjust for desired effect

def twinkle_effect_async():
    led_states = [(0, (0, 0, 0)) for _ in range(288)]  # (brightness, color) for each LED
    while True:
        for i in range(288):
            # Determine which strip and LED
            strip_index, led_index = divmod(i, leds_per_strip)
            if strip_index < len(strips):
                current_brightness, current_color = led_states[i]
                if random.random() < 0.002:  # 1% chance to start twinkling
                    if current_brightness == 0:  # If LED is off
                        current_color = wheel(random.randint(0, 255))  # New random color
                        current_brightness = 0.01  # Start brightening
                    elif current_brightness >= 0.1:  # If LED is on
                        current_brightness = 0  # Turn off
                    else:
                        current_brightness += 0.01  # Continue brightening
                elif current_brightness > 0:
                    if random.random() < 0.15:  # 5% chance to start dimming
                        current_brightness -= 0.01  # Start dimming
                    else:
                        # Keep the same brightness or very slightly adjust for natural flicker
                        current_brightness = min(0.1, current_brightness + random.uniform(-0.005, 0.005))
                # Ensure brightness doesn't go negative
                current_brightness = max(0, current_brightness)
                led_states[i] = (current_brightness, current_color)
                # Set the LED color directly on the strip
                strips[strip_index][led_index] = scale_color(current_color, current_brightness)
        # Update all LED strips
        for strip in strips:
            strip.write()
        time.sleep(0.1)  # Update speed, adjust for desired effect

def twinkle_effect_async2(max_lit=5):
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


def twinkle_effect_async3(max_lit=5):
    led_states = [(0, 0, (0, 0, 0)) for _ in range(288)]  # (brightness_stage, timer, color) for each LED
    lit_leds = set()

    def update_led_state(led_state):
        stage, timer, color = led_state
        if stage > 0:  # If LED is on
            if timer <= 0:
                if stage < len(power_brightness_steps):
                    stage += 1
                    timer = 0.04  # Set timer for next stage
                else:
                    stage = 0  # Turn off LED
                    timer = 0  # Reset timer
            else:
                timer -= 0.01  # Decrease timer by sleep time
        return stage, timer, color

    while True:
        # Count currently lit LEDs
        currently_lit = len(lit_leds)

        for i in range(288):
            strip_index, led_index = divmod(i, leds_per_strip)

            if strip_index < len(strips):
                stage, timer, current_color = led_states[i]

                if i in lit_leds:  # If this LED is currently lit
                    new_stage, new_timer, _ = update_led_state(led_states[i])
                    led_states[i] = (new_stage, new_timer, current_color)

                    if new_stage == 0:  # If the LED has just turned off
                        lit_leds.remove(i)
                else:  # If this LED is off
                    if currently_lit < max_lit and random.random() < 0.01:  # Chance to turn on if we can
                        current_color = wheel(random.randint(0, 255))
                        led_states[i] = (1, 0.04, current_color)  # Start at stage 1, set timer for first step
                        lit_leds.add(i)
                        currently_lit += 1

                brightness = power_brightness_steps[stage-1] if stage > 0 else 0
                strips[strip_index][led_index] = scale_color(current_color, brightness)

        # Update all LED strips
        for strip in strips:
            strip.write()

        time.sleep(0.01)  # Update rate, we manage the 40ms within the function
        
animation1 = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.5, 0.4, 0.7, 0.8, 0.9, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0.8, 0.7, 0.5, 0.4, 0.3, 0.2, 0.1, 0.1, 0]
        
def twinkle_effect_random(max_lit=5, brightness_scale = 0.08):
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
                    if len(animation1) == animation_index:
                        animation_index = 0
                    else:
                        animation_index += 1
                        
                current_brightness = animation1[animation_index - 1]
                        
                # Stash the led_state for the next run
                led_states[i] = (current_brightness, current_color)
                animation_states[i] = animation_index

                # Set the LED color directly on the strip
                strips[strip_index][led_index] = scale_color(current_color, current_brightness * brightness_scale)

        # Update all LED strips
        for strip in strips:
            strip.write()
        time.sleep(0.02)  # Update speed, adjust for desired effect


while True:
    #rainbow_cycle()
    #twinkle_effect_async3()
    twinkle_effect_random()
