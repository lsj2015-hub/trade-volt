from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # .env 파일에서 환경 변수를 로드하도록 설정
    model_config = SettingsConfigDict(
        env_file='.env', 
        env_file_encoding='utf-8',
        case_sensitive=False,
        extra='ignore'  # 추가 환경변수 무시
    )

    # --- ✅ OpenAI API ---
    OPENAI_API_KEY: str

    # --- ✅ 한국투자증권 KIS API ---
    KIS_APP_KEY: str
    KIS_APP_SECRET: str 
    KIS_BASE_URL: str = "https://openapi.koreainvestment.com:9443"  # 기본값 설정

    # --- ✅ KIWOOM API --- 
    KIWOOM_APP_KEY: str
    KIWOOM_SECRET_KEY: str
    KIWOOM_BASE_URL: str = "https://openapi.kiwoom.com"  # 기본값 설정

    # --- ✅ NAVER API --- 
    NAVER_CLIENT_ID: str
    NAVER_CLIENT_SECRET: str

    # --- ✅ DART API ---
    DART_API_KEY: str

    # --- ✅ 데이터베이스 및 캐시 설정 ---
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = ""
    
    # --- ✅ 성능 분석 관련 설정 ---
    PERFORMANCE_CACHE_TTL: int = 3600  # 1시간
    PERFORMANCE_MAX_TICKERS: int = 1000
    PERFORMANCE_CHUNK_SIZE: int = 50
    PERFORMANCE_TIMEOUT: int = 5
    PERFORMANCE_MAX_CHUNKS: int = 20

    # --- ✅ 파일 경로 설정 ---
    STOCK_LIST_JSON: Optional[str] = None
    DATA_DIR: str = "data"  # 데이터 파일 저장 디렉토리

    # --- ✅ 환율 API 설정 ---
    EXCHANGE_RATE_API_URL: str = "https://api.frankfurter.app/latest"
    CACHE_TTL_SECONDS: int = 3600  # 환율 정보 캐시 지속 시간 (초)
    DEFAULT_KRW_RATE: float = 1400.0  # 환율 조회 실패 시 기본값

    # --- ✅ API 요청 설정 ---
    REQUEST_TIMEOUT: int = 30  # API 요청 타임아웃 (초)
    MAX_RETRIES: int = 3  # 최대 재시도 횟수
    
    # --- ✅ 로깅 설정 ---
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # --- ✅ CORS 설정 ---
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ]
    
    # --- ✅ 애플리케이션 설정 ---
    APP_NAME: str = "Trade Volt API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # --- ✅ 보안 설정 ---
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # --- ✅ 환경변수 검증 ---
    def __post_init__(self):
        """필수 환경변수가 설정되었는지 검증"""
        required_vars = [
            'OPENAI_API_KEY',
            'KIS_APP_KEY', 
            'KIS_APP_SECRET',
            'KIWOOM_APP_KEY',
            'KIWOOM_SECRET_KEY',
            'NAVER_CLIENT_ID',
            'NAVER_CLIENT_SECRET',
            'DART_API_KEY'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not getattr(self, var, None):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"다음 환경변수가 설정되지 않았습니다: {', '.join(missing_vars)}")

    @property
    def is_production(self) -> bool:
        """프로덕션 환경 여부 반환"""
        return not self.DEBUG

    @property
    def cors_origins(self) -> list[str]:
        """CORS 허용 오리진 목록 반환"""
        if self.is_production:
            # 프로덕션에서는 실제 도메인 사용
            return ["https://yourdomain.com"]
        return self.ALLOWED_ORIGINS

# 설정 객체 생성 (애플리케이션 전체에서 이 객체를 통해 설정을 참조)
settings = Settings()