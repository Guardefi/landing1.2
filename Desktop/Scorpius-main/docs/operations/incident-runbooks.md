# Incident Response Runbooks

This document contains step-by-step runbooks for common operational incidents in the Scorpius platform.

## 🚨 Emergency Contact Information

- **On-Call Engineer**: PagerDuty escalation
- **Security Team**: security@scorpius.com
- **Infrastructure Lead**: infra@scorpius.com
- **Slack Channel**: `#scorpius-incidents`

## 📋 General Incident Response Process

1. **Acknowledge** the alert within 5 minutes
2. **Assess** the severity and impact
3. **Communicate** in #scorpius-incidents
4. **Investigate** using the appropriate runbook
5. **Resolve** the issue
6. **Document** lessons learned

---

## 🔥 High-Severity Incidents

### Mempool Transaction Spike

**Symptoms:**
- High memory usage (>80%)
- Increased latency (P95 > 5s)
- Queue backlog growing
- WebSocket connection drops

**Immediate Actions:**
```bash
# 1. Check current load
kubectl top pods -n scorpius
kubectl get hpa -n scorpius

# 2. Scale up mempool service immediately
kubectl scale deployment mempool-service --replicas=10 -n scorpius

# 3. Check Redis memory usage
kubectl exec -it redis-0 -n scorpius -- redis-cli info memory

# 4. Monitor queue depth
curl -s http://mempool-service/metrics | grep queue_depth
```

**Investigation Steps:**
1. Check Grafana dashboard: "Mempool Performance"
2. Review recent deployments in last 2 hours
3. Check for unusual transaction patterns
4. Verify external API dependencies

**Resolution:**
- If traffic spike: Maintain increased replicas for 30 minutes
- If memory leak: Restart affected pods
- If external dependency: Implement circuit breaker

**Prevention:**
- Review HPA scaling thresholds
- Implement rate limiting
- Add more monitoring alerts

---

### Database Connection Pool Exhaustion

**Symptoms:**
- Connection timeout errors
- `too many connections` in logs
- Application pods failing health checks

**Immediate Actions:**
```bash
# 1. Check current connections
kubectl exec -it postgres-0 -n scorpius -- psql -U scorpius -c "SELECT count(*) FROM pg_stat_activity;"

# 2. Kill idle connections
kubectl exec -it postgres-0 -n scorpius -- psql -U scorpius -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE state = 'idle' AND state_change < now() - interval '5 minutes';"

# 3. Restart application pods with connection issues
kubectl rollout restart deployment/api-gateway -n scorpius
kubectl rollout restart deployment/scanner-service -n scorpius

# 4. Check connection pool settings
kubectl get configmap app-config -n scorpius -o yaml | grep -A 5 database
```

**Investigation Steps:**
1. Review connection pool configuration
2. Check for connection leaks in application logs
3. Verify database performance metrics
4. Review recent code changes affecting database queries

**Resolution:**
- Increase connection pool size temporarily
- Fix connection leaks in application code
- Consider read replicas for read-heavy operations

**Prevention:**
- Implement connection pool monitoring
- Add circuit breakers for database calls
- Regular connection leak audits

---

### JWT Token Compromise

**Symptoms:**
- Unusual authentication patterns
- Security alerts from monitoring
- Multiple failed login attempts
- Suspicious API access patterns

**Immediate Actions:**
```bash
# 1. IMMEDIATELY rotate JWT secrets
kubectl create job jwt-rotation --from=cronjob/rotate-secrets -n scorpius

# 2. Invalidate all active sessions
kubectl exec -it redis-0 -n scorpius -- redis-cli FLUSHDB

# 3. Enable additional logging
kubectl patch configmap app-config -n scorpius --patch '{"data":{"LOG_LEVEL":"DEBUG","SECURITY_AUDIT":"true"}}'

# 4. Block suspicious IP addresses (if identified)
kubectl apply -f - <<EOF
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: block-suspicious-ips
  namespace: scorpius
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  ingress:
  - from:
    - ipBlock:
        cidr: 0.0.0.0/0
        except:
        - SUSPICIOUS_IP/32
EOF
```

**Investigation Steps:**
1. Review authentication logs for patterns
2. Check source IPs and geolocation
3. Audit user accounts for compromise
4. Review API access logs
5. Check for privilege escalation

**Resolution:**
- Force password reset for affected users
- Implement additional MFA requirements
- Review and update access controls
- Notify affected users

**Prevention:**
- Implement rate limiting on auth endpoints
- Add anomaly detection for login patterns
- Regular security awareness training
- Implement IP whitelisting where appropriate

---

## 🔧 Medium-Severity Incidents

### High CPU Utilization

**Symptoms:**
- CPU usage >80% sustained
- Increased response times
- HPA scaling events

**Investigation:**
```bash
# 1. Identify high-CPU pods
kubectl top pods -n scorpius --sort-by=cpu

# 2. Get detailed resource usage
kubectl describe pod HIGH_CPU_POD -n scorpius

# 3. Check for CPU-intensive processes
kubectl exec -it HIGH_CPU_POD -n scorpius -- top

# 4. Review recent deployments
kubectl rollout history deployment/AFFECTED_SERVICE -n scorpius
```

**Resolution:**
- Scale horizontally if traffic-related
- Optimize inefficient code/queries
- Adjust resource limits if needed

---

### Disk Space Critical

**Symptoms:**
- Disk usage >85%
- Pod evictions
- Write failures

**Investigation:**
```bash
# 1. Check disk usage across nodes
kubectl get nodes -o wide
kubectl describe nodes | grep -A 5 "Allocated resources"

# 2. Find large files/directories
kubectl exec -it POD_NAME -n scorpius -- du -sh /* | sort -h

# 3. Check log file sizes
kubectl exec -it POD_NAME -n scorpius -- du -sh /var/log/*
```

