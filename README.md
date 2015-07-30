# synapse
## Intro
Python-based cross platform cooperative computing framework.
Cooperating synapse applications transparently communicate
with one another using cell-like dictionaries.

Each synapse application can work independently and need
not be aware of other synapse applications that need to
access its cells dictionary.

##Installation
python setup.py sdist

##Usage
Synapse applications can be used for any purpose or the
synapse package can be used as a communication and data
sharing framework for any application that would like to
use the cell framework.

This section outlines the most basic usage of the package:
cooperating client and server synapse applications.

To start an interactive "synapse" application:

    python -i -m synapse.main

A synapse interactive application will be started and
an interactive prompt will be displayed.

    Synapse Console Interface v1.0
    Use exit() plus Return to exit.
    sc>

At this point, you may start the synapse server to create a cell dictionary and
make your cells available to synapse clients.

    sc> c = synapse_server(2500)
    sc> import math
    sc> c.pi = math.pi

Start another interactive synapse application and connect to your server.

    python -i -m synapse.main
    Synapse Console Interface v1.0
    Use exit() plus Return to exit.
    sc> s = synapse_client(2500)
    sc> s.pi
    3.141592653589793

Notice how the client has a real-time view into the server's data.
Each synapse server should have a unique port number for a specific host.
If your server is on another host, you may specify a hostname or IP address.

    sc> r = synapse_client(2500, '192.168.0.35');

This will connect to the synapse server on '192.168.0.35' on port 2500.
Connections may be bi-directional.  That is, a synapse application may be both a server and client.