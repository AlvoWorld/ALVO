# Data Engineer Heartbeat Checklist

## Daily Checks (Every 2 hours)

### 🔴 Critical Alerts
- [ ] OpenRouter API key validity (check for 401 errors)
- [ ] Database connection health (PostgreSQL & SQLite)
- [ ] API server responsiveness (port 8000)
- [ ] Scheduler execution status

### 🟡 Warning Checks
- [ ] Agent heartbeat success rate (>80%)
- [ ] Error agent investigation (persistent errors)
- [ ] Disk space usage (<85%)
- [ ] Memory usage (<85%)
- [ ] CPU load average (<2.0)

### 🟢 Info Checks
- [ ] Log file sizes and rotation
- [ ] ETL pipeline status (if configured)
- [ ] Data warehouse connectivity
- [ ] Backup verification

## Weekly Checks

### Data Pipeline Health
- [ ] Review ETL job success/failure rates
- [ ] Validate data freshness in warehouses
- [ ] Check for schema drift in data sources
- [ ] Monitor data quality metrics

### Storage Systems
- [ ] Database vacuum/analyze (PostgreSQL)
- [ ] Index usage statistics
- [ ] Backup integrity verification
- [ ] Archive old logs/metrics

### API Integrations
- [ ] Test external API connectivity
- [ ] Review API rate limit usage
- [ ] Validate webhook endpoints
- [ ] Check authentication token expiration

## Monthly Checks

### Architecture Review
- [ ] Data model review and optimization
- [ ] ETL pipeline performance analysis
- [ ] Storage cost optimization
- [ ] Security audit of data access

### Documentation
- [ ] Update data dictionary
- [ ] Review data lineage documentation
- [ ] Update runbooks for common issues
- [ ] Capacity planning review

## Incident Response

### When OpenRouter API fails (401):
1. Immediately notify CTO/DevOps
2. Check environment variables for API key
3. Verify key validity in OpenRouter dashboard
4. Coordinate key rotation if needed
5. Monitor agent recovery after fix

### When database errors occur:
1. Check for transaction isolation issues
2. Review connection pool status
3. Examine recent schema changes
4. Consult DBA for deep investigation

### When agent heartbeats fail:
1. Check individual agent logs
2. Verify LLM API connectivity
3. Validate agent-specific configurations
4. Escalate to appropriate domain expert

## Metrics to Track

### Pipeline Metrics
- ETL job success rate (%)
- Data latency (source to warehouse)
- Data volume processed (daily)
- Error rates by pipeline stage

### System Metrics
- Database query performance (avg response time)
- Connection pool utilization
- Storage I/O wait times
- Network API call latency

### Data Quality Metrics
- Completeness (% null values)
- Validity (% conforming to schema)
- Consistency (cross-system checks)
- Timeliness (data freshness)

## Contacts for Escalation

- **CTO**: OpenRouter API key issues, budget approvals
- **DevOps Engineer**: API key rotation, infrastructure issues
- **Database Administrator**: Persistent DB errors, performance issues
- **Data Analyst**: Data quality concerns, validation requirements

---
*Last updated: 2026-03-30 01:52:46 UTC*
*Next review: 2026-04-05*