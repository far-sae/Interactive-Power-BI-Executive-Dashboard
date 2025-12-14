# Power BI Executive Dashboard - Data Source Configuration

## Overview
This document provides configuration details for connecting to various data sources.

---

## 1. Microsoft SQL Server Connection

### Connection String
```
Server: your-server-name.database.windows.net
Database: ExecutiveDashboard_DW
Authentication: SQL Server / Windows Authentication
Port: 1433 (default)
```

### Power BI Connection Setup

**Method 1: SQL Server (Import)**
```
1. Get Data → SQL Server
2. Server: your-server-name
3. Database: ExecutiveDashboard_DW
4. Data Connectivity mode: Import
5. Advanced options:
   - Command timeout: 30 minutes
   - SQL statement: (leave blank for all tables)
   - Relationship columns: Enabled
```

**Method 2: SQL Server (DirectQuery)**
```
1. Get Data → SQL Server
2. Server: your-server-name
3. Database: ExecutiveDashboard_DW
4. Data Connectivity mode: DirectQuery
5. Select tables
6. Click Load
```

### Power Query M Code
```m
let
    Source = Sql.Database("your-server-name", "ExecutiveDashboard_DW", [
        CommandTimeout = #duration(0, 0, 30, 0)
    ]),
    Navigation = Source{[Schema="dbo"]}[Data]
in
    Navigation
```

### SQL Server Optimization Settings
```sql
-- Enable Read Committed Snapshot Isolation
ALTER DATABASE ExecutiveDashboard_DW
SET READ_COMMITTED_SNAPSHOT ON;

-- Update statistics
EXEC sp_updatestats;

-- Rebuild indexes
ALTER INDEX ALL ON dbo.FactSales REBUILD;
```

---

## 2. Excel File Connection

### File Location
```
Network Path: \\shared-drive\data\excel_files\
Local Path: C:\Data\ExecutiveDashboard\excel\
```

### Power BI Connection
```
1. Get Data → Excel
2. Browse to file location
3. Select worksheets/tables
4. Transform data as needed
5. Click Load
```

### Power Query M Code
```m
let
    Source = Excel.Workbook(
        File.Contents("\\shared-drive\data\excel_files\SalesData.xlsx"), 
        null, 
        true
    ),
    Sheet1 = Source{[Item="Sales",Kind="Sheet"]}[Data],
    PromotedHeaders = Table.PromoteHeaders(Sheet1, [PromoteAllScalars=true]),
    ChangedType = Table.TransformColumnTypes(PromotedHeaders,{
        {"Date", type date},
        {"Amount", Currency.Type},
        {"Quantity", Int64.Type}
    })
in
    ChangedType
```

### Refresh Behavior
- **Incremental refresh**: Not supported for Excel
- **Full refresh**: Entire file reloaded each refresh
- **Best practice**: Use for small reference tables only

---

## 3. REST API Connection

### Generic REST API Configuration

**Example: Custom Sales API**
```
Endpoint: https://api.company.com/sales/v1
Authentication: OAuth 2.0 or API Key
Rate Limit: 100 requests/minute
```

### Power BI Connection
```
1. Get Data → Web
2. URL: https://api.company.com/sales/v1/data
3. Advanced:
   - HTTP request header parameters:
     - Authorization: Bearer {token}
     - Content-Type: application/json
4. OK → Parse JSON response
```

### Power Query M Code
```m
let
    // API Configuration
    BaseUrl = "https://api.company.com/sales/v1",
    ApiKey = "your-api-key",
    
    // Function to get data
    GetData = (endpoint as text) =>
        let
            Source = Json.Document(
                Web.Contents(
                    BaseUrl & endpoint,
                    [
                        Headers = [
                            #"Authorization" = "Bearer " & ApiKey,
                            #"Content-Type" = "application/json"
                        ]
                    ]
                )
            ),
            #"Converted to Table" = Table.FromList(
                Source[data], 
                Splitter.SplitByNothing(), 
                null, 
                null, 
                ExtraValues.Error
            ),
            #"Expanded Column" = Table.ExpandRecordColumn(
                #"Converted to Table", 
                "Column1", 
                {"id", "date", "amount", "customer"}
            )
        in
            #"Expanded Column",
    
    // Get sales data
    SalesData = GetData("/sales")
in
    SalesData
```

