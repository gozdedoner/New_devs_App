from datetime import datetime
from decimal import Decimal
from typing import Dict, Any
from fastapi import HTTPException
from sqlalchemy import text

# ✅ GLOBAL POOL KULLAN
from app.core.database_pool import db_pool


async def calculate_monthly_revenue(
    property_id: str,
    month: int,
    year: int,
    tenant_id: str,
    db_session=None
) -> Decimal:
    """
    Calculates revenue for a specific month.
    """

    start_date = datetime(year, month, 1)

    if month < 12:
        end_date = datetime(year, month + 1, 1)
    else:
        end_date = datetime(year + 1, 1, 1)

    if not db_session:
        raise HTTPException(status_code=500, detail="Database session required")

    query = text("""
        SELECT COALESCE(SUM(total_amount), 0) as total
        FROM reservations
        WHERE property_id = :property_id
        AND tenant_id = :tenant_id
        AND check_in_date >= :start_date
        AND check_in_date < :end_date
    """)

    result = await db_session.execute(query, {
        "property_id": property_id,
        "tenant_id": tenant_id,
        "start_date": start_date,
        "end_date": end_date
    })

    row = result.fetchone()

    return Decimal(str(row.total))


async def calculate_total_revenue(property_id: str, tenant_id: str) -> Dict[str, Any]:
    """
    Aggregates revenue from database.
    """

    try:

        # ✅ CHECK GLOBAL POOL
        if not db_pool.session_factory:
            raise HTTPException(status_code=500, detail="Database pool not initialized")

        async with db_pool.get_session() as session:

            query = text("""
                SELECT 
                    property_id,
                    COALESCE(SUM(total_amount), 0) as total_revenue,
                    COUNT(*) as reservation_count
                FROM reservations 
                WHERE property_id = :property_id 
                AND tenant_id = :tenant_id
                GROUP BY property_id
            """)

            result = await session.execute(query, {
                "property_id": property_id,
                "tenant_id": tenant_id
            })

            row = result.fetchone()

            if not row:
                return {
                    "property_id": property_id,
                    "tenant_id": tenant_id,
                    "total": "0.00",
                    "currency": "USD",
                    "count": 0
                }

            total_revenue = Decimal(str(row.total_revenue))

            return {
                "property_id": property_id,
                "tenant_id": tenant_id,
                "total": str(total_revenue),
                "currency": "USD",
                "count": row.reservation_count
            }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Revenue calculation failed: {str(e)}"
        )
