from threading import Thread
from inputs import get_gamepad
from thunder_remote import ControllerMapping


class AlarmClock(Thread):
    def __init__(self, callback, remote):
        Thread.__init__(self)
        self.callback = callback
        self.name = "alarm_clock"
        self.remote = remote

    def run(self):
        while self.remote.is_sleeping:
            events = get_gamepad()

            for _ in events:
                if _.code in ControllerMapping.WAKE_UP:
                    self.callback()
