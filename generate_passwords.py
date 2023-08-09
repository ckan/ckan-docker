import base64
import os

fn = ".pw"
vn = {}

pwvars = ["POSTGRES_PASSWORD", "CKAN_DB_PASSWORD", "DATASTORE_READONLY_PASSWORD","CKAN_SYSADMIN_PASSWORD"]

print("[setup_passwords] attempting to setup secure passwords")

with open(fn, 'w') as f:
    f.truncate(0)
    for pwvar in pwvars:
        with open('/dev/urandom', 'rb') as rand_file:
            pw = base64.urlsafe_b64encode(rand_file.read(12)).decode('utf-8')
            f.write(f"{pwvar}={pw}\n")
            vn[pwvar] = pw

POSTGRES_PASSWORD = vn["POSTGRES_PASSWORD"]
CKAN_DB_PASSWORD = vn["CKAN_DB_PASSWORD"]
DATASTORE_READONLY_PASSWORD = vn["DATASTORE_READONLY_PASSWORD"]
CKAN_SYSADMIN_PASSWORD = vn["CKAN_SYSADMIN_PASSWORD"]

CKAN_DB_USER = os.environ.get('CKAN_DB_USER')
CKAN_DB = os.environ.get('CKAN_DB')
DATASTORE_DB_USER = os.environ.get('DATASTORE_DB_USER')
DATASTORE_DB_READONLY_USER = os.environ.get('DATASTORE_DB_READONLY_USER')
DATASTORE_DB = os.environ.get('DATASTORE_DB')
POSTGRES_HOST = os.environ.get('POSTGRES_HOST')

with open(fn, 'a') as f:
    f.write(f"CKAN_SQLALCHEMY_URL=postgresql://{CKAN_DB_USER}:{CKAN_DB_PASSWORD}@{POSTGRES_HOST}/{CKAN_DB}\n")
    f.write(f"CKAN_DATASTORE_WRITE_URL=postgresql://{CKAN_DB_USER}:{CKAN_DB_PASSWORD}@{POSTGRES_HOST}/{DATASTORE_DB}\n") 
    f.write(f"CKAN_DATASTORE_READ_URL=postgresql://{DATASTORE_DB_READONLY_USER}:{DATASTORE_READONLY_PASSWORD}@{POSTGRES_HOST}/{DATASTORE_DB}\n") 

print("[setup_passwords] password file: '.pw' created successfully")