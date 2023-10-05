import base64
import os
import secrets
import logging

# Password length set to 16 characters
plen = 16

def generate_passwords(variables):
    passwords = {}
    for variable in variables:
        password = secrets.token_urlsafe(plen)
        passwords[variable] = password
    return passwords

def write_passwords_to_file(passwords, filename):
    try:
        with open(filename, 'w') as f:
            for variable, password in passwords.items():
                if variable == "CKAN___API_TOKEN__JWT__SECRET" :
                    # Prepend 'string:' to the API token secret
                    prepended_apitoken = "string:" + passwords['CKAN___API_TOKEN__JWT__SECRET']
                    f.write(f"CKAN___API_TOKEN__JWT__ENCODE__SECRET={prepended_apitoken}\n")
                    os.environ['CKAN___API_TOKEN__JWT__ENCODE__SECRET'] = prepended_apitoken
                    f.write(f"CKAN___API_TOKEN__JWT__DECODE__SECRET={prepended_apitoken}\n")
                    os.environ['CKAN___API_TOKEN__JWT__DECODE__SECRET'] = prepended_apitoken
                else:
                    f.write(f"{variable}={password}\n")
                    os.environ[variable] = password
        print(f"[generate_passwords] Passwords written to '{filename}' successfully.")
    except Exception as e:
        logging.error(f"Failed to write passwords to '{filename}': {str(e)}")

def write_urls_to_file(filename):
    try:
        with open(filename, 'a') as f:
            CKAN_DB_USER = os.environ.get('CKAN_DB_USER')
            CKAN_DB_PASSWORD = os.environ.get('CKAN_DB_PASSWORD')
            CKAN_DB = os.environ.get('CKAN_DB')
            DATASTORE_READONLY_USER = os.environ.get('DATASTORE_READONLY_USER')
            DATASTORE_READONLY_PASSWORD = os.environ.get('DATASTORE_READONLY_PASSWORD')
            DATASTORE_DB = os.environ.get('DATASTORE_DB')
            POSTGRES_HOST = os.environ.get('POSTGRES_HOST')
            f.write(f"CKAN_SQLALCHEMY_URL=postgresql://{CKAN_DB_USER}:{CKAN_DB_PASSWORD}@{POSTGRES_HOST}/{CKAN_DB}\n")
            f.write(f"CKAN_DATASTORE_WRITE_URL=postgresql://{CKAN_DB_USER}:{CKAN_DB_PASSWORD}@{POSTGRES_HOST}/{DATASTORE_DB}\n") 
            f.write(f"CKAN_DATASTORE_READ_URL=postgresql://{DATASTORE_READONLY_USER}:{DATASTORE_READONLY_PASSWORD}@{POSTGRES_HOST}/{DATASTORE_DB}\n")
        print(f"[generate_passwords] Database URL's written to '{filename}' successfully.")
    except Exception as e:
        logging.error(f"Failed to write database URL's to '{filename}': {str(e)}")

def main():
    pwvars = [
        "POSTGRES_PASSWORD",
        "CKAN_DB_PASSWORD",
        "DATASTORE_READONLY_PASSWORD",
        "CKAN_SYSADMIN_PASSWORD",
        "CKAN___BEAKER__SESSION__SECRET",
        "CKAN___API_TOKEN__JWT__SECRET",
    ]

    vn = generate_passwords(pwvars)

    # Write database passwords to .dbpw
    db_passwords = [
        "POSTGRES_PASSWORD",
        "CKAN_DB_PASSWORD",
        "DATASTORE_READONLY_PASSWORD",
    ]
    write_passwords_to_file({variable: vn[variable] for variable in db_passwords}, ".dbpw")

    # Write CKAN passwords to .ckpw
    ck_passwords = [
        "CKAN_DB_PASSWORD",
        "DATASTORE_READONLY_PASSWORD",
        "CKAN_SYSADMIN_PASSWORD",
        "CKAN___BEAKER__SESSION__SECRET",
        "CKAN___API_TOKEN__JWT__SECRET",
    ]
    write_passwords_to_file({variable: vn[variable] for variable in ck_passwords}, ".ckpw")

    write_urls_to_file(".ckpw")

    print("\nThe CKAN_SYSADMIN_PASSWORD password is: " + vn['CKAN_SYSADMIN_PASSWORD'] + "\n")

    # Rest of your code

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()