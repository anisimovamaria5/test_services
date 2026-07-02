from sqlalchemy import Table, Column, Integer, String, DateTime, func, MetaData

metadata = MetaData()

stock_events = Table(
    'stock_events',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('sku', String, nullable=False),
    Column('qty', Integer, nullable=False),
    Column('warehouse', String, nullable=False),
    Column('event', String, nullable=False),
    Column('event_time', DateTime, server_default=func.now())
)

stock_agg = Table(
    'stock_agg',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('sku', String, nullable=False),
    Column('warehouse', String, nullable=False),
    Column('total_qty', Integer, nullable=False),
    Column('updated_time', DateTime, server_default=func.now())
)
