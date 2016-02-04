from synapse import *
r0 = synapse_http_client(port=2500)
r1 = synapse_http_client(port=2501)
r0.get_cell('pi')
r1.get_cell('e')

