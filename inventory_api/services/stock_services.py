from sqlalchemy.ext.asyncio import AsyncConnection

from inventory_api.repositories import EventRepository, StockRepository
from inventory_api.redis_pub import publish_event
from shared.config import Channels
from shared.schemas import EventMessage
from shared.logger import get_logger

logger = get_logger(__name__)

class StockService:
    """Бизнес-логика управления складом"""
    
    def __init__(self):
        self.event_repo = EventRepository()
        self.stock_repo = StockRepository()
    
    async def process_receipt(self, conn: AsyncConnection, sku: str, qty: int, warehouse: str) -> int:
        """Обработка прихода товара"""

        event_id = await self.event_repo.create_event(
            conn=conn,
            sku=sku,
            qty=qty, 
            warehouse=warehouse,
            event_type='receipts'
        )

        event = EventMessage(
            type=Channels.RECEIPT,
            sku=sku,
            qty=qty,
            warehouse=warehouse
        )
        await publish_event(Channels.RECEIPT, event.model_dump_json())
        
        logger.info(f"Receipt processed: sku={sku}, qty={qty}, warehouse={warehouse}")
        return event_id
    
    async def process_issue(self, conn: AsyncConnection, sku: str, qty: int, warehouse: str) -> int:
        """Обработка расхода товара"""

        stock = await self.stock_repo.get_stock(conn, warehouse, sku)
        current_qty = stock[0]['total_qty'] if stock else 0
        
        if current_qty < qty:
            raise ValueError(f"Not enough stock. Available: {current_qty}, requested: {qty}")
        
        event_id = await self.event_repo.create_event(
            conn=conn,
            sku=sku,
            qty=-qty, 
            warehouse=warehouse,
            event_type='issue'
        )
        
        event = EventMessage(
            type=Channels.ISSUE,
            sku=sku,
            qty=qty,
            warehouse=warehouse
        )
        await publish_event(Channels.ISSUE, event.model_dump_json())
        
        logger.info(f"Issue processed: sku={sku}, qty={qty}, warehouse={warehouse}")
        return event_id
    
    async def get_stock(self, conn: AsyncConnection, warehouse: str, sku: str = None) -> list:
        """Получение остатков"""
        
        return await self.stock_repo.get_stock(conn, warehouse, sku)
    
    async def get_summary(self, conn, top_n: int = 5) -> list:
        """Получение сводки"""

        data = await self.stock_repo.get_summary(conn, top_n)
        
        top_skus = [
            {'sku': row.sku, 'total_qty': row.total_qty}
            for row in data['top_skus']
        ]
        
        return [
            {
                'warehouse': row.warehouse,
                'total_qty': row.total_qty,
                'sku_count': row.sku_count,
                'top_skus': top_skus
            }
            for row in data['warehouses']
        ]