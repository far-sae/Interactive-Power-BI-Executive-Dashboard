"""
Email Distribution Automation for Power BI Reports
Purpose: Automatically distribute dashboard reports to stakeholders
Supports: PDF exports, embedded reports, subscription management
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import requests
import json
import os
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PowerBIEmailDistributor:
    """
    Automated email distribution for Power BI reports
    """
    
    def __init__(self, smtp_server, smtp_port, sender_email, sender_password):
        """
        Initialize email distributor
        
        Args:
            smtp_server (str): SMTP server address
            smtp_port (int): SMTP port (typically 587 for TLS)
            sender_email (str): Sender email address
            sender_password (str): Sender email password
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password
    
    def send_email_with_attachment(self, recipient_email, subject, body, 
                                   attachment_path=None, html_body=None):
        """
        Send email with optional attachment
        
        Args:
            recipient_email (str or list): Recipient email(s)
            subject (str): Email subject
            body (str): Email body (plain text)
            attachment_path (str): Path to attachment file
            html_body (str): HTML formatted email body
            
        Returns:
            bool: Success status
        """
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.sender_email
            
            # Handle multiple recipients
            if isinstance(recipient_email, list):
                message["To"] = ", ".join(recipient_email)
                recipients = recipient_email
            else:
                message["To"] = recipient_email
                recipients = [recipient_email]
            
            # Add body
            text_part = MIMEText(body, "plain")
            message.attach(text_part)
            
            # Add HTML body if provided
            if html_body:
                html_part = MIMEText(html_body, "html")
                message.attach(html_part)
            
            # Add attachment if provided
            if attachment_path and os.path.exists(attachment_path):
                with open(attachment_path, "rb") as attachment:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(attachment.read())
                
                encoders.encode_base64(part)
                
                filename = os.path.basename(attachment_path)
                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename= {filename}",
                )
                
                message.attach(part)
            
            # Create secure connection and send email
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, recipients, message.as_string())
            
            logger.info(f"Email sent successfully to {recipients}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
    
    def send_embedded_report_email(self, recipient_email, report_url, subject, 
                                   custom_message=""):
        """
        Send email with embedded Power BI report link
        
        Args:
            recipient_email (str or list): Recipient email(s)
            report_url (str): Power BI report URL
            subject (str): Email subject
            custom_message (str): Additional message
            
        Returns:
            bool: Success status
        """
        # Plain text body
        body = f"""
Dear Stakeholder,

{custom_message}

Please find the latest Executive Dashboard report at the link below:

{report_url}

This report is updated automatically and provides real-time insights into key business metrics.

Best regards,
Business Intelligence Team
        """
        
        # HTML body with styling
        html_body = f"""
        <html>
          <body style="font-family: Arial, sans-serif; color: #333;">
            <h2 style="color: #003366;">Executive Dashboard Report</h2>
            <p>Dear Stakeholder,</p>
            <p>{custom_message}</p>
            <p>Please access the latest dashboard report:</p>
            <div style="margin: 20px 0;">
              <a href="{report_url}" 
                 style="background-color: #003366; 
                        color: white; 
                        padding: 12px 24px; 
                        text-decoration: none; 
                        border-radius: 4px;
                        display: inline-block;">
                View Dashboard
              </a>
            </div>
            <p style="font-size: 12px; color: #666;">
              This report is updated automatically and provides real-time insights 
              into key business metrics.
            </p>
            <hr style="border: 1px solid #eee; margin: 20px 0;">
            <p style="font-size: 11px; color: #999;">
              Business Intelligence Team<br>
              Report Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
            </p>
          </body>
        </html>
        """
        
        return self.send_email_with_attachment(
            recipient_email, subject, body, html_body=html_body
        )
    
    def send_kpi_summary_email(self, recipient_email, kpi_data, subject):
        """
        Send email with KPI summary
        
        Args:
            recipient_email (str or list): Recipient email(s)
            kpi_data (dict): KPI metrics to include
            subject (str): Email subject
            
        Returns:
            bool: Success status
        """
        # Format KPIs as text
        kpi_text = "\n".join([f"{key}: {value}" for key, value in kpi_data.items()])
        
        body = f"""
Executive Dashboard - Daily KPI Summary
Generated: {datetime.now().strftime('%B %d, %Y')}

Key Performance Indicators:
{kpi_text}

For detailed analysis, please access the full dashboard.

Best regards,
Business Intelligence Team
        """
        
        # Format KPIs as HTML table
        kpi_rows = ""
        for key, value in kpi_data.items():
            kpi_rows += f"""
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #eee;">{key}</td>
                <td style="padding: 8px; border-bottom: 1px solid #eee; font-weight: bold;">{value}</td>
            </tr>
            """
        
        html_body = f"""
        <html>
          <body style="font-family: Arial, sans-serif;">
            <h2 style="color: #003366;">Executive Dashboard - Daily KPI Summary</h2>
            <p style="color: #666;">Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
            
            <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
              <thead>
                <tr style="background-color: #003366; color: white;">
                  <th style="padding: 12px; text-align: left;">Metric</th>
                  <th style="padding: 12px; text-align: left;">Value</th>
                </tr>
              </thead>
              <tbody>
                {kpi_rows}
              </tbody>
            </table>
            
            <p style="font-size: 12px; color: #666;">
              For detailed analysis, please access the full dashboard.
            </p>
          </body>
        </html>
        """
        
        return self.send_email_with_attachment(
            recipient_email, subject, body, html_body=html_body
        )


class DistributionScheduler:
    """
    Manage scheduled report distributions
    """
    
    def __init__(self, config_file='distribution_config.json'):
        """
        Initialize scheduler with configuration
        
        Args:
            config_file (str): Path to distribution configuration file
        """
        self.config_file = config_file
        self.load_config()
    
    def load_config(self):
        """Load distribution configuration from file"""
        try:
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
            logger.info("Distribution configuration loaded")
        except FileNotFoundError:
            logger.warning(f"Configuration file {self.config_file} not found")
            self.config = {}
    
    def get_recipients_for_report(self, report_name):
        """
        Get recipient list for a specific report
        
        Args:
            report_name (str): Report name
            
        Returns:
            list: Recipient email addresses
        """
        return self.config.get('reports', {}).get(report_name, {}).get('recipients', [])
    
    def get_schedule_for_report(self, report_name):
        """
        Get distribution schedule for a report
        
        Args:
            report_name (str): Report name
            
        Returns:
            dict: Schedule configuration
        """
        return self.config.get('reports', {}).get(report_name, {}).get('schedule', {})


def create_sample_distribution_config():
    """
    Create sample distribution configuration file
    """
    config = {
        "smtp": {
            "server": "smtp.office365.com",
            "port": 587,
            "sender_email": "bi-reports@company.com"
        },
        "reports": {
            "Executive Dashboard": {
                "report_url": "https://app.powerbi.com/groups/xxx/reports/yyy",
                "recipients": [
                    "ceo@company.com",
                    "cfo@company.com",
                    "coo@company.com"
                ],
                "schedule": {
                    "frequency": "daily",
                    "time": "08:00",
                    "timezone": "EST"
                },
                "include_kpi_summary": True
            },
            "Sales Dashboard": {
                "report_url": "https://app.powerbi.com/groups/xxx/reports/zzz",
                "recipients": [
                    "sales-team@company.com"
                ],
                "schedule": {
                    "frequency": "weekly",
                    "day": "Monday",
                    "time": "09:00"
                },
                "include_kpi_summary": False
            }
        }
    }
    
    with open('distribution_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    logger.info("Sample distribution configuration created")


def main():
    """
    Main execution function
    """
    # Example usage
    
    # SMTP Configuration (use environment variables in production)
    SMTP_SERVER = "smtp.office365.com"
    SMTP_PORT = 587
    SENDER_EMAIL = "bi-reports@company.com"
    SENDER_PASSWORD = "your-password"  # Use secure storage
    
    # Initialize distributor
    distributor = PowerBIEmailDistributor(
        SMTP_SERVER, SMTP_PORT, SENDER_EMAIL, SENDER_PASSWORD
    )
    
    # Example 1: Send embedded report link
    report_url = "https://app.powerbi.com/groups/your-workspace/reports/your-report"
    recipients = ["executive@company.com"]
    
    distributor.send_embedded_report_email(
        recipients,
        report_url,
        subject="Executive Dashboard - Weekly Update",
        custom_message="Please review the latest performance metrics."
    )
    
    # Example 2: Send KPI summary
    kpi_data = {
        "Total Revenue": "$5.2M",
        "Revenue Growth (YoY)": "+12.5%",
        "Gross Profit Margin": "42.3%",
        "Customer Satisfaction": "4.6/5.0",
        "Active Customers": "1,247"
    }
    
    distributor.send_kpi_summary_email(
        recipients,
        kpi_data,
        subject="Executive Dashboard - Daily KPI Summary"
    )
    
    logger.info("Distribution completed")


if __name__ == "__main__":
    main()
