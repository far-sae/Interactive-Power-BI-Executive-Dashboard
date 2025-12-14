# Power BI Executive Dashboard - Setup Guide

## Prerequisites

### Software Requirements
- Power BI Desktop (latest version)
- SQL Server Management Studio (SSMS) 18+
- Python 3.8 or higher
- Git (for version control)
- Power BI Premium workspace (or Pro with PPU)

### Access Requirements
- SQL Server database access (read/write)
- Power BI Service account (with Premium capacity)
- Azure Active Directory account (for RLS)
- Power BI REST API permissions
- SMTP server access (for email automation)

### Permissions Needed
- SQL Server: db_datareader, db_datawriter
- Power BI: Workspace Admin or Member
- Azure AD: Application registration rights
- Network: Firewall rules for SQL Server access

---

## Installation Steps

### Step 1: SQL Server Database Setup

**1.1 Create Database**
```bash
# Navigate to SQL scripts folder
cd "sql/schema"

# Run scripts in order in SQL Server Management Studio (SSMS)
# Connect to your SQL Server instance
```

Run these scripts in sequence:
1. `01_create_database.sql` - Creates ExecutiveDashboard_DW database
2. `02_create_dimensions.sql` - Creates dimension tables
3. `03_create_facts.sql` - Creates fact tables

**1.2 Populate Sample Data**
```bash
cd "../sample_data"
```

Run these scripts:
1. `01_populate_dimdate.sql` - Populates date dimension (2020-2030)
2. `02_populate_dimensions.sql` - Populates sample dimension data

**1.3 Create Stored Procedures**
```bash
cd "../stored_procedures"
```

Run:
1. `usp_etl_procedures.sql` - Creates ETL and utility procedures

**1.4 Verify Installation**
```sql
-- Check all tables exist
SELECT 
    SCHEMA_NAME(schema_id) AS SchemaName,
    name AS TableName,
    create_date
FROM sys.tables
ORDER BY name;

-- Check row counts
EXEC sp_MSforeachtable 'SELECT ''?'' AS TableName, COUNT(*) AS RowCount FROM ?';

-- Run data quality check
EXEC dbo.usp_DataQualityCheck;
```

---

### Step 2: Python Environment Setup

**2.1 Create Virtual Environment**
```bash
# Navigate to python folder
cd python

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate
```

**2.2 Install Dependencies**
```bash
# Install required packages
pip install -r requirements.txt

# Verify installation
pip list
```

**2.3 Test Python Scripts**
```bash
# Test anomaly detection
python anomaly_detection/anomaly_detector.py

# Test trend analysis
python trend_analysis/trend_analyzer.py

# Test data utilities
python data_processing/data_utilities.py
```

---

### Step 3: Power BI Desktop Configuration

**3.1 Open Power BI Desktop**
1. Launch Power BI Desktop
2. File → Options → Python scripting
3. Set Python home directory to your virtual environment

**3.2 Connect to SQL Server**
1. Get Data → SQL Server
2. Server: `your-server-name`
3. Database: `ExecutiveDashboard_DW`
4. Data Connectivity mode: Import (or DirectQuery for large tables)
5. Click OK

**3.3 Load Tables**

Select these tables:
- All Dimension tables (DimDate, DimCustomer, DimProduct, etc.)
- All Fact tables (FactSales, FactFinancial, etc.)

Click "Load" to import data.

**3.4 Create Relationships**

In Model View, create relationships:
```
FactSales[DateKey] → DimDate[DateKey] (Many-to-One)
FactSales[CustomerKey] → DimCustomer[CustomerKey] (Many-to-One)
FactSales[ProductKey] → DimProduct[ProductKey] (Many-to-One)
FactSales[EmployeeKey] → DimEmployee[EmployeeKey] (Many-to-One)
FactSales[GeographyKey] → DimGeography[GeographyKey] (Many-to-One)
FactSales[ChannelKey] → DimChannel[ChannelKey] (Many-to-One)

FactFinancial[DateKey] → DimDate[DateKey] (Many-to-One)
FactFinancial[AccountKey] → DimAccount[AccountKey] (Many-to-One)
FactFinancial[GeographyKey] → DimGeography[GeographyKey] (Many-to-One)

FactCustomerInteraction[DateKey] → DimDate[DateKey] (Many-to-One)
FactCustomerInteraction[CustomerKey] → DimCustomer[CustomerKey] (Many-to-One)
FactCustomerInteraction[EmployeeKey] → DimEmployee[EmployeeKey] (Many-to-One)

FactOperationalMetrics[DateKey] → DimDate[DateKey] (Many-to-One)
FactOperationalMetrics[GeographyKey] → DimGeography[GeographyKey] (Many-to-One)

FactSalesPipeline[DateKey] → DimDate[DateKey] (Many-to-One)
FactSalesPipeline[CustomerKey] → DimCustomer[CustomerKey] (Many-to-One)
FactSalesPipeline[ProductKey] → DimProduct[ProductKey] (Many-to-One)
FactSalesPipeline[EmployeeKey] → DimEmployee[EmployeeKey] (Many-to-One)
```

