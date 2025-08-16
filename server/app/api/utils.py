# ===========================================
# app/api/utils.py - 유틸리티 및 AI 관련
# ===========================================
from fastapi import APIRouter, Depends, HTTPException
from starlette.concurrency import run_in_threadpool
import openai
import logging

from app.schemas import (
    TranslationRequest, TranslationResponse, 
    AIChatRequest, AIChatResponse
)
from app.core.dependencies import get_translation_service, get_llm_service

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/util/translate", response_model=TranslationResponse)
async def translate_text(
    req: TranslationRequest,
    ts = Depends(get_translation_service)
):
    """텍스트 번역"""
    try:
        translated_text = await run_in_threadpool(ts.translate_to_korean, req.text)
        return {"translated_text": translated_text}
    except Exception as e:
        logger.error(f"번역 오류: {e}")
        raise HTTPException(status_code=500, detail="번역 중 오류가 발생했습니다.")

@router.post("/ai/chat", response_model=AIChatResponse)
async def chat_with_ai(
    req: AIChatRequest,
    llm = Depends(get_llm_service)
):
    """LLM 기반 주식 분석 Q&A"""
    try:
        response = await llm.get_qa_response(
            symbol=req.symbol,
            user_question=req.question,
            financial_data=req.financial_data,
            history_data=req.history_data,
            news_data=req.news_data
        )
        return {"response": response}
    except openai.APIError as e:
        logger.error(f"OpenAI API 오류 발생: {e.status_code} - {e.message}")
        raise HTTPException(
            status_code=e.status_code or 503, 
            detail=f"AI 서비스에 문제가 발생했습니다: {e.message}"
        )
    except Exception as e:
        logger.error(f"AI 채팅 오류: {e}")
        raise HTTPException(status_code=500, detail="AI 서비스 오류가 발생했습니다.")
