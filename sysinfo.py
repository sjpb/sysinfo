""" WiP: Get information about host hardware.

    Requires following commands to be available:
        lscpu
        lshw (with sudo)
        free
    TODO: remove need for root for memory info
    TODO: sort output/python api.
"""

import subprocess, pprint, collections, os, glob

# chassis:
DMI_ROOT = '/sys/devices/virtual/dmi/id/'
chassis_info = {
    'product_name': open(os.path.join(DMI_ROOT, 'product_name')).read().strip(),
    'sys_vendor': open(os.path.join(DMI_ROOT, 'sys_vendor')).read().strip(),
}
print(chassis_info)

# cpu info:
cpuinfo = {} # key->str, value->str
lscpu = subprocess.run(['lscpu'], capture_output=True, text=True)
for line in lscpu.stdout.splitlines():
    if not line.isspace():
        k, v = line.split(':')
        cpuinfo[k.strip()] = v.strip()
pprint.pprint(cpuinfo)

# network (adaptor) info:
NETROOT = '/sys/class/net'
devnames = [dev for dev in os.listdir(NETROOT) if os.path.exists(os.path.join(NETROOT, dev, 'device'))]
netinfo = {}
for dev in devnames:
    speed = open(os.path.join(NETROOT, dev, 'speed')).read().strip()
    if not speed or int(speed) < 1:
        continue
    netinfo[dev] = {'speed': '%s Mbits/s' % speed } # Mbits/sec as per https://www.kernel.org/doc/Documentation/ABI/testing/sysfs-class-net
    vendor_id = open(os.path.join(NETROOT, dev, 'device/vendor')).read().strip()
    device_id = open(os.path.join(NETROOT, dev, 'device/device')).read().strip()
    pci_id = os.path.basename(os.path.realpath(os.path.join(NETROOT, dev, 'device')))  # e.g. '0000:82:00.1'
    lspci = subprocess.run(['lspci', '-d', '%s:%s' % (vendor_id, device_id), '-nn'], capture_output=True, text=True)
    for descr in lspci.stdout.splitlines():
        if descr.split()[0] in pci_id: # descr[0] e.g. '82:00.1'
            netinfo[dev]['descr'] = descr
            break
pprint.pprint(netinfo)
    
# memory info:
# size:
free = subprocess.run(['free', '-h', '--si'], capture_output=True, text=True)
lines = [line.split() for line in free.stdout.splitlines()]
if lines[0][0] != 'total' or lines[1][0] != 'Mem:':
    raise ValueError('unexpected result from free:\n%s' % free.stdout)
meminfo = {'total': lines[1][1]}
mem_types = []
for dimm in glob.glob('/sys/devices/system/edac/mc/mc*/dimm*'):
    mem_type = open(os.path.join(dimm, 'dimm_mem_type')).read().strip()
    mem_types.append(mem_type)
meminfo['type'] = list(set(mem_types))
print(meminfo)