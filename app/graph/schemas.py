from typing import Literal
from pydantic import BaseModel


class SourceRouteDecision(BaseModel):
    source_route: Literal["docs", "code", "both", "none"]