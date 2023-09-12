import base64
import os
import secrets

fn = ".pw"
vn = {}

pwvars = ["POSTGRES_PASSWORD", "CKAN_DB_PASSWORD", "DATASTORE_READONLY_PASSWORD","CKAN_SYSADMIN_PASSWORD", \
            "CKAN___BEAKER__SESSION__SECRET"]

print("\n[setup_passwords] attempting to setup secure passwords")

with open(fn, 'w') as f:
    plen = 16
    f.truncate(0)
    for pwvar in pwvars:
      pw = secrets.token_urlsafe(plen)
      f.write(f"{pwvar}={pw}\n")
      vn[pwvar] = pw


# Set up the environment variables from the values in the .pw file
POSTGRES_PASSWORD = vn["POSTGRES_PASSWORD"]
CKAN_DB_PASSWORD = vn["CKAN_DB_PASSWORD"]
DATASTORE_READONLY_PASSWORD = vn["DATASTORE_READONLY_PASSWORD"]
CKAN_SYSADMIN_PASSWORD = vn["CKAN_SYSADMIN_PASSWORD"]
CKAN___BEAKER__SESSION__SECRET = vn["CKAN___BEAKER__SESSION__SECRET"]

# The API_TOKEN is a JWT token, which is a special case
jwtpw = secrets.token_urlsafe(plen)

with open(fn, 'a') as f:
    f.write(f"CKAN___API_TOKEN__JWT__ENCODE__SECRET=string:" + str(jwtpw) + "\n")
    f.write(f"CKAN___API_TOKEN__JWT__DECODE__SECRET=string:" + str(jwtpw) + "\n")

CKAN___API_TOKEN__JWT__ENCODE__SECRET = "string:" + str(jwtpw)
CKAN___API_TOKEN__JWT__DECODE__SECRET = "string:" + str(jwtpw)

# Now the database URL's which include the password generated above
CKAN_DB_USER = os.environ.get('CKAN_DB_USER')
CKAN_DB = os.environ.get('CKAN_DB')
DATASTORE_DB_USER = os.environ.get('DATASTORE_DB_USER')
DATASTORE_READONLY_USER = os.environ.get('DATASTORE_READONLY_USER')
DATASTORE_DB = os.environ.get('DATASTORE_DB')
POSTGRES_HOST = os.environ.get('POSTGRES_HOST')

# Now write out the Database URL's
with open(fn, 'a') as f:
    f.write(f"CKAN_SQLALCHEMY_URL=postgresql://{CKAN_DB_USER}:{CKAN_DB_PASSWORD}@{POSTGRES_HOST}/{CKAN_DB}\n")
    f.write(f"CKAN_DATASTORE_WRITE_URL=postgresql://{CKAN_DB_USER}:{CKAN_DB_PASSWORD}@{POSTGRES_HOST}/{DATASTORE_DB}\n") 
    f.write(f"CKAN_DATASTORE_READ_URL=postgresql://{DATASTORE_READONLY_USER}:{DATASTORE_READONLY_PASSWORD}@{POSTGRES_HOST}/{DATASTORE_DB}\n") 

print("[setup_passwords] password file: '.pw' created successfully")
print("\nThe CKAN_SYSADMIN_PASSWORD password is: " + CKAN_SYSADMIN_PASSWORD + "\n")
