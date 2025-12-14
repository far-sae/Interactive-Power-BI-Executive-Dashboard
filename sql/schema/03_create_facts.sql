/*
 * Executive Dashboard - Fact Tables Creation
 * Purpose: Creates all fact tables for the star schema
 * Optimized for: High-performance aggregations and Power BI queries
 */

USE ExecutiveDashboard_DW;
GO

-- =============================================
-- Fact: Sales Transactions
-- =============================================
IF OBJECT_ID('dbo.FactSales', 'U') IS NOT NULL 
    DROP TABLE dbo.FactSales;
GO

CREATE TABLE dbo.FactSales
(
    SalesKey BIGINT IDENTITY(1,1) PRIMARY KEY,
    DateKey INT NOT NULL,
    CustomerKey INT NOT NULL,
    ProductKey INT NOT NULL,
    EmployeeKey INT NOT NULL,
    GeographyKey INT NOT NULL,
    ChannelKey INT NOT NULL,
    
    -- Transaction Identifiers
    OrderNumber VARCHAR(50) NOT NULL,
    OrderLineNumber SMALLINT NOT NULL,
    InvoiceNumber VARCHAR(50) NULL,
    
    -- Measures
    Quantity DECIMAL(18,2) NOT NULL,
    UnitPrice DECIMAL(18,2) NOT NULL,
    UnitCost DECIMAL(18,2) NOT NULL,
    DiscountAmount DECIMAL(18,2) NOT NULL DEFAULT 0,
    DiscountPercent DECIMAL(5,2) NOT NULL DEFAULT 0,
    
    -- Calculated Measures
    SalesAmount AS (Quantity * UnitPrice),
    TotalCost AS (Quantity * UnitCost),
    GrossProfit AS (Quantity * UnitPrice - Quantity * UnitCost),
    NetSales AS (Quantity * UnitPrice - DiscountAmount),
    
    -- Additional Metrics
    TaxAmount DECIMAL(18,2) NOT NULL DEFAULT 0,
    FreightAmount DECIMAL(18,2) NOT NULL DEFAULT 0,
    TotalAmount AS (Quantity * UnitPrice - DiscountAmount + TaxAmount + FreightAmount),
    
    -- Audit Fields
    OrderDate DATETIME NOT NULL,
    ShipDate DATETIME NULL,
    DueDate DATETIME NULL,
    CreatedDate DATETIME NOT NULL DEFAULT GETDATE(),
    ModifiedDate DATETIME NOT NULL DEFAULT GETDATE(),
    
    -- Foreign Keys
    CONSTRAINT FK_FactSales_DimDate FOREIGN KEY (DateKey) 
        REFERENCES dbo.DimDate(DateKey),
    CONSTRAINT FK_FactSales_DimCustomer FOREIGN KEY (CustomerKey) 
        REFERENCES dbo.DimCustomer(CustomerKey),
    CONSTRAINT FK_FactSales_DimProduct FOREIGN KEY (ProductKey) 
        REFERENCES dbo.DimProduct(ProductKey),
    CONSTRAINT FK_FactSales_DimEmployee FOREIGN KEY (EmployeeKey) 
        REFERENCES dbo.DimEmployee(EmployeeKey),
    CONSTRAINT FK_FactSales_DimGeography FOREIGN KEY (GeographyKey) 
        REFERENCES dbo.DimGeography(GeographyKey),
    CONSTRAINT FK_FactSales_DimChannel FOREIGN KEY (ChannelKey) 
        REFERENCES dbo.DimChannel(ChannelKey)
);
GO

-- Indexes for optimal query performance
CREATE NONCLUSTERED INDEX IX_FactSales_DateKey ON dbo.FactSales(DateKey);
CREATE NONCLUSTERED INDEX IX_FactSales_CustomerKey ON dbo.FactSales(CustomerKey);
CREATE NONCLUSTERED INDEX IX_FactSales_ProductKey ON dbo.FactSales(ProductKey);
CREATE NONCLUSTERED INDEX IX_FactSales_OrderNumber ON dbo.FactSales(OrderNumber);
CREATE NONCLUSTERED INDEX IX_FactSales_OrderDate ON dbo.FactSales(OrderDate);
GO

-- =============================================
-- Fact: Financial Performance
-- =============================================
IF OBJECT_ID('dbo.FactFinancial', 'U') IS NOT NULL 
    DROP TABLE dbo.FactFinancial;
GO

