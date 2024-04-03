#############################
### Build DataPusher Plus ###
#############################
FROM ubuntu:jammy


LABEL maintainer="Minhaj"




# Set timezone
ENV TZ=UTC
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone


# Set Locale
ENV LC_ALL=en_US.UTF-8


ENV SRC_DIR=/srv/app/src
ENV VENV=/usr/lib/ckan/dpplus_venv
ENV CFG_DIR=/etc/ckan/datapusher


WORKDIR ${SRC_DIR}


# Set the locale         
RUN apt-get update
RUN apt-get install --no-install-recommends -y locales
RUN sed -i "/$LC_ALL/s/^# //g" /etc/locale.gen
RUN dpkg-reconfigure --frontend=noninteractive locales
RUN update-locale LANG=${LC_ALL}
RUN apt-get install -y software-properties-common
RUN add-apt-repository ppa:deadsnakes/ppa

# Install apt-utils and other dependencies
RUN apt-get install --no-install-recommends -y \
   apt-utils \
   build-essential \
   libxslt1-dev \
   libxml2-dev \
   libffi-dev \
   wget \
   curl \
   unzip \
   git \
   libpq-dev \
   file

# Install Python 3.9 (check if it's available in the default repo first)
# If not available, use the previously added PPA
RUN apt-get install -y python3.9 python3.9-dev python3.9-venv

# Set Python 3.9 as the default Python version
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.9 1
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.9 1

# Install pip for Python 3.9
RUN apt-get install -y python3-pip

# Clean up APT when done
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*


#install qsv;
RUN wget https://github.com/jqnatividad/qsv/releases/download/0.108.0/qsv-0.108.0-x86_64-unknown-linux-gnu.zip
RUN unzip qsv-0.108.0-x86_64-unknown-linux-gnu.zip
RUN rm qsv-0.108.0-x86_64-unknown-linux-gnu.zip
RUN mv qsv* /usr/local/bin


#python env setup; link python3 to python cmd; make venv; install uwsgi;
RUN python3 -m venv ${VENV}
RUN ${VENV}/bin/pip install uwsgi


#install tests 
#Add custom values before installing tests https://github.com/dathere/testing-datapusher-plus.git
#and unable the script in startup.sh
#RUN git clone --branch master https://github.com/dathere/testing-datapusher-plus.git
#RUN ${VENV}/bin/pip install -r testing-datapusher-plus/requirements.txt
#RUN cd ..


#INSTALL DATAPUSHER-PLUS FROM SOURCE REPO
RUN git clone --branch 0.15.0 https://github.com/datHere/datapusher-plus
RUN cd ${SRC_DIR}/datapusher-plus && \
   ${VENV}/bin/pip install -r requirements-dev.txt && \
   ${VENV}/bin/pip install -e . 

   
RUN ${VENV}/bin/pip install Flask==2.3.3 
RUN ${VENV}/bin/pip install Werkzeug==2.3.0



#SETUP CONFIG/SETTINGS.PY
RUN mkdir -p ${CFG_DIR}
COPY example.env ${SRC_DIR}/datapusher-plus/datapusher/.env
ENV JOB_CONFIG=${SRC_DIR}/datapusher-plus/datapusher/.env


 
RUN curl https://raw.githubusercontent.com/dathere/datapusher-plus/0.15.0/deployment/datapusher-uwsgi.ini -o ${CFG_DIR}/uwsgi.ini




COPY ./entrypoint/startup.sh /startup.sh
RUN chmod +x /startup.sh




ENTRYPOINT [ "bash", "-c", "/startup.sh" ]




EXPOSE 8800
