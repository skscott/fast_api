#!/bin/bash
# Usage: ./killport.sh 5678
PORT=$1
if [ -z "$PORT" ]; then
  echo "Usage: $0 <port>"
  exit 1
fi

PIDS=$(sudo lsof -t -iTCP:$PORT -sTCP:LISTEN)
if [ -z "$PIDS" ]; then
  echo "✅ No process found on port $PORT"
else
  echo "⚠️ Killing processes on port $PORT: $PIDS"
  sudo kill -9 $PIDS
fi
