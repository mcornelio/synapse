from synapse import *
r = synapse_http_client(port=2500)
x = synapse_http_client(port=2500,context='xray')
print("root.pi=%g, xray.e=%g" % (r['pi'], x['e']))

