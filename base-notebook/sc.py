# install the apport exception handler if available
try:
    import apport_python_hook
except ImportError:
    pass
else:
    apport_python_hook.install()

try:
    import tensorflow as tf
except ImportError:
    pass
else:
    old_init = tf.Session.__init__


    def myinit(session_object, target='', graph=None, config=None):
        if config is None:
            config = tf.ConfigProto()
        config.gpu_options.allow_growth = True
        return old_init(session_object, target=target, graph=graph,
                        config=config)


    tf.Session.__init__ = myinit
