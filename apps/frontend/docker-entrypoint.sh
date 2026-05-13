#!/bin/sh
# Substitutes ORCHESTRATOR_URL into the nginx template at container start.
set -e
: "${ORCHESTRATOR_URL:=http://orchestrator:8000}"
export ORCHESTRATOR_URL
envsubst '$ORCHESTRATOR_URL' < /etc/nginx/templates/default.conf.template \
  > /etc/nginx/conf.d/default.conf
