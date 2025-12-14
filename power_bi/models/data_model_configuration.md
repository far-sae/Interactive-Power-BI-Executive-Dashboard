# Power BI Data Model Configuration Guide

## Overview
This document describes the data model relationships and configuration for the Executive Dashboard.

## Star Schema Architecture

### Fact Tables (Center of Star)
1. **FactSales** - Sales transactions
2. **FactFinancial** - Financial performance data
3. **FactCustomerInteraction** - Customer engagement metrics
4. **FactOperationalMetrics** - Daily operational KPIs
5. **FactSalesPipeline** - Sales opportunities and pipeline

### Dimension Tables (Points of Star)
1. **DimDate** - Calendar and fiscal date attributes
2. **DimCustomer** - Customer master data
3. **DimProduct** - Product catalog
4. **DimEmployee** - Employee and sales rep information
5. **DimGeography** - Geographic and territory data
6. **DimChannel** - Sales channel information
7. **DimAccount** - Financial account hierarchy

## Table Relationships

### FactSales Relationships
```
FactSales [DateKey] --> DimDate [DateKey]
  - Cardinality: Many-to-One
  - Cross-filter direction: Single
  - Filter propagation: From DimDate to FactSales

FactSales [CustomerKey] --> DimCustomer [CustomerKey]
  - Cardinality: Many-to-One
  - Cross-filter direction: Single
  - Filter propagation: From DimCustomer to FactSales

FactSales [ProductKey] --> DimProduct [ProductKey]
  - Cardinality: Many-to-One
  - Cross-filter direction: Single
  - Filter propagation: From DimProduct to FactSales

FactSales [EmployeeKey] --> DimEmployee [EmployeeKey]
  - Cardinality: Many-to-One
  - Cross-filter direction: Single
  - Filter propagation: From DimEmployee to FactSales

FactSales [GeographyKey] --> DimGeography [GeographyKey]
  - Cardinality: Many-to-One
  - Cross-filter direction: Single
  - Filter propagation: From DimGeography to FactSales

FactSales [ChannelKey] --> DimChannel [ChannelKey]
  - Cardinality: Many-to-One
  - Cross-filter direction: Single
  - Filter propagation: From DimChannel to FactSales
```

### FactFinancial Relationships
```
FactFinancial [DateKey] --> DimDate [DateKey]
FactFinancial [AccountKey] --> DimAccount [AccountKey]
FactFinancial [GeographyKey] --> DimGeography [GeographyKey]
```

### FactCustomerInteraction Relationships
```
FactCustomerInteraction [DateKey] --> DimDate [DateKey]
FactCustomerInteraction [CustomerKey] --> DimCustomer [CustomerKey]
FactCustomerInteraction [EmployeeKey] --> DimEmployee [EmployeeKey]
```

### FactOperationalMetrics Relationships
```
FactOperationalMetrics [DateKey] --> DimDate [DateKey]
FactOperationalMetrics [GeographyKey] --> DimGeography [GeographyKey]
```

### FactSalesPipeline Relationships
```
FactSalesPipeline [DateKey] --> DimDate [DateKey]
FactSalesPipeline [CustomerKey] --> DimCustomer [CustomerKey]
FactSalesPipeline [ProductKey] --> DimProduct [ProductKey]
FactSalesPipeline [EmployeeKey] --> DimEmployee [EmployeeKey]
```

## Import Mode vs DirectQuery

### Recommended Configuration:
- **Import Mode**: DimDate, DimGeography, DimChannel, DimAccount, DimEmployee
  - These are smaller dimension tables with infrequent changes
  
- **DirectQuery**: FactSales, FactFinancial (for real-time data)
  - Large fact tables that update frequently
  
- **Aggregations**: Create aggregation tables for common queries
  - Monthly/Quarterly sales summaries
  - Regional performance rollups

## Performance Optimization

### 1. Mark as Date Table
- Mark `DimDate` as a date table
- Set `FullDate` column as the date column

### 2. Create Hierarchies

**Geography Hierarchy:**
```
Continent > Country > Region > State > City
```

**Product Hierarchy:**
```
ProductFamily > ProductLine > ProductCategory > ProductSubcategory > ProductName
```

**Date Hierarchy:**
```
CalendarYear > CalendarQuarter > CalendarYearMonth > FullDate
```

**Employee Hierarchy:**
```
Division > Department > ManagerName > FullName
```

### 3. Set Data Types Correctly
- All key columns: Whole Number
- All monetary amounts: Decimal Number (Fixed decimal)
- Dates: Date or DateTime
- Percentages: Decimal Number

### 4. Column Properties
- Hide technical columns (keys) from report view
- Set default summarization for measure columns to "Don't summarize"
- Format columns appropriately (currency, percentage, etc.)

### 5. Composite Models
- Use composite models to combine Import and DirectQuery for optimal performance
- Enable user-defined aggregations on DirectQuery tables

## Data Refresh Strategy

### Full Refresh
- Run daily at 2:00 AM
- All dimension tables
- Smaller fact tables

### Incremental Refresh
Configure for large fact tables:

**FactSales:**
- Archive: Data older than 2 years
- Incremental: Last 90 days
- Detect data changes: Yes (based on ModifiedDate)

**FactFinancial:**
- Archive: Data older than 3 years
- Incremental: Last 12 months

## Power Query Transformations

### Common Transformations
1. Remove unnecessary columns from source
2. Rename columns to business-friendly names
3. Set correct data types
4. Create calculated columns only when necessary (prefer DAX measures)
5. Merge queries to denormalize where appropriate

### Example M Code for Date Table
```m
let
    Source = Sql.Database("YourServer", "ExecutiveDashboard_DW"),
    DimDate = Source{[Schema="dbo",Item="DimDate"]}[Data],
    FilteredRows = Table.SelectRows(DimDate, each [IsCurrent] = true),
    RemovedColumns = Table.RemoveColumns(FilteredRows,{"EffectiveDate", "ExpirationDate"}),
    ChangedType = Table.TransformColumnTypes(RemovedColumns, {
        {"DateKey", Int64.Type},
        {"FullDate", type date},
        {"CalendarYear", Int64.Type}
    })
in
    ChangedType
```

## Row-Level Security (RLS)

RLS rules are defined in separate files. See `/security/rls_definitions/` for details.

## Best Practices

1. **Use surrogate keys** for all relationships (already implemented)
2. **Minimize bidirectional filtering** - use only when absolutely necessary
3. **Avoid many-to-many relationships** - redesign the model instead
4. **Create measures in a dedicated table** - see DAX measures files
5. **Use variables in DAX** for better performance and readability
6. **Avoid calculated columns** when measures can achieve the same result
7. **Implement aggregation tables** for commonly used summaries
8. **Use query folding** in Power Query whenever possible

## Validation Checklist

- [ ] All relationships are many-to-one (or one-to-many from dimension perspective)
- [ ] DimDate is marked as date table
- [ ] All hierarchies are created
- [ ] Technical columns are hidden
- [ ] Data types are correct
- [ ] Default summarization is set appropriately
- [ ] Incremental refresh is configured for large fact tables
- [ ] Row-level security rules are tested
- [ ] Model size is optimized (< 1GB for Premium)
- [ ] Query performance is acceptable (< 3 seconds for most visuals)
