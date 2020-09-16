#!/usr/bin/env python

# Copyright (c) 2019 Computer Vision Center (CVC) at the Universitat Autonoma de
# Barcelona (UAB).
#
# This work is licensed under the terms of the MIT license.
# For a copy, see <https://opensource.org/licenses/MIT>.

# Allows controlling a vehicle with a keyboard. For a simpler and more
# documented example, please take a look at tutorial.py.

"""
Welcome to CARLA manual control.

Use ARROWS or WASD keys for control.

    W            : throttle
    S            : brake
    A/D          : steer left/right
    Q            : toggle reverse
    Space        : hand-brake
    P            : toggle autopilot
    M            : toggle manual transmission
    ,/.          : gear up/down

    L            : toggle next light type
    SHIFT + L    : toggle high beam
    Z/X          : toggle right/left blinker
    I            : toggle interior light

    TAB          : change sensor position
    ` or N       : next sensor
    [1-9]        : change to sensor [1-9]
    G            : toggle radar visualization
    C            : change weather (Shift+C reverse)
    Backspace    : change vehicle

    R            : toggle recording images to disk

    CTRL + R     : toggle recording of simulation (replacing any previous)
    CTRL + P     : start replaying last recorded simulation
    CTRL + +     : increments the start time of the replay by 1 second (+SHIFT = 10 seconds)
    CTRL + -     : decrements the start time of the replay by 1 second (+SHIFT = 10 seconds)

    F1           : toggle HUD
    H/?          : toggle help
    ESC          : quit
"""

from __future__ import print_function

import glob
import os
import sys
import random
import time
import numpy as np
import cv2

try:
    sys.path.append(glob.glob('../../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla
IM_WIDTH = 640
IM_HEIGHT = 480


def process_img(image):
    i = np.array(image.raw_data)
    print(i.shape)
    i2 = i.reshape((IM_HEIGHT,IM_WIDTH,4))
    i3 = i2[:,:,:3]
    cv2.imshow("",i3)
    cv2.waitKey(1)
    return i3/255.0

actor_list=[]
try:
    client = carla.Client("localhost",2000)
    client.set_timeout(5.0)

    world = client.get_world()
    blueprint_library = world.get_blueprint_library()

    bp = blueprint_library.filter("model3")[0]
    print(bp)

    spawn_point = random.choice(world.get_map().get_spawn_points())

    vehicle = world.spawn_actor(bp,spawn_point)
    #vehicle.set_autopilot(True)

    vehicle.apply_control(carla.VehicleControl(throttle=1.0,steer =0.0))
    actor_list.append(vehicle)

    #camera
    cam_bp = blueprint_library.find("sensor.camera.rgb")
    cam_bp.set_attribute("image_size_x",f"{IM_WIDTH}")
    cam_bp.set_attribute("image_size_y", f"{IM_HEIGHT}")
    cam_bp.set_attribute("fov","110")

    spawn_point = carla.Transform(carla.Location(x=2.5,z=0.7))

    sensor = world.spawn_actor(cam_bp,spawn_point,attach_to=vehicle)
    actor_list.append(sensor)
    sensor.listen(lambda data:process_img(data))

    time.sleep(10)

finally:
    for actor in actor_list:
        actor.destroy()
        print("all cleaned up!")