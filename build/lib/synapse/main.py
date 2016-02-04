__author__ = 'mcornelio'

import sys
from . import *

def exit(status=1):
    """Synapse Exit Routine"""
    print "good_bye"
    os._exit(status)

quit = exit

def main():
    sys.ps1, sys.ps2 = ('sc> ', '... ')
    print synapse.title
    print synapse.exit_prompt

    #sys.tracebacklimit = 0

    try:
        for file in sys.argv[1:]:
            print "execfile(%s)" % file
            execfile(file)
    finally:
        pass

if __name__ == '__main__':
    main()