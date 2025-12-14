# Power BI Premium Configuration Guide

## Overview
This document outlines the Power BI Premium configuration for optimal performance and scalability.

## Premium Capacity Planning

### Capacity SKU Recommendations

**Small Organization (< 500 users)**
- **SKU**: P1 (EM3 for testing)
- **V-Cores**: 8
- **Memory**: 25 GB
- **Max Concurrent Refreshes**: 6
- **Estimated Cost**: ~$5,000/month

**Medium Organization (500-2,000 users)**
- **SKU**: P2
- **V-Cores**: 16
- **Memory**: 50 GB
- **Max Concurrent Refreshes**: 12
- **Estimated Cost**: ~$10,000/month

**Large Enterprise (2,000+ users)**
- **SKU**: P3 or higher
- **V-Cores**: 32+
- **Memory**: 100+ GB
- **Max Concurrent Refreshes**: 24+
- **Estimated Cost**: $20,000+/month

## Incremental Refresh Configuration

### Setup Steps

1. **Define Parameters in Power Query**
```m
// RangeStart Parameter
RangeStart = DateTime.From("1/1/2020")

// RangeEnd Parameter  
RangeEnd = DateTime.Now()
```

2. **Filter Table Using Parameters**
```m
let
    Source = Sql.Database("server", "database"),
    FilteredData = Table.SelectRows(Source, 
        each [OrderDate] >= RangeStart and [OrderDate] < RangeEnd)
in
    FilteredData
```

3. **Configure Incremental Refresh Policy**

**FactSales Table:**
- Archive data: Starting 2 years before refresh date
- Incrementally refresh: Last 90 days
- Detect data changes: Yes (based on ModifiedDate column)
- Only refresh complete days: Yes

**FactFinancial Table:**
- Archive data: Starting 3 years before refresh date
- Incrementally refresh: Last 12 months
- Detect data changes: Yes
- Only refresh complete periods: Yes (months)

**FactOperationalMetrics Table:**
- Archive data: Starting 1 year before refresh date
- Incrementally refresh: Last 30 days
- Detect data changes: Yes

## Refresh Schedule Configuration

### Production Schedule

**Weekdays (Monday-Friday):**
- 02:00 - Full refresh (dimensions)
- 06:00 - Incremental refresh (facts)
- 10:00 - Incremental refresh (facts)
- 14:00 - Incremental refresh (facts)
- 18:00 - Incremental refresh (facts)
- 22:00 - Incremental refresh (facts)

**Weekends (Saturday-Sunday):**
- 02:00 - Full refresh (all tables)
- 14:00 - Incremental refresh (facts)

### Refresh Failure Handling

**Retry Policy:**
- Max retries: 3
- Retry interval: 10 minutes
- Exponential backoff: Enabled

**Notification Settings:**
- Email on failure: Enabled
- Recipients: bi-team@company.com, data-admin@company.com
- Include error details: Yes

## Performance Optimization

### 1. Query Optimization

**Implement Query Folding:**
- Push filters to data source
- Use native SQL queries where possible
- Avoid calculated columns in Power Query

**Example - Optimized Query:**
```m
let
    Source = Sql.Database("server", "database"),
    Navigation = Source{[Schema="dbo",Item="FactSales"]}[Data],
    FilteredRows = Table.SelectRows(Navigation, 
        each [OrderDate] >= RangeStart and [OrderDate] < RangeEnd),
    RemovedColumns = Table.RemoveColumns(FilteredRows, 
        {"Unnecessary_Column1", "Unnecessary_Column2"})
in
    RemovedColumns
```

### 2. Data Model Optimization

**Column Storage:**
- Remove unused columns
- Use appropriate data types (smallest possible)
- Disable auto date/time hierarchy for unused columns

**Relationships:**
- Single direction filtering where possible
- Avoid bidirectional unless absolutely necessary
- Use surrogate keys (integer) for relationships

**Aggregations:**
```dax
// Create aggregation table for common queries
SalesAggregated = 
SUMMARIZE(
    FactSales,
    DimDate[CalendarYearMonth],
    DimProduct[ProductCategory],
    DimGeography[Region],
    "TotalSales", SUM(FactSales[SalesAmount]),
    "TotalQuantity", SUM(FactSales[Quantity]),
    "OrderCount", DISTINCTCOUNT(FactSales[OrderNumber])
)
```

