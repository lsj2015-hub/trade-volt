# ===========================================
# app/api/krx.py - KRX 관련 데이터
# ===========================================
from fastapi import APIRouter, Depends, HTTPException
from starlette.concurrency import run_in_threadpool
import logging

from app.schemas import (
    TradingVolumeRequest, TradingVolumeResponse,
    NetPurchaseRequest, NetPurchaseResponse
)
from app.core.dependencies import get_krx_service

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/krx/trading-volume", response_model=TradingVolumeResponse)
async def get_trading_volume(
    request: TradingVolumeRequest,
    krx = Depends(get_krx_service)
):
    """투자자별 매매동향을 조회합니다."""
    try:
        result = await run_in_threadpool(
            krx.get_trading_volume,
            request.start_date,
            request.end_date,
            request.ticker,
            request.detail,
            request.institution_only
        )
        if not result:
            raise HTTPException(status_code=404, detail="매매동향 데이터를 찾을 수 없습니다.")
        return result
    except Exception as e:
        logger.error(f"매매동향 조회 오류: {e}")
        if not isinstance(e, HTTPException):
            raise HTTPException(status_code=500, detail="매매동향 조회 중 오류가 발생했습니다.")
        raise

@router.post("/krx/net-purchases", response_model=NetPurchaseResponse)
async def get_top_net_purchases(
    request: NetPurchaseRequest,
    krx = Depends(get_krx_service)
):
    """순매수 상위 종목을 조회합니다."""
    try:
        result = await run_in_threadpool(
            krx.get_top_net_purchases,
            request.start_date,
            request.end_date,
            request.market,
            request.investor
        )
        if not result:
            raise HTTPException(status_code=404, detail="순매수 데이터를 찾을 수 없습니다.")
        return result
    except Exception as e:
        logger.error(f"순매수 조회 오류: {e}")
        if not isinstance(e, HTTPException):
            raise HTTPException(status_code=500, detail="순매수 조회 중 오류가 발생했습니다.")
        raise
