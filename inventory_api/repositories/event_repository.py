from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncConnection
from shared.models import stock_events

class EventRepository:
    """Репозиторий для работы с событиями"""
    
    async def create_event(
        self, 
        conn: AsyncConnection,
        sku: str, 
        qty: int, 
        warehouse: str, 
        event_type: str
    ) -> int:
        """Создание события"""
        
        result = await conn.execute(
            insert(stock_events).values(
                sku=sku,
                qty=qty,
                warehouse=warehouse,
                event=event_type
            ).returning(stock_events.c.id)
        )
        row = result.fetchone()
        return row.id if row else None