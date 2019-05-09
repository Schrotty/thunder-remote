from RemoteControl import RemoteControl


class MonsterBorgRemote:
    def __init__(self):
        pass
        # self.remote = RemoteControl()

        # if self.remote.is_available():
        #    self.remote.start()
        #    self.remote.events.on_stick_left_y += self.on_stick_left

    def calc_stick_percent(self, state):
        if state == 0:
            return 1.0

        i = ((100.0 / 255) * state) / 100
        if state > 128:
            return i * -1

        return i

    def on_stick_left(self, code, state):
        print self.calc_stick_percent(state)


mbr = MonsterBorgRemote()
print mbr.calc_stick_percent(0)
print mbr.calc_stick_percent(128)
print mbr.calc_stick_percent(255)