CREATE TABLE dbo.FactFinancial
(
    FinancialKey BIGINT IDENTITY(1,1) PRIMARY KEY,
    DateKey INT NOT NULL,
    AccountKey INT NOT NULL,
    GeographyKey INT NOT NULL,
    
    -- Measures
    Amount DECIMAL(18,2) NOT NULL,
    Budget DECIMAL(18,2) NULL,
    Forecast DECIMAL(18,2) NULL,
    
    -- Calculated Measures
    Variance AS (Amount - Budget),
    VariancePercent AS (CASE WHEN Budget <> 0 THEN ((Amount - Budget) / Budget) * 100 ELSE 0 END),
    
    -- Audit Fields
    FiscalPeriod VARCHAR(7) NOT NULL,
    CreatedDate DATETIME NOT NULL DEFAULT GETDATE(),
    ModifiedDate DATETIME NOT NULL DEFAULT GETDATE(),
    
    -- Foreign Keys
    CONSTRAINT FK_FactFinancial_DimDate FOREIGN KEY (DateKey) 
        REFERENCES dbo.DimDate(DateKey),
    CONSTRAINT FK_FactFinancial_DimAccount FOREIGN KEY (AccountKey) 
        REFERENCES dbo.DimAccount(AccountKey),
    CONSTRAINT FK_FactFinancial_DimGeography FOREIGN KEY (GeographyKey) 
        REFERENCES dbo.DimGeography(GeographyKey)
);
GO

CREATE NONCLUSTERED INDEX IX_FactFinancial_DateKey ON dbo.FactFinancial(DateKey);
CREATE NONCLUSTERED INDEX IX_FactFinancial_AccountKey ON dbo.FactFinancial(AccountKey);
CREATE NONCLUSTERED INDEX IX_FactFinancial_FiscalPeriod ON dbo.FactFinancial(FiscalPeriod);
GO

-- =============================================
-- Fact: Customer Interactions
-- =============================================
IF OBJECT_ID('dbo.FactCustomerInteraction', 'U') IS NOT NULL 
    DROP TABLE dbo.FactCustomerInteraction;
GO

CREATE TABLE dbo.FactCustomerInteraction
(
    InteractionKey BIGINT IDENTITY(1,1) PRIMARY KEY,
    DateKey INT NOT NULL,
    CustomerKey INT NOT NULL,
    EmployeeKey INT NOT NULL,
    
    -- Interaction Details
    InteractionID VARCHAR(50) NOT NULL UNIQUE,
    InteractionType VARCHAR(50) NOT NULL, -- Call, Email, Meeting, Support Ticket
    InteractionChannel VARCHAR(50) NOT NULL, -- Phone, Email, Chat, In-Person
    InteractionStatus VARCHAR(50) NOT NULL, -- Open, In Progress, Closed
    InteractionOutcome VARCHAR(100) NULL,
    
    -- Measures
    DurationMinutes INT NULL,
    SatisfactionScore DECIMAL(3,2) NULL, -- 1-5 scale
    ResponseTimeHours DECIMAL(10,2) NULL,
    ResolutionTimeHours DECIMAL(10,2) NULL,
    
    -- Flags
    IsFirstContact BIT NOT NULL DEFAULT 0,
    IsResolved BIT NOT NULL DEFAULT 0,
    RequiresFollowUp BIT NOT NULL DEFAULT 0,
    
    -- Audit Fields
    InteractionDate DATETIME NOT NULL,
    CreatedDate DATETIME NOT NULL DEFAULT GETDATE(),
    ModifiedDate DATETIME NOT NULL DEFAULT GETDATE(),
    
    -- Foreign Keys
    CONSTRAINT FK_FactInteraction_DimDate FOREIGN KEY (DateKey) 
        REFERENCES dbo.DimDate(DateKey),
    CONSTRAINT FK_FactInteraction_DimCustomer FOREIGN KEY (CustomerKey) 
        REFERENCES dbo.DimCustomer(CustomerKey),
    CONSTRAINT FK_FactInteraction_DimEmployee FOREIGN KEY (EmployeeKey) 
        REFERENCES dbo.DimEmployee(EmployeeKey)
);
GO

CREATE NONCLUSTERED INDEX IX_FactInteraction_DateKey ON dbo.FactCustomerInteraction(DateKey);
CREATE NONCLUSTERED INDEX IX_FactInteraction_CustomerKey ON dbo.FactCustomerInteraction(CustomerKey);
CREATE NONCLUSTERED INDEX IX_FactInteraction_Type ON dbo.FactCustomerInteraction(InteractionType);
GO

-- =============================================
-- Fact: Operational Metrics (Daily Snapshot)
-- =============================================
IF OBJECT_ID('dbo.FactOperationalMetrics', 'U') IS NOT NULL 
    DROP TABLE dbo.FactOperationalMetrics;
GO

