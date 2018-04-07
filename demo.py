import time
from robot import Robot

r = Robot(wait_for_start_button=False)

while True:
    print({'mode': r.mode, 'zone': r.zone})
    time.sleep(1)