**Resolution:**
- Clean up old log files
- Implement log rotation
- Scale storage volumes
- Archive old data

---

### Service Discovery Issues

**Symptoms:**
- Services unable to communicate
- DNS resolution failures
- Connection refused errors

**Investigation:**
```bash
# 1. Check service endpoints
kubectl get endpoints -n scorpius

# 2. Test DNS resolution
kubectl run -it --rm debug --image=busybox --restart=Never -- nslookup SERVICE_NAME.scorpius.svc.cluster.local

# 3. Check service configurations
kubectl get services -n scorpius -o wide

# 4. Verify network policies
kubectl get networkpolicies -n scorpius
```

**Resolution:**
- Restart CoreDNS if DNS issues
- Fix service selector labels
- Update network policies
- Restart affected pods

---

## 🛠️ Low-Severity Incidents

### Slow Database Queries

**Investigation:**
```sql
-- Check slow queries
SELECT query, mean_time, calls 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;

-- Check active queries
SELECT pid, now() - pg_stat_activity.query_start AS duration, query 
FROM pg_stat_activity 
WHERE (now() - pg_stat_activity.query_start) > interval '5 minutes';
```

**Resolution:**
- Add missing indexes
- Optimize query plans
- Consider query caching

---

### Memory Leaks

**Investigation:**
```bash
# 1. Monitor memory usage over time
kubectl top pods -n scorpius --sort-by=memory

# 2. Check memory limits and requests
kubectl describe pod POD_NAME -n scorpius | grep -A 5 Limits

# 3. Get heap dumps (if Java/Node.js)
kubectl exec -it POD_NAME -n scorpius -- jcmd PID GC.run_finalization
```

**Resolution:**
- Restart affected pods
- Analyze heap dumps
- Fix memory leaks in code
- Adjust memory limits

---

## 📊 Monitoring and Alerting

### Key Metrics to Monitor

1. **Application Metrics:**
   - Response time (P50, P95, P99)
   - Error rate
   - Throughput (RPS)
   - Active connections

2. **Infrastructure Metrics:**
   - CPU utilization
   - Memory usage
   - Disk space
   - Network I/O

3. **Business Metrics:**
   - Transaction processing rate
   - User authentication success rate
   - API endpoint availability

### Alert Thresholds

| Metric | Warning | Critical |
|--------|---------|----------|
| CPU Usage | >70% | >85% |
| Memory Usage | >80% | >90% |
| Disk Space | >80% | >90% |
| Error Rate | >5% | >10% |
| Response Time P95 | >2s | >5s |

---

## 🔍 Debugging Tools and Commands

### Kubernetes Debugging

```bash
# Get pod logs
kubectl logs POD_NAME -n scorpius --tail=100 -f

# Describe pod for events
kubectl describe pod POD_NAME -n scorpius

# Execute commands in pod
kubectl exec -it POD_NAME -n scorpius -- /bin/bash

# Port forward for local debugging
kubectl port-forward POD_NAME 8080:8080 -n scorpius

# Check resource usage
kubectl top pods -n scorpius
kubectl top nodes
```

### Database Debugging

```sql
-- Check database connections
SELECT count(*) FROM pg_stat_activity;

-- Check database size
SELECT pg_size_pretty(pg_database_size('scorpius'));

-- Check table sizes
SELECT relname, pg_size_pretty(pg_total_relation_size(relid))
FROM pg_catalog.pg_statio_user_tables
ORDER BY pg_total_relation_size(relid) DESC;

-- Check for locks
SELECT * FROM pg_locks WHERE NOT granted;
```

### Network Debugging

```bash
# Test connectivity between pods
kubectl run -it --rm debug --image=busybox --restart=Never -- wget -qO- http://SERVICE_NAME:PORT/health

# Check DNS resolution
kubectl run -it --rm debug --image=busybox --restart=Never -- nslookup SERVICE_NAME

# Check network policies
kubectl get networkpolicies -n scorpius -o yaml
```

---

## 📝 Post-Incident Actions

### Immediate (Within 1 hour)
1. Confirm issue is resolved
2. Document timeline in incident channel
3. Remove any temporary fixes
4. Update stakeholders

### Short-term (Within 24 hours)
1. Write incident report
2. Identify root cause
3. Create action items for prevention
4. Update runbooks if needed

### Long-term (Within 1 week)
1. Implement preventive measures
2. Conduct blameless post-mortem
3. Update monitoring and alerting
4. Share lessons learned with team

---

## 📞 Escalation Procedures

### Severity Levels

**P0 - Critical (Page immediately)**
- Complete service outage
- Data breach or security incident
- Financial impact >$10k/hour

**P1 - High (Page during business hours)**
- Partial service degradation
- Performance issues affecting users
- Security vulnerabilities

**P2 - Medium (Email notification)**
- Minor service issues
- Non-critical component failures
- Scheduled maintenance needed

**P3 - Low (Ticket only)**
- Documentation updates
- Non-urgent improvements
- Monitoring adjustments

### Contact Escalation

1. **Primary On-Call** (5 minutes)
2. **Secondary On-Call** (10 minutes)
3. **Engineering Manager** (15 minutes)
4. **CTO** (30 minutes for P0 only)

---

## 🔗 Related Resources

- [Grafana Dashboards](https://grafana.scorpius.com)
- [PagerDuty Runbooks](https://scorpius.pagerduty.com)
- [Slack #scorpius-incidents](https://scorpius.slack.com/channels/scorpius-incidents)
- [Post-Mortem Template](./post-mortem-template.md)
- [Security Incident Response](../security/incident-response.md)

---

*Last Updated: December 2024*
*Next Review: March 2025* 