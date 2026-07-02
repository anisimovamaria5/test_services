from aiohttp import web
from inventory_api.services import StockService
from shared.database import async_engine
from shared.schemas import ReceiptRequest, IssueRequest, StockResponse, SummaryResponse
from shared.logger import get_logger

logger = get_logger(__name__)

class Handlers:
    """HTTP-обработчики для API"""
    
    def __init__(self):
        self.stock_service = StockService()
    
    async def post_receipts(self, request: web.Request) -> web.Response:
        """POST /receipts"""

        try:
            data = await request.json()
            validated = ReceiptRequest(**data)
        except Exception as e:
            return web.json_response(
                {'error': 'Неверные данные', 'detail': str(e)},
                status=400
            )
        
        try:
            async with async_engine.begin() as conn:
                event_id = await self.stock_service.process_receipt(
                    conn=conn,
                    sku=validated.sku,
                    qty=validated.qty,
                    warehouse=validated.warehouse
                )
            
            return web.json_response({
                'status': 'ok',
                'event_id': event_id
            })
            
        except Exception as e:
            logger.error(f"Ошибка: {e}", exc_info=True)
            return web.json_response(
                {'error': 'Внутренняя ошибка сервера'},
                status=500
            )
    
    async def post_issues(self, request: web.Request) -> web.Response:
        """POST /issues"""

        try:
            data = await request.json()
            validated = IssueRequest(**data)
        except Exception as e:
            return web.json_response(
                {'error': 'Неверные данные', 'detail': str(e)},
                status=400
            )
        
        try:
            async with async_engine.begin() as conn:
                event_id = await self.stock_service.process_issue(
                    conn=conn,
                    sku=validated.sku,
                    qty=validated.qty,
                    warehouse=validated.warehouse
                )
            
            return web.json_response({
                'status': 'ok',
                'event_id': event_id
            })
            
        except ValueError as e:
            return web.json_response(
                {'error': str(e)},
                status=400
            )
        except Exception as e:
            logger.error(f"Ошибка: {e}", exc_info=True)
            return web.json_response(
                {'error': 'Внутренняя ошибка сервера'},
                status=500
            )
    
    async def get_stock(self, request: web.Request) -> web.Response:
        """GET /stock"""

        warehouse = request.query.get('warehouse')
        sku = request.query.get('sku')
        
        if not warehouse:
            return web.json_response(
                {'error': 'параметр warehouse является обязательным'},
                status=400
            )
        
        try:
            async with async_engine.connect() as conn:
                stock = await self.stock_service.get_stock(conn, warehouse, sku)
            
            response = [
                StockResponse(sku=item['sku'], total_qty=item['total_qty']).model_dump()
                for item in stock
            ]
            
            return web.json_response(response)
            
        except Exception as e:
            logger.error(f"Ошибка: {e}", exc_info=True)
            return web.json_response(
                {'error': 'Внутренняя ошибка сервера'},
                status=500
            )
    
    async def get_stock_summary(self, request: web.Request) -> web.Response:
        """GET /stock/summary"""

        top_n = request.query.get('top_n', 5)
        
        try:
            top_n = int(top_n)
            if top_n < 1:
                top_n = 5
        except ValueError:
            top_n = 5
        
        try:
            async with async_engine.connect() as conn:
                summary = await self.stock_service.get_summary(conn, top_n)
            
            response = [
                SummaryResponse(**item).model_dump()
                for item in summary
            ]
            
            return web.json_response(response)
            
        except Exception as e:
            logger.error(f"Ошибка: {e}", exc_info=True)
            return web.json_response(
                {'error': 'Внутренняя ошибка сервера'},
                status=500
            )