from threading import Thread
from inputs import get_gamepad
from thunder_remote import ControllerMapping


class AlarmClock(Thread):
    """Alarm clock for waking a remote control

    Waits for an input and then reactivates the remote cntrol.
    """

    def __init__(self, callback, remote):
        """Create a new alarm clock and start it.

        :param callback: The method to call just before the clock dies.
        :param remote: The remote-control the clock watches.
        """
        Thread.__init__(self)
        self.callback = callback
        self.daemon = True
        self.name = "alarm_clock"
        self.remote = remote
        self.start()

    def run(self):
        """The method which is running on start up.

        :return: void
        """
        while self.remote.is_sleeping:
            events = get_gamepad()

            for _ in events:
                if _.code in ControllerMapping.WAKE_UP:
                    self.callback()
