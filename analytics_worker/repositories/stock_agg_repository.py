from sqlalchemy import select, insert, update
from sqlalchemy.ext.asyncio import AsyncConnection
from shared.models import stock_agg

class StockAggRepository:
    """Репозиторий для обновления"""
    
    async def update_stock(self, conn: AsyncConnection, sku: str, warehouse: str, delta: int) -> None:
        """Обновление остатка (создает запись, если ее нет)"""
        
        stmt = select(stock_agg).where(
            stock_agg.c.sku == sku,
            stock_agg.c.warehouse == warehouse
        )
        result = await conn.execute(stmt)
        row = result.fetchone()
        
        if row:
            new_qty = row.total_qty + delta
            await conn.execute(
                update(stock_agg).where(
                    stock_agg.c.sku == sku,
                    stock_agg.c.warehouse == warehouse
                ).values(total_qty=new_qty)
            )
        else:
            await conn.execute(
                insert(stock_agg).values(
                    sku=sku,
                    warehouse=warehouse,
                    total_qty=delta
                )
            )