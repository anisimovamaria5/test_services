from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncConnection
from shared.models import stock_agg

class StockRepository:
    """Репозиторий для работы с агрегатами"""
    
    async def get_stock(self, conn: AsyncConnection, warehouse: str, sku: str = None) -> list:
        """Получение остатков по складу"""
        query = select(stock_agg.c.sku, stock_agg.c.total_qty).where(
            stock_agg.c.warehouse == warehouse
        )
        if sku:
            query = query.where(stock_agg.c.sku == sku)
        
        result = await conn.execute(query)
        rows = result.fetchall()
        return [
            {'sku': row.sku, 'total_qty': row.total_qty}
            for row in rows
        ]
    
    async def get_summary(self, conn: AsyncConnection, top_n: int) -> dict:
        """Получение сводки по складам и топ-SKU"""

        warehouse_query = select(
            stock_agg.c.warehouse,
            func.sum(stock_agg.c.total_qty).label('total_qty'),
            func.count(stock_agg.c.sku).label('sku_count')
        ).group_by(stock_agg.c.warehouse)
        
        result = await conn.execute(warehouse_query)
        warehouses = result.fetchall()
        
        top_skus_query = select(
            stock_agg.c.sku,
            func.sum(stock_agg.c.total_qty).label('total_qty')
        ).group_by(stock_agg.c.sku).order_by(
            desc('total_qty')
        ).limit(top_n)
        
        result = await conn.execute(top_skus_query)
        top_skus = result.fetchall()
        
        return {
            'warehouses': warehouses,
            'top_skus': top_skus
        }