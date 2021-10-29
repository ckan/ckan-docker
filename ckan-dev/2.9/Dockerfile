FROM ckan/ckan-base:testing-only.2.9

LABEL maintainer="brett@kowh.ai"

ENV APP_DIR=/srv/app
ENV SRC_EXTENSIONS_DIR=/srv/app/src_extensions

# Install packages needed by the dev requirements
RUN apk add --no-cache libffi-dev

# Set up Python3 virtual environment
RUN cd ${APP_DIR} && \
    source ${APP_DIR}/bin/activate

# Virtual environment binaries/scripts to be used first
ENV PATH=${APP_DIR}/bin:${PATH} 

# Install CKAN dev requirements
# Will need to change this eventually - when CKAN 2.9 is out
# wget https://raw.githubusercontent.com/ckan/ckan/master/dev-requirements.txt
# RUN pip3 install --no-binary :all: -r https://raw.githubusercontent.com/ckan/ckan/master/dev-requirements.txt
RUN pip3 install -r https://raw.githubusercontent.com/ckan/ckan/master/dev-requirements.txt

# Create folder for local extensions sources
RUN mkdir $SRC_EXTENSIONS_DIR

COPY setup/start_ckan_development.sh ${APP_DIR}

CMD ["/srv/app/start_ckan_development.sh"]
