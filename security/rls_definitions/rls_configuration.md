# Row-Level Security (RLS) Configuration for Executive Dashboard

## Overview
Row-level security ensures users only see data they are authorized to access based on their role and organizational hierarchy.

## Security Roles

### 1. Executive (C-Suite)
**Access Level**: Full access to all data

**DAX Filter**: None (no restrictions)

```dax
-- No filter applied - full data access
TRUE()
```

---

### 2. Regional Manager
**Access Level**: Data for assigned region only

**DAX Filter**:
```dax
-- Filter by user's region
DimGeography[Region] = USERNAME()
    || DimGeography[Region] IN 
    {
        LOOKUPVALUE(
            DimEmployee[Region],
            DimEmployee[Email],
            USERPRINCIPALNAME()
        )
    }
```

**Alternative using email mapping**:
```dax
DimGeography[Region] = 
    LOOKUPVALUE(
        DimEmployee[Region],
        DimEmployee[Email],
        USERPRINCIPALNAME()
    )
```

---

### 3. Department Head
**Access Level**: Data for assigned department only

**DAX Filter**:
```dax
DimEmployee[Department] = 
    LOOKUPVALUE(
        DimEmployee[Department],
        DimEmployee[Email],
        USERPRINCIPALNAME()
    )
```

---

### 4. Sales Representative
**Access Level**: Own sales data + assigned customers

**DAX Filter**:
```dax
-- Filter to sales rep's own transactions
DimEmployee[Email] = USERPRINCIPALNAME()
    ||
-- Or assigned customers
DimCustomer[AccountManager] = 
    LOOKUPVALUE(
        DimEmployee[FullName],
        DimEmployee[Email],
        USERPRINCIPALNAME()
    )
```

---

### 5. Finance Team
**Access Level**: All financial data, limited customer details

**DAX Filter on Customer Table**:
```dax
-- Anonymize customer names for finance
TRUE()
-- Customer details masked in visuals via field-level security
```

**Note**: Use field-level security to hide sensitive customer fields

---

### 6. Analyst (Read-Only)
**Access Level**: All data, no editing rights

**DAX Filter**: 
```dax
TRUE()
```

**Note**: Read-only enforced through Power BI Service permissions, not RLS

---

## Implementation Steps

### Step 1: Create Security Table
Create a mapping table for user permissions:

```sql
CREATE TABLE dbo.UserSecurity (
    UserEmail VARCHAR(200) PRIMARY KEY,
    UserRole VARCHAR(50),
    Region VARCHAR(100),
    Department VARCHAR(100),
    SalesTerritory VARCHAR(100),
    EmployeeID VARCHAR(50)
);

-- Sample data
INSERT INTO dbo.UserSecurity VALUES
('john.doe@company.com', 'Executive', NULL, NULL, NULL, 'EMP-001'),
('jane.smith@company.com', 'Regional Manager', 'US East', NULL, 'US East', 'EMP-002'),
('bob.jones@company.com', 'Sales Rep', 'US West', 'Sales', 'US West', 'EMP-005');
```

### Step 2: Create RLS Roles in Power BI Desktop

1. **Modeling Tab** → **Manage Roles**
2. **Create Role** for each security level
3. **Add DAX filters** to relevant tables

### Step 3: Test RLS in Power BI Desktop

1. **Modeling Tab** → **View As**
2. Select role to test
3. Optionally add specific user
4. Verify data visibility

### Step 4: Assign Users to Roles in Power BI Service

1. Publish report to Power BI Service
2. Navigate to dataset **Security** settings
3. Add users/groups to each role
4. Save changes

---

## Advanced RLS Patterns

### Dynamic Security Using Security Table

**On DimGeography:**
```dax
[Region] IN 
    CALCULATETABLE(
        VALUES(UserSecurity[Region]),
        UserSecurity[UserEmail] = USERPRINCIPALNAME()
    )
```

### Hierarchical Security (Manager sees team data)

**On DimEmployee:**
```dax
-- User sees own data
[Email] = USERPRINCIPALNAME()
    ||
-- Or data from direct reports
[ManagerEmployeeID] = 
    LOOKUPVALUE(
        DimEmployee[EmployeeID],
        DimEmployee[Email],
        USERPRINCIPALNAME()
    )
```

### Date-Based Security (Historical restrictions)

**On DimDate:**
```dax
-- Only show last 90 days for certain roles
[FullDate] >= DATE(YEAR(TODAY()), MONTH(TODAY()), DAY(TODAY())) - 90
```

### Customer Segmentation Security

**On DimCustomer:**
```dax
-- Only Premium customers for premium support team
[CustomerSegment] = "Premium"
```

---

## Testing Matrix

| Role | Test User | Expected Data Access |
|------|-----------|---------------------|
| Executive | ceo@company.com | All regions, all departments |
| Regional Manager | manager.east@company.com | US East region only |
| Department Head | sales.director@company.com | Sales department only |
| Sales Rep | rep1@company.com | Own sales + assigned customers |
| Finance Team | finance@company.com | All financial data |
| Analyst | analyst@company.com | All data, read-only |

---

## Security Best Practices

### 1. Performance Optimization
- Keep RLS filters simple
- Avoid complex calculations in RLS
- Use security tables for dynamic assignments
- Test performance with RLS enabled

### 2. Maintenance
- Document all RLS rules
- Regular audit of user assignments
- Remove access for departed employees
- Review quarterly

### 3. Compliance
- Log all access attempts
- Regular security reviews
- Align with data governance policies
- Document business justification

### 4. Error Handling
- Graceful handling of missing user assignments
- Clear messaging when no data visible
- Fallback roles for edge cases

---

## Troubleshooting

### Issue: User sees no data
**Solution**: 
- Verify user assigned to role
- Check RLS filter syntax
- Ensure user email matches USERPRINCIPALNAME()

### Issue: User sees too much data
**Solution**:
- Review role assignments (user may be in multiple roles)
- Check for conflicting filters
- Verify most restrictive role applies

### Issue: Performance degradation
**Solution**:
- Simplify RLS DAX expressions
- Create indexed security tables
- Use Import mode instead of DirectQuery for security table

---

## Integration with Azure AD

For enterprise deployments, integrate with Azure Active Directory:

1. **Dynamic Groups**: Automatically assign users based on AD attributes
2. **Group-Based Security**: Assign AD groups to roles
3. **Synchronized Mappings**: Keep security table in sync with AD

**Example Security Table Update from AD:**
```sql
-- Sync script (run via Azure Function or SSIS)
MERGE dbo.UserSecurity AS target
USING (
    SELECT 
        mail AS UserEmail,
        department AS Department,
        office AS Region,
        jobTitle AS UserRole
    FROM AzureAD.Users
) AS source
ON target.UserEmail = source.UserEmail
WHEN MATCHED THEN UPDATE SET
    target.Department = source.Department,
    target.Region = source.Region,
    target.UserRole = source.UserRole
WHEN NOT MATCHED THEN INSERT
    (UserEmail, Department, Region, UserRole)
    VALUES (source.UserEmail, source.Department, source.Region, source.UserRole);
```

---

## RLS Validation Checklist

- [ ] All roles defined
- [ ] DAX filters tested
- [ ] Users assigned to appropriate roles
- [ ] Performance tested with RLS enabled
- [ ] Documentation updated
- [ ] Stakeholders informed
- [ ] Compliance requirements met
- [ ] Audit trail configured
