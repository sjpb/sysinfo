""" WiP: Get information about host hardware.

    Requires following commands to be available:
        cpuinfo
        lshw (with sudo)
        free
    TODO: sort output/python api.
"""

import subprocess, pprint, collections, json

# cpu info:
cpuinfo = {} # key->str, value->str
lscpu = subprocess.run(['lscpu'], capture_output=True, text=True)
for line in lscpu.stdout.splitlines():
    if not line.isspace():
        k, v = line.split(':')
        cpuinfo[k.strip()] = v.strip()
pprint.pprint(cpuinfo)

# network (adaptor) info
netadaptinfo = []
lshwnet = subprocess.run(['sudo', 'lshw', '-class', 'network'], capture_output=True, text=True)
for line in lshwnet.stdout.splitlines():
    if not line.isspace():
        k, v = [w.strip() for w  in line.split(':', 1)]
        if k.startswith('*-network'):
            netadaptinfo.append({})
        netadaptinfo[-1][k] = v
pprint.pprint(netadaptinfo)

# memory size:
free = subprocess.run(['free', '-h'], capture_output=True, text=True)
lines = [line.split() for line in free.stdout.splitlines()]
if lines[0][0] != 'total' or lines[1][0] != 'Mem:':
    raise ValueError('unexpected result from free:\n%s' % free.stdout)
memsize = lines[1][1]
print(memsize)

# memory info:
lshwmem = subprocess.run(['sudo', 'lshw', '-class', 'memory', '-short'], capture_output=True, text=True)
lines = lshwmem.stdout.splitlines()
header = lines[0]
descr_col = lines[0].find('Description')
if descr_col < 0:
    raise ValueError('Did not find "Description" in header %r' % header)
ddr_info = []
for line in lines:
    if "DDR" in line:
        descr = line[descr_col:].split()
        mem_size = descr[0]
        mem_type = [d for d in descr if 'DDR' in d][0]
        hz = descr.index('MHz')
        mem_speed = '%s %s' % (descr[hz - 1], descr[hz])
        ddr_info.append((mem_size, mem_type, mem_speed)
unique_ddr = collections.Counter(ddr_info)
meminfo = ['%i x %s' % (v, k) for k, v in unique_ddr.items()]
print(meminfo)
