"""
Trend Analysis and Forecasting for Power BI Executive Dashboard
Purpose: Time series analysis, trend detection, and forecasting
Uses: ARIMA, Exponential Smoothing, Linear Regression
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Statistical libraries
from scipy import stats
from scipy.signal import find_peaks

# Time series libraries
try:
    from statsmodels.tsa.seasonal import seasonal_decompose
    from statsmodels.tsa.holtwinters import ExponentialSmoothing
    from statsmodels.tsa.arima.model import ARIMA
    from statsmodels.tsa.stattools import adfuller
except ImportError:
    print("Warning: statsmodels not installed. Some features may not work.")

from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error


class TrendAnalyzer:
    """
    Comprehensive trend analysis and forecasting toolkit
    """
    
    def __init__(self):
        """Initialize the trend analyzer"""
        self.model = None
        self.seasonal_period = 7  # Default: weekly seasonality
    
    def detect_trend_direction(self, series, window=30):
        """
        Detect overall trend direction
        
        Args:
            series (Series): Time series data
            window (int): Window size for trend calculation
            
        Returns:
            dict: Trend information
        """
        # Calculate moving average
        ma = series.rolling(window=window).mean()
        
        # Calculate trend slope using linear regression
        X = np.arange(len(series)).reshape(-1, 1)
        y = series.values
        
        lr = LinearRegression()
        lr.fit(X, y)
        slope = lr.coef_[0]
        
        # Determine trend direction
        if slope > 0.01:
            direction = "Upward"
        elif slope < -0.01:
            direction = "Downward"
        else:
            direction = "Stable"
        
        # Calculate trend strength (R²)
        from sklearn.metrics import r2_score
        predictions = lr.predict(X)
        strength = r2_score(y, predictions)
        
        return {
            'direction': direction,
            'slope': slope,
            'strength': strength,
            'moving_average': ma.iloc[-1] if len(ma) > 0 else None
        }
    
    def seasonal_decomposition(self, series, period=7, model='additive'):
        """
        Perform seasonal decomposition
        
        Args:
            series (Series): Time series data
            period (int): Seasonal period
            model (str): 'additive' or 'multiplicative'
            
        Returns:
            DataFrame: Decomposed components
        """
        try:
            result = seasonal_decompose(
                series, 
                model=model, 
                period=period,
                extrapolate_trend='freq'
            )
            
            df = pd.DataFrame({
                'observed': result.observed,
                'trend': result.trend,
                'seasonal': result.seasonal,
                'residual': result.resid
            })
            
            return df
        except Exception as e:
            print(f"Seasonal decomposition error: {e}")
            return None
    
    def detect_seasonality(self, series, max_lag=365):
        """
        Detect seasonal patterns using autocorrelation
        
        Args:
            series (Series): Time series data
            max_lag (int): Maximum lag to test
            
        Returns:
            dict: Seasonality information
        """
        # Calculate autocorrelation
        autocorr = [series.autocorr(lag=i) for i in range(1, min(max_lag, len(series)))]
        
        # Find peaks in autocorrelation
        peaks, properties = find_peaks(autocorr, height=0.5)
        
        if len(peaks) > 0:
            primary_period = peaks[0] + 1
            has_seasonality = True
        else:
            primary_period = None
            has_seasonality = False
        
        return {
            'has_seasonality': has_seasonality,
            'primary_period': primary_period,
            'peak_lags': peaks + 1 if len(peaks) > 0 else []
        }
    
    def forecast_arima(self, series, steps=30, order=(1, 1, 1)):
        """
        Forecast using ARIMA model
        
        Args:
            series (Series): Historical time series data
            steps (int): Number of steps to forecast
            order (tuple): ARIMA order (p, d, q)
            
        Returns:
            DataFrame: Forecast with confidence intervals
        """
        try:
            # Fit ARIMA model
            model = ARIMA(series, order=order)
            fitted_model = model.fit()
            
            # Generate forecast
            forecast_result = fitted_model.forecast(steps=steps)
            
            # Get prediction intervals
            forecast_df = fitted_model.get_forecast(steps=steps).summary_frame()
            
            return forecast_df
        except Exception as e:
            print(f"ARIMA forecast error: {e}")
            return None
    
    def forecast_exponential_smoothing(self, series, steps=30, seasonal_periods=7):
        """
        Forecast using Exponential Smoothing (Holt-Winters)
        
        Args:
            series (Series): Historical time series data
            steps (int): Number of steps to forecast
            seasonal_periods (int): Seasonal period
            
        Returns:
            DataFrame: Forecast results
        """
        try:
            # Fit exponential smoothing model
            model = ExponentialSmoothing(
                series,
                seasonal_periods=seasonal_periods,
                trend='add',
                seasonal='add',
                initialization_method='estimated'
            )
            fitted_model = model.fit()
            
            # Generate forecast
            forecast = fitted_model.forecast(steps=steps)
            
            forecast_df = pd.DataFrame({
                'forecast': forecast,
                'model': 'Exponential Smoothing'
            })
            
            return forecast_df
        except Exception as e:
            print(f"Exponential Smoothing forecast error: {e}")
            return None
    
    def forecast_linear_trend(self, series, steps=30):
        """
        Simple linear trend forecast
        
        Args:
            series (Series): Historical time series data
            steps (int): Number of steps to forecast
            
        Returns:
            DataFrame: Forecast results
        """
        # Prepare data
        X = np.arange(len(series)).reshape(-1, 1)
        y = series.values
        
        # Fit linear regression
        lr = LinearRegression()
        lr.fit(X, y)
        
        # Generate forecast
        future_X = np.arange(len(series), len(series) + steps).reshape(-1, 1)
        forecast = lr.predict(future_X)
        
        forecast_df = pd.DataFrame({
            'forecast': forecast,
            'model': 'Linear Trend'
        })
        
        return forecast_df
    
    def calculate_growth_metrics(self, series):
        """
        Calculate various growth metrics
        
        Args:
            series (Series): Time series data
            
        Returns:
            dict: Growth metrics
        """
        # Month-over-month growth
        mom_growth = series.pct_change().iloc[-1] * 100
        
        # Year-over-year growth (if enough data)
        if len(series) >= 365:
            yoy_growth = ((series.iloc[-1] - series.iloc[-365]) / series.iloc[-365]) * 100
        else:
            yoy_growth = None
        
        # CAGR (Compound Annual Growth Rate)
        if len(series) >= 365:
            years = len(series) / 365
            cagr = (((series.iloc[-1] / series.iloc[0]) ** (1 / years)) - 1) * 100
        else:
            cagr = None
        
        # Average growth rate
        avg_growth = series.pct_change().mean() * 100
        
        return {
            'mom_growth': mom_growth,
            'yoy_growth': yoy_growth,
            'cagr': cagr,
            'avg_growth_rate': avg_growth,
            'current_value': series.iloc[-1],
            'start_value': series.iloc[0]
        }
    
    def identify_peaks_and_troughs(self, series, prominence=0.1):
        """
        Identify significant peaks and troughs
        
        Args:
            series (Series): Time series data
            prominence (float): Minimum prominence for peak detection
            
        Returns:
            dict: Peaks and troughs information
        """
        values = series.values
        
        # Find peaks
        peaks, peak_properties = find_peaks(values, prominence=prominence)
        
        # Find troughs (peaks in negative signal)
        troughs, trough_properties = find_peaks(-values, prominence=prominence)
        
        return {
            'peak_indices': peaks.tolist(),
            'peak_values': values[peaks].tolist(),
            'trough_indices': troughs.tolist(),
            'trough_values': values[troughs].tolist(),
            'peak_count': len(peaks),
            'trough_count': len(troughs)
        }
    
    def test_stationarity(self, series):
        """
        Test if time series is stationary using Augmented Dickey-Fuller test
        
        Args:
            series (Series): Time series data
            
        Returns:
            dict: Stationarity test results
        """
        try:
            result = adfuller(series.dropna())
            
            return {
                'is_stationary': result[1] < 0.05,
                'adf_statistic': result[0],
                'p_value': result[1],
                'critical_values': result[4]
            }
        except Exception as e:
            print(f"Stationarity test error: {e}")
            return None


def analyze_sales_trends(df, date_column='Date', value_column='TotalSales', 
                        forecast_days=30):
    """
    Comprehensive sales trend analysis for Power BI
    
    Args:
        df (DataFrame): Sales data
        date_column (str): Date column name
        value_column (str): Value column to analyze
        forecast_days (int): Days to forecast
        
    Returns:
        dict: Complete trend analysis results
    """
    # Ensure date column is datetime
    df[date_column] = pd.to_datetime(df[date_column])
    df = df.sort_values(date_column)
    
    # Create time series
    series = df.set_index(date_column)[value_column]
    
    # Initialize analyzer
    analyzer = TrendAnalyzer()
    
    # Run analyses
    results = {
        'trend': analyzer.detect_trend_direction(series),
        'seasonality': analyzer.detect_seasonality(series),
        'growth_metrics': analyzer.calculate_growth_metrics(series),
        'peaks_troughs': analyzer.identify_peaks_and_troughs(series),
        'stationarity': analyzer.test_stationarity(series)
    }
    
    # Generate forecasts
    results['forecast_linear'] = analyzer.forecast_linear_trend(series, steps=forecast_days)
    
    try:
        results['forecast_arima'] = analyzer.forecast_arima(series, steps=forecast_days)
        results['forecast_exponential'] = analyzer.forecast_exponential_smoothing(
            series, steps=forecast_days
        )
    except Exception as e:
        print(f"Advanced forecasting error: {e}")
        results['forecast_arima'] = None
        results['forecast_exponential'] = None
    
    # Seasonal decomposition
    try:
        results['decomposition'] = analyzer.seasonal_decomposition(series, period=7)
    except:
        results['decomposition'] = None
    
    return results


def main_example():
    """
    Example usage of trend analyzer
    """
    # Generate sample data
    np.random.seed(42)
    dates = pd.date_range('2023-01-01', periods=365, freq='D')
    
    # Trend + Seasonality + Noise
    trend = np.linspace(80000, 120000, 365)
    seasonal = 10000 * np.sin(np.arange(365) * 2 * np.pi / 7)  # Weekly pattern
    noise = np.random.normal(0, 5000, 365)
    sales = trend + seasonal + noise
    
    df = pd.DataFrame({
        'Date': dates,
        'TotalSales': sales
    })
    
    # Run analysis
    results = analyze_sales_trends(df, forecast_days=30)
    
    print("=" * 60)
    print("TREND ANALYSIS RESULTS")
    print("=" * 60)
    print(f"\nTrend Direction: {results['trend']['direction']}")
    print(f"Trend Strength (R²): {results['trend']['strength']:.4f}")
    print(f"Slope: {results['trend']['slope']:.2f}")
    
    print(f"\nHas Seasonality: {results['seasonality']['has_seasonality']}")
    print(f"Primary Period: {results['seasonality']['primary_period']} days")
    
    print(f"\nGrowth Metrics:")
    print(f"  CAGR: {results['growth_metrics']['cagr']:.2f}%")
    print(f"  Avg Growth Rate: {results['growth_metrics']['avg_growth_rate']:.2f}%")
    
    print(f"\nPeaks: {results['peaks_troughs']['peak_count']}")
    print(f"Troughs: {results['peaks_troughs']['trough_count']}")
    
    print(f"\nIs Stationary: {results['stationarity']['is_stationary']}")
    
    return results


if __name__ == "__main__":
    results = main_example()
