FROM    angus:genericservice

#
# Service
#
COPY angus /angus

#
# Entrypoint
#
COPY docker-entrypoint.sh /
RUN chmod +x /docker-entrypoint.sh
