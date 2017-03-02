FROM 773153459320.dkr.ecr.eu-west-1.amazonaws.com/angus.box/genericservice

#
# Service
#
COPY angus /angus

#
# Entrypoint
#
COPY docker-entrypoint.sh /
RUN chmod +x /docker-entrypoint.sh
