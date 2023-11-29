# First stage: Install curl
FROM registry.access.redhat.com/ubi9 AS ubi-micro-build
RUN mkdir -p /mnt/rootfs
RUN dnf install --installroot /mnt/rootfs curl --releasever 9 --setopt install_weak_deps=false --nodocs -y && \
    dnf --installroot /mnt/rootfs clean all && \
    rpm --root /mnt/rootfs -e --nodeps setup

# Second stage: build keycloak image
FROM quay.io/keycloak/keycloak:latest

# Copy curl from the first stage
COPY --from=ubi-micro-build /mnt/rootfs /

# Enable health and metrics support
ENV KC_HEALTH_ENABLED=true

ENV KC_DB=postgres
ENV KC_DB_URL=<DBURL>
ENV KC_DB_USERNAME=<DBUSERNAME>
ENV KC_DB_PASSWORD=<DBPASSWORD>
ENV KC_HOSTNAME=localhost
ENTRYPOINT ["/opt/keycloak/bin/kc.sh","start-dev", "--import-realm"]