CREATE TABLE dbo.FactOperationalMetrics
(
    MetricKey BIGINT IDENTITY(1,1) PRIMARY KEY,
    DateKey INT NOT NULL,
    GeographyKey INT NOT NULL,
    
    -- Inventory Metrics
    InventoryValue DECIMAL(18,2) NULL,
    InventoryUnits INT NULL,
    StockoutIncidents INT NULL,
    
    -- Operations Metrics
    OrdersProcessed INT NULL,
    OrdersFulfilled INT NULL,
    OrdersCancelled INT NULL,
    AverageProcessingTimeHours DECIMAL(10,2) NULL,
    
    -- Customer Service Metrics
    SupportTicketsOpened INT NULL,
    SupportTicketsClosed INT NULL,
    AverageHandleTimeMinutes DECIMAL(10,2) NULL,
    FirstCallResolutionRate DECIMAL(5,2) NULL,
    
    -- Website/Digital Metrics
    WebsiteVisitors INT NULL,
    WebsitePageViews INT NULL,
    WebsiteConversionRate DECIMAL(5,2) NULL,
    AverageSessionDurationMinutes DECIMAL(10,2) NULL,
    
    -- Employee Metrics
    EmployeeCount INT NULL,
    EmployeeUtilizationRate DECIMAL(5,2) NULL,
    OvertimeHours DECIMAL(10,2) NULL,
    
    -- Audit Fields
    CreatedDate DATETIME NOT NULL DEFAULT GETDATE(),
    
    -- Foreign Keys
    CONSTRAINT FK_FactMetrics_DimDate FOREIGN KEY (DateKey) 
        REFERENCES dbo.DimDate(DateKey),
    CONSTRAINT FK_FactMetrics_DimGeography FOREIGN KEY (GeographyKey) 
        REFERENCES dbo.DimGeography(GeographyKey)
);
GO

CREATE NONCLUSTERED INDEX IX_FactMetrics_DateKey ON dbo.FactOperationalMetrics(DateKey);
CREATE NONCLUSTERED INDEX IX_FactMetrics_GeographyKey ON dbo.FactOperationalMetrics(GeographyKey);
GO

-- =============================================
-- Fact: Sales Pipeline/Opportunities
-- =============================================
IF OBJECT_ID('dbo.FactSalesPipeline', 'U') IS NOT NULL 
    DROP TABLE dbo.FactSalesPipeline;
GO

CREATE TABLE dbo.FactSalesPipeline
(
    PipelineKey BIGINT IDENTITY(1,1) PRIMARY KEY,
    DateKey INT NOT NULL,
    CustomerKey INT NOT NULL,
    ProductKey INT NOT NULL,
    EmployeeKey INT NOT NULL,
    
    -- Opportunity Details
    OpportunityID VARCHAR(50) NOT NULL,
    OpportunityName VARCHAR(200) NOT NULL,
    OpportunityStage VARCHAR(50) NOT NULL, -- Prospecting, Qualification, Proposal, Negotiation, Closed Won, Closed Lost
    
    -- Measures
    EstimatedValue DECIMAL(18,2) NOT NULL,
    ProbabilityPercent DECIMAL(5,2) NOT NULL,
    ExpectedRevenue AS (EstimatedValue * ProbabilityPercent / 100),
    
    -- Dates
    CreatedDate DATETIME NOT NULL,
    ExpectedCloseDate DATE NULL,
    ActualCloseDate DATE NULL,
    LastActivityDate DATE NULL,
    
    -- Flags
    IsWon BIT NOT NULL DEFAULT 0,
    IsActive BIT NOT NULL DEFAULT 1,
    
    -- Foreign Keys
    CONSTRAINT FK_FactPipeline_DimDate FOREIGN KEY (DateKey) 
        REFERENCES dbo.DimDate(DateKey),
    CONSTRAINT FK_FactPipeline_DimCustomer FOREIGN KEY (CustomerKey) 
        REFERENCES dbo.DimCustomer(CustomerKey),
    CONSTRAINT FK_FactPipeline_DimProduct FOREIGN KEY (ProductKey) 
        REFERENCES dbo.DimProduct(ProductKey),
    CONSTRAINT FK_FactPipeline_DimEmployee FOREIGN KEY (EmployeeKey) 
        REFERENCES dbo.DimEmployee(EmployeeKey)
);
GO

CREATE NONCLUSTERED INDEX IX_FactPipeline_DateKey ON dbo.FactSalesPipeline(DateKey);
CREATE NONCLUSTERED INDEX IX_FactPipeline_CustomerKey ON dbo.FactSalesPipeline(CustomerKey);
CREATE NONCLUSTERED INDEX IX_FactPipeline_Stage ON dbo.FactSalesPipeline(OpportunityStage);
GO

PRINT 'All fact tables created successfully.';
GO