### Pagination Handling
```m
let
    GetAllPages = (url as text) =>
        let
            GetPage = (pageUrl) =>
                let
                    Response = Json.Document(Web.Contents(pageUrl)),
                    Data = Response[data],
                    NextPage = Response[nextPage]
                in
                    if NextPage = null then
                        Data
                    else
                        List.Combine({Data, @GetPage(NextPage)}),
            
            AllData = GetPage(url),
            ToTable = Table.FromList(AllData, Splitter.SplitByNothing())
        in
            ToTable
in
    GetAllPages
```

---

## 4. Azure SQL Database

### Connection String
```
Server: your-server.database.windows.net,1433
Database: ExecutiveDashboard_DW
User ID: {username}@{server}
Password: {password}
Encrypt: yes
TrustServerCertificate: no
Connection Timeout: 30
```

### Power BI Connection
```
1. Get Data → Azure → Azure SQL Database
2. Server: your-server.database.windows.net
3. Database: ExecutiveDashboard_DW
4. Data Connectivity mode: DirectQuery (recommended for large datasets)
5. Advanced options:
   - Enable MARS: Yes
   - Include relationship columns: Yes
```

### Managed Identity Authentication
```m
let
    Source = AzureSql.Database(
        "your-server.database.windows.net",
        "ExecutiveDashboard_DW",
        [
            Authentication = AzureActiveDirectory
        ]
    )
in
    Source
```

---

## 5. Salesforce Connection

### Prerequisites
- Salesforce API access
- Connected App configured
- OAuth credentials

### Power BI Connection
```
1. Get Data → Online Services → Salesforce Objects
2. Login to Salesforce
3. Select objects:
   - Account
   - Opportunity
   - Contact
   - Custom Objects
4. Click Load
```

### Custom SOQL Query
```m
let
    Source = Salesforce.Data("https://yourinstance.salesforce.com"),
    Query = Salesforce.Query(
        Source,
        "SELECT Id, Name, Amount, CloseDate, StageName 
         FROM Opportunity 
         WHERE CloseDate >= LAST_N_DAYS:90"
    )
in
    Query
```

---

## 6. Azure Blob Storage

### Configuration
```
Storage Account: companystorage
Container: powerbi-data
Access: SAS Token or Access Key
```

### Power BI Connection
```
1. Get Data → Azure → Azure Blob Storage
2. Account name or URL: 
   https://companystorage.blob.core.windows.net
3. Authentication:
   - Account Key: Use storage account key
   - SAS URL: Use SAS token
```

### Power Query M Code
```m
let
    Source = AzureStorage.Blobs(
        "https://companystorage.blob.core.windows.net/powerbi-data"
    ),
    #"Filtered Files" = Table.SelectRows(
        Source, 
        each Text.EndsWith([Name], ".csv")
    ),
    #"Downloaded Files" = Table.AddColumn(
        #"Filtered Files", 
        "Binary", 
        each [Content]
    ),
    #"Parsed CSV" = Table.AddColumn(
        #"Downloaded Files",
        "Data",
        each Csv.Document([Binary])
    ),
    #"Combined Files" = Table.Combine(#"Parsed CSV"[Data])
in
    #"Combined Files"
```

---

## 7. AWS S3 Connection

### Prerequisites
- AWS Access Key ID
- AWS Secret Access Key
- S3 bucket name and region

### Power BI Connection (via Python)
```python
import pandas as pd
import boto3
from io import StringIO

# AWS Configuration
s3_client = boto3.client(
    's3',
    aws_access_key_id='YOUR_ACCESS_KEY',
    aws_secret_access_key='YOUR_SECRET_KEY',
    region_name='us-east-1'
)

# Get data from S3
response = s3_client.get_object(
    Bucket='your-bucket-name',
    Key='data/sales_data.csv'
)

# Read CSV
df = pd.read_csv(response['Body'])

# Output to Power BI
dataset = df
```

