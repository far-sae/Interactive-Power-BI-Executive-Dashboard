/*
 * Executive Dashboard - Sample Data Generation
 * Purpose: Populates dimension and fact tables with realistic sample data
 * Note: This generates test data for demonstration purposes
 */

USE ExecutiveDashboard_DW;
GO

-- =============================================
-- Populate DimGeography
-- =============================================
SET IDENTITY_INSERT dbo.DimGeography ON;

INSERT INTO dbo.DimGeography (GeographyKey, GeographyID, Country, Region, SubRegion, State, City, PostalCode, SalesTerritory, TerritoryManager, Continent, TimeZone, IsActive)
VALUES
(1, 'GEO-US-EAST', 'United States', 'East', 'Northeast', 'New York', 'New York', '10001', 'US East', 'John Smith', 'North America', 'EST', 1),
(2, 'GEO-US-WEST', 'United States', 'West', 'Pacific', 'California', 'Los Angeles', '90001', 'US West', 'Sarah Johnson', 'North America', 'PST', 1),
(3, 'GEO-US-CENTRAL', 'United States', 'Central', 'Midwest', 'Illinois', 'Chicago', '60601', 'US Central', 'Mike Wilson', 'North America', 'CST', 1),
(4, 'GEO-US-SOUTH', 'United States', 'South', 'Southeast', 'Texas', 'Houston', '77001', 'US South', 'Emily Davis', 'North America', 'CST', 1),
(5, 'GEO-UK', 'United Kingdom', 'Europe', 'Western Europe', 'England', 'London', 'SW1A 1AA', 'UK & Ireland', 'James Brown', 'Europe', 'GMT', 1),
(6, 'GEO-DE', 'Germany', 'Europe', 'Central Europe', 'Bavaria', 'Munich', '80331', 'Central Europe', 'Anna Mueller', 'Europe', 'CET', 1),
(7, 'GEO-FR', 'France', 'Europe', 'Western Europe', 'Île-de-France', 'Paris', '75001', 'France', 'Pierre Dubois', 'Europe', 'CET', 1),
(8, 'GEO-JP', 'Japan', 'Asia Pacific', 'East Asia', 'Tokyo', 'Tokyo', '100-0001', 'Japan', 'Yuki Tanaka', 'Asia', 'JST', 1),
(9, 'GEO-AU', 'Australia', 'Asia Pacific', 'Oceania', 'New South Wales', 'Sydney', '2000', 'Australia & NZ', 'David Lee', 'Oceania', 'AEST', 1),
(10, 'GEO-CA', 'Canada', 'North America', 'NA North', 'Ontario', 'Toronto', 'M5H 2N2', 'Canada', 'Robert Chen', 'North America', 'EST', 1);

SET IDENTITY_INSERT dbo.DimGeography OFF;
GO

-- =============================================
-- Populate DimChannel
-- =============================================
SET IDENTITY_INSERT dbo.DimChannel ON;

INSERT INTO dbo.DimChannel (ChannelKey, ChannelID, ChannelName, ChannelType, ChannelCategory, IsActive)
VALUES
(1, 'CH-ONLINE', 'Online Store', 'Online', 'E-Commerce', 1),
(2, 'CH-RETAIL', 'Retail Stores', 'Retail', 'Physical', 1),
(3, 'CH-PARTNER', 'Partner Network', 'Partner', 'Indirect', 1),
(4, 'CH-DIRECT', 'Direct Sales', 'Direct', 'Direct', 1),
(5, 'CH-MOBILE', 'Mobile App', 'Online', 'E-Commerce', 1),
(6, 'CH-MARKETPLACE', 'Third-Party Marketplace', 'Online', 'Marketplace', 1);

SET IDENTITY_INSERT dbo.DimChannel OFF;
GO

-- =============================================
-- Populate DimAccount (Financial)
-- =============================================
SET IDENTITY_INSERT dbo.DimAccount ON;

INSERT INTO dbo.DimAccount (AccountKey, AccountID, AccountName, AccountType, AccountCategory, AccountSubcategory, ParentAccountID, AccountLevel, IsActive)
VALUES
-- Revenue Accounts
(1, 'REV-001', 'Total Revenue', 'Revenue', 'Operating Revenue', 'Sales Revenue', NULL, 1, 1),
(2, 'REV-002', 'Product Sales', 'Revenue', 'Operating Revenue', 'Sales Revenue', 'REV-001', 2, 1),
(3, 'REV-003', 'Service Revenue', 'Revenue', 'Operating Revenue', 'Service Revenue', 'REV-001', 2, 1),
(4, 'REV-004', 'Subscription Revenue', 'Revenue', 'Operating Revenue', 'Recurring Revenue', 'REV-001', 2, 1),

-- Expense Accounts
(5, 'EXP-001', 'Total Expenses', 'Expense', 'Operating Expenses', 'OPEX', NULL, 1, 1),
(6, 'EXP-002', 'Cost of Goods Sold', 'Expense', 'Direct Costs', 'COGS', 'EXP-001', 2, 1),
(7, 'EXP-003', 'Sales & Marketing', 'Expense', 'Operating Expenses', 'S&M', 'EXP-001', 2, 1),
(8, 'EXP-004', 'Research & Development', 'Expense', 'Operating Expenses', 'R&D', 'EXP-001', 2, 1),
(9, 'EXP-005', 'General & Administrative', 'Expense', 'Operating Expenses', 'G&A', 'EXP-001', 2, 1),

