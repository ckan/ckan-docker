PORT := 8003

env313:
	mamba create -y -p ./env313 python=3.13 pyproj gunicorn
	./env313/bin/python -m pip install titiler==0.19.0 google-cloud-logging aiocache[redis] matplotlib pydantic-settings uvicorn fastapi==0.115.4

dev: env313
	PROJ_DATA=env313/share/proj PORT=$(PORT) ./env313/bin/python app/main.py
