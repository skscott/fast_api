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
source /home/ss/Source/fast_api/.venv/bin/activate
cd ~/Source/fast_api
uvicorn app.main:app --reload
```
### Quick Fix: Kill the Process Using the Port
```
fuser -k 8000/tcp

```
### clear python cache
```
find . -type d -name __pycache__ -exec rm -r {} +
```

## Seed readings

curl -X POST http://localhost:8000/import/meter-readings \
  -F "file=@reading_seed.csv"
