from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session
from sqlalchemy import or_
import pandas as pd
import io

from app.core.database import get_db
from app.models.trade_record import TradeRecord
from app.api.routes_auth import get_current_user

router = APIRouter(prefix="/api/data", tags=["data"])

@router.get("/")
def get_data(
    skip: int = Query(0, description="Pagination skip"),
    limit: int = Query(20, description="Pagination limit"),
    keyword: str = Query(None, description="Search keyword matching importer or product"),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    query = db.query(TradeRecord)
    
    if keyword:
        query = query.filter(
            or_(
                TradeRecord.importer.ilike(f"%{keyword}%"),
                TradeRecord.product.ilike(f"%{keyword}%"),
                TradeRecord.hs_code.ilike(f"%{keyword}%")
            )
        )
        
    total = query.count()
    records = query.offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "data": records
    }

@router.get("/export")
def export_data(
    keyword: str = Query(None, description="Search keyword matching importer or product"),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    query = db.query(TradeRecord)
    if keyword:
        query = query.filter(
            or_(
                TradeRecord.importer.ilike(f"%{keyword}%"),
                TradeRecord.product.ilike(f"%{keyword}%"),
                TradeRecord.hs_code.ilike(f"%{keyword}%")
            )
        )
        
    records = query.all()
    if not records:
        raise HTTPException(status_code=404, detail="No data found to export.")
        
    # Convert to standard dict list
    data_list = []
    for r in records:
        data_list.append({
            "Date": r.date.isoformat() if r.date else "",
            "Importer": r.importer,
            "HsCode": r.hs_code,
            "Product": r.product,
            "Quantity": r.quantity,
            "QuantityUnit": r.quantity_unit,
            "Value": r.value,
            "ValueUnit": r.value_unit,
            "UnitPrice": r.unit_price
        })
        
    df = pd.DataFrame(data_list)
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Trade Data')
    output.seek(0)
    
    headers = {
        'Content-Disposition': 'attachment; filename="exported_data.xlsx"'
    }
    
    return Response(
        content=output.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers
    )
