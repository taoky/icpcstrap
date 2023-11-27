#!/bin/bash

MSG="由于内存不足，earlyoom 已结束进程 $EARLYOOM_NAME 以保证用户界面流畅。"

RATELIMIT="/tmp/earlyoom-ratelimit"

(
    flock -x 200 -w 2
    if [ -f "$RATELIMIT" ]; then
        CURRENT=$(date +%s)
        FILE=$(stat -c %Y "$RATELIMIT")

        DIFF=$((CURRENT-FILE))
        # 10 seconds rate-limit
        if [ "$DIFF" -lt 10 ]; then
            echo "Rate-limited earlyoom notification"
            exit 0
        fi
    fi
    touch "$RATELIMIT"
) 200>"$RATELIMIT"

wall "$MSG"
date >> /tmp/earlyoom-record
DISPLAY=:0 sudo -u icpc zenity --error --text "$MSG" &
DISPLAY=:1 sudo -u icpc zenity --error --text "$MSG" &
