import os
import csv

from multiprocessing import Process, Queue
from inputs import devices, get_gamepad
from RemoteControlEvents import RemoteControlEvents
from thunder_remote.ControllerMapping import ControllerMapping

test_bool = False


class RemoteControl:
    event_queue = Queue()

    remote_online = False
    debug = False
    is_sleeping = False

    def __init__(self, profile="default", debug_mode=False, profiles_path='profiles', start_sleeping=False):
        RemoteControl.debug = debug_mode
        RemoteControl.is_sleeping = start_sleeping

        self.events = RemoteControlEvents()
        self.remote_online = False
        self.tries_loading_profile = 1
        self.profile = profile
        self.controller_name = "Unknown"
        self.thread = None
        self.remote_found = True
        self.profile_loaded = False
        self.profiles_path = profiles_path
        self.start_sleeping = start_sleeping
        self.alarm = None

        print "> INIT REMOTE CONTROL"
        print "> Looking for gamepad..."
        if not devices.gamepads:
            self.remote_found = False
            print "> No gamepad detected!"
        else:
            print "> Gamepad detected!"

        print ">"
        print "> Loading profile '" + self.profile + "'"

        controller_mapping = self.load_profile()
        if not self.profile_loaded:
            print "> Unable to load a profile!"
        else:
            print "> Profile for '" + self.controller_name + "' loaded!"

        print ">"

        if self.remote_found and self.profile_loaded:
            self.proc = Process(group=None, target=RemoteControl.control, name="thunder_remote",
                                args=(RemoteControl.event_queue, start_sleeping, debug_mode, controller_mapping))

            print "> Remote control is now available!"
        else:
            print "> Remote control is unavailable!"

    def activate(self):
        global test_bool
        test_bool = True

        if self.remote_online:
            print "> Remote control already activated!"
        else:
            self.remote_online = True
            if self.start_sleeping:
                self.sleep()

            self.proc.start()

    def deactivate(self):
        self.remote_online = False

    def wake(self):
        if self.is_sleeping:
            self.is_sleeping = False

            self.events.wake_up()

    def sleep(self):
        if not RemoteControl.is_sleeping:
            RemoteControl.is_sleeping = True

    def listen(self):
        if not RemoteControl.event_queue.empty():
            print RemoteControl.event_queue.get()
            RemoteControl.event_queue.empty()

    def load_profile(self):

        controller_mapping = ControllerMapping()

        try:
            path = self.profiles_path + '/' + self.profile + '.csv'
            if RemoteControl.debug:
                print ">", path

            if self.profiles_path is 'profiles':
                path = os.path.dirname(os.path.realpath(__file__)) + '/' + path

            if not os.path.isfile(path):
                print "> Profile '" + self.profile + "' not found!"
                return

            self.tries_loading_profile += 1
            with open(path, 'r') as csvFile:
                reader = csv.DictReader(csvFile)

                for profile in reader:
                    # CONTROLLER NAME
                    self.controller_name = profile['CONTROLLER']

                    # LEFT BUTTONS
                    controller_mapping.BTN_NORTH = profile['BTN_NORTH']
                    controller_mapping.BTN_EAST = profile['BTN_EAST']
                    controller_mapping.BTN_SOUTH = profile['BTN_SOUTH']
                    controller_mapping.BTN_WEST = profile['BTN_WEST']

                    # START AND SELECT
                    controller_mapping.START = profile['START']
                    controller_mapping.SELECT = profile['SELECT']

                    # CROSS
                    controller_mapping.CROSS_Y = profile['CROSS_Y']
                    controller_mapping.CROSS_X = profile['CROSS_X']

                    # STICK R & STICK L
                    controller_mapping.STICK_RIGHT_Y = profile['STICK_R_Y']
                    controller_mapping.STICK_RIGHT_X = profile['STICK_R_X']
                    controller_mapping.STICK_LEFT_Y = profile['STICK_L_Y']
                    controller_mapping.STICK_LEFT_X = profile['STICK_L_X']

                    # TRIGGER AND SHOULDER
                    controller_mapping.TRIGGER_R = profile['TRIGGER_R']
                    controller_mapping.SHOULDR_R = profile['SHOULDER_R']
                    controller_mapping.TRIGGER_L = profile['TRIGGER_L']
                    controller_mapping.SHOULDR_L = profile['SHOULDER_L']

                    # THUMBS
                    controller_mapping.THUMB_R = profile['THUMB_R']
                    controller_mapping.THUMB_L = profile['THUMB_L']

                    # WAKE UP
                    controller_mapping.WAKE_UP = profile['WAKE_UP']

                    # STICK VALUES
                    controller_mapping.STICK_CENTER = int(profile['STICK_CENTER'])
                    controller_mapping.STICK_L_MAX = int(profile['STICK_L_MAX'])
                    controller_mapping.STICK_L_MIN = int(profile['STICK_L_MIN'])
                    controller_mapping.STICK_R_MAX = int(profile['STICK_R_MAX'])
                    controller_mapping.STICK_R_MIN = int(profile['STICK_R_MIN'])

                    # STICK DEAD ZONES
                    controller_mapping.STICK_L_DEAD = int(profile['STICK_L_DEAD'])
                    controller_mapping.STICK_R_DEAD = int(profile['STICK_R_DEAD'])

                    self.profile_loaded = True

        except (KeyError, IOError):
            print "> Invalid profile! Switching back to default!"
            self.profile = "default"
            if self.tries_loading_profile == 1:
                self.load_profile()
            else:
                self.profile_loaded = False

        return controller_mapping

    def is_available(self):
        return self.remote_found

    @classmethod
    def percent_value(cls, state):
        max_val = 0
        min_val = 128.0

        if 255 >= state > 128:
            max_val = 255.0
            min_val = 128.0

        val = round((state - min_val) / (max_val - min_val), 2)
        return val * -1 if state >= 128 else val

    @classmethod
    def control(cls, queue, sleeping, debug, controller_mapping):
        is_running = True
        is_sleeping = sleeping
        is_debug = debug

        prev_cross_state = None

        while is_running:
            events = get_gamepad()
            for event in events:
                code = event.code
                state = event.state

                if not is_sleeping:
                    if is_debug:
                        events.on_any(code, state)

                    # BUTTON RELEASED
                    if state == 0:

                        # RIGHT BUTTONS
                        if code in controller_mapping.BTN_NORTH:
                            # events.on_north(code, state)
                            queue.put(events.on_north, code, state)

                        if code in controller_mapping.BTN_EAST:
                            events.on_east(code, state)

                        if code in controller_mapping.BTN_SOUTH:
                            events.on_south(code, state)

                        if code in controller_mapping.BTN_WEST:
                            events.on_west(code, state)

                        # START AND SELECT
                        if code in controller_mapping.START:
                            # events.on_start(code, state)
                            queue.put(['on_start', code, state])

                        if code in controller_mapping.SELECT:
                            events.on_select(code, state)

                    # CONTROLLER CROSS
                    if code in controller_mapping.CROSS_Y or code in controller_mapping.CROSS_X:

                        # CROSS NORTH AND SOUTH
                        if code in controller_mapping.CROSS_Y:
                            if state == -1:
                                events.on_cross_north_p(code, state)
                                prev_cross_state = -1

                            if state == 1:
                                events.on_cross_south_p(code, state)
                                prev_cross_state = 1

                            if state == 0:
                                if prev_cross_state == 1:
                                    events.on_cross_south_r(code, state)
                                else:
                                    events.on_cross_north_r(code, state)

                        # CROSS WEST AND EAST
                        if code in controller_mapping.CROSS_X:
                            if state == -1:
                                events.on_cross_west_p(code, state)
                                prev_cross_state = -1

                            if state == 1:
                                events.on_cross_east_p(code, state)
                                prev_cross_state = 1

                            if state == 0:
                                if prev_cross_state == 1:
                                    events.on_cross_east_r(code, state)
                                else:
                                    events.on_cross_west_r(code, state)

                    # TRIGGERS
                    if code in controller_mapping.TRIGGER_L or code in controller_mapping.TRIGGER_R:

                        # LEFT TRIGGER
                        if code in controller_mapping.TRIGGER_L:
                            events.on_trigger_left(code, state)

                        # RIGHT TRIGGER
                        if code in controller_mapping.TRIGGER_R:
                            events.on_trigger_right(code, state)

                    # SHOULDERS
                    if code in controller_mapping.SHOULDR_L or code in controller_mapping.SHOULDR_R:

                        # LEFT SHOULDER
                        if code in controller_mapping.SHOULDR_L:

                            # ON RELEASE
                            if state == 0:
                                events.on_shoulder_left_r(code, state)

                            # WHEN PRESSED
                            if state == 1:
                                events.on_shoulder_left_p(code, state)

                        # RIGHT SHOULDER
                        if code in controller_mapping.SHOULDR_R:

                            # ON RELEASE
                            if state == 0:
                                events.on_shoulder_right_r(code, state)

                            # WHEN PRESSED
                            if state == 1:
                                events.on_shoulder_right_p(code, state)

                    # LEFT STICK
                    if code in controller_mapping.STICK_LEFT_X or code in controller_mapping.STICK_LEFT_Y:

                        # ANY MOVEMENT
                        events.on_stick_left(code, state)

                        # X-AXIS
                        if code in controller_mapping.STICK_LEFT_X:

                            # ANY X-AXIS MOVEMENT
                            events.on_stick_left_x(code, RemoteControl.percent_value(state))

                            # MOVEMENT EAST
                            if state >= controller_mapping.STICK_CENTER:
                                events.on_stick_left_east(code, RemoteControl.percent_value(state))

                            # MOVEMENT WEST
                            if state < 255:
                                events.on_stick_left_west(code, RemoteControl.percent_value(state))

                        # Y-AXIS
                        if code in controller_mapping.STICK_LEFT_Y:

                            # ANY Y-AXIS MOVEMENT
                            events.on_stick_left_y(code, RemoteControl.percent_value(state))

                            # MOVEMENT NORTH
                            if state >= controller_mapping.STICK_CENTER:
                                events.on_stick_left_north(code, RemoteControl.percent_value(state))

                            # MOVEMENT SOUTH
                            if state < 255:
                                events.on_stick_left_south(code, RemoteControl.percent_value(state))

                    # RIGHT STICK
                    if code in controller_mapping.STICK_RIGHT_X or code in controller_mapping.STICK_RIGHT_Y:

                        # ANY MOVEMENT
                        events.on_stick_right(code, state)

                        # X-AXIS
                        if code in controller_mapping.STICK_RIGHT_X:

                            # ANY X-AXIS MOVEMENT
                            events.on_stick_right_x(code, RemoteControl.percent_value(state))

                            # MOVEMENT EAST
                            if state >= controller_mapping.STICK_CENTER:
                                events.on_stick_right_east(code, RemoteControl.percent_value(state))

                            # MOVEMENT WEST
                            if state < 255:
                                events.on_stick_right_west(code, RemoteControl.percent_value(state))

                        # Y-AXIS
                        if code in controller_mapping.STICK_RIGHT_Y:

                            # ANY Y-AXIS MOVEMENT
                            events.on_stick_right_y(code, RemoteControl.percent_value(state))

                            # MOVEMENT NORTH
                            if state >= controller_mapping.STICK_CENTER:
                                events.on_stick_right_north(code, RemoteControl.percent_value(state))

                            # MOVEMENT SOUTH
                            if state < 255:
                                events.on_stick_right_south(code, RemoteControl.percent_value(state))
                else:
                    if code in controller_mapping.WAKE_UP:
                        is_sleeping = False
                        queue.put([is_sleeping])