### 3. Composite Model Configuration

**Import vs DirectQuery Strategy:**

**Import Mode:**
- DimDate (small, static)
- DimGeography (small, infrequent changes)
- DimChannel (small, static)
- Monthly/Quarterly aggregations

**DirectQuery:**
- FactSales (large, real-time updates needed)
- FactFinancial (large, frequent updates)

**Dual Mode:**
- DimCustomer (moderate size, used in both contexts)
- DimProduct (moderate size, used in both contexts)

## Large Dataset Strategies

### 1. Partitioning Strategy

Partition large tables by:
- Date (monthly partitions for fact tables)
- Region (for globally distributed data)
- Product category (for product-centric analysis)

### 2. Large Dataset Storage Format

Enable Large Dataset Storage Format for:
- Better compression
- Faster query performance
- Support for datasets > 10 GB

**Enable via PowerShell:**
```powershell
Set-PowerBIDataset -DatasetId "your-dataset-id" 
    -LargeStorageFormat Enabled
```

### 3. Memory Management

**Monitor Memory Usage:**
- Set up capacity monitoring
- Configure alerts for high memory usage (>80%)
- Implement auto-pause for idle datasets

## Power BI Embedded Configuration

### Embedding for External Users

**Capacity Assignment:**
- Use dedicated P1+ capacity for embedded scenarios
- Separate from internal reporting capacity

**Row-Level Security:**
- Implement dynamic RLS based on embedded user context
- Use effective user name in embedded scenarios

**Performance Considerations:**
- Pre-load frequently accessed reports
- Implement caching strategies
- Use report pagination for large datasets

## Monitoring & Alerts

### Capacity Metrics to Monitor

**Key Metrics:**
- CPU percentage (alert if > 80% for 5 minutes)
- Memory percentage (alert if > 85%)
- DQ/LC per second (DirectQuery/Live Connection)
- Refresh duration
- Query duration

**Power BI Metrics App:**
- Install and configure
- Create custom alerts
- Set up automated reports

### Performance Analyzer

**Regular Analysis:**
- Weekly performance review
- Identify slow visuals
- Optimize DAX queries
- Review data source performance

## Disaster Recovery

### Backup Strategy

**Dataset Backup:**
- Export PBIX files weekly
- Store in Azure Blob Storage
- Maintain 30-day retention

**Configuration Backup:**
- Document all RLS rules
- Export workspace settings
- Backup gateway configurations

### Recovery Procedures

**Dataset Recovery:**
1. Restore PBIX from backup
2. Reconfigure data source connections
3. Republish to workspace
4. Reapply RLS and sharing permissions
5. Test all functionality

**Expected RTO:** 2 hours
**Expected RPO:** 24 hours (daily backups)

## Compliance & Governance

### Data Classification

**Sensitivity Labels:**
- **Highly Confidential**: Executive financial data
- **Confidential**: Department-level metrics
- **Internal**: General business metrics
- **Public**: Published reports

**Apply via:**
```powershell
Set-PowerBIDataset -DatasetId "your-dataset-id" 
    -SensitivityLabel "Highly Confidential"
```

### Audit Logging

**Enable Audit Logs:**
- Track all report access
- Monitor data exports
- Log sharing activities
- Review quarterly

**Log Retention:**
- 90 days in Power BI Service
- Archive to Azure Log Analytics for long-term storage

## Cost Optimization

### Cost Reduction Strategies

1. **Right-size capacity:** Monitor usage and adjust SKU
2. **Implement auto-pause:** For non-production workspaces
3. **Use Premium Per User (PPU):** For smaller user groups
4. **Optimize refresh frequency:** Balance freshness vs cost
5. **Consolidate workspaces:** Reduce capacity sprawl

### Cost Monitoring

**Monthly Review:**
- Capacity utilization reports
- Cost per user analysis
- Identify unused datasets
- Optimize refresh schedules

---

## Implementation Checklist

- [ ] Premium capacity provisioned
- [ ] Incremental refresh configured
- [ ] Refresh schedules set up
- [ ] Performance optimizations applied
- [ ] Monitoring and alerts configured
- [ ] Backup procedures established
- [ ] Disaster recovery tested
- [ ] Compliance labels applied
- [ ] Audit logging enabled
- [ ] Cost optimization reviewed
- [ ] Documentation completed
- [ ] Team training conducted
