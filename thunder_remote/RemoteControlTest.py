from thunder_remote.RemoteControl import RemoteControl


def wake_up(remote):
    remote.is_sleeping = False

    print "> I'm awake!"


def sleep(remote):
    remote.sleep()


remote = RemoteControl()
if remote.is_available():
    remote.events.wake_up += lambda code, state: wake_up(remote)
    remote.events.on_west += lambda code, state: sleep(remote)

    remote.activate()

while True:
    if remote.is_sleeping:
        pass
    else:
        remote.wake()
