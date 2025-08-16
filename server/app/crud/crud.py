from sqlalchemy.orm import Session
from app.models import models
from app.services.korea_investment_service import KoreaInvestmentService
from data.securites_trading_fee import TRADING_FEES
import time

kis_service = KoreaInvestmentService()

def create_transaction(db: Session, transaction: models.Transaction):
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction

def get_portfolio(db: Session):
    """
    전체 포트폴리오 잔고를 계산합니다.
    휴일/주말을 고려하여 가장 최근 영업일의 종가를 현재가/전일가로 사용합니다.
    """
    all_buys = db.query(models.Transaction).filter(models.Transaction.transaction_type == 'BUY').all()
    all_sells = db.query(models.Transaction).filter(models.Transaction.transaction_type == 'SELL').all()

    holdings = {}
    
    for buy in all_buys:
        if buy.stock_code not in holdings:
            holdings[buy.stock_code] = {
                'quantity': 0, 'total_buy_amount': 0, 'total_buy_commission': 0,
                'name': buy.stock_name, 'market': buy.market.value
            }
        buy_amount = buy.quantity * buy.price
        commission_rate = TRADING_FEES['DOMESTIC_FEE']['buy_commission_rate'] if buy.market.value == 'KOR' else TRADING_FEES['OVERSEAS_FEE']['buy_commission_rate']
        commission = buy_amount * commission_rate
        holdings[buy.stock_code]['quantity'] += buy.quantity
        holdings[buy.stock_code]['total_buy_amount'] += buy_amount
        holdings[buy.stock_code]['total_buy_commission'] += commission

    for sell in all_sells:
        if sell.stock_code in holdings:
            holdings[sell.stock_code]['quantity'] -= sell.quantity

    portfolio_list = []
    total_purchase_amount_including_fees = 0

    for code, data in holdings.items():
        if data['quantity'] > 1e-9:
            total_bought_quantity = data['quantity'] + sum(s.quantity for s in all_sells if s.stock_code == code)
            total_cost = data['total_buy_amount'] + data['total_buy_commission']
            bep_price = total_cost / total_bought_quantity if total_bought_quantity > 0 else 0
            
            item = {'stock_code': code, 'stock_name': data['name'], 'market': data['market'],
                    'quantity': data['quantity'], 'average_price': bep_price}
            portfolio_list.append(item)
            total_purchase_amount_including_fees += item['quantity'] * item['average_price']
            
    total_assets = 0
    total_days_gain = 0

    for item in portfolio_list:
        # --- 🌟 여기가 핵심: 견고하게 수정된 가격 조회 함수를 사용합니다. ---
        # 1. 현재가 조회 (오늘 기준 가장 최근 영업일 종가)
        price_str = kis_service.get_current_price(item['market'], item['stock_code'])
        current_price = float(price_str) if price_str and price_str.replace('.', '', 1).isdigit() else 0.0
        
        # 2. 전일 종가 조회 (어제 기준 가장 최근 영업일 종가)
        prev_close_str = kis_service.get_previous_day_price(item['market'], item['stock_code'])
        # 전일 종가를 찾지 못하면, 보수적으로 현재가와 동일하게 처리하여 일일 손익을 0으로 만듭니다.
        prev_close_price = float(prev_close_str) if prev_close_str and prev_close_str.replace('.', '', 1).isdigit() else current_price
        
        days_gain = (current_price - prev_close_price) * item['quantity']
        
        item['days_gain'] = days_gain
        total_days_gain += days_gain
        
        purchase_amount_bep = item['average_price'] * item['quantity']
        valuation = current_price * item['quantity']
        profit_loss = valuation - purchase_amount_bep
        return_rate = (profit_loss / purchase_amount_bep) * 100 if purchase_amount_bep > 0 else 0
        
        item.update({
            'current_price': current_price, 'valuation': valuation,
            'profit_loss': profit_loss, 'return_rate': return_rate
        })
        total_assets += valuation

    total_profit_loss = total_assets - total_purchase_amount_including_fees
    total_return_rate = (total_profit_loss / total_purchase_amount_including_fees) * 100 if total_purchase_amount_including_fees > 0 else 0

    return {
        "portfolio": portfolio_list,
        "total_assets": total_assets,
        "total_profit_loss": total_profit_loss,
        "total_return_rate": total_return_rate,
        "total_days_gain": total_days_gain,
    }

def get_holding_by_stock_code(db: Session, stock_code: str):
    """ 특정 종목의 잔고를 계산합니다. """
    portfolio_data = get_portfolio(db)
    for holding in portfolio_data['portfolio']:
        if holding['stock_code'] == stock_code:
            return holding
    return None