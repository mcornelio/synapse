import synapse
import time
# Create Cell Engines
r = synapse.get_cell_engine()
x = synapse.get_cell_engine(context='xray')
import math
# Set a few values
r['pi'] = math.pi
x['e'] = math.e
r['running'] = True
# Start our receiver
synapse._server(2500)

print('Server Running on http://localhost:2500/ (root, xray)')
while(r['running'] == True):
    time.sleep(1)

synapse.exit()