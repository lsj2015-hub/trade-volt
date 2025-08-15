import requests
import json
import os
import io
import zipfile
from datetime import datetime, timedelta
from typing import List
import logging

from app.config import settings
from app.schemas import StockItem, OverseasStockSearchResponse, TokenData

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class KoreaInvestmentService:
    def __init__(self):
        self.APP_KEY = settings.KIS_APP_KEY
        self.APP_SECRET = settings.KIS_APP_SECRET
        self.BASE_URL = settings.KIS_BASE_URL
        self._token_data_path = "kis_token.json"
        
        logger.info(f"✅ KIS Service initializing for REAL server: {self.BASE_URL}")
        
