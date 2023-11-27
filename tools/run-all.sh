#!/bin/bash

OUT=log.txt
: > "$OUT"

# all.txt contains IP addresses, one per line
cp all.txt list.txt

ROUND=0
while :; do
  echo "Running round $((++ROUND)), $(wc -l < list.txt) host(s) to go" >> "$OUT"
  rm -f failed.txt
  for i in $(<list.txt); do
    (
      ssh -J icpc root@"$i" \
        'set -eo pipefail;' "$@" ||
        echo "$i" >> failed.txt 
    ) &
  done
  wait

  if [ ! -f failed.txt ]; then
    echo "No more failed hosts" >> "$OUT"
    break
  fi
  echo "$(wc -l < failed.txt) failed host(s) this round:" >> "$OUT"
  cat failed.txt >> "$OUT"
  mv failed.txt list.txt
done
