import requests
import json
from datetime import datetime, timedelta
import logging
from ..config import settings, Settings

logger = logging.getLogger(__name__)

class KiwoomAuth:
  def __init__(self, settings: Settings):
    self.settings = settings
    self.APP_KEY = settings.KIWOOM_APP_KEY
    self.APP_SECRET = settings.KIWOOM_SECRET_KEY
    self.BASE_URL = settings.KIWOOM_BASE_URL
    self.access_token = None
    self.token_expires_at = None
    if not all([self.APP_KEY, self.APP_SECRET, self.BASE_URL]):
      logger.error("❌ .env 파일에서 API 키를 로드하는 데 실패했습니다.")
    else:
      logger.info("✅ 인증 모듈 초기화 완료.")

  def _issue_token(self):
    """
    Kiwoom REST API 공식 가이드에 따라 인증 토큰을 발급받습니다.
    """
    url = f"{self.BASE_URL}/oauth2/token"
    headers = { "Content-Type": "application/json;charset=UTF-8" }
    body = {
      "grant_type": "client_credentials", 
      "appkey": self.APP_KEY, 
      "secretkey": self.APP_SECRET
    }

    try:
      response = requests.post(url, headers=headers, data=json.dumps(body))
      response.raise_for_status()
      token_data = response.json()
      if "token" in token_data:
        self.access_token = token_data["token"]
        expires = datetime.strptime(token_data["expires_dt"], "%Y%m%d%H%M%S")
        self.token_expires_at = expires - timedelta(minutes=5)
        logger.info("✅ 신규 접근 토큰 발급 성공.")
        return True
      else:
        logger.error(f"❌ 토큰 발급 실패: {token_data.get('return_msg', '알 수 없는 오류')}")
        return False
    except requests.exceptions.RequestException as e:
      logger.error(f"❌ API 요청 실패: {e}")
      return False

  def get_access_token(self):
    """
    유효한 액세스 토큰을 반환합니다. 만료되었거나 없는 경우 새로 발급받습니다.
    """
    if self.access_token and self.token_expires_at and self.token_expires_at > datetime.now():
      logger.debug("기존 토큰을 재사용합니다.")
      return self.access_token
      
    if self._issue_token():
      return self.access_token
      
    return None
  
# 애플리케이션 전체에서 공유할 싱글턴(Singleton) 인스턴스 생성
auth_instance = KiwoomAuth(settings=settings)