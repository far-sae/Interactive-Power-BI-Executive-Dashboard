/*
 * Executive Dashboard - Stored Procedure: ETL for Sales Data
 * Purpose: ETL process to load sales transactions from staging to fact table
 */

USE ExecutiveDashboard_DW;
GO

-- Drop procedure if exists
IF OBJECT_ID('dbo.usp_LoadFactSales', 'P') IS NOT NULL
    DROP PROCEDURE dbo.usp_LoadFactSales;
GO

CREATE PROCEDURE dbo.usp_LoadFactSales
    @StartDate DATE = NULL,
    @EndDate DATE = NULL
AS
BEGIN
    SET NOCOUNT ON;
    
    -- Set default date range if not provided
    IF @StartDate IS NULL
        SET @StartDate = DATEADD(DAY, -30, GETDATE());
    
    IF @EndDate IS NULL
        SET @EndDate = GETDATE();
    
    DECLARE @RecordsInserted INT = 0;
    DECLARE @RecordsUpdated INT = 0;
    DECLARE @ErrorMessage NVARCHAR(4000);
    
    BEGIN TRY
        BEGIN TRANSACTION;
        
        -- Log start
        PRINT 'Starting ETL process for FactSales...';
        PRINT 'Date Range: ' + CAST(@StartDate AS VARCHAR(20)) + ' to ' + CAST(@EndDate AS VARCHAR(20));
        
        -- Insert/Update logic would go here
        -- This is a template - actual implementation would depend on source system
        
        /*
        Example ETL logic:
        
        INSERT INTO dbo.FactSales (
            DateKey, CustomerKey, ProductKey, EmployeeKey, GeographyKey, ChannelKey,
            OrderNumber, OrderLineNumber, Quantity, UnitPrice, UnitCost, 
            DiscountAmount, DiscountPercent, TaxAmount, FreightAmount, OrderDate
        )
        SELECT 
            CAST(FORMAT(s.OrderDate, 'yyyyMMdd') AS INT) AS DateKey,
            c.CustomerKey,
            p.ProductKey,
            e.EmployeeKey,
            g.GeographyKey,
            ch.ChannelKey,
            s.OrderNumber,
            s.LineNumber,
            s.Quantity,
            s.UnitPrice,
            s.UnitCost,
            s.DiscountAmount,
            s.DiscountPercent,
            s.TaxAmount,
            s.FreightAmount,
            s.OrderDate
        FROM Staging.Sales s
        INNER JOIN dbo.DimCustomer c ON s.CustomerID = c.CustomerID AND c.IsCurrent = 1
        INNER JOIN dbo.DimProduct p ON s.ProductID = p.ProductID AND p.IsCurrent = 1
        INNER JOIN dbo.DimEmployee e ON s.EmployeeID = e.EmployeeID AND e.IsCurrent = 1
        INNER JOIN dbo.DimGeography g ON s.GeographyID = g.GeographyID
        INNER JOIN dbo.DimChannel ch ON s.ChannelID = ch.ChannelID
        WHERE s.OrderDate BETWEEN @StartDate AND @EndDate
        AND NOT EXISTS (
            SELECT 1 FROM dbo.FactSales fs 
            WHERE fs.OrderNumber = s.OrderNumber 
            AND fs.OrderLineNumber = s.LineNumber
        );
        
        SET @RecordsInserted = @@ROWCOUNT;
        */
        
        COMMIT TRANSACTION;
        
        PRINT 'ETL process completed successfully.';
        PRINT 'Records Inserted: ' + CAST(@RecordsInserted AS VARCHAR(10));
        PRINT 'Records Updated: ' + CAST(@RecordsUpdated AS VARCHAR(10));
        
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0
            ROLLBACK TRANSACTION;
        
        SET @ErrorMessage = ERROR_MESSAGE();
        PRINT 'Error occurred during ETL process: ' + @ErrorMessage;
        
        -- Re-throw the error
        THROW;
    END CATCH
END;
GO

-- =============================================
-- Stored Procedure: Incremental Refresh
-- =============================================
IF OBJECT_ID('dbo.usp_IncrementalRefresh', 'P') IS NOT NULL
    DROP PROCEDURE dbo.usp_IncrementalRefresh;
GO

CREATE PROCEDURE dbo.usp_IncrementalRefresh
    @TableName NVARCHAR(128),
    @WindowDays INT = 90
