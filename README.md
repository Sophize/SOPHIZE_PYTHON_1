# SOPHIZE_PYTHON_1
A `Machine` server in Python. Requires python 3.7

## Setup

See https://cloud.google.com/appengine/docs/standard/python3/building-app/writing-web-service

```
python -m venv env
source env/bin/activate
pip install  -r app/requirements.txt
cd app && python main.py
```

## Deploy

```
cd app
./deploy.sh
```
