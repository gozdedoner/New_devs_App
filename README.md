PropertyFlow Debug Assignment
Overview

This repository contains my solution for the PropertyFlow revenue dashboard debugging assignment.

The main focus areas addressed:

Tenant-aware revenue calculation

Removal of unsafe mock fallback logic

Proper database pool validation

Financial precision handling using Decimal

Improved error handling with meaningful HTTP responses

Fixes Implemented
1️⃣ Revenue Calculation

Ensured tenant_id is always included in queries.

Used COALESCE(SUM(...), 0) to prevent null issues.

Returned revenue as string to preserve financial precision.

Removed mock fallback behavior to avoid incorrect financial reporting.

2️⃣ Database Pool Handling

Added explicit validation for database pool availability.

Prevented silent failures when session factory is not initialized.

Improved error propagation using HTTPException.

3️⃣ Monthly Revenue Function

Required active db_session

Proper date range calculation

Secure parameter binding using SQLAlchemy text

Error Handling

If the database pool is not available, the API now correctly returns:

500 - Revenue calculation failed: Database pool not available


instead of returning misleading mock values.

Technical Notes

SQLAlchemy async sessions

Parameterized queries

Decimal-safe financial calculations

Clean separation of service logic

Author

Gözde Döner
