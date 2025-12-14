"""
Data Processing Utilities for Power BI Executive Dashboard
Purpose: Common data transformation and preparation functions
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pyodbc
from sqlalchemy import create_engine


class DataConnector:
    """
    Centralized data connection manager for various sources
    """
    
    def __init__(self):
        """Initialize data connector"""
        self.sql_connection = None
        self.engine = None
    
    def connect_to_sql_server(self, server, database, username=None, password=None, 
                              trusted_connection=True):
        """
        Connect to SQL Server database
        
        Args:
            server (str): Server name or IP
            database (str): Database name
            username (str): Username (if not using Windows auth)
            password (str): Password (if not using Windows auth)
            trusted_connection (bool): Use Windows authentication
            
        Returns:
            connection: SQL Server connection
        """
        if trusted_connection:
            conn_str = (
                f"DRIVER={{SQL Server}};"
                f"SERVER={server};"
                f"DATABASE={database};"
                f"Trusted_Connection=yes;"
            )
        else:
            conn_str = (
                f"DRIVER={{SQL Server}};"
                f"SERVER={server};"
                f"DATABASE={database};"
                f"UID={username};"
                f"PWD={password};"
            )
        
        self.sql_connection = pyodbc.connect(conn_str)
        
        # Also create SQLAlchemy engine for pandas integration
        if trusted_connection:
            engine_str = f"mssql+pyodbc://@{server}/{database}?driver=SQL+Server&trusted_connection=yes"
        else:
            engine_str = f"mssql+pyodbc://{username}:{password}@{server}/{database}?driver=SQL+Server"
        
        self.engine = create_engine(engine_str)
        
        return self.sql_connection
    
    def query_to_dataframe(self, query):
        """
        Execute SQL query and return as DataFrame
        
        Args:
            query (str): SQL query
            
        Returns:
            DataFrame: Query results
        """
        if self.engine:
            return pd.read_sql(query, self.engine)
        elif self.sql_connection:
            return pd.read_sql(query, self.sql_connection)
        else:
            raise ConnectionError("No database connection established")
    
    def load_fact_sales(self, start_date=None, end_date=None):
        """
        Load sales fact table data
        
        Args:
            start_date (str): Start date filter (YYYY-MM-DD)
            end_date (str): End date filter (YYYY-MM-DD)
            
        Returns:
            DataFrame: Sales data
        """
        query = """
        SELECT 
            fs.*,
            dd.FullDate,
            dd.CalendarYear,
            dd.CalendarYearMonth,
            dd.MonthName,
            dc.CustomerName,
            dc.CustomerSegment,
            dc.Region,
            dp.ProductName,
            dp.ProductCategory,
            de.FullName as EmployeeName,
            dg.Country,
            dch.ChannelName
        FROM dbo.FactSales fs
        INNER JOIN dbo.DimDate dd ON fs.DateKey = dd.DateKey
        INNER JOIN dbo.DimCustomer dc ON fs.CustomerKey = dc.CustomerKey
        INNER JOIN dbo.DimProduct dp ON fs.ProductKey = dp.ProductKey
        INNER JOIN dbo.DimEmployee de ON fs.EmployeeKey = de.EmployeeKey
        INNER JOIN dbo.DimGeography dg ON fs.GeographyKey = dg.GeographyKey
        INNER JOIN dbo.DimChannel dch ON fs.ChannelKey = dch.ChannelKey
        """
        
        if start_date:
            query += f"\nWHERE dd.FullDate >= '{start_date}'"
            if end_date:
                query += f" AND dd.FullDate <= '{end_date}'"
        elif end_date:
            query += f"\nWHERE dd.FullDate <= '{end_date}'"
        
        return self.query_to_dataframe(query)
    
    def close(self):
        """Close database connection"""
        if self.sql_connection:
            self.sql_connection.close()
        if self.engine:
            self.engine.dispose()


class DataTransformer:
    """
    Data transformation and cleaning utilities
    """
    
    @staticmethod
    def handle_missing_values(df, strategy='mean', columns=None):
        """
        Handle missing values in DataFrame
        
        Args:
            df (DataFrame): Input data
            strategy (str): 'mean', 'median', 'mode', 'forward_fill', 'drop'
            columns (list): Specific columns to process (None = all)
            
        Returns:
            DataFrame: Cleaned data
        """
        df_clean = df.copy()
        
        if columns is None:
            columns = df_clean.columns
        
        for col in columns:
            if df_clean[col].dtype in [np.float64, np.int64]:
                if strategy == 'mean':
                    df_clean[col].fillna(df_clean[col].mean(), inplace=True)
                elif strategy == 'median':
                    df_clean[col].fillna(df_clean[col].median(), inplace=True)
                elif strategy == 'forward_fill':
                    df_clean[col].fillna(method='ffill', inplace=True)
                elif strategy == 'drop':
                    df_clean.dropna(subset=[col], inplace=True)
            else:
                if strategy == 'mode':
                    df_clean[col].fillna(df_clean[col].mode()[0], inplace=True)
                elif strategy == 'forward_fill':
                    df_clean[col].fillna(method='ffill', inplace=True)
                elif strategy == 'drop':
                    df_clean.dropna(subset=[col], inplace=True)
        
        return df_clean
    
    @staticmethod
    def remove_outliers(df, column, method='iqr', threshold=1.5):
        """
        Remove outliers from DataFrame
        
        Args:
            df (DataFrame): Input data
            column (str): Column to check for outliers
            method (str): 'iqr' or 'zscore'
            threshold (float): IQR multiplier or Z-score threshold
            
        Returns:
            DataFrame: Data without outliers
        """
        df_clean = df.copy()
        
        if method == 'iqr':
            Q1 = df_clean[column].quantile(0.25)
            Q3 = df_clean[column].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - threshold * IQR
            upper_bound = Q3 + threshold * IQR
            
            df_clean = df_clean[
                (df_clean[column] >= lower_bound) & 
                (df_clean[column] <= upper_bound)
            ]
        
        elif method == 'zscore':
            from scipy import stats
            z_scores = np.abs(stats.zscore(df_clean[column]))
            df_clean = df_clean[z_scores < threshold]
        
        return df_clean
    
    @staticmethod
    def create_date_features(df, date_column):
        """
        Extract date features from datetime column
        
        Args:
            df (DataFrame): Input data
            date_column (str): Date column name
            
        Returns:
            DataFrame: Data with additional date features
        """
        df_enhanced = df.copy()
        df_enhanced[date_column] = pd.to_datetime(df_enhanced[date_column])
        
        df_enhanced['Year'] = df_enhanced[date_column].dt.year
        df_enhanced['Quarter'] = df_enhanced[date_column].dt.quarter
        df_enhanced['Month'] = df_enhanced[date_column].dt.month
        df_enhanced['MonthName'] = df_enhanced[date_column].dt.month_name()
        df_enhanced['Week'] = df_enhanced[date_column].dt.isocalendar().week
        df_enhanced['DayOfWeek'] = df_enhanced[date_column].dt.dayofweek
        df_enhanced['DayName'] = df_enhanced[date_column].dt.day_name()
        df_enhanced['DayOfMonth'] = df_enhanced[date_column].dt.day
        df_enhanced['DayOfYear'] = df_enhanced[date_column].dt.dayofyear
        df_enhanced['IsWeekend'] = df_enhanced['DayOfWeek'].isin([5, 6])
        df_enhanced['IsMonthStart'] = df_enhanced[date_column].dt.is_month_start
        df_enhanced['IsMonthEnd'] = df_enhanced[date_column].dt.is_month_end
        df_enhanced['IsQuarterStart'] = df_enhanced[date_column].dt.is_quarter_start
        df_enhanced['IsQuarterEnd'] = df_enhanced[date_column].dt.is_quarter_end
        
        return df_enhanced
    
    @staticmethod
    def aggregate_by_period(df, date_column, value_columns, period='D'):
        """
        Aggregate data by time period
        
        Args:
            df (DataFrame): Input data
            date_column (str): Date column name
            value_columns (list): Columns to aggregate
            period (str): 'D'=daily, 'W'=weekly, 'M'=monthly, 'Q'=quarterly, 'Y'=yearly
            
        Returns:
            DataFrame: Aggregated data
        """
        df_agg = df.copy()
        df_agg[date_column] = pd.to_datetime(df_agg[date_column])
        df_agg = df_agg.set_index(date_column)
        
        # Define aggregation functions
        agg_dict = {col: 'sum' for col in value_columns}
        
        # Resample and aggregate
        result = df_agg.resample(period).agg(agg_dict).reset_index()
        
        return result
    
    @staticmethod
    def calculate_running_totals(df, date_column, value_column, group_by=None):
        """
        Calculate running totals
        
        Args:
            df (DataFrame): Input data
            date_column (str): Date column for sorting
            value_column (str): Column to sum
            group_by (list): Columns to group by
            
        Returns:
            DataFrame: Data with running totals
        """
        df_result = df.copy()
        df_result = df_result.sort_values(date_column)
        
        if group_by:
            df_result[f'{value_column}_RunningTotal'] = df_result.groupby(group_by)[value_column].cumsum()
        else:
            df_result[f'{value_column}_RunningTotal'] = df_result[value_column].cumsum()
        
        return df_result
    
    @staticmethod
    def calculate_period_over_period(df, date_column, value_column, periods=1):
        """
        Calculate period-over-period changes
        
        Args:
            df (DataFrame): Input data (must be sorted by date)
            date_column (str): Date column name
            value_column (str): Value column
            periods (int): Number of periods to compare
            
        Returns:
            DataFrame: Data with PoP calculations
        """
        df_result = df.copy()
        df_result = df_result.sort_values(date_column)
        
        # Calculate change
        df_result[f'{value_column}_Previous'] = df_result[value_column].shift(periods)
        df_result[f'{value_column}_Change'] = df_result[value_column] - df_result[f'{value_column}_Previous']
        df_result[f'{value_column}_PctChange'] = (
            df_result[f'{value_column}_Change'] / df_result[f'{value_column}_Previous']
        ) * 100
        
        return df_result


class MetricsCalculator:
    """
    Business metrics calculation utilities
    """
    
    @staticmethod
    def calculate_customer_metrics(sales_df, customer_column, value_column):
        """
        Calculate customer-related metrics
        
        Args:
            sales_df (DataFrame): Sales data
            customer_column (str): Customer identifier column
            value_column (str): Sales value column
            
        Returns:
            DataFrame: Customer metrics
        """
        metrics = sales_df.groupby(customer_column).agg({
            value_column: ['sum', 'mean', 'count', 'std']
        }).reset_index()
        
        metrics.columns = [customer_column, 'TotalSales', 'AvgOrderValue', 
                          'OrderCount', 'SalesStdDev']
        
        # Calculate additional metrics
        metrics['SalesCV'] = metrics['SalesStdDev'] / metrics['AvgOrderValue']  # Coefficient of variation
        
        return metrics
    
    @staticmethod
    def calculate_rfm(df, customer_col, date_col, value_col, reference_date=None):
        """
        Calculate RFM (Recency, Frequency, Monetary) analysis
        
        Args:
            df (DataFrame): Transaction data
            customer_col (str): Customer column
            date_col (str): Date column
            value_col (str): Sales value column
            reference_date: Reference date for recency calculation
            
        Returns:
            DataFrame: RFM scores
        """
        if reference_date is None:
            reference_date = df[date_col].max()
        
        df[date_col] = pd.to_datetime(df[date_col])
        
        rfm = df.groupby(customer_col).agg({
            date_col: lambda x: (reference_date - x.max()).days,  # Recency
            value_col: ['count', 'sum']  # Frequency, Monetary
        }).reset_index()
        
        rfm.columns = [customer_col, 'Recency', 'Frequency', 'Monetary']
        
        # Calculate RFM scores (1-5 scale)
        rfm['R_Score'] = pd.qcut(rfm['Recency'], 5, labels=[5, 4, 3, 2, 1])
        rfm['F_Score'] = pd.qcut(rfm['Frequency'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5])
        rfm['M_Score'] = pd.qcut(rfm['Monetary'], 5, labels=[1, 2, 3, 4, 5])
        
        # Combined RFM score
        rfm['RFM_Score'] = rfm['R_Score'].astype(str) + rfm['F_Score'].astype(str) + rfm['M_Score'].astype(str)
        
        return rfm


# Example usage
if __name__ == "__main__":
    print("Data Processing Utilities loaded successfully")
    print("\nAvailable classes:")
    print("  - DataConnector: Database connectivity")
    print("  - DataTransformer: Data cleaning and transformation")
    print("  - MetricsCalculator: Business metrics calculation")
