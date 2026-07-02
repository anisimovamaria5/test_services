from analytics_worker.repositories import StockAggRepository
from shared.config import Channels
from shared.logger import get_logger

logger = get_logger(__name__)

class StockAggregator:
    """Сервис агрегации событий"""
    
    def __init__(self):
        self.repo = StockAggRepository()
    
    async def process_event(self, conn, event) -> None:
        """Обработка события и обновление агрегатов"""

        if event.type == Channels.RECEIPT:
            delta = event.qty
        elif event.type == Channels.ISSUE:
            delta = -event.qty
        else:
            logger.warning(f"Неизвестный тип события: {event.type}")
            return
        
        await self.repo.update_stock(
            conn=conn,
            sku=event.sku,
            warehouse=event.warehouse,
            delta=delta
        )
        
        logger.debug(f"Aggregated: sku={event.sku}, delta={delta}, warehouse={event.warehouse}")