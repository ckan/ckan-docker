#!/bin/sh
# Deterministic MinIO bucket bootstrap for the local ckanext-s3filestore spike.
# Runs once via the minio-init service, then exits; ckan waits on its success.
set -eu

: "${MINIO_ENDPOINT_URL:?MINIO_ENDPOINT_URL is required}"
: "${MINIO_ROOT_USER:?MINIO_ROOT_USER is required}"
: "${MINIO_ROOT_PASSWORD:?MINIO_ROOT_PASSWORD is required}"
: "${MINIO_BUCKET_NAME:?MINIO_BUCKET_NAME is required}"

mc alias set local "${MINIO_ENDPOINT_URL}" "${MINIO_ROOT_USER}" "${MINIO_ROOT_PASSWORD}"
mc mb --ignore-existing "local/${MINIO_BUCKET_NAME}"

# Belt-and-suspenders: deny anonymous/public access at the bucket policy
# level, in addition to ckanext.s3filestore.acl=private on the upload side.
mc anonymous set none "local/${MINIO_BUCKET_NAME}"

mc ls local
