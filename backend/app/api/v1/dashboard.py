from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
from decimal import Decimal, ROUND_HALF_UP

from app.services.cache import get_revenue_summary
from app.core.auth import authenticate_request as get_current_user

router = APIRouter()


@router.get("/dashboard/summary")
async def get_dashboard_summary(
    property_id: str,
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:

    # ✅ FIX 1 — Strict tenant isolation (NO default fallback)
    tenant_id = getattr(current_user, "tenant_id", None)

    if not tenant_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid tenant context"
        )

    # Fetch revenue
    revenue_data = await get_revenue_summary(property_id, tenant_id)

    if not revenue_data:
        raise HTTPException(
            status_code=404,
            detail="Revenue data not found"
        )

    # ✅ FIX 2 — Decimal-safe rounding (financial accuracy)
    total_revenue = revenue_data["total"]

    if isinstance(total_revenue, Decimal):
        total_revenue = total_revenue.quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP
        )
    else:
        total_revenue = Decimal(str(total_revenue)).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP
        )

    return {
        "property_id": revenue_data["property_id"],
        "total_revenue": float(total_revenue),
        "currency": revenue_data["currency"],
        "reservations_count": revenue_data["count"]
    }
