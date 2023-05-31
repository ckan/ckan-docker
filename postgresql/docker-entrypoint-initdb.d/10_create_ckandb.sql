\set ckan_db_password '\'' `echo $CKAN_DB_PASSWORD` '\''

CREATE ROLE ckandbuser NOSUPERUSER CREATEDB CREATEROLE LOGIN PASSWORD :ckan_db_password;
CREATE DATABASE ckandb OWNER ckandbuser ENCODING 'utf-8';
