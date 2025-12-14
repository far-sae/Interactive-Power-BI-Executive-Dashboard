"""
Anomaly Detection for Power BI Executive Dashboard
Purpose: Detect anomalies in sales, revenue, and operational metrics
Uses: Isolation Forest and statistical methods
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from scipy import stats
import warnings
warnings.filterwarnings('ignore')


class AnomalyDetector:
    """
    Advanced anomaly detection using multiple methods:
    - Isolation Forest (ML-based)
    - Z-Score (Statistical)
    - IQR (Interquartile Range)
    - Moving Average Deviation
    """
    
    def __init__(self, contamination=0.05):
        """
        Initialize anomaly detector
        
        Args:
            contamination (float): Expected proportion of anomalies (default: 5%)
        """
        self.contamination = contamination
        self.scaler = StandardScaler()
        self.iso_forest = IsolationForest(
            contamination=contamination,
            random_state=42,
            n_estimators=100
        )
    
    def detect_isolation_forest(self, data, features):
        """
        Detect anomalies using Isolation Forest algorithm
        
        Args:
            data (DataFrame): Input data
            features (list): List of column names to analyze
            
        Returns:
            DataFrame: Data with anomaly flags and scores
        """
        df = data.copy()
        
        # Prepare features
        X = df[features].values
        
        # Handle missing values
        X = np.nan_to_num(X, nan=0.0)
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Fit and predict
        predictions = self.iso_forest.fit_predict(X_scaled)
        anomaly_scores = self.iso_forest.score_samples(X_scaled)
        
        # Add results to dataframe
        df['is_anomaly_if'] = predictions == -1
        df['anomaly_score_if'] = anomaly_scores
        
        return df
    
    def detect_zscore(self, data, column, threshold=3):
        """
        Detect anomalies using Z-score method
        
        Args:
            data (DataFrame): Input data
            column (str): Column name to analyze
            threshold (float): Z-score threshold (default: 3)
            
        Returns:
            DataFrame: Data with Z-score anomaly flags
        """
        df = data.copy()
        
        # Calculate z-scores
        z_scores = np.abs(stats.zscore(df[column], nan_policy='omit'))
        
        # Flag anomalies
        df[f'is_anomaly_zscore_{column}'] = z_scores > threshold
        df[f'zscore_{column}'] = z_scores
        
        return df
    
    def detect_iqr(self, data, column, multiplier=1.5):
        """
        Detect anomalies using Interquartile Range (IQR) method
        
        Args:
            data (DataFrame): Input data
            column (str): Column name to analyze
            multiplier (float): IQR multiplier (default: 1.5)
            
        Returns:
            DataFrame: Data with IQR anomaly flags
        """
        df = data.copy()
        
        Q1 = df[column].quantile(0.25)
        Q3 = df[column].quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - multiplier * IQR
        upper_bound = Q3 + multiplier * IQR
        
        df[f'is_anomaly_iqr_{column}'] = (
            (df[column] < lower_bound) | (df[column] > upper_bound)
        )
        df[f'iqr_lower_bound_{column}'] = lower_bound
        df[f'iqr_upper_bound_{column}'] = upper_bound
        
        return df
    
    def detect_moving_average_deviation(self, data, column, window=7, threshold=2):
        """
        Detect anomalies based on deviation from moving average
        
        Args:
            data (DataFrame): Input data (must be sorted by date)
            column (str): Column name to analyze
            window (int): Moving average window size
            threshold (float): Standard deviation multiplier
            
        Returns:
            DataFrame: Data with moving average anomaly flags
        """
        df = data.copy()
        
        # Calculate moving average and std
        df[f'ma_{column}'] = df[column].rolling(window=window, center=False).mean()
        df[f'std_{column}'] = df[column].rolling(window=window, center=False).std()
        
        # Calculate deviation
        df[f'deviation_{column}'] = np.abs(df[column] - df[f'ma_{column}'])
        
        # Flag anomalies
        df[f'is_anomaly_ma_{column}'] = (
            df[f'deviation_{column}'] > threshold * df[f'std_{column}']
        )
        
        return df
    
    def detect_all(self, data, numeric_columns, date_column=None):
        """
        Run all anomaly detection methods
        
        Args:
            data (DataFrame): Input data
            numeric_columns (list): List of numeric columns to analyze
            date_column (str): Date column for time-based analysis
            
        Returns:
            DataFrame: Data with all anomaly detection results
        """
        df = data.copy()
        
        # Sort by date if provided
        if date_column:
            df = df.sort_values(date_column)
        
        # Isolation Forest on all numeric features
        df = self.detect_isolation_forest(df, numeric_columns)
        
        # Individual column analysis
        for col in numeric_columns:
            df = self.detect_zscore(df, col)
            df = self.detect_iqr(df, col)
            
            if date_column:
                df = self.detect_moving_average_deviation(df, col)
        
        # Create consensus anomaly flag
        anomaly_columns = [col for col in df.columns if 'is_anomaly' in col]
        df['anomaly_count'] = df[anomaly_columns].sum(axis=1)
        df['is_anomaly_consensus'] = df['anomaly_count'] >= 2
        
        return df
    
    def get_anomaly_summary(self, data):
        """
        Generate summary statistics for detected anomalies
        
        Args:
            data (DataFrame): Data with anomaly detection results
            
        Returns:
            dict: Summary statistics
        """
        anomaly_columns = [col for col in data.columns if 'is_anomaly' in col]
        
        summary = {
            'total_records': len(data),
            'method_counts': {},
            'consensus_anomalies': data['is_anomaly_consensus'].sum() if 'is_anomaly_consensus' in data.columns else 0
        }
        
        for col in anomaly_columns:
            summary['method_counts'][col] = data[col].sum()
        
        return summary


def prepare_sales_data_for_anomaly_detection(df):
    """
    Prepare sales data from Power BI for anomaly detection
    
    Args:
        df (DataFrame): Raw sales data from Power BI
        
    Returns:
        DataFrame: Prepared data
    """
    # Aggregate by date
    daily_sales = df.groupby('Date').agg({
        'SalesAmount': 'sum',
        'Quantity': 'sum',
        'GrossProfit': 'sum',
        'OrderNumber': 'nunique',
        'CustomerKey': 'nunique'
    }).reset_index()
    
    daily_sales.columns = ['Date', 'TotalSales', 'TotalQuantity', 
                           'TotalProfit', 'OrderCount', 'CustomerCount']
    
    # Calculate derived metrics
    daily_sales['AvgOrderValue'] = daily_sales['TotalSales'] / daily_sales['OrderCount']
    daily_sales['AvgItemsPerOrder'] = daily_sales['TotalQuantity'] / daily_sales['OrderCount']
    daily_sales['ProfitMargin'] = daily_sales['TotalProfit'] / daily_sales['TotalSales']
    
    return daily_sales


def main_example():
    """
    Example usage of the anomaly detector
    """
    # This would be called from Power BI with actual data
    # For demonstration, creating sample data
    
    np.random.seed(42)
    dates = pd.date_range('2024-01-01', periods=365, freq='D')
    
    # Generate normal data with some anomalies
    sales = np.random.normal(100000, 15000, 365)
    
    # Inject anomalies
    sales[50] = 200000  # Spike
    sales[100] = 30000  # Drop
    sales[200] = 250000  # Large spike
    
    df = pd.DataFrame({
        'Date': dates,
        'TotalSales': sales,
        'TotalQuantity': np.random.normal(1000, 150, 365),
        'OrderCount': np.random.normal(500, 75, 365)
    })
    
    # Initialize detector
    detector = AnomalyDetector(contamination=0.05)
    
    # Detect anomalies
    numeric_cols = ['TotalSales', 'TotalQuantity', 'OrderCount']
    result = detector.detect_all(df, numeric_cols, date_column='Date')
    
    # Get summary
    summary = detector.get_anomaly_summary(result)
    
    print("Anomaly Detection Summary:")
    print(f"Total Records: {summary['total_records']}")
    print(f"Consensus Anomalies: {summary['consensus_anomalies']}")
    print("\nDetection Method Results:")
    for method, count in summary['method_counts'].items():
        print(f"  {method}: {count}")
    
    # Return results for Power BI
    return result[['Date', 'TotalSales', 'is_anomaly_consensus', 
                   'anomaly_count', 'anomaly_score_if']]


if __name__ == "__main__":
    # Example execution
    results = main_example()
    print("\nSample Anomalies Detected:")
    print(results[results['is_anomaly_consensus'] == True])
