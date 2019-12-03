from tracerobot.listener import Listener

# Singleton listener, required for decorators to work
LISTENER = Listener()

def tracerobot_init(tracerobot_config=None):
    LISTENER.configure(tracerobot_config)
    LISTENER.register_to_module_namespace(globals())
