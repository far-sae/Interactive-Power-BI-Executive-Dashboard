/*
 * Executive Dashboard - Dimension Tables Creation
 * Purpose: Creates all dimension tables for the star schema
 * Star Schema Design: Optimized for Power BI performance
 */

USE ExecutiveDashboard_DW;
GO

-- =============================================
-- Dimension: Calendar/Date Dimension
-- =============================================
IF OBJECT_ID('dbo.DimDate', 'U') IS NOT NULL 
    DROP TABLE dbo.DimDate;
GO

CREATE TABLE dbo.DimDate
(
    DateKey INT PRIMARY KEY NOT NULL,
    FullDate DATE NOT NULL,
    DayOfMonth TINYINT NOT NULL,
    DayName VARCHAR(10) NOT NULL,
    DayOfWeek TINYINT NOT NULL,
    DayOfYear SMALLINT NOT NULL,
    WeekOfYear TINYINT NOT NULL,
    MonthName VARCHAR(10) NOT NULL,
    MonthOfYear TINYINT NOT NULL,
    CalendarQuarter TINYINT NOT NULL,
    CalendarYear SMALLINT NOT NULL,
    CalendarYearMonth VARCHAR(7) NOT NULL,
    CalendarYearQuarter VARCHAR(7) NOT NULL,
    FiscalQuarter TINYINT NOT NULL,
    FiscalYear SMALLINT NOT NULL,
    FiscalYearMonth VARCHAR(7) NOT NULL,
    FiscalYearQuarter VARCHAR(7) NOT NULL,
    IsWeekend BIT NOT NULL,
    IsHoliday BIT NOT NULL DEFAULT 0,
    HolidayName VARCHAR(50) NULL
);
GO

CREATE NONCLUSTERED INDEX IX_DimDate_FullDate ON dbo.DimDate(FullDate);
CREATE NONCLUSTERED INDEX IX_DimDate_YearMonth ON dbo.DimDate(CalendarYearMonth);
GO

-- =============================================
-- Dimension: Customer
-- =============================================
IF OBJECT_ID('dbo.DimCustomer', 'U') IS NOT NULL 
    DROP TABLE dbo.DimCustomer;
GO

CREATE TABLE dbo.DimCustomer
(
    CustomerKey INT IDENTITY(1,1) PRIMARY KEY,
    CustomerID VARCHAR(50) NOT NULL UNIQUE,
    CustomerName VARCHAR(200) NOT NULL,
    CustomerType VARCHAR(50) NOT NULL, -- Enterprise, SMB, Individual
    IndustryVertical VARCHAR(100) NULL,
    CompanySize VARCHAR(50) NULL, -- Small, Medium, Large, Enterprise
    Country VARCHAR(100) NOT NULL,
    Region VARCHAR(100) NOT NULL,
    State VARCHAR(100) NULL,
    City VARCHAR(100) NULL,
    PostalCode VARCHAR(20) NULL,
    AccountManager VARCHAR(100) NULL,
    CustomerSegment VARCHAR(50) NOT NULL, -- Premium, Standard, Basic
    AcquisitionDate DATE NOT NULL,
    IsActive BIT NOT NULL DEFAULT 1,
    LifetimeValue DECIMAL(18,2) NULL,
    CreditLimit DECIMAL(18,2) NULL,
    -- SCD Type 2 fields
    EffectiveDate DATE NOT NULL DEFAULT GETDATE(),
    ExpirationDate DATE NULL,
    IsCurrent BIT NOT NULL DEFAULT 1
);
GO

CREATE NONCLUSTERED INDEX IX_DimCustomer_CustomerID ON dbo.DimCustomer(CustomerID);
CREATE NONCLUSTERED INDEX IX_DimCustomer_Region ON dbo.DimCustomer(Region);
CREATE NONCLUSTERED INDEX IX_DimCustomer_Segment ON dbo.DimCustomer(CustomerSegment);
CREATE NONCLUSTERED INDEX IX_DimCustomer_IsCurrent ON dbo.DimCustomer(IsCurrent);
GO

-- =============================================
-- Dimension: Product
-- =============================================
IF OBJECT_ID('dbo.DimProduct', 'U') IS NOT NULL 
    DROP TABLE dbo.DimProduct;
GO

CREATE TABLE dbo.DimProduct
(
    ProductKey INT IDENTITY(1,1) PRIMARY KEY,
    ProductID VARCHAR(50) NOT NULL UNIQUE,
    ProductName VARCHAR(200) NOT NULL,
    ProductCategory VARCHAR(100) NOT NULL,
    ProductSubcategory VARCHAR(100) NULL,
    ProductFamily VARCHAR(100) NULL,
    ProductLine VARCHAR(100) NULL,
    Brand VARCHAR(100) NULL,
    Manufacturer VARCHAR(200) NULL,
    UnitPrice DECIMAL(18,2) NOT NULL,
    StandardCost DECIMAL(18,2) NOT NULL,
    ListPrice DECIMAL(18,2) NOT NULL,
    ProductColor VARCHAR(50) NULL,
    ProductSize VARCHAR(50) NULL,
    ProductWeight DECIMAL(10,2) NULL,
    IsActive BIT NOT NULL DEFAULT 1,
    LaunchDate DATE NULL,
    DiscontinuedDate DATE NULL,
    -- SCD Type 2 fields
    EffectiveDate DATE NOT NULL DEFAULT GETDATE(),
    ExpirationDate DATE NULL,
    IsCurrent BIT NOT NULL DEFAULT 1
);
GO

