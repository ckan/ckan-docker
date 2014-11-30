FROM phusion/baseimage:0.9.15
MAINTAINER Open Knowledge

# set UTF-8 locale
RUN locale-gen en_US.UTF-8 && \
    echo 'LANG="en_US.UTF-8"' > /etc/default/locale

RUN apt-get -qq update

# Install required packages
RUN DEBIAN_FRONTEND=noninteractive apt-get -qq -y install \
        python-minimal \
        python-dev \
        python-virtualenv \
        libevent-dev \
        libpq-dev \
        libxml2-dev \
        libxslt1-dev \
        build-essential

# Install required packages
RUN DEBIAN_FRONTEND=noninteractive apt-get -qq -y install \
        apache2 \
        libapache2-mod-wsgi \
        postfix \
        git \
        libgeos-c1 \
        supervisor

ENV HOME /root
ENV CKAN_HOME /usr/lib/ckan/default
ENV CKAN_CONFIG /etc/ckan/default
ENV CONFIG_FILE ckan.ini
ENV CONFIG_OPTIONS custom_options.ini
ENV CKAN_DATA /var/lib/ckan
ENV CKAN_INI $CKAN_CONFIG/$CONFIG_FILE

# Create directories & virtual env for CKAN
RUN virtualenv $CKAN_HOME
RUN mkdir -p $CKAN_CONFIG $CKAN_DATA /var/log/ckan
RUN chown www-data:www-data $CKAN_DATA

# copy CKAN and any extenstions in the source directory
ADD docker/ckan/pip_install_req.sh /usr/local/sbin/pip_install_req

# copy CKAN and any extenstions in the source directory
ADD _src/ $CKAN_HOME/src/
ONBUILD ADD _src/ $CKAN_HOME/src/
RUN $CKAN_HOME/bin/pip install pip==1.4.1
# install what we've just copied
RUN pip_install_req
ONBUILD RUN pip_install_req
RUN ln -s $CKAN_HOME/src/ckan/ckan/config/who.ini $CKAN_CONFIG/who.ini
ONBUILD RUN ln -s $CKAN_HOME/src/ckan/ckan/config/who.ini $CKAN_CONFIG/who.ini

# Copy any custom config
COPY _etc/ckan/ $CKAN_CONFIG/
ONBUILD COPY _etc/ckan/ $CKAN_CONFIG/

# Make config file
RUN $CKAN_HOME/bin/paster make-config ckan ${CKAN_CONFIG}/${CONFIG_FILE}

# Configure apache
RUN a2dissite 000-default
RUN echo "Listen 8080" > /etc/apache2/ports.conf
COPY _etc/apache2/apache.wsgi $CKAN_CONFIG/apache.wsgi
ONBUILD COPY _etc/apache2/apache.wsgi $CKAN_CONFIG/apache.wsgi
COPY _etc/apache2/apache.conf /etc/apache2/sites-available/ckan_default.conf
ONBUILD COPY _etc/apache2/apache.conf /etc/apache2/sites-available/ckan_default.conf
RUN a2ensite ckan_default

# Configure postfix
COPY _etc/postfix/main.cf /etc/postfix/main.cf
ONBUILD COPY _etc/postfix/main.cf /etc/postfix/main.cf

# Configure supervisor
COPY _etc/supervisor/conf.d/ /etc/supervisor/conf.d/
ONBUILD COPY _etc/supervisor/conf.d/ /etc/supervisor/conf.d/

# Configure cron
COPY _etc/cron.d/ /etc/cron.d/
RUN chmod 600 -R /etc/cron.d/
ONBUILD COPY _etc/cron.d/ /etc/cron.d/
ONBUILD RUN chmod 600 -R /etc/cron.d/

# Configure runit
ADD docker/ckan/my_init.d/ /etc/my_init.d/
ONBUILD COPY _etc/my_init.d/ /etc/my_init.d/
ADD docker/ckan/svc/ /etc/service/

CMD ["/sbin/my_init"]

VOLUME ["/usr/lib/ckan", "/var/lib/ckan", "/etc/ckan"]
EXPOSE 8080

RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Disable SSH
RUN rm -rf /etc/service/sshd /etc/my_init.d/00_regen_ssh_host_keys.sh
