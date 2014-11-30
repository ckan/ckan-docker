FROM phusion/baseimage:0.9.15
MAINTAINER Open Knowledge

# set UTF-8 locale
RUN locale-gen en_US.UTF-8 && \
    echo 'LANG="en_US.UTF-8"' > /etc/default/locale

ENV CKAN_DATA /var/lib/ckan
ENV PGDATA /var/lib/postgresql/9.3/main
ENV PGMAIN /etc/postgresql/9.3/main

RUN mkdir -p $CKAN_DATA && chown -R www-data:www-data $CKAN_DATA

RUN echo "postgres:x:107:" >> /etc/group
RUN echo "postgres:x:103:107:PostgreSQL administrator,,,:/var/lib/postgresql:/bin/bash" >> /etc/passwd
RUN mkdir -p $PGDATA && chown -R postgres:postgres $PGDATA
RUN mkdir -p $PGMAIN && chown -R postgres:postgres $PGMAIN

CMD ["/sbin/my_init"]

VOLUME ["/var/lib/ckan", "/etc/postgresql/9.3/main", "/var/lib/postgresql/9.3/main"]
