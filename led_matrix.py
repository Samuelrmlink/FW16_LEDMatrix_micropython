from machine import Pin
from neopixel import NeoPixel
import time
import random

gpio_starting_pin = 8
led_update_counter = 0
low_power_brightness = 0.01
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
    twinkle_color = scale_color((255, 255, 255),0.1)  # White

    # Turn off all LEDs
    set_all_leds((0, 0, 0))
    
    # Randomly turn on a few groups
    for _ in range(random.randint(1, 4)):  # Number of twinkles
        group_index = random.randint(0, 288 - 1)
        color = wheel((group_index * 256 // 288) & 255)
        scaled_color = scale_color(color, low_power_brightness)
        set_led(group_index, scaled_color)
    update_leds()
    print("w")
    time.sleep(1)

while True:
    #rainbow_cycle()
    twinkle_effect()
        
#for x in range(0, 288):
#    set_led(x, (2, 0, 0))
#    update_leds()
#    time.sleep_ms(0)


#pin = Pin(15, Pin.OUT)
#np = NeoPixel(pin, 36)
#for x in range(0, 36):
#    np[x] = (0, 0, 0)
#    np.write()