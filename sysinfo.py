""" PoC """

import subprocess, pprint

cpuinfo = {} # key->str, value->str
lscpu = subprocess.run(['lscpu'], capture_output=True, text=True)
for line in lscpu.stdout.splitlines():
    if not line.isspace():
        k, v = line.split(':')
        cpuinfo[k.strip()] = v.strip()
pprint.pprint(cpuinfo)
