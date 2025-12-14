"""
Power BI Data Refresh Automation Script
Purpose: Automate dataset refresh in Power BI Service using REST API
Requires: Power BI Premium or Pro license with API access
"""

import requests
import json
import time
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('powerbi_refresh.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class PowerBIRefreshManager:
    """
    Manages Power BI dataset refresh operations via REST API
    """
    
    def __init__(self, client_id, client_secret, tenant_id):
        """
        Initialize Power BI API client
        
        Args:
            client_id (str): Azure AD App Client ID
            client_secret (str): Azure AD App Client Secret
            tenant_id (str): Azure AD Tenant ID
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.tenant_id = tenant_id
        self.access_token = None
        self.base_url = "https://api.powerbi.com/v1.0/myorg"
        
    def get_access_token(self):
        """
        Obtain OAuth access token from Azure AD
        
        Returns:
            str: Access token
        """
        url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'scope': 'https://analysis.windows.net/powerbi/api/.default'
        }
        
        try:
            response = requests.post(url, headers=headers, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data['access_token']
            
            logger.info("Successfully obtained access token")
            return self.access_token
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to obtain access token: {e}")
            raise
    
    def get_headers(self):
        """
        Get request headers with authentication
        
        Returns:
            dict: HTTP headers
        """
        if not self.access_token:
            self.get_access_token()
        
        return {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
    
    def trigger_dataset_refresh(self, workspace_id, dataset_id, notification_enabled=True):
        """
        Trigger dataset refresh
        
        Args:
            workspace_id (str): Power BI Workspace ID
            dataset_id (str): Dataset ID to refresh
            notification_enabled (bool): Send notification on completion
            
        Returns:
            bool: Success status
        """
        url = f"{self.base_url}/groups/{workspace_id}/datasets/{dataset_id}/refreshes"
        
        payload = {
            "notifyOption": "MailOnFailure" if notification_enabled else "NoNotification"
        }
        
        try:
            response = requests.post(
                url,
                headers=self.get_headers(),
                json=payload
            )
            response.raise_for_status()
            
            logger.info(f"Successfully triggered refresh for dataset {dataset_id}")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to trigger refresh: {e}")
            if hasattr(e.response, 'text'):
                logger.error(f"Response: {e.response.text}")
            return False
    
    def get_refresh_history(self, workspace_id, dataset_id, top=10):
        """
        Get refresh history for a dataset
        
        Args:
            workspace_id (str): Power BI Workspace ID
            dataset_id (str): Dataset ID
            top (int): Number of records to retrieve
            
        Returns:
            list: Refresh history records
        """
        url = f"{self.base_url}/groups/{workspace_id}/datasets/{dataset_id}/refreshes?$top={top}"
        
        try:
            response = requests.get(url, headers=self.get_headers())
            response.raise_for_status()
            
            history = response.json()
            logger.info(f"Retrieved {len(history.get('value', []))} refresh records")
            
            return history.get('value', [])
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get refresh history: {e}")
            return []
    
    def wait_for_refresh_completion(self, workspace_id, dataset_id, 
                                   max_wait_minutes=60, check_interval=30):
        """
        Wait for dataset refresh to complete
        
        Args:
            workspace_id (str): Power BI Workspace ID
            dataset_id (str): Dataset ID
            max_wait_minutes (int): Maximum time to wait
            check_interval (int): Seconds between status checks
            
        Returns:
            str: Final refresh status
        """
        logger.info(f"Waiting for refresh completion (max {max_wait_minutes} minutes)...")
        
        start_time = time.time()
        max_wait_seconds = max_wait_minutes * 60
        
        while True:
            elapsed = time.time() - start_time
            
            if elapsed > max_wait_seconds:
                logger.warning("Refresh check timed out")
                return "Timeout"
            
            # Get latest refresh status
            history = self.get_refresh_history(workspace_id, dataset_id, top=1)
            
            if history:
                status = history[0].get('status')
                logger.info(f"Current refresh status: {status}")
                
                if status in ['Completed', 'Failed', 'Cancelled']:
                    return status
            
            time.sleep(check_interval)
    
    def refresh_multiple_datasets(self, refresh_config):
        """
        Refresh multiple datasets in sequence
        
        Args:
            refresh_config (list): List of dataset configurations
                [{'workspace_id': 'xxx', 'dataset_id': 'yyy', 'wait': True}, ...]
            
        Returns:
            dict: Results for each dataset
        """
        results = {}
        
        for config in refresh_config:
            workspace_id = config['workspace_id']
            dataset_id = config['dataset_id']
            wait = config.get('wait', False)
            dataset_name = config.get('name', dataset_id)
            
            logger.info(f"Refreshing dataset: {dataset_name}")
            
            success = self.trigger_dataset_refresh(workspace_id, dataset_id)
            
            if success and wait:
                status = self.wait_for_refresh_completion(workspace_id, dataset_id)
                results[dataset_name] = status
            else:
                results[dataset_name] = "Triggered" if success else "Failed"
        
        return results
    
    def get_dataset_info(self, workspace_id, dataset_id):
        """
        Get dataset information
        
        Args:
            workspace_id (str): Power BI Workspace ID
            dataset_id (str): Dataset ID
            
        Returns:
            dict: Dataset information
        """
        url = f"{self.base_url}/groups/{workspace_id}/datasets/{dataset_id}"
        
        try:
            response = requests.get(url, headers=self.get_headers())
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get dataset info: {e}")
            return None


def load_refresh_schedule():
    """
    Load refresh schedule from configuration file
    
    Returns:
        dict: Refresh schedule configuration
    """
    try:
        with open('refresh_schedule.json', 'r') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        logger.error("refresh_schedule.json not found")
        return None


def main():
    """
    Main execution function
    """
    # Load credentials (in production, use Azure Key Vault)
    # These should be stored securely, not hardcoded
    CLIENT_ID = "your-client-id"
    CLIENT_SECRET = "your-client-secret"
    TENANT_ID = "your-tenant-id"
    
    # Initialize refresh manager
    manager = PowerBIRefreshManager(CLIENT_ID, CLIENT_SECRET, TENANT_ID)
    
    # Example: Refresh configuration
    refresh_config = [
        {
            'workspace_id': 'your-workspace-id',
            'dataset_id': 'your-dataset-id',
            'name': 'Executive Dashboard Dataset',
            'wait': True
        }
    ]
    
    # Execute refresh
    logger.info("=" * 60)
    logger.info("POWER BI DATASET REFRESH STARTED")
    logger.info("=" * 60)
    
    results = manager.refresh_multiple_datasets(refresh_config)
    
    # Log results
    logger.info("=" * 60)
    logger.info("REFRESH RESULTS")
    logger.info("=" * 60)
    
    for dataset_name, status in results.items():
        logger.info(f"{dataset_name}: {status}")
    
    # Send summary notification (implement as needed)
    send_notification_email(results)


def send_notification_email(results):
    """
    Send email notification with refresh results
    
    Args:
        results (dict): Refresh results
    """
    # Implement email notification
    # This is a placeholder - implement using smtplib or SendGrid
    logger.info("Email notification sent (placeholder)")


if __name__ == "__main__":
    main()
