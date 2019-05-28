from thunder_remote.RemoteControl import RemoteControl


def say_hello():
    print "> Hello there!"


def wake_up(rc):
    print "> WAKE UP"

    rc.wake()


def sleep(rc):
    print "> SLEEP"

    rc.sleep()


def kill_rc(rc):
    rc.deactivate()


def any(code):
    print ">", code


def print_val(state):
    print ">", state


if __name__ == "__main__":
    remote = RemoteControl(profile="default", start_sleeping=True, debug_mode=False)
    if remote.is_available():
        remote.events.wake_up += lambda: wake_up(remote)
        remote.events.on_west += lambda code, state: sleep(remote)
        remote.events.on_any += lambda code, state: any(state)
        remote.events.on_select += lambda code, state: kill_rc(remote)
        remote.events.on_north += lambda code, state: say_hello()

        remote.events.on_stick_left_y += lambda code, state: print_val(state)
        remote.events.on_stick_right_y += lambda code, state: print_val(state)

        remote.activate()

    while remote.remote_online:
        remote.listen()
        if remote.is_sleeping:
            pass
