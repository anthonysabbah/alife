#!/usr/bin/dumb-init /bin/sh

### docker entrypoint script, for starting redis stack
BASEDIR=/opt/redis-stack
cd ${BASEDIR}

CMD=${BASEDIR}/bin/redis-server
if [ -f /redis-stack.conf ]; then
    CONFFILE=/redis-stack.conf
fi

if [ -z "${REDIS_DATA_DIR}" ]; then
    REDIS_DATA_DIR=/data
fi

if [ -z "${REDISEARCH_ARGS}" ]; then
REDISEARCH_ARGS="MAXSEARCHRESULTS 10000 MAXAGGREGATERESULTS 10000"
fi

# daemonize redis to set up indices
${CMD} \
${CONFFILE} \
--dir ${REDIS_DATA_DIR} \
--protected-mode no \
--daemonize yes \
--loadmodule /opt/redis-stack/lib/redisearch.so ${REDISEARCH_ARGS} \
--loadmodule /opt/redis-stack/lib/redistimeseries.so ${REDISTIMESERIES_ARGS} \
--loadmodule /opt/redis-stack/lib/rejson.so ${REDISJSON_ARGS} \
${REDIS_ARGS}

# REDIS SEARCH INDEXES:
redis-cli FT.CREATE worldIdx ON JSON PREFIX 1 t: SCHEMA $.tick AS tick NUMERIC $.maxFitness as maxFitness NUMERIC
redis-cli FT.CREATE genomes ON JSON PREFIX 1 gene: SCHEMA $.hash AS hash TEXT $.fitness as fitness NUMERIC

# CREATE TIMESERIES TO TRACK MAX CREATURE FITNESS:
TS.CREATE maxFitness

redis-cli save
redis-cli shutdown

${CMD} \
${CONFFILE} \
--dir ${REDIS_DATA_DIR} \
--protected-mode no \
--daemonize no \
--loadmodule /opt/redis-stack/lib/redisearch.so ${REDISEARCH_ARGS} \
--loadmodule /opt/redis-stack/lib/redistimeseries.so ${REDISTIMESERIES_ARGS} \
--loadmodule /opt/redis-stack/lib/rejson.so ${REDISJSON_ARGS} \
${REDIS_ARGS}