CREATE NONCLUSTERED INDEX IX_DimProduct_ProductID ON dbo.DimProduct(ProductID);
CREATE NONCLUSTERED INDEX IX_DimProduct_Category ON dbo.DimProduct(ProductCategory);
CREATE NONCLUSTERED INDEX IX_DimProduct_IsCurrent ON dbo.DimProduct(IsCurrent);
GO

-- =============================================
-- Dimension: Employee/Sales Representative
-- =============================================
IF OBJECT_ID('dbo.DimEmployee', 'U') IS NOT NULL 
    DROP TABLE dbo.DimEmployee;
GO

CREATE TABLE dbo.DimEmployee
(
    EmployeeKey INT IDENTITY(1,1) PRIMARY KEY,
    EmployeeID VARCHAR(50) NOT NULL UNIQUE,
    FirstName VARCHAR(100) NOT NULL,
    LastName VARCHAR(100) NOT NULL,
    FullName VARCHAR(200) NOT NULL,
    Email VARCHAR(200) NULL,
    JobTitle VARCHAR(100) NOT NULL,
    Department VARCHAR(100) NOT NULL,
    Division VARCHAR(100) NULL,
    ManagerEmployeeID VARCHAR(50) NULL,
    ManagerName VARCHAR(200) NULL,
    HireDate DATE NOT NULL,
    TerminationDate DATE NULL,
    IsActive BIT NOT NULL DEFAULT 1,
    SalesTerritory VARCHAR(100) NULL,
    Region VARCHAR(100) NULL,
    Office VARCHAR(100) NULL,
    PhoneNumber VARCHAR(50) NULL,
    -- SCD Type 2 fields
    EffectiveDate DATE NOT NULL DEFAULT GETDATE(),
    ExpirationDate DATE NULL,
    IsCurrent BIT NOT NULL DEFAULT 1
);
GO

CREATE NONCLUSTERED INDEX IX_DimEmployee_EmployeeID ON dbo.DimEmployee(EmployeeID);
CREATE NONCLUSTERED INDEX IX_DimEmployee_Department ON dbo.DimEmployee(Department);
CREATE NONCLUSTERED INDEX IX_DimEmployee_IsCurrent ON dbo.DimEmployee(IsCurrent);
GO

-- =============================================
-- Dimension: Geography/Sales Territory
-- =============================================
IF OBJECT_ID('dbo.DimGeography', 'U') IS NOT NULL 
    DROP TABLE dbo.DimGeography;
GO

CREATE TABLE dbo.DimGeography
(
    GeographyKey INT IDENTITY(1,1) PRIMARY KEY,
    GeographyID VARCHAR(50) NOT NULL UNIQUE,
    Country VARCHAR(100) NOT NULL,
    Region VARCHAR(100) NOT NULL,
    SubRegion VARCHAR(100) NULL,
    State VARCHAR(100) NULL,
    City VARCHAR(100) NULL,
    PostalCode VARCHAR(20) NULL,
    SalesTerritory VARCHAR(100) NOT NULL,
    TerritoryManager VARCHAR(200) NULL,
    Continent VARCHAR(50) NOT NULL,
    TimeZone VARCHAR(100) NULL,
    IsActive BIT NOT NULL DEFAULT 1
);
GO

CREATE NONCLUSTERED INDEX IX_DimGeography_Country ON dbo.DimGeography(Country);
CREATE NONCLUSTERED INDEX IX_DimGeography_Territory ON dbo.DimGeography(SalesTerritory);
GO

-- =============================================
-- Dimension: Channel
-- =============================================
IF OBJECT_ID('dbo.DimChannel', 'U') IS NOT NULL 
    DROP TABLE dbo.DimChannel;
GO

CREATE TABLE dbo.DimChannel
(
    ChannelKey INT IDENTITY(1,1) PRIMARY KEY,
    ChannelID VARCHAR(50) NOT NULL UNIQUE,
    ChannelName VARCHAR(100) NOT NULL,
    ChannelType VARCHAR(50) NOT NULL, -- Online, Retail, Partner, Direct
    ChannelCategory VARCHAR(50) NULL,
    IsActive BIT NOT NULL DEFAULT 1
);
GO

-- =============================================
-- Dimension: Account (for financial metrics)
-- =============================================
IF OBJECT_ID('dbo.DimAccount', 'U') IS NOT NULL 
    DROP TABLE dbo.DimAccount;
GO

CREATE TABLE dbo.DimAccount
(
    AccountKey INT IDENTITY(1,1) PRIMARY KEY,
    AccountID VARCHAR(50) NOT NULL UNIQUE,
    AccountName VARCHAR(200) NOT NULL,
    AccountType VARCHAR(50) NOT NULL, -- Asset, Liability, Equity, Revenue, Expense
    AccountCategory VARCHAR(100) NOT NULL,
    AccountSubcategory VARCHAR(100) NULL,
    ParentAccountID VARCHAR(50) NULL,
    AccountLevel TINYINT NOT NULL,
    IsActive BIT NOT NULL DEFAULT 1
);
GO

CREATE NONCLUSTERED INDEX IX_DimAccount_Type ON dbo.DimAccount(AccountType);
GO

PRINT 'All dimension tables created successfully.';
GO