AS
BEGIN
    SET NOCOUNT ON;
    
    DECLARE @SQL NVARCHAR(MAX);
    DECLARE @CutoffDate DATE = DATEADD(DAY, -@WindowDays, GETDATE());
    DECLARE @Message NVARCHAR(500);
    
    SET @Message = 'Starting incremental refresh for ' + @TableName;
    PRINT @Message;
    PRINT 'Cutoff Date: ' + CAST(@CutoffDate AS VARCHAR(20));
    
    -- Delete old data based on table
    IF @TableName = 'FactSales'
    BEGIN
        DELETE FROM dbo.FactSales
        WHERE OrderDate < @CutoffDate;
        
        PRINT 'Deleted ' + CAST(@@ROWCOUNT AS VARCHAR(10)) + ' old records from FactSales';
    END
    ELSE IF @TableName = 'FactOperationalMetrics'
    BEGIN
        DELETE FROM dbo.FactOperationalMetrics
        WHERE DateKey < CAST(FORMAT(@CutoffDate, 'yyyyMMdd') AS INT);
        
        PRINT 'Deleted ' + CAST(@@ROWCOUNT AS VARCHAR(10)) + ' old records from FactOperationalMetrics';
    END
    
    PRINT 'Incremental refresh completed for ' + @TableName;
END;
GO

-- =============================================
-- Stored Procedure: Data Quality Checks
-- =============================================
IF OBJECT_ID('dbo.usp_DataQualityCheck', 'P') IS NOT NULL
    DROP PROCEDURE dbo.usp_DataQualityCheck;
GO

CREATE PROCEDURE dbo.usp_DataQualityCheck
AS
BEGIN
    SET NOCOUNT ON;
    
    PRINT '========================================';
    PRINT 'DATA QUALITY CHECK REPORT';
    PRINT '========================================';
    PRINT '';
    
    -- Check for orphaned records in FactSales
    DECLARE @OrphanedSales INT;
    
    SELECT @OrphanedSales = COUNT(*)
    FROM dbo.FactSales fs
    WHERE NOT EXISTS (SELECT 1 FROM dbo.DimDate d WHERE d.DateKey = fs.DateKey);
    
    PRINT 'Orphaned Sales Records (missing DateKey): ' + CAST(@OrphanedSales AS VARCHAR(10));
    
    -- Check for negative sales amounts
    DECLARE @NegativeSales INT;
    
    SELECT @NegativeSales = COUNT(*)
    FROM dbo.FactSales
    WHERE Quantity < 0 OR UnitPrice < 0;
    
    PRINT 'Sales with negative values: ' + CAST(@NegativeSales AS VARCHAR(10));
    
    -- Check dimension row counts
    PRINT '';
    PRINT 'Dimension Table Row Counts:';
    PRINT '----------------------------';
    
    DECLARE @RowCount INT;
    
    SELECT @RowCount = COUNT(*) FROM dbo.DimCustomer WHERE IsCurrent = 1;
    PRINT 'Active Customers: ' + CAST(@RowCount AS VARCHAR(10));
    
    SELECT @RowCount = COUNT(*) FROM dbo.DimProduct WHERE IsCurrent = 1;
    PRINT 'Active Products: ' + CAST(@RowCount AS VARCHAR(10));
    
    SELECT @RowCount = COUNT(*) FROM dbo.DimEmployee WHERE IsCurrent = 1;
    PRINT 'Active Employees: ' + CAST(@RowCount AS VARCHAR(10));
    
    SELECT @RowCount = COUNT(*) FROM dbo.DimGeography;
    PRINT 'Geographies: ' + CAST(@RowCount AS VARCHAR(10));
    
    -- Check fact table counts
    PRINT '';
    PRINT 'Fact Table Row Counts:';
    PRINT '----------------------';
    
    SELECT @RowCount = COUNT(*) FROM dbo.FactSales;
    PRINT 'Sales Transactions: ' + CAST(@RowCount AS VARCHAR(10));
    
    SELECT @RowCount = COUNT(*) FROM dbo.FactFinancial;
    PRINT 'Financial Records: ' + CAST(@RowCount AS VARCHAR(10));
    
    PRINT '';
    PRINT '========================================';
    PRINT 'DATA QUALITY CHECK COMPLETED';
    PRINT '========================================';
END;
GO

PRINT 'Stored procedures created successfully.';
GO
