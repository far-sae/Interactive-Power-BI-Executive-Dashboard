# Quick Start Guide - Power BI Executive Dashboard

## ⚡ 5-Minute Setup

### Prerequisites Checklist
- [ ] SQL Server installed and accessible
- [ ] Power BI Desktop installed (latest version)
- [ ] Python 3.8+ installed
- [ ] Power BI Premium workspace or Pro license

---

## 🚀 Rapid Deployment

### Step 1: Database Setup (10 minutes)
```sql
-- Run these scripts in SQL Server Management Studio in order:
1. sql/schema/01_create_database.sql
2. sql/schema/02_create_dimensions.sql
3. sql/schema/03_create_facts.sql
4. sql/sample_data/01_populate_dimdate.sql
5. sql/sample_data/02_populate_dimensions.sql
```

### Step 2: Python Setup (5 minutes)
```bash
cd python
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 3: Power BI Configuration (15 minutes)

**Connect to Data:**
1. Open Power BI Desktop
2. Get Data → SQL Server
3. Server: `your-server-name`, Database: `ExecutiveDashboard_DW`
4. Load all dimension and fact tables

**Create Relationships:**
- Auto-detect relationships (Modeling → Manage Relationships)
- Verify all fact tables connect to dimensions via foreign keys

**Add Measures:**
- Create table named "Measures"
- Copy measures from `power_bi/dax/` folder
- Paste into Power BI

**Mark Date Table:**
- Right-click DimDate → Mark as date table
- Date column: FullDate

### Step 4: Create Basic Dashboard (20 minutes)

**Page 1: Executive Overview**
```
Add these visuals:
1. KPI Cards (Top): Total Revenue, Revenue Growth %, Profit Margin
2. Line Chart: Revenue trend over time (DimDate[FullDate] x [Total Sales])
3. Bar Chart: Sales by Region (DimGeography[Region] x [Total Sales])
4. Donut Chart: Sales by Product Category
5. Slicers: Date range, Region
```

### Step 5: Publish (5 minutes)
```
1. Home → Publish
2. Select workspace (Premium/Pro)
3. Configure data source credentials
4. Set up scheduled refresh (daily at 2 AM)
```

**Total Time: ~55 minutes** ✅

---

## 📊 Essential DAX Measures (Copy & Paste)

```dax
// Basic Sales Metrics
Total Sales = SUM(FactSales[SalesAmount])

Total Orders = DISTINCTCOUNT(FactSales[OrderNumber])

Average Order Value = DIVIDE([Total Sales], [Total Orders], 0)

Gross Profit = SUM(FactSales[GrossProfit])

Gross Profit Margin = DIVIDE([Gross Profit], [Total Sales], 0)

// Time Intelligence
Sales YTD = TOTALYTD([Total Sales], DimDate[FullDate])

Sales Previous Year = CALCULATE([Total Sales], SAMEPERIODLASTYEAR(DimDate[FullDate]))

Sales YoY Growth % = 
DIVIDE([Total Sales] - [Sales Previous Year], [Sales Previous Year], 0) * 100

// Customer Metrics
Active Customers = DISTINCTCOUNT(FactSales[CustomerKey])

