#!/usr/bin/env python3
# This script is written by qinmaye originally
# Edited with reading from IP list & retrying & set -eo pipefail.

import sys, re, subprocess
from subprocess import PIPE
from pathlib import Path
import json

USER = 'root'
PORT = '22'
DIR = '/home/icpc/Desktop'
# DIR = '/tmp'
SSH_OPTIONS = ['-o', 'StrictHostKeyChecking=no', '-o', 'ConnectTimeout=10']

is_ip   = lambda s: re.match(r'[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+', s) or s == "all" or re.fullmatch(r'[A-Z][0-9][0-9]', s)
is_file = lambda s: Path(s).exists()
execute = lambda args: subprocess.Popen(args, stdout=PIPE, stderr=PIPE)
remote  = lambda host, cmd:   ['ssh', '-p', PORT] + SSH_OPTIONS + [host] + cmd
send    = lambda host, files: ['scp', '-P', PORT] + SSH_OPTIONS + files + ["%s:%s" % (host, DIR)]
decode  = lambda b: '\n'.join([' ' * 4 + l for l in b.decode('utf-8').strip().splitlines()])

argv = sys.argv[1:]

if not argv:
  nm = sys.argv[0]
  print('Usage:')
  print('  {} --peek 192.168.1.100'.format(nm))
  print('  {} --exec ls /home/jsoi/Desktop 192.168.1.100'.format(nm))
  print('  {} readme.pdf day1.zip 129.168.1.{{1..100}}'.format(nm))
  print('  auto detects file/IP addr') 
  exit(1)

IPs, files, peek = [], [], None
for name in argv:
  if name.startswith('--'):
    if name == '--peek': peek = ['true']
    if name == '--exec': peek = []
  elif peek is None and is_file(name): files.append(name)
  elif is_ip(name): IPs.append(name)
  else: peek.append(name)

if IPs[0] == "all":
  IPs = []
  with open("icpc.json") as f:
    icpc = json.load(f)
  for i in icpc:
    if i.startswith("192"):
      IPs.append(i)

RETRY = 3
procs = []
for ip in IPs:
  host = '{}@{}'.format(USER, ip)
  if peek:
    assert len(peek) == 1
    peek0 = ["set -eo pipefail; " + peek[0]]
    cmd = remote(host, peek0)
  else:
    cmd = send(host, files)
  p = execute(cmd)
  procs.append((p, ip, cmd, RETRY))

failed = []

while len(procs) != 0:
  p = procs.pop()
  p, ip, cmd, retry = p
  (stdout, stderr) = p.communicate()
  print('>>>', ip, end=' ')
  if p.returncode == 0:
    print("OK")
    print(decode(stdout))
  else:
    print(f"ERROR (retry={retry})")
    print(decode(stderr))
    if retry > 0:
      p = execute(cmd)
      procs.append((p, ip, cmd, retry - 1))
    else:
      failed.append(ip)

print("Failed:")
print(failed)
