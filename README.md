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

    python setup.py install

##Starting a synapse application
To start an interactive "synapse" application:

    python -i -m synapse.main

A synapse interactive application will be started and
an interactive prompt will be displayed.

    Synapse Console Interface v1.0
    Use exit() plus Return to exit.
    sc>

You may also specify a list of python script files
to be executed following the -m python.main argument.
For example:

    python -i -m synapse.main myscript1.py myscript2.py myscriptn.py

These scripts are executed in the '__main__' context.

##What Is Synapse
At its core, synapse is a console application that wraps a virtual spreadsheet
with named cells.

You may get and set named cells within the spreadsheet.
Synapse cells are very similar to cells in a typical spreadsheet.  
You may set and get the cells in a synapse spreadsheet after instantiating
a synapse spreadsheet.

    sc> c = synapse_spreadsheet()
    sc> import math
    sc> c.set_cell('pi', math.pi)
    sc> mypi = c.get_cell('pi')

##Cell Values
A cell may contain any JSON encodable value.  That is:
* None
* numbers (integers or floats)
* strings
* lists or arrays enclosed in square brackets: [1,2,3]
* objects enclosed in curly braces: {'a':1, 'b':2, 'c':'apple'}

###Formulas
Like a spreadsheet, you may attach formulas to
a synapse cell.  When a synapse is
read, and it has an attached formula, the formula is
evaluated to determine the value of the item.  You may
attach a formula to a cell using the set_cell method.

You may use either a lambda expression or a defined function
as a formula.  Formulas always take 2 arguments, a key and a value.
For example, the following function defines a formula:

    sc> def pi360_formula(key,value=None):
    sc>     return math.pi * 360

The following lambda expression also defines a formula:

    sc> pi360_formula = lambda key,value : math.pi * 360

Once the formula is defined, you can attach the formula to a cell
with the set_formula method for the spreadsheet.

    sc> c.set_cell('pi360', pi360_formula)

Now, when you access the cell, the formula will be evaluated and its value returned.
For example:

    sc> theValue = c.pi360

###Guards
Unlike a spreadsheet, you may attach guards to a synapse cell.
Guards are used to validate a value before setting a cell's value.

Guards are defined in a similar fashion to formulas.  That is,
guards may be defined as either a function or lambda expression that
takes two arguments, a key and a value.  The guard should either
(1) return a value which will be set as the cell's value, or (2) raise an error.

    sc> def oddOnly_Guard(key, value):
    ...     if value % 2:
    ...         return value
    ...     else:
    ...         raise RuntimeError("not odd")
    ...
    sc> c.set_guard('oddOnly', oddOnly_Guard)
    sc> c.oddOnly = 3
    sc> print c.oddOnly
    3
    sc> c.oddOnly = 4
    RuntimeError: not odd

###Servers
Synapse applications can export their spreadsheets by acting as a server.
To do this, use the synapse_server function and specify a port number.

    sc> c = synapse_server(2500)

Please note, formulas and guards can only be defined on the server side spreadsheet.
That is, you may only define formulas and guards for the spreadsheet
in the current synapse application.

###Clients
You may get and set a server's cells from another synapse application that
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

Please note, you cannot set formulas or guards on a remote synapse application server.

##Why Synapse
Synapse applications are designed to be a normal console application that wraps
a hardware or software device and exposes its capabilities as the values
of one or more cells in a virtual spreadsheet.

Typically, this is done by formulas and guards that perform a side-effect
as a result of getting or setting a cell.

As a trivial example, a synapse application could be defined that maintains the
status of a remote computer's disk or memory utilization.  A formula
could be attached to a cell in a synapse application that when read would return the amount of
bytes available on a particular device or within a particular directory.

Synapse does away with complex RPC, SOAP, or HTTP protocols and allows the user
to treat remote synapse application spreadsheets as though they were local to
their application.