Customer Retention Rate = 
VAR PrevCustomers = CALCULATETABLE(VALUES(FactSales[CustomerKey]), DATEADD(DimDate[FullDate], -1, YEAR))
VAR RetainedCustomers = COUNTROWS(INTERSECT(VALUES(FactSales[CustomerKey]), PrevCustomers))
RETURN DIVIDE(RetainedCustomers, COUNTROWS(PrevCustomers), 0)
```

---

## 🔐 Quick RLS Setup

### Create Roles (Modeling → Manage Roles)

**Executive Role:**
```dax
// No filter - sees all data
TRUE()
```

**Regional Manager Role:**
```dax
// Filter DimGeography table
[Region] = LOOKUPVALUE(DimEmployee[Region], DimEmployee[Email], USERPRINCIPALNAME())
```

**Sales Rep Role:**
```dax
// Filter DimEmployee table
[Email] = USERPRINCIPALNAME()
```

### Test RLS
```
Modeling → View As → Select Role → Add email address → OK
```

---

## 📈 Quick Visualizations

### KPI Card
```
Visual: Card
Field: [Total Sales]
Format: $0.0,,M (displays as millions)
```

### Revenue Trend
```
Visual: Line Chart
Axis: DimDate[FullDate]
Values: [Total Sales], [Sales Previous Year]
Legend: None
```

### Regional Performance
```
Visual: Map
Location: DimGeography[Country]
Size: [Total Sales]
Color: [Gross Profit Margin]
```

### Top Products
```
Visual: Bar Chart (Horizontal)
Axis: DimProduct[ProductName]
Values: [Total Sales]
Filters: Top 10 by [Total Sales]
```

---

## 🔄 Quick Refresh Setup

### Manual Refresh
```
Power BI Desktop: Home → Refresh
Power BI Service: Dataset → Refresh now
```

### Scheduled Refresh
```
1. Dataset Settings → Scheduled refresh
2. Toggle ON
3. Frequency: Daily
4. Time: 2:00 AM
5. Send failure notifications to: your-email@company.com
6. Apply
```

---

## 🐛 Quick Troubleshooting

### Cannot connect to SQL Server
```
✓ Check server name: ping your-server-name
✓ Check SQL Server is running: services.msc
✓ Test in SSMS first
✓ Check firewall rules
```

### Refresh fails
```
✓ Verify credentials: Dataset → Settings → Data source credentials
✓ Check data source availability
✓ Review error in refresh history
✓ Test query in SQL Server
```

### Visuals are slow
```
✓ Run Performance Analyzer (View → Performance Analyzer)
✓ Optimize DAX (remove iterators where possible)
✓ Reduce data (use filters, aggregations)
✓ Enable incremental refresh for large tables
```

### RLS not working
```
✓ Test with "View As" in Desktop
✓ Check user assigned to role in Service
✓ Verify USERPRINCIPALNAME() matches user email
✓ Review DAX filter syntax
```

---

## 📞 Quick Help

### Common Tasks

**Export data from visual:**
```
Click "..." on visual → Export data → CSV or Excel
```

**Create bookmark:**
```
View → Bookmarks → Add bookmark → Name it → Use for navigation
```

**Schedule subscription:**
```
Report → Subscribe → Daily/Weekly → Email → Subscribe
```

**Share report:**
```
Share button → Add email addresses → Share
(User needs Power BI Pro license)
```

### Keyboard Shortcuts

- **Ctrl + S**: Save
- **Ctrl + C / Ctrl + V**: Copy/Paste visual
- **Ctrl + G**: Group visuals
- **Ctrl + Shift + C**: Format painter
- **Ctrl + Alt + R**: Refresh data

---

## 📚 Quick Reference Links

**Documentation:**
- Installation Guide: `documentation/setup_guide/installation_guide.md`
- DAX Measures: `power_bi/dax/`
- Python Scripts: `python/`
- RLS Setup: `security/rls_definitions/rls_configuration.md`

**External Resources:**
- [Power BI Docs](https://docs.microsoft.com/power-bi/)
- [DAX Guide](https://dax.guide/)
- [Power BI Community](https://community.powerbi.com/)

**Support:**
- BI Team: bi-team@company.com
- Documentation: See PROJECT_SUMMARY.md
- Issues: [Your ticket system]

---

## ✅ Deployment Checklist

### Day 1 - Foundation
- [ ] SQL database created
- [ ] Sample data loaded
- [ ] Power BI connected to database
- [ ] Basic relationships established

### Day 2 - Development
- [ ] All measures created
- [ ] Visualizations built
- [ ] RLS configured
- [ ] Report published to Service

### Day 3 - Testing
- [ ] Test all visuals load correctly
- [ ] Verify RLS for each role
- [ ] Test data refresh
- [ ] User acceptance testing

### Day 4 - Deployment
- [ ] Production data loaded
- [ ] Scheduled refresh configured
- [ ] Users assigned to roles
- [ ] Training conducted

### Day 5 - Handover
- [ ] Documentation reviewed
- [ ] Support process established
- [ ] Monitoring set up
- [ ] Go-live celebration! 🎉

---

## 🎯 Success Criteria

**Week 1:**
- ✅ All executives can access dashboard
- ✅ Data refreshes successfully daily
- ✅ Key metrics are accurate
- ✅ RLS working for all roles

**Month 1:**
- ✅ 80% user adoption
- ✅ <5% support tickets
- ✅ Positive user feedback
- ✅ Performance <3 second load times

**Quarter 1:**
- ✅ Advanced features adopted
- ✅ Custom views created
- ✅ Mobile usage >20%
- ✅ Measurable business impact

---

**Remember:** Start simple, iterate based on feedback, and continuously optimize!

**Need Help?** Refer to full documentation in `documentation/` folder or contact BI team.

**Good luck with your deployment! 🚀**
