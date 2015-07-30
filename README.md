# synapse
## Intro
Python-based cross platform cooperative computing framework.
Cooperating synapse applications transparently communicate
with one another using progrmmable spreadsheet-like cells
that are managed in a cell dictionary.

Each synapse application can work independently and need
not be aware of other synapse applications that need to
access its internal cell dictionary.

##Installation
To install the "synapse" python package:

* Download or clone this repository
* CD into the repository
* Execute the following python command

    python setup.py develop

##Basic Usage
Synapse applications can be used for any purpose or the
synapse package can be used as a communication and data
sharing framework for any application that would like to
use a distibuted cell framework.

This section outlines the most basic usage of the package:
cooperating synapse client and server applications--setting
and getting cell values.

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

You may access a server's cells from another synapse application that
will act as a client to the synapse server. The synapse client can
access the server's cells as if they were locally defined within the
client.

To see this in action, start another interactive synapse application and connect to your server.

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

##Cell Values
Please note that cell values must be a JSON encodable value.  That is:
* None
* numbers (integers or floats)
* strings
* lists or arrays enclosed in square brackets: [1,2,3]
* objects enclosed in curly braces: {'a':1, 'b':2, 'c':'apple'}

##Programming Cells Using Formulas
Like spreadsheets, cells may have a formula that is evaluated when the cell value is requested.
_Formulas may be created by a server on its own cells only_.  A formula is specified as either a
"def'd" function or a lambda expression that returns a value.

Formulas receive 2 parameters when called: a key (the name of the cell) and an optional value.
For example, the following function defines a formula:

    def pi360_formula(key,value=None):
        return math.pi * 360

The following lambda expression also defines a formula:

    pi360_formula = lambda key,value : math.pi * 360

Using the "c" server cell dictionary from the example above, 
we can set a formula for a cell using the 'set_formula' method of the cell dictionary:

    c.set_formula('pi360', pi360_formula)

When the cell is referenced, the formula is evaluated and its result returned as the value of the cell.
For example:

    x = c.pi360 // evaluate the formula and return the formula's result for the pi360 cell

