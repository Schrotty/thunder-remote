from thunder_remote.DebugLevel import DebugLevel
from thunder_remote.RemoteControl import RemoteControl


def wake_up(rc):
    print "> WAKE UP"

    rc.wake()


def sleep(rc):
    print "> SLEEP"

    rc.sleep()


def kill_rc(rc):
    rc.deactivate()


def any(code):
    print "> [DEBUG] ANY EVENT"


def print_val(state):
    print ">", state


def percent_value((state, c, a)):
    mod = 1
    values = c

    if state not in values:
        values = a
        mod = -1

        if state not in values:
            return 0

    return (state - float(values[0])) / (values[values.__len__() - 1] - values[0]) * mod


if __name__ == "__main__":
    '''
    print "> XBOX VALUES"
    deadzone = 2000
    common = range(deadzone, 32001)
    alt = range(-32000, deadzone * -1)
    alt.reverse()

    print "> {0}".format(percent_value(32000, c=common, a=alt))
    print "> {0}".format(percent_value(0, c=common, a=alt))
    print "> {0}".format(percent_value(-32000, c=common, a=alt))

    print ">"
    print "> CHINA VALUES"

    common = range(0, 118)
    common.reverse()

    alt = range(138, 256)

    print "> {0}".format(percent_value(0, c=common, a=alt))
    print "> {0}".format(percent_value(128, c=common, a=alt))
    print "> {0}".format(percent_value(255, c=common, a=alt))
    '''

    remote = RemoteControl(profile="default", start_sleeping=True, debug_level=DebugLevel.BASIC)
    if remote.is_available():
        remote.events.wake_up += lambda: wake_up(remote)
        remote.events.on_west += lambda code, state: sleep(remote)
        remote.events.on_any += lambda code, state: any(state)
        remote.events.on_select += lambda code, state: kill_rc(remote)

        remote.events.on_stick_left_y += lambda code, state: print_val(state)
        remote.events.on_stick_right_y += lambda code, state: print_val(state)

        remote.activate()

    while remote.remote_online:
        remote.listen()
        if remote.is_sleeping:
            pass
