import os
import csv
import threading

from thunder_remote import ControllerMapping
from inputs import devices, get_gamepad
from RemoteControlEvents import RemoteControlEvents
from thunder_remote.AlarmClock import AlarmClock


class RemoteControl:
    def __init__(self, profile="default", debug_mode=False, with_thread=True,
                 profiles_path='profiles', start_sleeping=False):
        self.events = RemoteControlEvents()

        self.tries_loading_profile = 1
        self.profile = profile
        self.controller_name = "Unknown"
        self.thread = None
        self.remote_found = True
        self.remote_online = False
        self.debug_mode = debug_mode
        self.profile_loaded = False
        self.with_thread = with_thread
        self.is_sleeping = False
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

        self.load_profile()
        if not self.profile_loaded:
            print "> Unable to load a profile!"
        else:
            print "> Profile for '" + self.controller_name + "' loaded!"

        print ">"

        if self.remote_found and self.profile_loaded:
            print "> Remote control is now available!"
        else:
            print "> Remote control is unavailable!"

    def activate(self):
        if self.remote_online:
            print "> Remote control already activated!"
        else:
            self.remote_online = True
            if not self.with_thread:
                print "> Running in main thread"
            else:
                self.thread = threading.Thread(target=self.control, args=())
                self.thread.name = "remote_control"
                self.thread.start()

            if self.start_sleeping:
                self.sleep()

    def deactivate(self):
        self.remote_online = False
        print "> Stop remote control"
        if not self.with_thread:
            return

        self.thread.join()

    def wake(self):
        if self.is_sleeping:
            self.is_sleeping = False
            self.alarm.join()

            self.events.wake_up()

    def sleep(self):
        if not self.is_sleeping:
            self.is_sleeping = True
            self.alarm = AlarmClock.launch_with_callback(callback=self.wake())

            print "> Activated sleep mode! Press '" + str(ControllerMapping.WAKE_UP) + "' for deactivating!"

    def percent_value(self, state):
        """

        :param state:
        :return:
        """
        max_val = 0
        min_val = 128.0

        if 255 >= state > 128:
            max_val = 255.0
            min_val = 128.0

        val = round((state - min_val) / (max_val - min_val), 2)
        return val * -1 if state >= 128 else val

    def load_profile(self):
        try:
            path = self.profiles_path + '/' + self.profile + '.csv'
            if self.debug_mode:
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
                    ControllerMapping.BTN_NORTH = profile['BTN_NORTH']
                    ControllerMapping.BTN_EAST = profile['BTN_EAST']
                    ControllerMapping.BTN_SOUTH = profile['BTN_SOUTH']
                    ControllerMapping.BTN_WEST = profile['BTN_WEST']

                    # START AND SELECT
                    ControllerMapping.START = profile['START']
                    ControllerMapping.SELECT = profile['SELECT']

                    # CROSS
                    ControllerMapping.CROSS_Y = profile['CROSS_Y']
                    ControllerMapping.CROSS_X = profile['CROSS_X']

                    # STICK R & STICK L
                    ControllerMapping.STICK_RIGHT_Y = profile['STICK_R_Y']
                    ControllerMapping.STICK_RIGHT_X = profile['STICK_R_X']
                    ControllerMapping.STICK_LEFT_Y = profile['STICK_L_Y']
                    ControllerMapping.STICK_LEFT_X = profile['STICK_L_X']

                    # TRIGGER AND SHOULDER
                    ControllerMapping.TRIGGER_R = profile['TRIGGER_R']
                    ControllerMapping.SHOULDR_R = profile['SHOULDER_R']
                    ControllerMapping.TRIGGER_L = profile['TRIGGER_L']
                    ControllerMapping.SHOULDR_L = profile['SHOULDER_L']

                    # THUMBS
                    ControllerMapping.THUMB_R = profile['THUMB_R']
                    ControllerMapping.THUMB_L = profile['THUMB_L']

                    # WAKE UP
                    ControllerMapping.WAKE_UP = profile['WAKE_UP']

                    # STICK VALUES
                    ControllerMapping.STICK_CENTER = int(profile['STICK_CENTER'])
                    ControllerMapping.STICK_L_MAX = int(profile['STICK_L_MAX'])
                    ControllerMapping.STICK_L_MIN = int(profile['STICK_L_MIN'])
                    ControllerMapping.STICK_R_MAX = int(profile['STICK_R_MAX'])
                    ControllerMapping.STICK_R_MIN = int(profile['STICK_R_MIN'])

                    # STICK DEAD ZONES
                    ControllerMapping.STICK_L_DEAD = int(profile['STICK_L_DEAD'])
                    ControllerMapping.STICK_R_DEAD = int(profile['STICK_R_DEAD'])

                    self.profile_loaded = True

        except (KeyError, IOError):
            print "> Invalid profile! Switching back to default!"
            self.profile = "default"
            if self.tries_loading_profile == 1:
                self.load_profile()
            else:
                self.profile_loaded = False

    def is_available(self):
        return self.remote_found

    def control(self):
        prev_cross_state = None

        while self.remote_online:
            events = get_gamepad()

            for event in events:
                code = event.code
                state = event.state

                if self.debug_mode:
                    self.events.on_any(code, state)

                # BUTTON RELEASED
                if state == 0:

                    # RIGHT BUTTONS
                    if code in ControllerMapping.BTN_NORTH:
                        self.events.on_north(code, state)

                    if code in ControllerMapping.BTN_EAST:
                        self.events.on_east(code, state)

                    if code in ControllerMapping.BTN_SOUTH:
                        self.events.on_south(code, state)

                    if code in ControllerMapping.BTN_WEST:
                        self.events.on_west(code, state)

                    # START AND SELECT
                    if code in ControllerMapping.START:
                        self.events.on_start(code, state)

                    if code in ControllerMapping.SELECT:
                        self.events.on_select(code, state)

                # CONTROLLER CROSS
                if code in ControllerMapping.CROSS_Y or code in ControllerMapping.CROSS_X:

                    # CROSS NORTH AND SOUTH
                    if code in ControllerMapping.CROSS_Y:
                        if state == -1:
                            self.events.on_cross_north_p(code, state)
                            prev_cross_state = -1

                        if state == 1:
                            self.events.on_cross_south_p(code, state)
                            prev_cross_state = 1

                        if state == 0:
                            if prev_cross_state == 1:
                                self.events.on_cross_south_r(code, state)
                            else:
                                self.events.on_cross_north_r(code, state)

                    # CROSS WEST AND EAST
                    if code in ControllerMapping.CROSS_X:
                        if state == -1:
                            self.events.on_cross_west_p(code, state)
                            prev_cross_state = -1

                        if state == 1:
                            self.events.on_cross_east_p(code, state)
                            prev_cross_state = 1

                        if state == 0:
                            if prev_cross_state == 1:
                                self.events.on_cross_east_r(code, state)
                            else:
                                self.events.on_cross_west_r(code, state)

                # TRIGGERS
                if code in ControllerMapping.TRIGGER_L or code in ControllerMapping.TRIGGER_R:

                    # LEFT TRIGGER
                    if code in ControllerMapping.TRIGGER_L:
                        self.events.on_trigger_left(code, state)

                    # RIGHT TRIGGER
                    if code in ControllerMapping.TRIGGER_R:
                        self.events.on_trigger_right(code, state)

                # SHOULDERS
                if code in ControllerMapping.SHOULDR_L or code in ControllerMapping.SHOULDR_R:

                    # LEFT SHOULDER
                    if code in ControllerMapping.SHOULDR_L:

                        # ON RELEASE
                        if state == 0:
                            self.events.on_shoulder_left_r(code, state)

                        # WHEN PRESSED
                        if state == 1:
                            self.events.on_shoulder_left_p(code, state)

                    # RIGHT SHOULDER
                    if code in ControllerMapping.SHOULDR_R:

                        # ON RELEASE
                        if state == 0:
                            self.events.on_shoulder_right_r(code, state)

                        # WHEN PRESSED
                        if state == 1:
                            self.events.on_shoulder_right_p(code, state)

                # LEFT STICK
                if code in ControllerMapping.STICK_LEFT_X or code in ControllerMapping.STICK_LEFT_Y:

                    # ANY MOVEMENT
                    self.events.on_stick_left(code, state)

                    # X-AXIS
                    if code in ControllerMapping.STICK_LEFT_X:

                        # ANY X-AXIS MOVEMENT
                        self.events.on_stick_left_x(code, self.percent_value(state))

                        # MOVEMENT EAST
                        if state >= ControllerMapping.STICK_CENTER:
                            self.events.on_stick_left_east(code, self.percent_value(state))

                        # MOVEMENT WEST
                        if state < 255:
                            self.events.on_stick_left_west(code, self.percent_value(state))

                    # Y-AXIS
                    if code in ControllerMapping.STICK_LEFT_Y:

                        # ANY Y-AXIS MOVEMENT
                        self.events.on_stick_left_y(code, self.percent_value(state))

                        # MOVEMENT NORTH
                        if state >= ControllerMapping.STICK_CENTER:
                            self.events.on_stick_left_north(code, self.percent_value(state))

                        # MOVEMENT SOUTH
                        if state < 255:
                            self.events.on_stick_left_south(code, self.percent_value(state))

                # RIGHT STICK
                if code in ControllerMapping.STICK_RIGHT_X or code in ControllerMapping.STICK_RIGHT_Y:

                    # ANY MOVEMENT
                    self.events.on_stick_right(code, state)

                    # X-AXIS
                    if code in ControllerMapping.STICK_RIGHT_X:

                        # ANY X-AXIS MOVEMENT
                        self.events.on_stick_right_x(code, self.percent_value(state))

                        # MOVEMENT EAST
                        if state >= ControllerMapping.STICK_CENTER:
                            self.events.on_stick_right_east(code, self.percent_value(state))

                        # MOVEMENT WEST
                        if state < 255:
                            self.events.on_stick_right_west(code, self.percent_value(state))

                    # Y-AXIS
                    if code in ControllerMapping.STICK_RIGHT_Y:

                        # ANY Y-AXIS MOVEMENT
                        self.events.on_stick_right_y(code, self.percent_value(state))

                        # MOVEMENT NORTH
                        if state >= ControllerMapping.STICK_CENTER:
                            self.events.on_stick_right_north(code, self.percent_value(state))

                        # MOVEMENT SOUTH
                        if state < 255:
                            self.events.on_stick_right_south(code, self.percent_value(state))
