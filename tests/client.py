import synapse
# Create local cell proxies
r = synapse._client(port=2500)
x = synapse._client(port=2500,context='xray')
# Get a few values
print("root.pi=%g, xray.e=%g" % (r['pi'], x['e']))

