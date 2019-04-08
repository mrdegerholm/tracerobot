from tracerobot.listener import Listener

# Singleton listener, required for decorators to work
LISTENER = Listener()

# Allow using listener methods from module root,
# e.g. tracerobot.start_suite()
for name in LISTENER.ACTIONS:
    globals()[name] = getattr(LISTENER, name)
