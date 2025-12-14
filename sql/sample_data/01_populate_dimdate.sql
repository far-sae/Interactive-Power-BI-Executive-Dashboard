/*
 * Executive Dashboard - Date Dimension Population
 * Purpose: Populates the DimDate table with 10 years of data
 * Range: 2020-2030
 */

USE ExecutiveDashboard_DW;
GO

-- Clear existing data
TRUNCATE TABLE dbo.DimDate;
GO

-- Declare variables
DECLARE @StartDate DATE = '2020-01-01';
DECLARE @EndDate DATE = '2030-12-31';
DECLARE @CurrentDate DATE = @StartDate;

-- Fiscal year settings (adjust as needed)
DECLARE @FiscalYearStartMonth INT = 7; -- July 1st fiscal year start

-- Insert date records
WHILE @CurrentDate <= @EndDate
BEGIN
    DECLARE @DateKey INT = CAST(FORMAT(@CurrentDate, 'yyyyMMdd') AS INT);
    DECLARE @Year SMALLINT = YEAR(@CurrentDate);
    DECLARE @Month TINYINT = MONTH(@CurrentDate);
    DECLARE @Day TINYINT = DAY(@CurrentDate);
    DECLARE @DayOfWeek TINYINT = DATEPART(WEEKDAY, @CurrentDate);
    
    -- Calculate fiscal year
    DECLARE @FiscalYear SMALLINT = CASE 
        WHEN @Month >= @FiscalYearStartMonth THEN @Year + 1 
        ELSE @Year 
    END;
    
    -- Calculate fiscal quarter
    DECLARE @FiscalMonth INT = ((@Month - @FiscalYearStartMonth + 12) % 12) + 1;
    DECLARE @FiscalQuarter TINYINT = CEILING(@FiscalMonth / 3.0);
    
    INSERT INTO dbo.DimDate (
        DateKey, FullDate, DayOfMonth, DayName, DayOfWeek, DayOfYear,
        WeekOfYear, MonthName, MonthOfYear, CalendarQuarter, CalendarYear,
        CalendarYearMonth, CalendarYearQuarter,
        FiscalQuarter, FiscalYear, FiscalYearMonth, FiscalYearQuarter,
        IsWeekend, IsHoliday
    )
    VALUES (
        @DateKey,
        @CurrentDate,
        @Day,
        DATENAME(WEEKDAY, @CurrentDate),
        @DayOfWeek,
        DATEPART(DAYOFYEAR, @CurrentDate),
        DATEPART(WEEK, @CurrentDate),
        DATENAME(MONTH, @CurrentDate),
        @Month,
        DATEPART(QUARTER, @CurrentDate),
        @Year,
        FORMAT(@CurrentDate, 'yyyy-MM'),
        FORMAT(@CurrentDate, 'yyyy') + '-Q' + CAST(DATEPART(QUARTER, @CurrentDate) AS VARCHAR(1)),
        @FiscalQuarter,
        @FiscalYear,
        FORMAT(@FiscalYear, '0000') + '-' + FORMAT(@FiscalMonth, '00'),
        FORMAT(@FiscalYear, '0000') + '-Q' + CAST(@FiscalQuarter AS VARCHAR(1)),
        CASE WHEN @DayOfWeek IN (1, 7) THEN 1 ELSE 0 END,
        0
    );
    
    SET @CurrentDate = DATEADD(DAY, 1, @CurrentDate);
END;

-- Update major US holidays
UPDATE dbo.DimDate SET IsHoliday = 1, HolidayName = 'New Year''s Day'
WHERE MonthOfYear = 1 AND DayOfMonth = 1;

UPDATE dbo.DimDate SET IsHoliday = 1, HolidayName = 'Independence Day'
WHERE MonthOfYear = 7 AND DayOfMonth = 4;

UPDATE dbo.DimDate SET IsHoliday = 1, HolidayName = 'Christmas Day'
WHERE MonthOfYear = 12 AND DayOfMonth = 25;

-- Thanksgiving (4th Thursday of November)
UPDATE dbo.DimDate SET IsHoliday = 1, HolidayName = 'Thanksgiving'
WHERE MonthOfYear = 11 
  AND DayName = 'Thursday'
  AND DayOfMonth BETWEEN 22 AND 28;

PRINT 'DimDate populated with ' + CAST(@@ROWCOUNT AS VARCHAR(10)) + ' records.';
GO

SELECT 
    MIN(FullDate) AS StartDate,
    MAX(FullDate) AS EndDate,
    COUNT(*) AS TotalDays,
    SUM(CASE WHEN IsHoliday = 1 THEN 1 ELSE 0 END) AS HolidayCount,
    SUM(CASE WHEN IsWeekend = 1 THEN 1 ELSE 0 END) AS WeekendDays
FROM dbo.DimDate;
GO
