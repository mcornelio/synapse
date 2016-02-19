import synapse
# Create local cell proxies
hr = synapse.http_cell_engine(port=2500)
hx = synapse.http_cell_engine(port=2500,context='xray')
rr = synapse.rpc_cell_engine(port=2501)
rx = synapse.rpc_cell_engine(port=2501,context='xray')
# Get a few values
print("(http) root.pi=%g, xray.e=%g" % (hr['pi'], hx['e']))
print("(rpc)  root.pi=%g, xray.e=%g" % (rr['pi'], rx['e']))

