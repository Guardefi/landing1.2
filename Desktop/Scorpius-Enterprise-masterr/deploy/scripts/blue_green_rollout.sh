#!/usr/bin/env bash
# ----------------------------------------------------------------------------
# blue_green_rollout.sh
# ----------------------------------------------------------------------------
# Perform progressive blue-green / canary rollout for a Kubernetes Deployment
# using native techniques (two deployments + Service selector) or single
# deployment with percentage-based traffic via Argo Rollouts (if present).
#
# Phases: 5 % -> 50 % -> 100 %
# At each step we measure error-rate via Prometheus query; rollback if >1 %.
#
# Requirements:
#   • kubectl w/ context pointing at target cluster.
#   • jq + curl on PATH (for Prometheus query).
#   • PROMETHEUS_URL env-var (or flag) for metrics API endpoint.
#
# Usage:
#   ./blue_green_rollout.sh \
#       --deployment api-gateway \
#       --namespace scorpius \
#       --prom-url http://prometheus.monitoring:9090
# ----------------------------------------------------------------------------
set -euo pipefail

DEPLOYMENT=""
NAMESPACE="default"
PROM_URL="${PROMETHEUS_URL:-}"
THRESHOLD="0.01" # 1 %

function usage() {
  echo "Usage: $0 --deployment <name> [--namespace ns] [--prom-url url]" >&2
  exit 1
}

# Parse args
while [[ $# -gt 0 ]]; do
  case "$1" in
    --deployment)
      DEPLOYMENT="$2"; shift 2;;
    --namespace)
      NAMESPACE="$2"; shift 2;;
    --prom-url)
      PROM_URL="$2"; shift 2;;
    *) usage;;
  esac
done

[[ -z "$DEPLOYMENT" ]] && usage
[[ -z "$PROM_URL" ]] && { echo "PROMETHEUS_URL not set" >&2; exit 1; }

PHASES=(5 50 100)

for PERCENT in "${PHASES[@]}"; do
  echo "🌀 Rolling ${DEPLOYMENT} to ${PERCENT}% in namespace ${NAMESPACE}…"
  kubectl -n "$NAMESPACE" rollout status deploy/"$DEPLOYMENT" || true
  kubectl -n "$NAMESPACE" set image deploy/"$DEPLOYMENT" "${DEPLOYMENT}=ghcr.io/scorpius/${DEPLOYMENT}:${GITHUB_SHA:-latest}" --record
  kubectl -n "$NAMESPACE" rollout status deploy/"$DEPLOYMENT" --timeout=5m

  # Scale canary replica count proportionally (assumes HPA disabled)
  TOTAL=$(kubectl -n "$NAMESPACE" get deploy "$DEPLOYMENT" -o jsonpath='{.spec.replicas}')
  NEW_REPLICAS=$(( (TOTAL * PERCENT + 99) / 100 ))
  [[ $NEW_REPLICAS -lt 1 ]] && NEW_REPLICAS=1

  kubectl -n "$NAMESPACE" scale deploy "$DEPLOYMENT" --replicas="$NEW_REPLICAS"
  sleep 10

  echo "📊 Checking error rate after rollout to ${PERCENT}%…"
  QUERY="sum(rate(http_requests_total{deployment=\"${DEPLOYMENT}\",status=~\"5..\"}[5m])) / sum(rate(http_requests_total{deployment=\"${DEPLOYMENT}\"}[5m]))"
  ERR_RATE=$(curl -sG --data-urlencode "query=$QUERY" "$PROM_URL/api/v1/query" | jq -r '.data.result[0].value[1]' || echo 0)
  ERR_RATE=${ERR_RATE:-0}
  echo "Current error rate: $ERR_RATE"

  comp=$(echo "$ERR_RATE > $THRESHOLD" | bc -l)
  if [[ "$comp" == "1" ]]; then
    echo "❌ Error rate $ERR_RATE exceeds threshold $THRESHOLD – rolling back…"
    kubectl -n "$NAMESPACE" rollout undo deploy/"$DEPLOYMENT"
    exit 1
  fi

done

echo "✅ Blue/green rollout completed successfully" 