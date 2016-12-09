FROM    debian:jessie

#
# Distrib dependencies
#

RUN   apt-get update && apt-get install -y \
      python-pip \
      python-dateutil \
      python \
      && apt-get clean \
      && rm -rf /var/lib/apt/lists/*

#
# Angus Framework
#
RUN   pip install angus-framework==0.0.2

#
# Service
#
COPY angus /angus

#
# Entrypoint
#
COPY docker-entrypoint.sh /

ENTRYPOINT ["/docker-entrypoint.sh"]

EXPOSE 80
