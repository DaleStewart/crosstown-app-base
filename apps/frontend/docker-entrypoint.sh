#!/bin/sh
# Substitutes ORCHESTRATOR_URL + derived ORCHESTRATOR_HOST into the nginx
# template at container start. ORCHESTRATOR_HOST is the bare hostname used
# for upstream Host header + TLS SNI — required by Azure Container Apps
# ingress, which rejects the TLS handshake otherwise (nginx logs:
# "peer closed connection in SSL handshake ... while SSL handshaking to
# upstream", resulting in a 502 to the browser).
set -e
: "${ORCHESTRATOR_URL:=http://orchestrator:8000}"
ORCHESTRATOR_HOST=$(printf '%s' "$ORCHESTRATOR_URL" | sed -E 's#^[a-z]+://##; s#/.*$##; s#:.*$##')
export ORCHESTRATOR_URL ORCHESTRATOR_HOST
envsubst '$ORCHESTRATOR_URL $ORCHESTRATOR_HOST' \
  < /etc/nginx/templates/default.conf.template \
  > /etc/nginx/conf.d/default.conf
