FROM    angus:genericservice

#
# Service
#
COPY angus /angus

#
# Entrypoint
#
COPY docker-entrypoint.sh /