**3.5 Configure Date Table**
1. Right-click DimDate table
2. Select "Mark as date table"
3. Choose "FullDate" as the date column

**3.6 Create Measures**

Create a new table called "Measures":
1. Home → Enter Data → Create empty table named "Measures"
2. Copy DAX measures from `/power_bi/dax/` folder:
   - `sales_measures.dax`
   - `financial_measures.dax`
   - `customer_operational_measures.dax`

3. Paste measures into Power BI (right-click Measures table → New Measure)

**3.7 Create Hierarchies**

**Date Hierarchy:**
1. In DimDate, create hierarchy: Calendar
2. Add levels: CalendarYear → CalendarQuarter → CalendarYearMonth → FullDate

**Geography Hierarchy:**
1. In DimGeography, create hierarchy: Location
2. Add levels: Continent → Country → Region → State → City

**Product Hierarchy:**
1. In DimProduct, create hierarchy: Product
2. Add levels: ProductFamily → ProductCategory → ProductSubcategory → ProductName

**3.8 Format Columns**
- Currency columns: Format as Currency ($)
- Percentage columns: Format as Percentage (%)
- Date columns: Format as Date (MM/DD/YYYY)
- Hide all key columns from report view

---

### Step 4: Create Visualizations

Refer to `/power_bi/templates/dashboard_design_guide.md` for detailed visualization specifications.

**Create these pages:**
1. Executive Overview
2. Financial Performance
3. Sales Analytics
4. Customer Insights
5. Operational Metrics
6. Predictive Analytics

For each page:
1. Insert → New Page
2. Add visuals as specified in design guide
3. Configure slicers and filters
4. Set up cross-filtering
5. Add bookmarks for saved views

---

### Step 5: Implement Row-Level Security

**5.1 Create Roles**
1. Modeling → Manage Roles
2. Create these roles:
   - Executive (no filters)
   - Regional_Manager
   - Department_Head
   - Sales_Representative
   - Finance_Team
   - Analyst

**5.2 Add DAX Filters**

For each role, add filters as specified in `/security/rls_definitions/rls_configuration.md`

Example for Regional_Manager:
```dax
-- On DimGeography table
[Region] = LOOKUPVALUE(
    DimEmployee[Region],
    DimEmployee[Email],
    USERPRINCIPALNAME()
)
```

**5.3 Test RLS**
1. Modeling → View As
2. Select role to test
3. Add specific user email
4. Verify correct data visibility

---

### Step 6: Configure Incremental Refresh

**6.1 Create Parameters**
1. Transform Data (Power Query)
2. Manage Parameters → New
3. Create "RangeStart" parameter (Date/Time, Default: 1/1/2020)
4. Create "RangeEnd" parameter (Date/Time, Default: Current Date)

**6.2 Filter Tables**

For FactSales:
```m
= Table.SelectRows(Source, 
    each [OrderDate] >= RangeStart and [OrderDate] < RangeEnd)
```

**6.3 Set Incremental Refresh Policy**
1. Right-click FactSales → Incremental Refresh
2. Configure:
   - Archive data: 2 years before refresh
   - Incrementally refresh: Last 90 days
   - Detect data changes: Yes (ModifiedDate)
3. Apply

Repeat for other fact tables with appropriate settings.

---

### Step 7: Publish to Power BI Service

**7.1 Publish Report**
1. Home → Publish
2. Select Power BI Premium workspace
3. Wait for upload to complete
4. Click "Open in Power BI"

**7.2 Configure Data Source Credentials**
1. In Power BI Service, go to dataset Settings
2. Data source credentials → Edit credentials
3. Authentication method: Windows or Database
4. Enter credentials
5. Privacy level: Organizational
6. Click "Sign in"

**7.3 Configure Scheduled Refresh**
1. Dataset Settings → Scheduled refresh
2. Enable: Keep your data up to date
3. Refresh frequency: Daily
4. Time zones: Select your timezone
5. Add refresh times (e.g., 2:00 AM, 6:00 AM, 10:00 AM, 2:00 PM, 6:00 PM)
6. Email notifications: Enabled
7. Click "Apply"

**7.4 Assign RLS Roles to Users**
1. Navigate to workspace
2. Click "..." on dataset → Security
3. For each role, add users/groups
4. Save

