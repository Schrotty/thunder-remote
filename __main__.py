from thunder_remote.RemoteControl import RemoteControl


def wake_up(remote):
    remote.control()


def sleep(remote):
    remote.sleep()


def any(code):
    print ">", code


if __name__ == "__main__":
    remote = RemoteControl(profile="madness", start_sleeping=True, debug_mode=False)
    if remote.is_available():
        remote.events.wake_up += lambda: wake_up(remote)
        remote.events.on_west += lambda code, state: sleep(remote)
        remote.events.on_any += lambda code, state: any(state)

        remote.activate()

    while True:
        remote.listen()
        if remote.is_sleeping:
            pass