---

## 8. SharePoint List Connection

### SharePoint Site
```
Site URL: https://company.sharepoint.com/sites/ExecutiveDashboard
List Name: Sales Targets
```

### Power BI Connection
```
1. Get Data → Online Services → SharePoint Online List
2. Site URL: https://company.sharepoint.com/sites/ExecutiveDashboard
3. Select lists:
   - Sales Targets
   - Product Catalog
   - Customer Contacts
4. Click Load
```

### Power Query M Code
```m
let
    Source = SharePoint.Tables(
        "https://company.sharepoint.com/sites/ExecutiveDashboard",
        [ApiVersion = 15]
    ),
    #"Sales Targets" = Source{[Title="Sales Targets"]}[Items],
    #"Removed Columns" = Table.RemoveColumns(
        #"Sales Targets",
        {"Attachments", "GUID", "ComplianceAssetId"}
    )
in
    #"Removed Columns"
```

---

## 9. OData Feed

### Configuration
```
OData Endpoint: https://api.company.com/odata/v4/
Entity Sets: Sales, Products, Customers
```

### Power BI Connection
```
1. Get Data → OData Feed
2. URL: https://api.company.com/odata/v4/
3. Authentication: Basic or OAuth
4. Select entity sets
5. Click Load
```

---

## 10. Google Analytics

### Prerequisites
- Google Analytics account
- API access enabled
- View ID

### Power BI Connection
```
1. Get Data → Online Services → Google Analytics
2. Sign in with Google account
3. Select:
   - Account
   - Property
   - View
4. Choose metrics and dimensions
5. Click Load
```

---

## Data Gateway Configuration

### On-Premises Data Gateway

**Installation:**
1. Download from: https://powerbi.microsoft.com/gateway/
2. Install on server with data source access
3. Sign in with Power BI account
4. Register gateway

**Configuration:**
1. Power BI Service → Settings → Manage gateways
2. Add data sources:
   - SQL Server (on-premises)
   - File system
   - Other on-premises sources
3. Configure credentials
4. Test connection

**Best Practices:**
- Install on dedicated server
- Use personal mode for individual developers
- Enable high availability mode for production
- Regular updates and monitoring

---

## Connection Security

### Credential Storage
- **Power BI Service**: Encrypted credential storage
- **On-Premises**: Windows Credential Manager
- **Best Practice**: Use service accounts, not personal accounts

### Network Security
- Firewall rules for SQL Server (port 1433)
- VPN for remote connections
- IP whitelisting for cloud databases
- SSL/TLS encryption for all connections

### Authentication Methods
- **SQL Server**: Windows Authentication (preferred) or SQL Authentication
- **Azure**: Azure AD Authentication
- **APIs**: OAuth 2.0 or API Keys (stored securely)

---

## Refresh Configuration per Source

| Data Source | Refresh Frequency | Method | Gateway Required |
|-------------|------------------|--------|------------------|
| SQL Server (Cloud) | Every 2 hours | Scheduled | No |
| SQL Server (On-Prem) | Daily | Scheduled | Yes |
| Excel Files | Daily | Manual/Scheduled | Yes (if on network) |
| REST APIs | Every 4 hours | Scheduled | No |
| Salesforce | Every 8 hours | Scheduled | No |
| Azure Blob | Daily | Scheduled | No |
| SharePoint | Daily | Scheduled | No |

---

## Troubleshooting

### Common Connection Issues

**SQL Server:**
- Error: "Login failed" → Check credentials and permissions
- Error: "Server not found" → Verify server name and network connectivity
- Error: "Timeout" → Increase command timeout in Advanced options

**REST API:**
- Error: "401 Unauthorized" → Check API key/token
- Error: "429 Too Many Requests" → Implement rate limiting
- Error: "Malformed JSON" → Validate API response format

**Excel Files:**
- Error: "File not found" → Check file path and permissions
- Error: "External table not in expected format" → Verify Excel file isn't corrupted
