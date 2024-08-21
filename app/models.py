from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class DiscoveryAccountRequest(BaseModel):
    user_name: str = Field(..., description="User name of the account to discover")
    fecha_desde: str = Field(..., description="Start date in DD/MM/AAAA format")
    account_metrics: Optional[List[str]] = Field(None, description="Optional list of account metrics")
    media_metrics: Optional[List[str]] = Field(None, description="Optional list of media metrics")
    
    class Config:
        schema_extra = {
            "example": {
                "user_name": "example_user",
                "fecha_desde": "01/01/2024",
                "account_metrics": ["account_metric1", "account_metric2"],
                "media_metrics": ["media_metric1", "media_metric2"]
            }
        }
    
    @staticmethod
    def validate_fecha_desde(fecha_desde: str) -> datetime:
        try:
            return datetime.strptime(fecha_desde, "%d/%m/%Y")
        except ValueError:
            raise ValueError("fecha_desde must be in DD/MM/AAAA format")