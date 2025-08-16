# ===========================================
# app/api/sectors.py - 섹터 분석 관련
# ===========================================
from fastapi import APIRouter, Depends, HTTPException
from starlette.concurrency import run_in_threadpool
import logging

from app.schemas import (
    SectorTickerResponse, SectorAnalysisRequest, SectorAnalysisResponse
)
from app.core.dependencies import get_krx_service

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/sectors/groups")
def get_sector_groups(krx = Depends(get_krx_service)):
    """KOSPI, KOSDAQ 섹터 그룹 데이터를 제공합니다."""
    return krx.get_sector_groups()

@router.get("/sectors/tickers", response_model=SectorTickerResponse)
async def get_tickers_by_group(
    market: str, 
    group: str,
    krx = Depends(get_krx_service)
):
    """선택된 시장과 그룹에 속한 모든 섹터 티커와 이름을 반환합니다."""
    try:
        tickers_with_names = await run_in_threadpool(krx.get_tickers_by_group, market, group)
        formatted_tickers = [{"ticker": t, "name": n} for t, n in tickers_with_names]
        return {"tickers": formatted_tickers}
    except Exception as e:
        logger.error(f"섹터 티커 조회 오류: market={market}, group={group}, error={e}")
        raise HTTPException(status_code=404, detail="섹터 목록을 가져오는 데 실패했습니다.")

@router.post("/sectors/analysis", response_model=SectorAnalysisResponse)
async def analyze_sectors(
    request: SectorAnalysisRequest,
    krx = Depends(get_krx_service)
):
    """요청된 기간과 티커 목록에 대해 누적 수익률을 분석하여 반환합니다."""
    try:
        analysis_result = await run_in_threadpool(
            krx.analyze_sector_performance,
            request.start_date,
            request.end_date,
            request.tickers
        )
        if not analysis_result:
            raise HTTPException(status_code=404, detail="분석할 유효한 데이터를 찾을 수 없습니다.")

        return {"data": analysis_result}
    except Exception as e:
        logger.error(f"섹터 분석 API 오류: request={request.dict()}, error={e}")
        if not isinstance(e, HTTPException):
            raise HTTPException(status_code=500, detail="서버 내부에서 섹터 분석 중 오류가 발생했습니다.")
        raise