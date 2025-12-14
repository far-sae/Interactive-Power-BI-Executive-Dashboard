/*
 * Executive Dashboard Data Warehouse - Database Creation Script
 * Purpose: Creates the main database for the Power BI executive dashboard
 * Author: Enterprise BI Team
 * Version: 1.0.0
 */

USE master;
GO

-- Create database if it doesn't exist
IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = N'ExecutiveDashboard_DW')
BEGIN
    CREATE DATABASE ExecutiveDashboard_DW
    ON PRIMARY 
    (
        NAME = N'ExecutiveDashboard_DW_Data',
        FILENAME = N'C:\SQLData\ExecutiveDashboard_DW_Data.mdf',
        SIZE = 100MB,
        MAXSIZE = UNLIMITED,
        FILEGROWTH = 50MB
    )
    LOG ON 
    (
        NAME = N'ExecutiveDashboard_DW_Log',
        FILENAME = N'C:\SQLData\ExecutiveDashboard_DW_Log.ldf',
        SIZE = 50MB,
        MAXSIZE = 2GB,
        FILEGROWTH = 25MB
    );
    
    PRINT 'Database ExecutiveDashboard_DW created successfully.';
END
ELSE
BEGIN
    PRINT 'Database ExecutiveDashboard_DW already exists.';
END
GO

-- Set database options for optimal performance
ALTER DATABASE ExecutiveDashboard_DW
SET RECOVERY SIMPLE,
    ANSI_NULL_DEFAULT OFF,
    ANSI_NULLS OFF,
    ANSI_PADDING OFF,
    ANSI_WARNINGS OFF,
    ARITHABORT OFF,
    AUTO_CLOSE OFF,
    AUTO_CREATE_STATISTICS ON,
    AUTO_SHRINK OFF,
    AUTO_UPDATE_STATISTICS ON,
    AUTO_UPDATE_STATISTICS_ASYNC ON,
    CURSOR_CLOSE_ON_COMMIT OFF,
    CONCAT_NULL_YIELDS_NULL OFF,
    NUMERIC_ROUNDABORT OFF,
    QUOTED_IDENTIFIER OFF,
    RECURSIVE_TRIGGERS OFF,
    PAGE_VERIFY CHECKSUM,
    DB_CHAINING OFF;
GO

USE ExecutiveDashboard_DW;
GO

PRINT 'Database configuration completed successfully.';
GO
