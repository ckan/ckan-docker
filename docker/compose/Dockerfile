FROM phusion/baseimage:0.9.16
MAINTAINER Open Knowledge

# set UTF-8 locale
RUN locale-gen en_US.UTF-8 && \
    echo 'LANG="en_US.UTF-8"' > /etc/default/locale

RUN apt-get -qq update

# Install required packages
RUN DEBIAN_FRONTEND=noninteractive apt-get -qq -y install \
	python-pip
	

RUN pip install -U docker-compose
ENV DOCKER_HOST unix:///tmp/docker.sock

WORKDIR /src
CMD ["/bin/bash"]

RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
