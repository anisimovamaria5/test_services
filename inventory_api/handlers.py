from aiohttp import web
from sqlalchemy import desc, func, insert, select

from inventory_api.config import Channels
from inventory_api.database import async_engine
from inventory_api.models import stock_agg, stock_events
from inventory_api.redis_pub import publish_event
from shared.schemas import EventMessage, IssueRequest, ReceiptRequest, StockResponse, SummaryResponse, TopSkuResponse


class Handlers:
    """Класс-обработчик всех HTTP-запросов"""

    async def post_receipts(self, request: web.Request) -> web.Response:
        """
            Обработчик POST /receipts
            
            Args:
                request: HTTP запрос с JSON body {sku, qty, warehouse}
                
            Returns:
                web.Response: JSON с статусом операции
                
            Пример:
                POST /receipts
                {"sku": "A-100", "qty": 50, "warehouse": "WH-1"}
        """

        res = await request.json()

        try:
            validated = ReceiptRequest(**res)
        except Exception as e:
            return web.json_response(
                {'error': 'Неверные данные', 'Детали': str(e)},
                status=400
            )

        async with async_engine.begin() as conn:
            await conn.execute(
                insert(stock_events).values(
                    sku=validated.sku, 
                    qty=validated.qty, 
                    warehouse=validated.warehouse, 
                    event='receipts'
                )
            )
            event = EventMessage(
                type=Channels.RECEIPT,
                sku=validated.sku,
                qty=validated.qty,
                warehouse=validated.warehouse
            )
            await publish_event(Channels.RECEIPT, event.model_dump_json())


        return web.json_response({'status': 'ok'})

    async def post_issues(self, request: web.Request) -> web.Response:
        """
            Обработчик POST /issues
            
            Args:
                request: HTTP запрос с JSON body {sku, qty, warehouse}
                
            Returns:
                web.Response: JSON с статусом операции
                
            Пример:
                POST /issues
                {"sku": "A-100", "qty": 50, "warehouse": "WH-1"}
        """

        res = await request.json()

        try:
            validated = IssueRequest(**res)
        except Exception as e:
            return web.json_response(
                {'error': 'Неверные данные', 'Детали': str(e)},
                status=400
            )

        async with async_engine.begin() as conn:
            await conn.execute(
                insert(stock_events).values(
                    sku=validated.sku,
                    qty=-validated.qty,
                    warehouse=validated.warehouse,
                    event='issue'
                )
            )

            event = EventMessage(
                type=Channels.ISSUE,
                sku=validated.sku,
                qty=validated.qty,
                warehouse=validated.warehouse
            )
            await publish_event(Channels.ISSUE, event.model_dump_json())

        return web.json_response({'status': 'ok'})
    
    async def get_stock(self, request: web.Request) -> web.Response:
        """
            Обработчик GET /stock
            
            Возвращает текущие остатки по указанному складу.
            Можно фильтровать по sku.
            
            Args:
                request: HTTP запрос с query параметрами

            Returns:
                web.Response: JSON со списком остатков

            Пример:
            GET /stock?warehouse=WH-1&sku=A-100
        """

        sku = request.query.get('sku')
        warehouse = request.query.get('warehouse')

        if not warehouse:
                return web.json_response(
                    {'error': 'warehouse parameter is required'},
                    status=400
                )
        
        query = select(stock_agg.c.sku, stock_agg.c.total_qty).where(
            stock_agg.c.warehouse == warehouse
        )
        if sku:
            query = query.where(stock_agg.c.sku == sku)

        async with async_engine.connect() as conn:
            res = await conn.execute(query)
            rows = res.fetchall()

        response = [
                StockResponse(
                    sku=row.sku, 
                    total_qty=row.total_qty
            ).model_dump()
                for row in rows
            ]

        return web.json_response(response)
    
    async def get_stock_summary(self, request: web.Request) -> web.Response:
        """
            Обработчик GET /stock/summary
            
            Возвращает агрегированную статистику по складам и топ-sku
            
            Args:
                request: HTTP запрос с query параметрами

            Returns:
                web.Response: JSON с агрегированной статистикой
            
            Пример:
                GET /stock/summary?top_n=5
        """

        top_n_param = request.query.get('top_n', 5)

        try:
            top_n = int(top_n_param)
            if top_n < 1:
                top_n = 5
        except ValueError:
            top_n = 5
            
        async with async_engine.connect() as conn:
            data_warehouse = select(
                stock_agg.c.warehouse,
                func.sum(stock_agg.c.total_qty).label('total_qty'),
                func.count(stock_agg.c.sku).label('sku_count')
            ).group_by(stock_agg.c.warehouse)

            res_warehouses = await conn.execute(data_warehouse)
            warehouses = res_warehouses.fetchall()

            data_top_skus = select(
                stock_agg.c.sku,
                func.sum(stock_agg.c.total_qty).label('total_qty')
            ).group_by(stock_agg.c.sku).subquery()

            top_limit = select(data_top_skus).order_by(
                    desc(data_top_skus.c.total_qty)
                ).limit(top_n)
            res_top_skus = await conn.execute(top_limit)

            top_skus = [
                TopSkuResponse(sku=row.sku, total_qty=row.total_qty).model_dump()
                for row in res_top_skus.fetchall()
            ]

            response = [
                SummaryResponse(
                    warehouse=row.warehouse,
                    total_qty=row.total_qty,
                    sku_count=row.sku_count,
                    top_skus=top_skus
                ).model_dump()
                for row in warehouses
            ]

        return web.json_response(response)