ARG CKAN_VERSION=2.11.5
FROM docker.io/ckan/ckan-base:${CKAN_VERSION}

ARG CKANEXT_SPARK_COMMIT=6b040acc1b4048ac9c2f2b4941943f2617ee3bd7
ARG CKANEXT_S3FILESTORE_COMMIT=e972ae3c36489dcfc716f75063ac64c13cde1146

USER root

RUN pip3 install --no-cache-dir \
    "git+https://github.com/BU-Spark/ckanext-spark.git@${CKANEXT_SPARK_COMMIT}#egg=ckanext-spark"

# Phase 1 (credential-free) filestore spike dependency. See issue #9 and
# data-at-spark/minio-spike/README.md: BaseS3Uploader.upload_to_key reads the
# whole upload into memory before calling boto3, so multi-gigabyte uploads are
# not safe until a later phase resolves streaming/multipart behavior.
RUN pip3 install --no-cache-dir \
    "git+https://github.com/keitaroinc/ckanext-s3filestore.git@${CKANEXT_S3FILESTORE_COMMIT}#egg=ckanext-s3filestore"

COPY --chown=ckan-sys:ckan-sys ckan/docker-entrypoint.d/* /docker-entrypoint.d/
COPY --chown=ckan-sys:ckan-sys ckan/patches ${APP_DIR}/patches

USER ckan

RUN for patch_dir in "${APP_DIR}"/patches/*; do \
        if [ -d "${patch_dir}" ]; then \
            for patch_file in $(find "${patch_dir}" -maxdepth 1 -name '*.patch' -type f | sort -g); do \
                cd "${SRC_DIR}/$(basename "${patch_dir}")"; \
                patch -p1 < "${patch_file}"; \
            done; \
        fi; \
    done