---

### Step 8: Set Up Automation

**8.1 Configure Power BI API Access**
1. Go to Azure Portal
2. Azure Active Directory → App registrations → New registration
3. Name: "PowerBI Dashboard Automation"
4. Register application
5. Copy Application (client) ID and Tenant ID
6. Certificates & secrets → New client secret
7. Copy secret value

**8.2 Grant API Permissions**
1. API permissions → Add permission
2. Power BI Service → Delegated permissions
3. Select required permissions:
   - Dataset.Read.All
   - Dataset.ReadWrite.All
   - Report.Read.All
4. Grant admin consent

**8.3 Configure Automation Scripts**

Update `/automation/refresh_schedules/powerbi_refresh_automation.py`:
```python
CLIENT_ID = "your-client-id"
CLIENT_SECRET = "your-client-secret"
TENANT_ID = "your-tenant-id"
```

Update `/automation/email_distribution/email_automation.py`:
```python
SMTP_SERVER = "smtp.office365.com"
SENDER_EMAIL = "bi-reports@company.com"
SENDER_PASSWORD = "your-password"
```

**8.4 Schedule Automation**

**Windows Task Scheduler:**
```bash
# Create task to run refresh script daily
schtasks /create /tn "PowerBI Refresh" /tr "python powerbi_refresh_automation.py" /sc daily /st 01:00
```

**Linux Cron:**
```bash
# Add to crontab
0 1 * * * /path/to/python /path/to/powerbi_refresh_automation.py
```

---

### Step 9: Enable Advanced Analytics

**9.1 Enable Python Visuals**
1. In Power BI Desktop: File → Options → Python scripting
2. In Power BI Service: Admin portal → Python visuals → Enabled

**9.2 Add Python Visuals**
1. Insert → Python visual
2. Add required fields to Values
3. Paste Python script from `/python/` folder
4. Click Run

Example anomaly detection visual:
```python
import pandas as pd
from anomaly_detection.anomaly_detector import AnomalyDetector

# dataset is automatically available as pandas DataFrame
detector = AnomalyDetector()
result = detector.detect_all(dataset, ['SalesAmount'], 'Date')

# Create visualization
import matplotlib.pyplot as plt
plt.figure(figsize=(12, 6))
plt.plot(result['Date'], result['SalesAmount'], label='Sales')
plt.scatter(result[result['is_anomaly_consensus']]['Date'],
           result[result['is_anomaly_consensus']]['SalesAmount'],
           color='red', s=100, label='Anomaly')
plt.legend()
plt.show()
```

---

### Step 10: Testing & Validation

**10.1 Data Validation**
- [ ] Verify all tables loaded correctly
- [ ] Check relationship cardinality
- [ ] Validate measure calculations
- [ ] Test RLS for each role
- [ ] Confirm incremental refresh working

**10.2 Performance Testing**
- [ ] Run Performance Analyzer
- [ ] Optimize slow visuals
- [ ] Review DAX query plans
- [ ] Test with production data volumes

**10.3 User Acceptance Testing**
- [ ] Test with executive sponsors
- [ ] Gather feedback on visualizations
- [ ] Verify all drill-through paths work
- [ ] Test on mobile devices
- [ ] Validate email distributions

---

## Troubleshooting

### Common Issues

**Issue: Cannot connect to SQL Server**
- Check firewall rules
- Verify SQL Server is running
- Confirm TCP/IP protocol enabled
- Test connection in SSMS first

**Issue: Refresh fails**
- Check data source credentials
- Verify network connectivity
- Review error message in refresh history
- Check SQL Server logs

**Issue: RLS not working**
- Verify user email matches USERPRINCIPALNAME()
- Check role assignment in Power BI Service
- Test with "View As" in Desktop
- Review DAX filter syntax

**Issue: Python visuals not working**
- Verify Python installed correctly
- Check package versions
- Enable Python visuals in admin portal
- Review script errors in Power BI

---

## Next Steps

1. **Monitor Performance**: Set up capacity monitoring
2. **User Training**: Conduct training sessions
3. **Documentation**: Maintain updated documentation
4. **Feedback Loop**: Establish feedback mechanism
5. **Continuous Improvement**: Regular review and optimization

---

## Support Contacts

- **BI Team**: bi-team@company.com
- **Database Admin**: dba@company.com
- **Power BI Admin**: powerbi-admin@company.com
- **IT Support**: support@company.com

---

## Additional Resources

- [Power BI Documentation](https://docs.microsoft.com/power-bi/)
- [DAX Reference](https://dax.guide/)
- [SQL Server Documentation](https://docs.microsoft.com/sql/)
- Internal Wiki: [Your company wiki URL]
