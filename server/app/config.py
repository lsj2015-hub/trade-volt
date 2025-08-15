from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # .env 파일에서 환경 변수를 로드하도록 설정
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

    # --- ✅ OpenAI API ---
    OPENAI_API_KEY: str
    
    # --- ✅ KIWOOM API --- 
    KIWOOM_APP_KEY: str
    KIWOOM_SECRET_KEY: str
    KIWOOM_BASE_URL: str

    # --- ✅ KIWOOM API --- 
    KIS_APP_KEY: str
    KIS_APP_SECRET: str
    KIS_BASE_URL: str

    # --- ✅ NAVER API --- 
    NAVER_CLIENT_ID: str
    NAVER_CLIENT_SECRET: str

    # --- ✅ DART API ---
    DART_API_KEY: str

    # stock_list.json 경로 지정
    STOCK_LIST_JSON: str | None = None

    # 환율 API 기본 URL
    EXCHANGE_RATE_API_URL: str = "https://api.frankfurter.app/latest"
    
    # 환율 정보 캐시 지속 시간 (초), 기본값 1시간
    CACHE_TTL_SECONDS: int = 3600
    
    # 환율 조회 실패 시 사용할 기본값
    DEFAULT_KRW_RATE: float = 1350.0

# 설정 객체 생성 (애플리케이션 전체에서 이 객체를 통해 설정을 참조)
settings = Settings()