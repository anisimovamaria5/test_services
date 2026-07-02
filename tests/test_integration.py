import time
import uuid
import pytest
import asyncio
from aiohttp import ClientSession

pytestmark = pytest.mark.asyncio

BASE_URL = "http://inventory_api:8080"

class TestReceipts:

    async def test_receipt_success(self):
        """Успешный приход"""
        sku = f"TEST-{uuid.uuid4().hex[:8]}"
        warehouse = f"WH-{uuid.uuid4().hex[:8]}"
        
        async with ClientSession() as session:
            resp = await session.post(
                f'{BASE_URL}/receipts',
                json={'sku': sku, 'qty': 50, 'warehouse': warehouse}
            )
            assert resp.status == 200
            data = await resp.json()
            assert data['status'] == 'ok'

    async def test_receipt_invalid_qty(self):
        """Некорректное количество"""
        async with ClientSession() as session:
            resp = await session.post(
                f'{BASE_URL}/receipts',
                json={'sku': 'A-100', 'qty': -10, 'warehouse': 'WH-1'}
            )
            assert resp.status == 400
            data = await resp.json()
            assert 'error' in data

    async def test_receipt_missing_fields(self):
        """Отсутствуют поля"""
        async with ClientSession() as session:
            resp = await session.post(
                f'{BASE_URL}/receipts',
                json={'sku': 'A-100', 'qty': 50}
            )
            assert resp.status == 400
            data = await resp.json()
            assert 'error' in data


class TestStock:
    """Проверка остатков"""

    async def test_stock_after_receipt(self):
        """Проверка остатков после прихода"""
        sku = f"TEST-{uuid.uuid4().hex[:8]}"
        warehouse = f"WH-{uuid.uuid4().hex[:8]}"
        
        async with ClientSession() as session:
            await session.post(
                f'{BASE_URL}/receipts',
                json={'sku': sku, 'qty': 50, 'warehouse': warehouse}
            )
            await asyncio.sleep(3)
            
            resp = await session.get(
                f'{BASE_URL}/stock?warehouse={warehouse}&sku={sku}'
            )
            assert resp.status == 200
            data = await resp.json()
            assert data[0]['total_qty'] == 50

    async def test_stock_after_issue(self):
        """Проверка остатков после расхода"""
        sku = f"TEST-{uuid.uuid4().hex[:8]}"
        warehouse = f"WH-{uuid.uuid4().hex[:8]}"
        
        async with ClientSession() as session:
            await session.post(
                f'{BASE_URL}/receipts',
                json={'sku': sku, 'qty': 50, 'warehouse': warehouse}
            )
            await session.post(
                f'{BASE_URL}/issues',
                json={'sku': sku, 'qty': 20, 'warehouse': warehouse}
            )
            await asyncio.sleep(3)
            
            resp = await session.get(
                f'{BASE_URL}/stock?warehouse={warehouse}&sku={sku}'
            )
            assert resp.status == 200
            data = await resp.json()
            assert data[0]['total_qty'] == 30


class TestSummary:
    """Проверка сводки по складам"""

    async def test_summary_contains_warehouse(self):
        """Сводка содержит склад"""
        sku = f"TEST-{uuid.uuid4().hex[:8]}"
        warehouse = f"WH-{uuid.uuid4().hex[:8]}"
        
        async with ClientSession() as session:
            await session.post(
                f'{BASE_URL}/receipts',
                json={'sku': sku, 'qty': 50, 'warehouse': warehouse}
            )
            await asyncio.sleep(3)
            
            resp = await session.get(f'{BASE_URL}/stock/summary')
            summary = await resp.json()
            
            wh_data = next((item for item in summary if item['warehouse'] == warehouse), None)
            assert wh_data is not None
            assert wh_data['total_qty'] == 50
            assert wh_data['sku_count'] >= 1