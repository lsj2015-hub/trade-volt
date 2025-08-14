import requests
import json
import logging
from datetime import datetime
import pandas as pd
from .kiwoom_auth import auth_instance

logger = logging.getLogger(__name__)

class KiwoomDataHandler:
  """키움증권 API를 이용한 데이터 조회를 담당하는 클래스"""
  def __init__(self, auth_handler=auth_instance):
    self.auth = auth_handler
    self.BASE_URL = self.auth.BASE_URL
    logger.info("✅ 데이터 핸들러가 성공적으로 초기화되었습니다.")

  

# 데이터 핸들러 싱글턴 인스턴스 생성
data_handler_instance = KiwoomDataHandler()