from synapse import *
d0 = synapse_cell_dictionary()
c0 = synapse_cell_engine(d0)
s0 = synapse_http_server(port=2500,cells=d0)
d1 = synapse_cell_dictionary()
c1 = synapse_cell_engine(d1)
s1 = synapse_http_server(port=2501,cells=d1)
import math
c0.pi = math.pi
c1.e = math.e

