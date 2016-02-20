__author__ = 'mcornelio'

import sys
import os

class synapse_exit_type(type):
    def __repr__(self):
        return 'Use exit() to exit synapse'

class exit(object):
    """Synapse Exit Class"""
    __metaclass__ = synapse_exit_type
    def __init__(self,status=1):
        os._exit(status)

if __name__ == '__main__':
    import synapse
    synapse.main()