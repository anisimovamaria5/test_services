from pydantic import BaseModel, Field, PositiveInt, model_validator
from typing import Optional


class ReceiptRequest(BaseModel):
    sku: str = Field(..., min_length=1, max_length=50)
    qty: PositiveInt
    warehouse: str = Field(..., min_length=1, max_length=50)
    
    @model_validator(mode='after')
    def to_upper(self):
        self.sku = self.sku.upper()
        self.warehouse = self.warehouse.upper()
        return self


class IssueRequest(BaseModel):
    sku: str = Field(..., min_length=1, max_length=50)
    qty: PositiveInt
    warehouse: str = Field(..., min_length=1, max_length=50)
    
    @model_validator(mode='after')
    def to_upper(self):
        self.sku = self.sku.upper()
        self.warehouse = self.warehouse.upper()
        return self


class StockResponse(BaseModel):
    sku: str
    total_qty: int


class TopSkuResponse(BaseModel):
    sku: str
    total_qty: int


class SummaryResponse(BaseModel):
    warehouse: str
    total_qty: int
    sku_count: int
    top_skus: list[TopSkuResponse]


class EventMessage(BaseModel):
    type: str
    sku: str
    qty: int
    warehouse: str
    timestamp: Optional[str] = None