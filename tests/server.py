from synapse import *
r = synapse_get_cell_engine()
x = synapse_get_cell_engine(context='xray')
import math
r['pi'] = math.pi
x['e'] = math.e
synapse_server(2500)


