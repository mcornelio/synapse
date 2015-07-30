__author__ = 'mcornelio'

import sys
from . import *

def exit(status=1):
    """Nexus Exit Routine"""
    print "good_bye"
    os._exit(status)

quit = exit

def main():
    sys.ps1, sys.ps2 = ('sc> ', '... ')
    print nexus.title
    print nexus.exit_prompt

    #sys.tracebacklimit = 0

    try:
        for file in sys.argv[1:]:
            print "execfile(%s)" % file
            execfile(file)
    finally:
        pass

if __name__ == '__main__':
    main()