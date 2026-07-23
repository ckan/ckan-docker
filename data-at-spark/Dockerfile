ARG CKAN_VERSION=2.11.5
FROM docker.io/ckan/ckan-base:${CKAN_VERSION}

ARG CKANEXT_SPARK_COMMIT=aa47e11d0b174368152df919e1102ca873629768

USER root

RUN pip3 install --no-cache-dir \
    "git+https://github.com/BU-Spark/ckanext-spark.git@${CKANEXT_SPARK_COMMIT}#egg=ckanext-spark"

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
