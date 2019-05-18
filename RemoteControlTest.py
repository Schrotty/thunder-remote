from thunder_remote.RemoteControl import RemoteControl


def wake_up(remote):
    remote.control()


def sleep(remote):
    remote.sleep()


def any(code):
    print ">", code


remote = RemoteControl(start_sleeping=True, with_thread=False, debug_mode=True)
if remote.is_available():
    remote.events.wake_up += lambda: wake_up(remote)
    remote.events.on_west += lambda code, state: sleep(remote)
    remote.events.on_any += lambda code, state: any(state)

    remote.activate()

while True:
    if remote.is_sleeping:
        pass