-- Asset Accounts
(10, 'AST-001', 'Total Assets', 'Asset', 'Current Assets', 'Assets', NULL, 1, 1),
(11, 'AST-002', 'Cash & Cash Equivalents', 'Asset', 'Current Assets', 'Liquid Assets', 'AST-001', 2, 1),
(12, 'AST-003', 'Accounts Receivable', 'Asset', 'Current Assets', 'Receivables', 'AST-001', 2, 1),

-- Liability Accounts
(13, 'LIA-001', 'Total Liabilities', 'Liability', 'Current Liabilities', 'Liabilities', NULL, 1, 1),
(14, 'LIA-002', 'Accounts Payable', 'Liability', 'Current Liabilities', 'Payables', 'LIA-001', 2, 1);

SET IDENTITY_INSERT dbo.DimAccount OFF;
GO

-- =============================================
-- Populate DimEmployee (Sample Sales Team)
-- =============================================
SET IDENTITY_INSERT dbo.DimEmployee ON;

INSERT INTO dbo.DimEmployee (EmployeeKey, EmployeeID, FirstName, LastName, FullName, Email, JobTitle, Department, Division, ManagerEmployeeID, ManagerName, HireDate, TerminationDate, IsActive, SalesTerritory, Region, Office, PhoneNumber, EffectiveDate, ExpirationDate, IsCurrent)
VALUES
(1, 'EMP-001', 'Michael', 'Thompson', 'Michael Thompson', 'mthompson@company.com', 'VP of Sales', 'Sales', 'Commercial', NULL, NULL, '2018-01-15', NULL, 1, NULL, 'North America', 'New York', '555-0101', '2018-01-15', NULL, 1),
(2, 'EMP-002', 'Jennifer', 'Martinez', 'Jennifer Martinez', 'jmartinez@company.com', 'Sales Director', 'Sales', 'Commercial', 'EMP-001', 'Michael Thompson', '2019-03-20', NULL, 1, 'US East', 'East', 'New York', '555-0102', '2019-03-20', NULL, 1),
(3, 'EMP-003', 'David', 'Anderson', 'David Anderson', 'danderson@company.com', 'Sales Director', 'Sales', 'Commercial', 'EMP-001', 'Michael Thompson', '2019-05-10', NULL, 1, 'US West', 'West', 'Los Angeles', '555-0103', '2019-05-10', NULL, 1),
(4, 'EMP-004', 'Lisa', 'Wong', 'Lisa Wong', 'lwong@company.com', 'Account Executive', 'Sales', 'Commercial', 'EMP-002', 'Jennifer Martinez', '2020-02-01', NULL, 1, 'US East', 'East', 'New York', '555-0104', '2020-02-01', NULL, 1),
(5, 'EMP-005', 'Robert', 'Garcia', 'Robert Garcia', 'rgarcia@company.com', 'Account Executive', 'Sales', 'Commercial', 'EMP-003', 'David Anderson', '2020-04-15', NULL, 1, 'US West', 'West', 'San Francisco', '555-0105', '2020-04-15', NULL, 1),
(6, 'EMP-006', 'Amanda', 'Collins', 'Amanda Collins', 'acollins@company.com', 'Sales Manager', 'Sales', 'Commercial', 'EMP-001', 'Michael Thompson', '2019-08-01', NULL, 1, 'US Central', 'Central', 'Chicago', '555-0106', '2019-08-01', NULL, 1),
(7, 'EMP-007', 'Christopher', 'Taylor', 'Christopher Taylor', 'ctaylor@company.com', 'Account Executive', 'Sales', 'Commercial', 'EMP-006', 'Amanda Collins', '2020-06-20', NULL, 1, 'US Central', 'Central', 'Chicago', '555-0107', '2020-06-20', NULL, 1),
(8, 'EMP-008', 'Sarah', 'Parker', 'Sarah Parker', 'sparker@company.com', 'International Sales Director', 'Sales', 'International', 'EMP-001', 'Michael Thompson', '2018-11-01', NULL, 1, 'Europe', 'Europe', 'London', '555-0108', '2018-11-01', NULL, 1),
(9, 'EMP-009', 'Thomas', 'Schmidt', 'Thomas Schmidt', 'tschmidt@company.com', 'Account Executive', 'Sales', 'International', 'EMP-008', 'Sarah Parker', '2020-09-15', NULL, 1, 'Central Europe', 'Europe', 'Munich', '555-0109', '2020-09-15', NULL, 1),
(10, 'EMP-010', 'Maria', 'Rodriguez', 'Maria Rodriguez', 'mrodriguez@company.com', 'Customer Success Manager', 'Customer Success', 'Commercial', NULL, NULL, '2019-07-01', NULL, 1, NULL, 'North America', 'New York', '555-0110', '2019-07-01', NULL, 1);

SET IDENTITY_INSERT dbo.DimEmployee OFF;
GO

PRINT 'Sample dimension data populated successfully.';
GO
