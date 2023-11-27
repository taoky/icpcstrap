import subprocess
import json
import sys

with open("icpc.json") as f:
    icpc = json.load(f)

seat = sys.argv[1]
ips = []
for i in icpc:
    if icpc[i]["name"] == seat:
        ips.append(i)

assert len(ips) == 1
ip = ips[0]

p = subprocess.run(["python3", "push.py", ip, "--exec", "XAUTHORITY=/run/user/1000/gdm/Xauthority xwd -root -display :0 > /tmp/test.xwd && zstd -f --rm /tmp/test.xwd"])
p = subprocess.run(["python3", "push.py", ip, "--pull", "/tmp/test.xwd.zst"])
p = subprocess.run(["unzstd -f --rm test.xwd.zst && convert test.xwd test.png && xdg-open test.png"], shell=True)
