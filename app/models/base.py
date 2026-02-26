from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class CoreModel(BaseModel):
    """
    Base model for all schemas to provide standard fields.
    """
    model_config = ConfigDict(from_attributes=True)
    
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
