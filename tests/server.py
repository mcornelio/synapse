import synapse
import time
import os
import threading

# Create Cell Engines
r = synapse.get_cell_engine()
x = synapse.get_cell_engine(context='xray')
import math
# Set a few values
r['pi'] = math.pi
x['e'] = math.e
r['running'] = True

def quit_server():
    time.sleep(1)
    os._exit(1)

def running_guard(key, value=None):
    if value == True:
        t = threading.Thread(target=quit_server)
        t.daemon = True
        t.start()
    return value

r.set_guard('running', running_guard)

# Start our receiver
hs = synapse.http_server(2500)
rs = synapse.rpc_server(2501)

print('Server Running on %s (root, xray)' % 'http://127.0.0.1:2500/')
print('Server Running on %s (root, xray)' % 'rpc://127.0.0.1:2501/')
