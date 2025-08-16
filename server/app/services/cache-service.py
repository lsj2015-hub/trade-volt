# ===========================================
# server/app/services/cache_service.py 캐싱 서비스
# ===========================================

import redis
import json
import hashlib
from typing import Optional, Any
import logging

logger = logging.getLogger(__name__)

class CacheService:
    def __init__(self):
        try:
            self.redis_client = redis.Redis(
                host='localhost', 
                port=6379, 
                db=0, 
                decode_responses=True,
                socket_timeout=1
            )
            # 연결 테스트
            self.redis_client.ping()
            self.enabled = True
            logger.info("✅ Redis 캐시 연결 성공")
        except Exception as e:
            logger.warning(f"⚠️ Redis 연결 실패, 캐싱 비활성화: {e}")
            self.redis_client = None
            self.enabled = False
    
    def _generate_key(self, prefix: str, **kwargs) -> str:
        """캐시 키 생성"""
        key_data = json.dumps(kwargs, sort_keys=True)
        key_hash = hashlib.md5(key_data.encode()).hexdigest()[:8]
        return f"{prefix}:{key_hash}"
    
    def get(self, prefix: str, **kwargs) -> Optional[Any]:
        """캐시에서 데이터 조회"""
        if not self.enabled:
            return None
            
        try:
            key = self._generate_key(prefix, **kwargs)
            cached_data = self.redis_client.get(key)
            if cached_data:
                return json.loads(cached_data)
        except Exception as e:
            logger.warning(f"캐시 조회 실패: {e}")
        return None
    
    def set(self, prefix: str, data: Any, ttl: int = 3600, **kwargs) -> bool:
        """캐시에 데이터 저장"""
        if not self.enabled:
            return False
            
        try:
            key = self._generate_key(prefix, **kwargs)
            self.redis_client.setex(key, ttl, json.dumps(data))
            return True
        except Exception as e:
            logger.warning(f"캐시 저장 실패: {e}")
            return False

# 전역 캐시 인스턴스
cache_service = CacheService()