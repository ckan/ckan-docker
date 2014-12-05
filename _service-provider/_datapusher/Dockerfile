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

ENV DATAPUSHER_HOME /usr/lib/ckan/datapusher
RUN virtualenv $DATAPUSHER_HOME

ADD datapusher $DATAPUSHER_HOME/src/datapusher
RUN pip install pip==1.4.1
RUN pip install -r $DATAPUSHER_HOME/src/datapusher/requirements.txt

WORKDIR $DATAPUSHER_HOME/src/datapusher/

CMD [ "python", "datapusher/main.py", "deployment/datapusher_settings.py"]
