FROM ckan/ckan-base:2.10.1
#FROM ckan/ckan-base:2.9.9

# Set up environment variables
ENV APP_DIR=/srv/app
ENV TZ=UTC
RUN echo ${TZ} > /etc/timezone

# Make sure both files are not exactly the same
RUN if ! [ /usr/share/zoneinfo/${TZ} -ef /etc/localtime ]; then \
  cp /usr/share/zoneinfo/${TZ} /etc/localtime ;\
  fi ;

# For production copy the source files into the image (Dev will mount them as a volume)
COPY src ${APP_DIR}/src_extensions

# Install the extension(s) you wrote for your own project
RUN pip install ckanext-oidc-pkce && \
  # pip install $APP_DIR/src_extensions/ckanext-oidc-pkce && \
  pip install $APP_DIR/src_extensions/ckanext-auscope-theme
