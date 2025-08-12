# Create Database and User
```
sudo -u postgres psql
CREATE USER energy_tracker WITH PASSWORD 'e_Tracker1!';
CREATE DATABASE energy_tracker_v3_dev OWNER energy_tracker;
GRANT ALL PRIVILEGES ON DATABASE energy_tracker_v3_dev TO energy_tracker;
```
## Verify
```
python -c "import os; from sqlalchemy import create_engine; from dotenv import load_dotenv; lo
```
# Run
```
source /home/ss/Source/fast_api/venv/bin/activate
cd ~/source/fast_api
uvicorn app.main:app --reload
DEBUG_MODE=1 uvicorn app.main:app --reload

```
### Quick Fix: Kill the Process Using the Port
```
fuser -k 8000/tcp
```

### killport.sh — Search & Destroy Port Loiterers
```
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

```





### clear python cache
```
find . -type d -name __pycache__ -exec rm -r {} +
```

## Seed readings

curl -X POST http://localhost:8000/import/meter-readings \
  -F "file=@reading_seed.csv"

curl -X POST http://localhost:8000/import/solar-readings \
  -F "file=@solar.csv"
