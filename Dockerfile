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
RUN pip install pip --upgrade
COPY requirements.txt /
RUN   pip install -r requirements.txt

#
# Service
#
COPY angus /angus

#
# Entrypoint
#
COPY docker-entrypoint.sh /

ENTRYPOINT ["/docker-entrypoint.sh"]

EXPOSE 8080
